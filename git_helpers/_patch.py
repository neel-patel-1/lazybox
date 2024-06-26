#!/usr/bin/env python3

import subprocess
import sys
import os

class Patch:
    email_header = None
    description_body = None
    diff = None
    author = None
    subject = None
    date = None
    fixes = None

    def decorate_for_backport(self, upstream_commit, comment_styles):
        texts_to_join = []
        if 'stable' in comment_styles:
            comment_line = 'commit %s upstream.' % upstream_commit
            if not comment_line in self.description_body.strip().split('\n'):
                texts_to_join.append('%s\n' % comment_line)

        texts_to_join.append(self.description_body.strip())

        user_name = subprocess.check_output(
                'git config --get user.name'.split()).decode().strip()
        user_email = subprocess.check_output(
                'git config --get user.email'.split()).decode().strip()
        signed_off_by_line = 'Signed-off-by: %s <%s>' % (user_name, user_email)
        if self.description_body.strip().split('\n')[-1] != signed_off_by_line:
            texts_to_join.append(signed_off_by_line)

        if 'cherry-pick' in comment_styles:
            comment_line = '(cherry picked from commit %s)' % upstream_commit
            if not comment_line in self.description_body.strip().split('\n'):
                texts_to_join.append(comment_line)

        self.description_body = '\n'.join(texts_to_join)

    def commit_in(self, remote_tree, repo=None):
        # find the upstream commit of the patch
        find_commit_in = os.path.join(os.path.dirname(sys.argv[0]),
                '__find_commit_in.sh')
        cmd = [find_commit_in, '--hash_only', '--author', self.author,
                '--title', self.subject, remote_tree]
        if repo != None:
            cmd += ['--repo', repo]

        return subprocess.check_output(cmd).decode().strip()

    def __str__(self):
        if self.has_three_dash:
            return '%s\n\n%s\n\n---\n%s' % (self.email_header, self.description_body,
                    self.diff)
        else:
            return '%s\n\n%s\n\ndiff --git%s' % (self.email_header, self.description_body,
                    self.diff)

    def __eq__(self, other):
        return (type(self) == type(other) and self.author == other.author and
                self.subject == other.subject and self.fixes == other.fixes)

    def __init__(self, filepath):
        with open(filepath, 'rb') as f:
            patch_content = f.read().decode(errors='replace')

        if '\n---\n' in patch_content:
            description_diff = patch_content.split('\n---\n')
            self.description = description_diff[0]
            self.diff = '\n---\n'.join(description_diff[1:])
            self.has_three_dash = True
        else:
            description_diff = patch_content.split('\ndiff --git')
            self.description = description_diff[0]
            self.diff = '\ndiff --git'.join(description_diff[1:])
            self.has_three_dash = False

        # description paragraphs
        desc_pars = self.description.split('\n\n')
        self.email_header = desc_pars[0]
        self.description_body = '\n\n'.join(desc_pars[1:]).strip()

        for line in self.email_header.split('\n'):
            if line.startswith('From: '):
                self.author = line.split('From: ')[1].strip()
            if line.startswith('Date: '):
                self.date = line.split('Date: ')[1].strip()
            if line.startswith('Subject: [PATCH'):
                subject_fields = line.split(']')[1:]
                self.subject = ']'.join(subject_fields).strip()
            elif line.startswith('Subject: '):
                self.subject = line[len('Subject: '):]

        self.fixes = []
        for line in self.description_body.split('\n'):
            if line.startswith ('From: '):
                self.author = line.split('From: ')[1].strip()
            if line.startswith('Fixes: '):
                self.fixes.append(line[len('Fixes: '):].strip())
