

from .api import get_games, get_players, get_events
from .printers import console
from .collectors import create_empty_player_container


def show_console(data):
    console(data, create_empty_player_container())


def mine(team, fromdate, todate, flokkur_id, collector):
    games = get_games(team, fromdate, todate, flokkur_id)
    for game in games:
        # print('=================')
        # print('%s %s %s' % (game['heima'], game['urslit'], game['uti']))
        game['players'] = get_players(team, game['game_id'])
        game['events'] = get_events(team, game['game_id'])
    return collector(games)
