import json
import logging
import math
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
            if not filter_dict['show1on1'] and row[1] is None:
                row_found = False
            if not filter_dict['show2on2'] and row[1] is not None:
                row_found = False
            if not filter_dict['showWin'] and row[3] == 1:
                row_found = False
            if not filter_dict['showDraw'] and row[3] is None:
                row_found = False
            if not filter_dict['showLoss'] and row[3] == 0:
                row_found = False
            if row_found:
                index += 1
                result.append({"index": index, "date": row[0], "partner": row[1], "rivals": row[2], "result": row[3]})
        return json.dumps(result)

    def get_players(self, filter_dict):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, long_name, '
                       '(SELECT COUNT(*) FROM matches WHERE partner = p.id OR rival1 = p.id OR rival2 = p.id) AS times '
                       'FROM players AS p WHERE times >= %d ORDER BY name' % filter_dict['minMatches'])
        rows = cursor.fetchall()
        result = {0: 'none'}
        for row in rows:
            result[row[0]] = row[1]
        return result

    def get_partner_list_json(self, filter_dict):
        cursor = self.connection.cursor()
        cursor.execute('SELECT name, (SELECT COUNT(*) FROM matches WHERE partner = p.id) AS times '
                       'FROM players AS p WHERE times >= %d ORDER BY name' % filter_dict['minMatches'])
        rows = cursor.fetchall()
        players = {}
        for row in rows:
            players[row[0]] = row[0]
        return json.dumps(players)

    def get_rival_list_json(self, filter_dict):
        cursor = self.connection.cursor()
        cursor.execute('SELECT name, (SELECT COUNT(*) FROM matches WHERE rival1 = p.id OR rival2 = p.id) AS times '
                       'FROM players AS p WHERE times >= %d ORDER BY name' % filter_dict['minMatches'])
        rows = cursor.fetchall()
        players = {}
        for row in rows:
            players[row[0]] = row[0]
        return json.dumps(players)

    def get_player_stats(self, filter_dict=Config.get_default_filter()):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, long_name FROM players')
        rows = cursor.fetchall()
        players = {}
        for row in rows:
            players[int(row[0])] = {"player": row[1], "total": 0, "pt": 0, "pw": 0, "pd": 0, "pl": 0,
                                    "rt": 0, "rw": 0, "rd": 0, "rl": 0, "tw": 0, "td": 0, "tl": 0}
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
            if not filter_dict['show1on1'] and not partner:
                row_found = False
            if not filter_dict['show2on2'] and partner:
                row_found = False
            if not filter_dict['showWin'] and result == 1:
                row_found = False
            if not filter_dict['showDraw'] and result is None:
                row_found = False
            if not filter_dict['showLoss'] and result == 0:
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
        others = {"player": "Others", "total": 0, "pt": 0, "pw": 0, "pd": 0, "pl": 0,
                  "rt": 0, "rw": 0, "rd": 0, "rl": 0, "tw": 0, "td": 0, "tl": 0, }
        for player in players:
            if player['total'] >= filter_dict['minMatches']:
                index += 1
                result.append({'index': index, 'player': player['player'], 'total': player['total'],
                               'pw': player['pw'], 'pd': player['pd'], 'pl': player['pl'],
                               'rw': player['rw'], 'rd': player['rd'], 'rl': player['rl'],
                               'pt': player['pt'], 'ps': f"{player['pw']}/{player['pd']}/{player['pl']}",
                               'rt': player['rt'], 'rs': f"{player['rw']}/{player['rd']}/{player['rl']}"})
            else:
                others['total'] += player['total']
                others['pw'] += player['pw']
                others['pd'] += player['pd']
                others['pl'] += player['pl']
                others['rw'] += player['rw']
                others['rd'] += player['rd']
                others['rl'] += player['rl']
                others['pt'] += player['pt']
                others['rt'] += player['rt']
        if others['total'] > 0:
            result.append({'index': index + 1, 'player': others['player'], 'total': others['total'],
                           'pw': others['pw'], 'pd': others['pd'], 'pl': others['pl'],
                           'rw': others['rw'], 'rd': others['rd'], 'rl': others['rl'],
                           'pt': others['pt'], 'ps': f"{others['pw']}/{others['pd']}/{others['pl']}",
                           'rt': others['rt'], 'rs': f"{others['rw']}/{others['rd']}/{others['rl']}"})
        return result

    def get_players_json(self, filter_dict):
        return json.dumps(self.get_player_stats(filter_dict))

    def get_statistics(self):
        messages = []
        cursor = self.connection.cursor()
        cursor.execute("SELECT match_date, result FROM matches")
        rows = cursor.fetchall()
        current_year = datetime.now().year
        matches_year = 0
        matches_total = 0
        wins_year = 0
        wins_total = 0
        draws_year = 0
        draws_total = 0
        loss_year = 0
        loss_total = 0
        date = None
        previous_date = None
        not_playing_days_year = 0
        not_playing_date_year = None
        not_playing_days_total = 0
        not_playing_date_total = None
        previous_win = None
        previous_loss = None
        not_loosing_days_year = 0
        not_loosing_date_year = None
        not_loosing_days_total = 0
        not_loosing_date_total = None
        not_winning_days_year = 0
        not_winning_date_year = None
        not_winning_days_total = 0
        not_winning_date_total = None
        not_wins_in_a_row = 0
        max_not_wins_in_a_row_year = 0
        max_not_wins_in_a_row_date_year = None
        max_not_wins_in_a_row_total = 0
        max_not_wins_in_a_row_date_total = None
        not_loss_in_a_row = 0
        max_not_loss_in_a_row_year = 0
        max_not_loss_in_a_row_date_year = None
        max_not_loss_in_a_row_total = 0
        max_not_loss_in_a_row_date_total = None
        wins_in_a_row = 0
        max_wins_in_a_row_year = 0
        max_wins_in_a_row_date_year = None
        max_wins_in_a_row_total = 0
        max_wins_in_a_row_date_total = None
        loss_in_a_row = 0
        max_loss_in_a_row_year = 0
        max_loss_in_a_row_date_year = None
        max_loss_in_a_row_total = 0
        max_loss_in_a_row_date_total = None
        for row in rows:
            date = datetime.strptime(row[0], '%Y-%m-%d')
            year = date.year
            result = row[1]
            matches_total += 1
            if year == current_year:
                matches_year += 1
            if result is None:
                draws_total += 1
                if year == current_year:
                    draws_year += 1
            elif result == 0:
                loss_total += 1
                if year == current_year:
                    loss_year += 1
            else:
                wins_total += 1
                if year == current_year:
                    wins_year += 1
            if previous_date is None:
                if result is None or result == 1:
                    previous_win = date
                    not_loss_in_a_row = 1
                    max_not_loss_in_a_row_total = 1
                    max_not_loss_in_a_row_date_total = date
                if result is None or result == 0:
                    previous_loss = date
                    not_wins_in_a_row = 1
                    max_not_wins_in_a_row_total = 1
                    max_not_wins_in_a_row_date_total = date
            else:
                last_match_delta = (date - previous_date).days
                if date.year == current_year and last_match_delta > not_playing_days_year:
                    not_playing_days_year = last_match_delta
                    not_playing_date_year = date
                if last_match_delta > not_playing_days_total:
                    not_playing_days_total = last_match_delta
                    not_playing_date_total = date
                if result is None or result == 1:
                    if previous_win:
                        not_winning_delta = (date - previous_win).days
                        if date.year == current_year and not_winning_delta > not_winning_days_year:
                            not_winning_days_year = not_winning_delta
                            not_winning_date_year = date
                        if not_winning_delta >= not_winning_days_total:
                            not_winning_days_total = not_winning_delta
                            not_winning_date_total = date
                    not_loss_in_a_row += 1
                    if date.year == current_year and not_loss_in_a_row > max_not_loss_in_a_row_year:
                        max_not_loss_in_a_row_year = not_loss_in_a_row
                        max_not_loss_in_a_row_date_year = date
                    if not_loss_in_a_row >= max_not_loss_in_a_row_total:
                        max_not_loss_in_a_row_total = not_loss_in_a_row
                        max_not_loss_in_a_row_date_total = date
                    if result == 1:
                        previous_win = date
                        not_wins_in_a_row = 0
                        wins_in_a_row += 1
                        loss_in_a_row = 0
                        if date.year == current_year and wins_in_a_row >= max_wins_in_a_row_year:
                            max_wins_in_a_row_year = wins_in_a_row
                            max_wins_in_a_row_date_year = date
                        if wins_in_a_row >= max_wins_in_a_row_total:
                            max_wins_in_a_row_total = wins_in_a_row
                            max_wins_in_a_row_date_total = date
                if result is None or result == 0:
                    if previous_loss:
                        not_loosing_delta = (date - previous_loss).days
                        if date.year == current_year and not_loosing_delta > not_loosing_days_year:
                            not_loosing_days_year = not_loosing_delta
                            not_loosing_date_year = date
                        if not_loosing_delta >= not_loosing_days_total:
                            not_loosing_days_total = not_loosing_delta
                            not_loosing_date_total = date
                    not_wins_in_a_row += 1
                    if date.year == current_year and not_wins_in_a_row > max_not_wins_in_a_row_year:
                        max_not_wins_in_a_row_year = not_wins_in_a_row
                        max_not_wins_in_a_row_date_year = date
                    if not_wins_in_a_row >= max_not_wins_in_a_row_total:
                        max_not_wins_in_a_row_total = not_wins_in_a_row
                        max_not_wins_in_a_row_date_total = date
                    if result == 0:
                        previous_loss = date
                        not_loss_in_a_row = 0
                        loss_in_a_row += 1
                        wins_in_a_row = 0
                        if date.year == current_year and loss_in_a_row >= max_loss_in_a_row_year:
                            max_loss_in_a_row_year = loss_in_a_row
                            max_loss_in_a_row_date_year = date
                        if loss_in_a_row >= max_loss_in_a_row_total:
                            max_loss_in_a_row_total = loss_in_a_row
                            max_loss_in_a_row_date_total = date
                if result is None:
                    wins_in_a_row = 0
                    loss_in_a_row = 0
            previous_date = date
        not_playing_days_current = (datetime.now() - date).days
        if not_playing_days_current >= not_playing_days_year:
            not_playing_days_year = not_playing_days_current
            not_playing_date_year = datetime.now()
            if not_playing_days_current >= not_playing_days_total:
                not_playing_days_total = not_playing_days_current
                not_playing_date_total = datetime.now()
        messages.extend([
            f"{not_playing_days_current} days without Padel ({not_playing_days_year} at "
            f"{not_playing_date_year.strftime('%y-%m-%d')} this year, {not_playing_days_total} at "
            f"{not_playing_date_total.strftime('%y-%m-%d')} in total)",
            f"{(datetime.now() - previous_loss).days} days without loosing a match ({not_loosing_days_year} at "
            f"{not_loosing_date_year.strftime('%y-%m-%d')} this year, {not_loosing_days_total} at "
            f"{not_loosing_date_total.strftime('%y-%m-%d')} in total)",
            f"{wins_in_a_row} consecutive matches won ({max_wins_in_a_row_year} at "
            f"{max_wins_in_a_row_date_year.strftime('%y-%m-%d')} this year, {max_wins_in_a_row_total} at "
            f"{max_wins_in_a_row_date_total.strftime('%y-%m-%d')} in total)",
            f"{not_loss_in_a_row} consecutive matches not loosing ({max_not_loss_in_a_row_year} at "
            f"{max_not_loss_in_a_row_date_year.strftime('%y-%m-%d')} this year, {max_not_loss_in_a_row_total} at "
            f"{max_not_loss_in_a_row_date_total.strftime('%y-%m-%d')} in total)",
            f"{(datetime.now() - previous_win).days} days without winning a match ({not_winning_days_year} at "
            f"{not_winning_date_year.strftime('%y-%m-%d')} this year, {not_winning_days_total} at "
            f"{not_winning_date_total.strftime('%y-%m-%d')} in total)",
            f"{loss_in_a_row} consecutive matches lost ({max_loss_in_a_row_year} at "
            f"{max_loss_in_a_row_date_year.strftime('%y-%m-%d')} this year, {max_loss_in_a_row_total} at "
            f"{max_loss_in_a_row_date_total.strftime('%y-%m-%d')} in total)",
            f"{not_wins_in_a_row} consecutive matches not winning ({max_not_wins_in_a_row_year} at "
            f"{max_not_wins_in_a_row_date_year.strftime('%y-%m-%d')} this year, {max_not_wins_in_a_row_total} at "
            f"{max_not_wins_in_a_row_date_total.strftime('%y-%m-%d')} in total)"
        ])

        wins_perc_year = wins_year * 100 / matches_year
        next_rnd_year = (int(wins_perc_year / 5) + 1) * 5
        wins_rnd_year = math.ceil(((next_rnd_year * matches_year) - (100 * wins_year)) / (100 - next_rnd_year))
        wins_perc_total = wins_total * 100 / matches_total
        next_rnd_total = (int(wins_perc_total / 5) + 1) * 5
        wins_rnd_total = math.ceil(((next_rnd_total * matches_total) - (100 * wins_total)) / (100 - next_rnd_total))
        loss_perc_year = loss_year * 100 / matches_year
        prev_rnd_year = (math.ceil(loss_perc_year / 5) - 1) * 5
        loss_rnd_year = math.ceil((100 * loss_year / prev_rnd_year) - matches_year)
        loss_perc_total = loss_total * 100 / matches_total
        prev_rnd_total = (math.ceil(loss_perc_total / 5) - 1) * 5
        loss_rnd_total = math.ceil((100 * loss_total / prev_rnd_total) - matches_total)
        messages.extend([
            f"{round(wins_perc_year, 1)}% victories this year ({wins_rnd_year} wins to {next_rnd_year}%), "
            f"{round(wins_perc_total, 1)}% victories in total ({wins_rnd_total} wins to {next_rnd_total}%)",
            f"{round(loss_perc_year, 1)}% defeats this year ({loss_rnd_year} wins to {prev_rnd_year}%), "
            f"{round(loss_perc_total, 1)}% defeats in total ({loss_rnd_total} wins to {prev_rnd_total}%)",
            f"{matches_year} matches this year ({wins_year}/{draws_year}/{loss_year}), "
            f"{matches_total} matches in total ({wins_total}/{draws_total}/{loss_total})"])

        games_year = []
        partner_year = []
        rival_year = []
        config = Config.get_default_filter()
        config['year'] = current_year
        for player in self.get_player_stats(config):
            if player['player'] == 'Others':
                continue
            if len(games_year) == 0 or player['total'] > games_year[0]['total']:
                games_year.insert(0, player)
            elif len(games_year) == 1 or player['total'] > games_year[1]['total']:
                games_year.insert(1, player)
            elif len(games_year) == 2 or player['total'] > games_year[2]['total']:
                games_year.insert(2, player)
            if len(partner_year) == 0 or player['pt'] > partner_year[0]['pt']:
                partner_year.insert(0, player)
            elif len(partner_year) == 1 or player['pt'] > partner_year[1]['pt']:
                partner_year.insert(1, player)
            elif len(partner_year) == 2 or player['pt'] > partner_year[2]['pt']:
                partner_year.insert(2, player)
            if len(rival_year) == 0 or player['rt'] > rival_year[0]['rt']:
                rival_year.insert(0, player)
            elif len(rival_year) == 1 or player['rt'] > rival_year[1]['rt']:
                rival_year.insert(1, player)
            elif len(rival_year) == 2 or player['rt'] > rival_year[2]['rt']:
                rival_year.insert(2, player)
        games_total = []
        partner_total = []
        rival_total = []
        for player in self.get_player_stats():
            if player['player'] == 'Others':
                continue
            if len(games_total) == 0 or player['total'] > games_total[0]['total']:
                games_total.insert(0, player)
            elif len(games_total) == 1 or player['total'] > games_total[1]['total']:
                games_total.insert(1, player)
            elif len(games_total) == 2 or player['total'] > games_total[2]['total']:
                games_total.insert(2, player)
            if len(partner_total) == 0 or player['pt'] > partner_total[0]['pt']:
                partner_total.insert(0, player)
            elif len(partner_total) == 1 or player['pt'] > partner_total[1]['pt']:
                partner_total.insert(1, player)
            elif len(partner_total) == 2 or player['pt'] > partner_total[2]['pt']:
                partner_total.insert(2, player)
            if len(rival_total) == 0 or player['rt'] > rival_total[0]['rt']:
                rival_total.insert(0, player)
            elif len(rival_total) == 1 or player['rt'] > rival_total[1]['rt']:
                rival_total.insert(1, player)
            elif len(rival_total) == 2 or player['rt'] > rival_total[2]['rt']:
                rival_total.insert(2, player)
        messages.extend([
            f"Matches this year: {games_year[0]['player']} {games_year[0]['total']} "
            f"{games_year[0]['pw'] + games_year[0]['rw']}/{games_year[0]['pd'] + games_year[0]['rd']}/"
            f"{games_year[0]['pl'] + games_year[0]['rl']}, {games_year[1]['player']} {games_year[1]['total']} "
            f"{games_year[1]['pw'] + games_year[1]['rw']}/{games_year[1]['pd'] + games_year[1]['rd']}/"
            f"{games_year[1]['pl'] + games_year[1]['rl']}, {games_year[2]['player']} {games_year[2]['total']} "
            f"{games_year[2]['pw'] + games_year[2]['rw']}/{games_year[2]['pd'] + games_year[2]['rd']}/"
            f"{games_year[2]['pl'] + games_year[2]['rl']}",
            f"Matches in total: {games_total[0]['player']} {games_total[0]['total']} "
            f"{games_total[0]['pw'] + games_total[0]['rw']}/{games_total[0]['pd'] + games_total[0]['rd']}/"
            f"{games_total[0]['pl'] + games_total[0]['rl']}, {games_total[1]['player']} {games_total[1]['total']} "
            f"{games_total[1]['pw'] + games_total[1]['rw']}/{games_total[1]['pd'] + games_total[1]['rd']}/"
            f"{games_total[1]['pl'] + games_total[1]['rl']}, {games_total[2]['player']} {games_total[2]['total']} "
            f"{games_total[2]['pw'] + games_total[2]['rw']}/{games_total[2]['pd'] + games_total[2]['rd']}/"
            f"{games_total[2]['pl'] + games_total[2]['rl']}",
            f"Partners this year: {partner_year[0]['player']} {partner_year[0]['pt']} {partner_year[0]['pw']}/"
            f"{partner_year[0]['pd']}/{partner_year[0]['pl']}, {partner_year[1]['player']} {partner_year[1]['pt']} "
            f"{partner_year[1]['pw']}/{partner_year[1]['pd']}/{partner_year[1]['pl']}, {partner_year[2]['player']} "
            f"{partner_year[2]['pt']} {partner_year[2]['pw']}/{partner_year[2]['pd']}/{partner_year[2]['pl']}",
            f"Partners in total: {partner_total[0]['player']} {partner_total[0]['pt']} {partner_total[0]['pw']}/"
            f"{partner_total[0]['pd']}/{partner_total[0]['pl']}, {partner_total[1]['player']} {partner_total[1]['pt']} "
            f"{partner_total[1]['pw']}/{partner_total[1]['pd']}/{partner_total[1]['pl']}, {partner_total[2]['player']} "
            f"{partner_total[2]['pt']} {partner_total[2]['pw']}/{partner_total[2]['pd']}/{partner_total[2]['pl']}",
            f"Rivals this year: {rival_year[0]['player']} {rival_year[0]['rt']} {rival_year[0]['rw']}/"
            f"{rival_year[0]['rd']}/{rival_year[0]['rl']}, {rival_year[1]['player']} {rival_year[1]['rt']} "
            f"{rival_year[1]['rw']}/{rival_year[1]['rd']}/{rival_year[1]['rl']}, {rival_year[2]['player']} "
            f"{rival_year[2]['rt']} {rival_year[2]['rw']}/{rival_year[2]['rd']}/{rival_year[2]['rl']}",
            f"Rivals in total: {rival_total[0]['player']} {rival_total[0]['rt']} {rival_total[0]['rw']}/"
            f"{rival_total[0]['rd']}/{rival_total[0]['rl']}, {rival_total[1]['player']} {rival_total[1]['rt']} "
            f"{rival_total[1]['rw']}/{rival_total[1]['rd']}/{rival_total[1]['rl']}, {rival_total[2]['player']} "
            f"{rival_total[2]['rt']} {rival_total[2]['rw']}/{rival_total[2]['rd']}/{rival_total[2]['rl']}"])
        return messages

    def insert_player(self, player, long_name):
        cursor = self.connection.cursor()
        cursor.execute(f'INSERT OR IGNORE INTO players(name, long_name) VALUES(?,?)', (player, long_name))
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
