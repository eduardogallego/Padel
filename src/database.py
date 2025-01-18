import json
import logging
import os
import sqlite3

from datetime import datetime
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

    def get_matches(self, filter_dict):
        cursor = self.connection.cursor()
        cursor.execute("SELECT m.match_date, p.name, "
                       "CASE WHEN m.rival2 IS NULL THEN r1.name "
                       "WHEN r1.name < r2.name THEN r1.name || ' / ' || r2.name "
                       "ELSE r2.name || ' / ' || r1.name "
                       "END AS rivals, m.result, m.partner, m.rival1, m.rival2 "
                       "FROM matches AS m LEFT JOIN players AS p ON m.partner = p.id "
                       "LEFT JOIN players AS r1 ON m.rival1 = r1.id "
                       "LEFT JOIN players AS r2 ON m.rival2 = r2.id "
                       "ORDER BY m.id DESC")
        rows = cursor.fetchall()
        result = []
        index = 0
        for row in rows:
            row_found = True
            for player in [filter_dict['player1'], filter_dict['player2'], filter_dict['player3']]:
                if player and row[4] != player and row[5] != player and row[6] != player:
                    row_found = False
                    break
            if filter_dict['year'] and filter_dict['year'] != datetime.strptime(row[0], '%Y-%m-%d').year:
                row_found = False
            if not filter_dict['1on1'] and row[1] is None:
                row_found = False
            if row_found:
                index += 1
                result.append({"index": index, "date": row[0], "partner": row[1], "rivals": row[2], "result": row[3]})
        return json.dumps(result)

    def get_players(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, name FROM players ORDER BY name')
        rows = cursor.fetchall()
        result = {0: 'none'}
        for row in rows:
            result[row[0]] = row[1]
        return result

    def get_partner_list_json(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT DISTINCT p.name FROM players p INNER JOIN matches m ON p.id = m.partner ORDER BY name')
        rows = cursor.fetchall()
        players = {}
        for row in rows:
            players[row[0]] = row[0]
        return json.dumps(players)

    def get_rival_list_json(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT name FROM players WHERE id IN '
                       '(SELECT rival1 FROM matches UNION SELECT rival2 FROM matches) ORDER BY name')
        rows = cursor.fetchall()
        players = {}
        for row in rows:
            players[row[0]] = row[0]
        return json.dumps(players)

    def get_players_json(self, filter_dict):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, name FROM players')
        rows = cursor.fetchall()
        players = {}
        for row in rows:
            players[int(row[0])] = {"player": row[1], "total": 0, "pt": 0, "pw": 0, "pd": 0, "pl": 0,
                                    "rt": 0, "rw": 0, "rd": 0, "rl": 0, "tw": 0, "td": 0, "tl": 0, }
        cursor.execute('SELECT partner, rival1, rival2, result, match_date FROM matches')
        rows = cursor.fetchall()
        for row in rows:
            row_found = True
            partner = row[0]
            rival1 = row[1]
            rival2 = row[2]
            result = row[3]
            date = row[4]
            for player in [filter_dict['player1'], filter_dict['player2'], filter_dict['player3']]:
                if player and partner != player and rival1 != player and rival2 != player:
                    row_found = False
                    break
            if filter_dict['year'] and filter_dict['year'] != datetime.strptime(date, '%Y-%m-%d').year:
                row_found = False
            if not filter_dict['1on1'] and not partner:
                row_found = False
            if not row_found:
                continue
            if partner is not None:
                player = players[partner]
                player['total'] += 1
                player['pt'] += 1
                if result is None:
                    player['pd'] += 1
                    player['td'] += 1
                elif result:
                    player['pw'] += 1
                    player['tw'] += 1
                else:
                    player['pl'] += 1
                    player['tl'] += 1
            for rival in [rival1, rival2]:
                if rival is not None:
                    player = players[rival]
                    player['total'] += 1
                    player['rt'] += 1
                    if result is None:
                        player['rd'] += 1
                        player['td'] += 1
                    elif result:
                        player['rw'] += 1
                        player['tw'] += 1
                    else:
                        player['rl'] += 1
                        player['tl'] += 1
        players = list(players.values())
        players = sorted(players, key=lambda k: (-k['total'], -k['tw'], -k['td'], -k['tl'], k['player'].lower()))
        players = [p for p in players if p['total'] > 0]
        result = []
        index = 0
        for player in players:
            index += 1
            result.append({'index': index, 'player': player['player'], 'total': player['total'],
                           'pw': player['pw'], 'pd': player['pd'], 'pl': player['pl'],
                           'rw': player['rw'], 'rd': player['rd'], 'rl': player['rl'],
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
