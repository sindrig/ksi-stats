import datetime
import sys
import os
import hashlib
import pickle

from suds.client import Client

WSDL_URL = 'http://www2.ksi.is/vefthjonustur/mot.asmx?WSDL'
MFL = '111'

client = Client(WSDL_URL)


def should_include_event(event, team):
    return event.FelagNumer == int(team)


def should_include_player(player, team):
    return player.FelagNumer == int(team)


def should_include_cup(name):
    return not (
        'innimót' in name or
        'fótbolti.net'in name
    )


def parse_game(game):
    return {
        'mot': game.MotNafn,
        'heima': game.FelagHeimaNafn,
        'uti': game.FelagUtiNafn,
        'urslit': (game.UrslitHeima, game.UrslitUti),
        'game_id': game.LeikurNumer,
        'date': game.LeikDagur,
    }


def parse_event(event):
    return {
        'player': (event.LeikmadurNumer, event.LeikmadurNafn.strip()),
        'shirt_number': event.TreyjuNumer,
        'minute': event.AtburdurMinuta,
        'event': event.AtburdurNafn,
    }


STARTING_POSITIONS = ('markmaður', 'fyrirliði', 'leikmaður')


def parse_player(player):
    return {
        'player': (player.LeikmadurNumer, player.LeikmadurNafn.strip()),
        'position': player.StadaNafn,
        'started': player.StadaNafn.lower() in STARTING_POSITIONS
    }


def cache(f):
    def func(*args, **kwargs):
        unique_string = str(args) + str(kwargs)
        encoded_unique_string = unique_string.encode('utf-8')
        md5sum = hashlib.md5()
        md5sum.update(encoded_unique_string)

        CACHE_FN = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'cache',
            f.__name__,
            '%s.pickle' % md5sum.hexdigest()
        )
        if not os.path.isdir(os.path.dirname(CACHE_FN)):
            os.makedirs(os.path.dirname(CACHE_FN))

        if os.path.exists(CACHE_FN):
            with open(CACHE_FN, 'rb') as fp:
                try:
                    return pickle.load(fp)
                except EOFError:
                    print('Could not get from cache, sorry.')
        result = f(*args, **kwargs)

        with open(CACHE_FN, 'wb') as fp:
            pickle.dump(result, fp)
        return result
    return func


@cache
def get_games(team, f, t):
    max_days = 364
    games = []
    while f < t:
        result = client.service.FelogLeikir(
            FelagNumer=team,
            DagsFra=f,
            DagsTil=min(f + datetime.timedelta(max_days), t),
            FlokkurNumer=MFL,
            VollurNumer='',
            Kyn=''
        )
        if hasattr(result, 'Villa'):
            print(result.Villa)
            sys.exit(1)
        if result.ArrayFelogLeikir:
            games += [
                parse_game(game) for game in
                result.ArrayFelogLeikir.FelogLeikir
                if should_include_cup(game.MotNafn.lower())
            ]
        f += datetime.timedelta(max_days)
    return games


@cache
def get_events(team, game_id):
    result = client.service.LeikurAtburdir(LeikurNumer=game_id)
    return [
        parse_event(event) for event in
        result.ArrayLeikurAtburdir.LeikurAtburdir
        if should_include_event(event, team)
    ]


@cache
def get_players(team, game_id):
    result = client.service.LeikurLeikmenn(LeikurNumer=game_id)
    return [
        parse_player(player) for player in
        result.ArrayLeikurLeikmenn.LeikurLeikmenn
        if should_include_player(player, team)
    ]
