# Sutro

<img
src="http://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Sutro_Tower_from_Grandview.jpg/300px-Sutro_Tower_from_Grandview.jpg"
alt="Sutro Tower in San Francisco, photo by Justin Beck" align="right">

Sutro is a simple send-only WebSocket server. It is written in Python using
`gevent`. It receives messages on an AMQP exchange and sends them to all
relevant connected WebSocket clients. Sutro is agnostic to the content of the
messages.

### Usage

The main application is in charge of managing authorization. Sutro validates
that incoming requests were authorized by the main application using HMAC-SHA1
with a shared secret key and an expiration time. The path portion of a
websocket request indicates which message "namespace" the socket will receive.

Messages are sent to Sutro via an AMQP [fan out
exchange](http://www.rabbitmq.com/tutorials/amqp-concepts.html#exchanges).
Each Sutro worker process binds to the exchange and will receive all messages
sent to it.  Messages are dispatched to appropriate websocket clients by
mapping the message's routing key to the socket namespace specified in the
websocket request.

### Further reading

Sutro is used and written for reddit.com's socket needs. Client and server code
examples can be found in its repos:

* [r2/r2/lib/websockets.py](https://github.com/reddit/reddit/blob/master/r2/r2/lib/websockets.py)
* [r2/r2/public/static/js/websocket.js](https://github.com/reddit/reddit/blob/master/r2/r2/public/static/js/websocket.js)

### Thanks

The lovely picture of Sutro Tower to the right is by [Justin Beck]
(http://en.wikipedia.org/wiki/File:Sutro_Tower_from_Grandview.jpg).
