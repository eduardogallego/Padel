import json
import logging
import os
import sqlite3

from sqlite3 import Error
from src.utils import Config


class Database:

    def __init__(self, config):
        self.db_file = f"{os.path.dirname(os.path.realpath(__file__))}/../{config.get('database_file')}"
        self.logger = logging.getLogger('database')
        self.config = config
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
        except Error as e:
            self.logger.exception("Database Error")

    def get_matches(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT m.match_date, p.name, "
                       "CASE WHEN m.rival2 IS NULL THEN r1.name "
                       "WHEN r1.name < r2.name THEN r1.name || ' / ' || r2.name "
                       "ELSE r2.name || ' / ' || r1.name "
                       "END AS rivals, m.result "
                       "FROM matches AS m LEFT JOIN players AS p ON m.partner = p.id "
                       "LEFT JOIN players AS r1 ON m.rival1 = r1.id "
                       "LEFT JOIN players AS r2 ON m.rival2 = r2.id "
                       "ORDER BY m.match_date DESC")
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append({"date": row[0], "partner": row[1], "rivals": row[2], "result": row[3]})
        return json.dumps(result)

    def get_players(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, name FROM players ORDER BY name')
        rows = cursor.fetchall()
        result = {0: 'none'}
        for row in rows:
            result[row[0]] = row[1]
        return result

    def get_players_json(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, name FROM players')
        rows = cursor.fetchall()
        players = {}
        for row in rows:
            players[int(row[0])] = {"player": row[1], "total": 0, "pt": 0, "pw": 0, "pd": 0,
                                    "pl": 0, "rt": 0, "rw": 0, "rd": 0, "rl": 0}
        cursor.execute('SELECT partner, rival1, rival2, result FROM matches')
        rows = cursor.fetchall()
        for row in rows:
            partner = row[0]
            rival1 = row[1]
            rival2 = row[2]
            result = row[3]
            if partner is not None:
                player = players[partner]
                player['total'] += 1
                player['pt'] += 1
                if result is None:
                    player['pd'] += 1
                elif result:
                    player['pw'] += 1
                else:
                    player['pl'] += 1
            for rival in [rival1, rival2]:
                if rival is not None:
                    player = players[rival]
                    player['total'] += 1
                    player['rt'] += 1
                    if result is None:
                        player['rd'] += 1
                    elif result:
                        player['rw'] += 1
                    else:
                        player['rl'] += 1
        players = list(players.values())
        players = sorted(players, key=lambda k: (-k['total'], -k['pw'], -k['pd'], -k['pl'], k['player'].lower()))
        result = []
        for player in players:
            result.append({'player': player['player'], 'total': player['total'], 'pw': player['pw'], 'pd': player['pd'],
                           'pl': player['pl'], 'rw': player['rw'], 'rd': player['rd'], 'rl': player['rl'],
                           'pt': player['pt'], 'ps': f"{player['pw']}/{player['pd']}/{player['pl']}",
                           'rt': player['rt'], 'rs': f"{player['rw']}/{player['rd']}/{player['rl']}"})
        return json.dumps(result)

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


if __name__ == "__main__":
    configuration = Config()
    database = Database(configuration)
    # print(f"Matches: {database.get_matches()}")
    # print(f"Players: {json.dumps(database.get_players())}")
    # print(f"Players JSON: {database.get_players_json()}")
    pass
