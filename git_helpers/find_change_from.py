#!/usr/bin/env python3

'''
Load a change from a patch or commit, and find matching change from patches
queue or commits range
'''

import argparse

import _git

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--patch', metavar='<file>',
            help='patch containing the change')
    parser.add_argument('--commit', metavar='<commit>',
            help='commit containing the change')
    parser.add_argument('--subject', metavar='<subject>',
            help='subject of the change')
    parser.add_argument('--author', metavar='<author name <author email>>',
            help='author of the change')

    parser.add_argument('--repo', metavar='<dir>', default='./',
            help='local repo to find the change from')
    parser.add_argument('--commits', metavar='<commits range reference>',
            help='commits range to find the change from')
    parser.add_argument('--patches', metavar='<patch file>', nargs='+',
            help='patch files to find the change from')
    args = parser.parse_args()

    if args.patch == None and args.commit == None and args.subject == None:
        print('--patch, --commit, or --subject should be set')
        exit(1)

    if args.commits == None and args.patches == None:
        print('--commits or --patches should be given')
        exit(1)

    if args.patch:
        change = _git.Change(patch_file=args.patch)
    elif args.commit:
        change = _git.Change(commit=args.commit, repo=args.repo)
    elif args.subject:
        change = _git.Change(subject=args.subject, author=args.author)

    if args.commits:
        matching_change = change.find_matching_commit(args.repo, args.commits)
        if matching_change == None:
            exit(1)
        print('%s ("%s")' %
                (matching_change.commit.hashid[:12], change.subject))
    else:
        matching_change = change.find_matching_patch(args.patches)
        if matching_change != None:
            print(matching_change.patch.file_name)
            exit(0)
        print('no matching patch file found')
        exit(1)

if __name__ == '__main__':
    main()
