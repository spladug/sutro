from setuptools import setup

setup(
    name="sutro",
    version="0.1",
    packages=[
        "sutro"
    ],
    install_requires=[
        "gevent",
        "gevent-websocket",
        "haigha",
        "PasteDeploy",
    ],
)
