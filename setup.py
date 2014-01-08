from setuptools import setup

setup(
    name="sutro",
    version="0.2",
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
