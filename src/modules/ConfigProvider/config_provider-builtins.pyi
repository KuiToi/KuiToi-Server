import secrets


class Config:
    def __init__(self, auth=None, game=None, server=None, options=None, web=None):
        self.Auth = auth or {"key": None, "private": True}
        self.Game = game or {"map": "gridmap_v2", "players": 8, "max_cars": 1}
        self.Server = server or {"name": "KuiToi-Server", "description": "Welcome to KuiToi Server!",
                                 "server_ip": "0.0.0.0", "server_port": 30814}
        self.Options = options or {"language": "en", "encoding": "utf8", "speed_limit": 0, "use_queue": False,
                                   "debug": False}
        self.WebAPI = web or {"enabled": False, "server_ip": "127.0.0.1", "server_port": 8433,
                              "secret_key": secrets.token_hex(16)}

    def __repr__(self):
        return "%s(Auth=%r, Game=%r, Server=%r)" % (self.__class__.__name__, self.Auth, self.Game, self.Server)
class config (Config): ...
