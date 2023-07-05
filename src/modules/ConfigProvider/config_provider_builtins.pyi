class Config:
    Auth: dict
    Game: dict
    Server: dict

    def __repr__(self):
        return "%s(Auth=%r, Game=%r, Server=%r)" % (self.__class__.__name__, self.Auth, self.Game, self.Server)

class config (Config): ...
