CLIENT_SERVER = {
    "host"  : "0.0.0.0",
    "port"  : 8000,
    "debug" : True
}

SHELL_SERVER = {
    "host"  : "10.1.10.16",
    "port"  : 8002
}

NODE_SERVER = {
    "host"  : "10.1.10.16",
    "port"  : 13002
}

DATABASE = {
    "host"      : "127.0.0.1",
    "user"      : "root",
    "passwd"    : "",
    "db"        : "telapi_classroom"
}

SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

try:
    from settings_local import *
except ImportError:
    pass
