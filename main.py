import argparse
import datetime
from ksi_stats.dataminer import mine, show_console
from ksi_stats.exporter import export_csv

fromdate = datetime.date(2007, 1, 1)
todate = datetime.date.today()
BERSERKIR = '141740'
DATE_FORMAT = '%d.%m.%Y'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['csv', 'console'])
    parser.add_argument('--fromdate', default=fromdate.strftime(DATE_FORMAT))
    parser.add_argument('--todate', default=todate.strftime(DATE_FORMAT))
    parser.add_argument('--teamid', default=BERSERKIR)
    parser.add_argument('--outfile')
    args = parser.parse_args()

    data = mine(
        args.teamid,
        datetime.datetime.strptime(args.fromdate, DATE_FORMAT),
        datetime.datetime.strptime(args.todate, DATE_FORMAT)
    )
    if args.action == 'console':
        show_console(data)
    elif args.action == 'csv':
        export_csv(data, args.outfile)
