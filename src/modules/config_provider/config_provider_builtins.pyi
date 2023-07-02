class Config:
    @staticmethod
    def __init__(self, auth=None, game=None, server=None):
        self.Auth = auth
        self.Game = game
        self.Server = server

    def __repr__(self):
        return "%s(Auth=%r, Game=%r, Server=%r)" % (self.__class__.__name__, self.Auth, self.Game, self.Server)

class config (Config): ...