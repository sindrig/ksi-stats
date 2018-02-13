import csv
from io import StringIO

from .collectors import minutes_played


def writer(f):
    def func(data, file_name):
        w = StringIO()
        f(data, w)
        if file_name:
            with open(file_name, 'w') as fp:
                fp.write(w.getvalue())
        else:
            print(w.getvalue())
    return func


@writer
def export_csv(data, fp):
    csv_writer = csv.writer(fp, delimiter=';')
    for i, player in enumerate(data.items()):
        (player_id, player_name), attributes = player
        if not i:
            keys = list(attributes.keys())
            csv_writer.writerow(['name'] + keys)
        csv_writer.writerow(
            [player_name] + [attributes[key] for key in keys]
        )


def print_player_ids(data):
    players_to_print = []
    for player, attributes in data.items():
        if attributes[minutes_played] > 90 * 5:
            players_to_print.append([player, attributes[minutes_played]])
    for (player_id, player_name), mins_played in sorted(
        players_to_print, key=lambda x: -x[1]
    ):
        print('%s %s: %s' % (player_id, player_name, mins_played))
