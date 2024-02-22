import logging
import sqlite3

from sqlite3 import Error


class Database:

    def __init__(self, config):
        self.db_file = config.get('database_file')
        self.logger = logging.getLogger('database')
        self.config = config
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
        except Error as e:
            self.logger.exception("Database Error")

    def get_players(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, name FROM players ORDER BY name')
        rows = cursor.fetchall()
        result = {0: 'none'}
        for row in rows:
            result[row[0]] = row[1]
        return result

    def insert_player(self, player):
        cursor = self.connection.cursor()
        cursor.execute(f'INSERT OR IGNORE INTO players(name) VALUES(?)', (player,))
        self.connection.commit()
        return cursor.rowcount

    def insert_match(self, match_date, partner, rival1, rival2, result):
        cursor = self.connection.cursor()
        cursor.execute(f'INSERT OR IGNORE INTO matches(match_date, partner, rival1, rival2, result) VALUES(?,?,?,?,?)',
                       (match_date, partner, rival1, rival2, result))
        self.connection.commit()
        return cursor.rowcount
