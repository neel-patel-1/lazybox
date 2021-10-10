#!/usr/bin/env python3

'''
This script gets number of commits per day for last one year and prints the
data in a heatmap-visualization-ready format (day, week, number of commits).

Example usage:

    $ cd linux
    $ $lazybox/scripts/git_contributions.py | \
            $lazybox/gnuplot/plot.py stdout --type heatmap
    2204227254202322335120345423321831233520131323410000
    2312243345610232335110136343311223344431125243310000
    4113322246110242423130924264212242433430132232211000
    2201123333200353245102554243211324435432221422410000
    1214333353100124322020323362221232435200232223130000
    0000110000000000020002000001000000011100000010000000
    0000000000000001100000001020100010000000010000100000
    # color samples: 0123456789
    # values range: [1-884]
    # unit of the number: 98.111

TODO
- specific branches
- more colors other than gray scale
- specific range of days
'''

import argparse
import datetime
import os
import subprocess

def get_commit_dates(repo, since, until):
    cmd = ['git', '-C', '%s' % repo]
    cmd += 'log --pretty=%cd --date=format:%Y-%m-%d'.split()
    cmd.append('--since=%s' % since)
    cmd.append('--until=%s' % until)
    return subprocess.check_output(cmd).decode().strip().split('\n')

def get_date_from_yyyymmdd(txt):
    return datetime.date(*[int(x) for x in txt.split('-')])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repos', nargs='+',
            help='git repositories to count commits')
    parser.add_argument('--since',
            help='since when in YYYY-MM-DD format')
    parser.add_argument('--until',
            help='until when in YYYY-MM-DD format')
    args = parser.parse_args()

    if args.until:
        until = get_date_from_yyyymmdd(args.until)
    else:
        until = datetime.date.today()

    if not args.since:
        start_date = until - datetime.timedelta(365)
    else:
        start_date = get_date_from_yyyymmdd(args.since)
    start_date -= datetime.timedelta(start_date.weekday())
    since = start_date.strftime('%Y-%m-%d')

    commit_dates = []
    for repo in args.repos:
        commit_dates += get_commit_dates(repo, since, until.strftime('%Y-%m-%d'))
    if len(commit_dates) == 0:
        return

    duration = (until - start_date).days + 1
    nr_commits = [0] * duration
    for commit_date in commit_dates:
        date = get_date_from_yyyymmdd(commit_date)
        index = (date - start_date).days
        nr_commits[index] += 1

    nr_weeks = duration // 7
    if duration % 7:
        nr_weeks += 1
    for day in range(0, 7):
        for week in range(0, nr_weeks):
            commits = 0
            idx = week * 7 + day

            if idx < duration:
                commits = nr_commits[idx]
            print('%d %d %d' % (day, week, commits))

if __name__ == '__main__':
    main()
