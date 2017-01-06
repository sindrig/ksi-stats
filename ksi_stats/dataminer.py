from collections import defaultdict

from .api import get_games, get_players, get_events
from .printers import console


def mine(team, fromdate, todate):
    games = get_games(team, fromdate, todate)
    for game in games:
        # print('=================')
        # print('%s %s %s' % (game['heima'], game['urslit'], game['uti']))
        game['players'] = get_players(team, game['game_id'])
        game['events'] = get_events(team, game['game_id'])
    return collect_statistics(games)


def show_console(data):
    console(data, create_empty_player_container())


started_count = 'started_count'
goals_scored = 'goals_scored'
penalty_goals = 'penalty_goals'
own_goals = 'own_goals'
yellow_cards = 'yellow_cards'
red_cards = 'red_cards'
sub_in = 'sub_in'
sub_out = 'sub_out'
games_played = 'games_played'
minutes_played = 'minutes_played'


def create_empty_player_container():
    return {
        # Derived from player
        started_count: 0,

        # Derived from events
        goals_scored: 0,
        penalty_goals: 0,
        own_goals: 0,
        yellow_cards: 0,
        red_cards: 0,
        sub_in: 0,
        sub_out: 0,

        # Derived from both
        games_played: 0,
        minutes_played: 0,
    }


def collect_statistics(games):
    players = defaultdict(create_empty_player_container)
    for game in games:
        game_length = 90
        if any(event['minute'] > 105 for event in game['events']):
            game_length = 120
        players_started = set()
        for player in game['players']:
            player_key = player['player']
            if player['started']:
                players_started.add(player_key)
                players[player_key][started_count] += 1
                players[player_key][games_played] += 1
                players[player_key][minutes_played] += game_length

        for event in game['events']:
            player_key = event['player']
            event_type = event['event']

            if event_type == 'Inn':
                if player_key in players_started:
                    players[player_key][started_count] -= 1
                    players[player_key][minutes_played] -= event['minute']
                else:
                    players[player_key][games_played] += 1
                    players[player_key][minutes_played] += (
                        game_length - event['minute']
                    )

                players[player_key][sub_in] += 1

            elif event_type == 'Út':
                players[player_key][minutes_played] -= (
                    game_length - event['minute']
                )
                players[player_key][sub_out] += 1

            elif event_type == 'Mark':
                players[player_key][goals_scored] += 1

            elif event_type == 'Áminning':
                players[player_key][yellow_cards] += 1

            elif (
                event_type == 'Brottvísun' or event_type == 'Brottvísun-2 gul'
            ):
                players[player_key][red_cards] += 1

            elif event_type == 'Mark úr víti':
                players[player_key][goals_scored] += 1
                players[player_key][penalty_goals] += 1

            elif event_type == 'Sjálfsmark':
                players[player_key][own_goals] += 1

            else:
                raise ValueError('Unknown event %s' % event_type)
    return players
