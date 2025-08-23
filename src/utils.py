import json
import logging
import logging.handlers
import os


class Config:

    def __init__(self):
        with open(f'{os.path.dirname(os.path.realpath(__file__))}/../config/config.json', "r") as config_file:
            self._config = json.load(config_file)

    def get(self, parameter):
        return self._config.get(parameter)

    @staticmethod
    def get_default_filter():
        return {'minMatches': 3, 'player1': None, 'player2': None, 'player3': None, 'showDraw': True,
                'showLoss': True, 'showWin': True, 'show1on1': True, 'show2on2': True, 'year': 0}


class Logger:
    def __init__(self):
        handler = logging.handlers.WatchedFileHandler('padel.log')
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d - %(levelname)s [%(threadName)s]- %(name)s: %(message)s",
            datefmt="%d/%b/%Y %H:%M:%S"))
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(handler)


class User:
    def __init__(self, user_id, user_name, user_password):
        self.user_id = user_id
        self.user_name = user_name
        self.user_password = user_password
        self.authenticated = False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id

    def get_user_name(self):
        return self.user_name

    def login(self, password):
        self.authenticated = (password == self.user_password)
        return self.authenticated

    def logout(self):
        self.authenticated = False
