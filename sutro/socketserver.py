import datetime
import hashlib
import hmac
import logging
import urlparse

import gevent
import geventwebsocket


LOG = logging.getLogger(__name__)


def is_subdomain(domain, base_domain):
    return domain == base_domain or domain.endswith("." + base_domain)


def is_allowed_origin(origin, whitelist):
    try:
        parsed = urlparse.urlparse(origin)
    except ValueError:
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    if parsed.port is not None and parsed.port not in (80, 443):
        return False

    for domain in whitelist:
        if is_subdomain(parsed.hostname, domain):
            return True
    return False


def constant_time_compare(actual, expected):
    """Return whether or not two strings match.

    The time taken is dependent on the number of characters provided instead of
    the number of characters that match which makes this function resistant to
    timing attacks.

    """
    actual_len = len(actual)
    expected_len = len(expected)
    result = actual_len ^ expected_len
    if expected_len > 0:
        for i in xrange(actual_len):
            result |= ord(actual[i]) ^ ord(expected[i % expected_len])
    return result == 0


class SocketServer(object):
    def __init__(self, dispatcher, allowed_origins, mac_secret):
        self.dispatcher = dispatcher
        self.allowed_origins = allowed_origins
        self.mac_secret = mac_secret

    def pump_messages(self, websocket):
        while websocket.receive():
            gevent.sleep()

    def send_broadcasts(self, websocket, namespace):
        try:
            for msg in self.dispatcher.listen(namespace):
                websocket.send(msg)
        except geventwebsocket.WebSocketError as e:
            LOG.debug("send failed: %r", e)
        finally:
            if not websocket.closed:
                websocket.close()

    def _get_validated_namespace(self, environ):
        namespace = environ.get("PATH_INFO", "")
        if not namespace:
            return

        try:
            query_string = environ["QUERY_STRING"]
            params = urlparse.parse_qs(query_string, strict_parsing=True)
            mac = params["h"][0]
            expires = params["e"][0]
            expiration_time = datetime.datetime.utcfromtimestamp(int(expires))
        except (KeyError, IndexError, ValueError):
            return

        if expiration_time < datetime.datetime.utcnow():
            return

        expected_mac = hmac.new(self.mac_secret, expires + namespace,
                                hashlib.sha1).hexdigest()
        if not constant_time_compare(mac, expected_mac):
            return

        return namespace

    def __call__(self, environ, start_response):
        websocket = environ.get("wsgi.websocket")

        if not websocket:
            start_response("400 Bad Request", [])
            return ["you are not a websocket"]

        if not is_allowed_origin(websocket.origin, self.allowed_origins):
            LOG.info("rejected connection from %s due to bad origin %r",
                     environ["REMOTE_ADDR"], websocket.origin)
            websocket.close(4003)
            return

        namespace = self._get_validated_namespace(environ)
        if not namespace:
            LOG.info("rejected connection from %s due to invalid namespace",
                     environ["REMOTE_ADDR"])
            websocket.close(4003)
            return

        listener = gevent.spawn(self.send_broadcasts, websocket, namespace)
        try:
            self.pump_messages(websocket)
        except geventwebsocket.WebSocketError as e:
            LOG.debug("receive failed: %r", e)
        finally:
            listener.kill(block=True)
