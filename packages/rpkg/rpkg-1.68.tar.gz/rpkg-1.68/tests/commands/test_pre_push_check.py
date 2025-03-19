# -*- coding: utf-8 -*-

import os
import subprocess

import git

import pyrpkg
from pyrpkg.sources import SourcesFile

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from . import CommandTestCase

SPECFILE_TEMPLATE = """Name:           test
Version:        1.0
Release:        1.0
Summary:        test

Group:          Applications/System
License:        GPLv2+

%s

%%description
Test

%%install
rm -f $RPM_BUILD_ROOT%%{_sysconfdir}/"""


class TestPrePushCheck(CommandTestCase):

    def setUp(self):
        super(TestPrePushCheck, self).setUp()

        self.dist = "rhel-8"
        self.make_new_git(self.module)

        moduledir = os.path.join(self.gitroot, self.module)
        subprocess.check_call(['git', 'clone', 'file://%s' % moduledir],
                              cwd=self.path, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        self.cloned_dir = os.path.join(self.path, self.module)
        self.cmd = pyrpkg.Commands(self.cloned_dir, self.lookaside,
                                   self.lookasidehash,
                                   self.lookaside_cgi, self.gitbaseurl,
                                   self.anongiturl, self.branchre,
                                   self.kojiprofile,
                                   self.build_client, self.user, self.dist,
                                   self.target, self.quiet)

        os.chdir(self.cloned_dir)

    @patch('pyrpkg.log.error')
    def test_push_is_blocked_by_untracked_patches(self, log_error):
        """
        Check that newly committed files are either tracked in git or listed
        in 'sources' file.
        """
        # Track SPEC and a.patch in git
        spec_file = self.module + ".spec"
        with open(spec_file, 'w') as f:
            f.write(SPECFILE_TEMPLATE % '''Patch0: a.patch
Patch1: b.patch
Patch2: c.patch
Patch3: d.patch
''')

        for patch_file in ('a.patch', 'b.patch', 'c.patch', 'd.patch'):
            with open(patch_file, 'w') as f:
                f.write(patch_file)

        # Track c.patch in sources
        sources_file = SourcesFile(self.cmd.sources_filename,
                                   self.cmd.source_entry_type)
        file_hash = self.cmd.lookasidecache.hash_file('c.patch')
        sources_file.add_entry(self.cmd.lookasidehash, 'c.patch', file_hash)
        sources_file.write()

        self.cmd.repo.index.add([spec_file, 'a.patch', 'sources'])
        self.cmd.repo.index.commit('add SPEC and patches')

        with self.assertRaises(SystemExit) as exc:
            self.cmd.pre_push_check("HEAD")

        self.assertEqual(exc.exception.code, 4)
        log_error.assert_called_once_with("Source file 'b.patch' was neither listed in the "
                                          "'sources' file nor tracked in git nor listed "
                                          "in additional sources. Push operation was cancelled")

        # Verify added files are committed but not pushed to origin
        local_repo = git.Repo(self.cloned_dir)
        git_tree = local_repo.head.commit.tree
        self.assertTrue('a.patch' in git_tree)
        self.assertTrue('b.patch' not in git_tree)
        self.assertTrue('c.patch' not in git_tree)
        self.assertTrue('d.patch' not in git_tree)

        sources_content = local_repo.git.show('master:sources').strip()
        with open('sources', 'r') as f:
            expected_sources_content = f.read().strip()
        self.assertEqual(expected_sources_content, sources_content)
