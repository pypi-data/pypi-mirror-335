# -*- coding: utf-8 -*-

import errno
import io
import os
import shutil
import subprocess
import tempfile
from datetime import datetime

import git
import rpm
import six
from pyrpkg import rpkgError

try:
    from unittest.mock import Mock, PropertyMock, call, mock_open, patch
except ImportError:
    from mock import Mock, PropertyMock, call, mock_open, patch

from utils import CommandTestCase


def mock_load_rpmdefines(self):
    """Mock Commands.load_rpmdefines by setting empty list to _rpmdefines

    :param Commands self: load_rpmdefines is an instance method of Commands,
    self is the instance whish is calling this method.
    """
    self._rpmdefines = []


def mock_load_spec(fake_spec):
    """Return a mocked load_spec method that sets a fake spec to Commands

    :param str fake_spec: an arbitrary string representing a fake spec
    file. What value is passed to fake_spec depends on the test purpose
    completely.
    """
    def mocked_load_spec(self):
        """Mocked load_spec to set fake spec to an instance of Commands

        :param Commands self: load_spec is an instance method of Commands, self
        is the instance which is calling this method.
        """
        self._spec = fake_spec
    return mocked_load_spec


def mock_load_branch_merge(fake_branch_merge):
    """Return a mocked load_branch_merge method

    The mocked method sets a fake branch name to _branch_merge.

    :param str fake_branch_merge: an arbitrary string representing a fake
    branch name. What value should be passed to fake_branch_merge depends on
    the test purpose completely.
    """
    def mocked_method(self):
        """
        Mocked load_branch_merge to set fake branch name to an instance of
        Commands.

        :param Commands self: load_branch_merge is an instance method of
        Commands, so self is the instance which is calling this method.
        """
        self._branch_merge = fake_branch_merge
    return mocked_method


class LoadNameVerRelTest(CommandTestCase):
    """Test case for Commands.load_nameverrel"""

    create_repo_per_test = False

    def setUp(self):
        super(LoadNameVerRelTest, self).setUp()
        self.cmd = self.make_commands()
        self.checkout_branch(self.cmd.repo, 'eng-rhel-6')
        self.tempdir = tempfile.mkdtemp(prefix='rpkg_test_')
        self._patchers = {
            name: patch("pyrpkg.%s" % name) for name in (
                "specfile_uses_rpmautospec",
                "rpmautospec_process_distgit",
                "rpmautospec_calculate_release_number",
            )
        }
        self.mocks = {name: patcher.start() for name, patcher in self._patchers.items()}
        self.mocks["specfile_uses_rpmautospec"].return_value = False

    def tearDown(self):
        super(LoadNameVerRelTest, self).tearDown()
        for patcher in self._patchers.values():
            patcher.stop()
        shutil.rmtree(self.tempdir)

    def test_load_from_spec(self):
        """Ensure name, version, release can be loaded from a valid SPEC"""
        self.cmd.load_nameverrel()
        self.assertEqual('docpkg', self.cmd._package_name_spec)
        self.assertEqual('0', self.cmd._epoch)
        self.assertEqual('1.2', self.cmd._ver)
        self.assertEqual('2.el6', self.cmd._rel)

    def test_load_spec_where_path_contains_space(self):
        """Ensure load_nameverrel works with a repo whose path contains space

        This test aims to test the space appearing in path does not break rpm
        command execution.

        For this test purpose, firstly, original repo has to be cloned to a
        new place which has a name containing arbitrary spaces.
        """
        cloned_repo_dir = os.path.join(self.tempdir, 'rpkg test cloned repo')
        if os.path.exists(cloned_repo_dir):
            shutil.rmtree(cloned_repo_dir)
        cloned_repo = self.cmd.repo.clone(cloned_repo_dir)

        # Switching to branch eng-rhel-6 explicitly is required by running this
        # on RHEL6/7 because an old version of git is available in the
        # repo.
        # The failure reason is, old version of git makes the master as the
        # active branch in cloned repository, whatever the current active
        # branch is in the remote repository.
        # As of fixing this, I ran test on Fedora 23 with git 2.5.5, and test
        # fails on RHEL7 with git 1.8.3.1
        cloned_repo.git.checkout('eng-rhel-6')

        cmd = self.make_commands(path=cloned_repo_dir)

        cmd.load_nameverrel()
        self.assertEqual('docpkg', cmd._package_name_spec)
        self.assertEqual('0', cmd._epoch)
        self.assertEqual('1.2', cmd._ver)
        self.assertEqual('2.el6', cmd._rel)
        self.assertIs(False, cmd._uses_autorelease)
        self.assertIs(False, cmd._uses_autochangelog)
        self.assertIs(False, cmd._uses_rpmautospec)

    @patch('pyrpkg.Commands.load_rpmdefines', new=mock_load_rpmdefines)
    @patch('pyrpkg.Commands.load_spec',
           new=mock_load_spec('unknown-rpm-option a-nonexistent-package.spec'))
    def test_load_when_rpm_fails(self):
        """Ensure rpkgError is raised when rpm command fails

        Commands.load_spec is mocked to help generate an incorrect rpm command
        line to cause the error that this test expects.

        Test test does not care about what rpm defines are retrieved from
        repository, so setting an empty list to Commands._rpmdefines is safe
        and enough.
        """
        self.assertRaises(rpkgError, self.cmd.load_nameverrel)

    def test_load_when_echo_text_from_spec(self):
        import utils
        self.write_file(os.path.join(self.cloned_repo_path, self.spec_file),
                        content=utils.spec_file_echo_text)

        self.cmd.load_nameverrel()
        self.assertEqual('docpkg', self.cmd._package_name_spec)
        self.assertEqual('0', self.cmd._epoch)
        self.assertEqual('1.2', self.cmd._ver)
        self.assertEqual('2.el6', self.cmd._rel)

    @patch("pyrpkg.specfile_uses_rpmautospec", new=None)
    @patch("pyrpkg.rpmautospec_process_distgit", new=None)
    @patch("pyrpkg.rpmautospec_calculate_release_number", new=None)
    def test_load_with_rpmautospec_pkg_missing(self):
        self.cmd.load_nameverrel()
        self.assertIs(0, self.cmd._uses_autorelease)
        self.assertIs(0, self.cmd._uses_autochangelog)
        self.assertIs(0, self.cmd._uses_rpmautospec)

    @patch("subprocess.Popen", wraps=subprocess.Popen)
    def test_load_with_rpmautospec(self, wrapped_popen):
        test_release_number = 123

        self.mocks["specfile_uses_rpmautospec"].return_value = True
        self.mocks["rpmautospec_process_distgit"].return_value = True
        self.mocks["rpmautospec_calculate_release_number"].return_value = test_release_number

        self.cmd.load_nameverrel()

        self.assertIs(True, self.cmd._uses_autorelease)
        self.assertIs(True, self.cmd._uses_autochangelog)
        self.assertIs(True, self.cmd._uses_rpmautospec)
        self.assertEqual(1, wrapped_popen.call_count)
        args, kwargs = wrapped_popen.call_args
        self.assertIn("_rpmautospec_release_number %d" % test_release_number, args[0])


class LoadBranchMergeTest(CommandTestCase):
    """Test case for testing Commands.load_branch_merge"""

    create_repo_per_test = False

    def setUp(self):
        super(LoadBranchMergeTest, self).setUp()

        self.cmd = self.make_commands()

    def test_load_branch_merge_from_eng_rhel_6(self):
        self.checkout_branch(self.cmd.repo, 'eng-rhel-6')
        self.cmd.load_branch_merge()
        self.assertEqual(self.cmd._branch_merge, 'eng-rhel-6')

    def test_load_branch_merge_from_eng_rhel_6_5(self):
        """
        Ensure load_branch_merge can work well against a more special branch
        eng-rhel-6.5
        """
        self.checkout_branch(self.cmd.repo, 'eng-rhel-6.5')
        self.cmd.load_branch_merge()
        self.assertEqual(self.cmd._branch_merge, 'eng-rhel-6.5')

    def test_load_branch_merge_from_not_remote_merge_branch(self):
        """Ensure load_branch_merge fails against local-branch

        A new local branch named local-branch is created for this test, loading
        branch merge from this local branch won't fail although there is no
        configuration item branch.local-branch.merge.
        """
        self.create_branch(self.cmd.repo, 'local-branch')
        self.checkout_branch(self.cmd.repo, 'local-branch')
        self.cmd.load_branch_merge()
        self.assertTrue(self.cmd.branch_merge, 'local-branch')

    def test_load_branch_merge_using_release_option(self):
        """Ensure load_branch_merge uses release specified via --release

        Switch to eng-rhel-6 branch, that is valid for load_branch_merge and to
        see if load_branch_merge still uses dist rather than such a valid
        branch.
        """
        self.checkout_branch(self.cmd.repo, 'eng-rhel-6')

        cmd = self.make_commands(dist='branch_merge')
        cmd.load_branch_merge()
        self.assertEqual('branch_merge', cmd._branch_merge)


class LoadRPMDefinesTest(CommandTestCase):
    """Test case for Commands.load_rpmdefines"""

    create_repo_per_test = False

    def setUp(self):
        super(LoadRPMDefinesTest, self).setUp()
        self.cmd = self.make_commands()

    def assert_loaded_rpmdefines(self, branch_name, expected_defines):
        self.checkout_branch(self.cmd.repo, branch_name)

        self.cmd.load_rpmdefines()
        self.assertTrue(self.cmd._rpmdefines)

        # Convert defines into dict for assertion conveniently. The dict
        # contains mapping from variable name to value. For example,
        # {
        #     '_sourcedir': '/path/to/src-dir',
        #     '_specdir': '/path/to/spec',
        #     '_builddir': '/path/to/build-dir',
        #     '_srcrpmdir': '/path/to/srcrpm-dir',
        #     'dist': 'el7'
        # }
        defines = dict([item.split(' ') for item in self.cmd._rpmdefines[1::2]])

        self.assertEqual(len(expected_defines), len(defines))
        for var, val in expected_defines.items():
            self.assertTrue(var in defines)
            self.assertEqual(val, defines[var])

    def test_load_rpmdefines_from_eng_rhel_6(self):
        """Run load_rpmdefines against branch eng-rhel-6"""
        expected_rpmdefines = {
            '_sourcedir': self.cloned_repo_path,
            '_specdir': self.cloned_repo_path,
            '_builddir': self.cloned_repo_path,
            '_srcrpmdir': self.cloned_repo_path,
            '_rpmdir': self.cloned_repo_path,
            '_rpmfilename': '%%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm',
            'dist': u'.el6',
            'rhel': u'6',
            'el6': u'1',
        }
        self.assert_loaded_rpmdefines('eng-rhel-6', expected_rpmdefines)

    def test_load_rpmdefines_from_eng_rhel_6_5(self):
        """Run load_rpmdefines against branch eng-rhel-6.5

        Working on a different branch name is the only difference from test
        method test_load_rpmdefines_from_eng_rhel_6.
        """
        expected_rpmdefines = {
            '_sourcedir': self.cloned_repo_path,
            '_specdir': self.cloned_repo_path,
            '_builddir': self.cloned_repo_path,
            '_srcrpmdir': self.cloned_repo_path,
            '_rpmdir': self.cloned_repo_path,
            '_rpmfilename': '%%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm',
            'dist': u'.el6_5',
            'rhel': u'6',
            'el6_5': u'1',
        }
        self.assert_loaded_rpmdefines('eng-rhel-6.5', expected_rpmdefines)

    @patch('pyrpkg.Commands.load_branch_merge',
           new=mock_load_branch_merge('invalid-branch-name'))
    def test_load_rpmdefines_against_invalid_branch(self):
        """Ensure load_rpmdefines if active branch name is invalid

        This test requires an invalid branch name even if
        Commands.load_branch_merge is able to get it from current active
        branch. So, I only care about the value returned from method
        load_branch_merge, and just mock it and let it return the value this
        test requires.
        """
        self.assertRaises(rpkgError, self.cmd.load_rpmdefines)


class CheckRepoWithOrWithoutDistOptionCase(CommandTestCase):
    """Check whether there are unpushed changes with or without specified dist

    Ensure check_repo works in a correct way to check if there are unpushed
    changes, and this should not be affected by specified dist or not.
    Bug 1169663 describes a concrete use case and this test case is designed
    as what that bug describs.
    """

    def setUp(self):
        super(CheckRepoWithOrWithoutDistOptionCase, self).setUp()

        private_branch = 'private-dev-branch'
        origin_repo = git.Repo(self.repo_path)
        origin_repo.git.checkout('master')
        origin_repo.git.branch(private_branch)
        self.make_a_dummy_commit(origin_repo)

        cloned_repo = git.Repo(self.cloned_repo_path)
        cloned_repo.git.pull()
        cloned_repo.git.checkout('-b', private_branch, 'origin/%s' % private_branch)
        for i in range(3):
            self.make_a_dummy_commit(cloned_repo)
        cloned_repo.git.push()

    def test_check_repo_with_specificed_dist(self):
        cmd = self.make_commands(self.cloned_repo_path, dist='eng-rhel-6')
        try:
            cmd.check_repo()
        except rpkgError as e:
            if 'There are unpushed changes in your repo' in e:
                self.fail('There are unpushed changes in your repo. This '
                          'should not happen. Something must be going wrong.')

            self.fail('Should not fail. Something must be going wrong.')

    def test_check_repo_without_specificed_dist(self):
        cmd = self.make_commands(self.cloned_repo_path)
        try:
            cmd.check_repo()
        except rpkgError as e:
            if 'There are unpushed changes in your repo' in e:
                self.fail('There are unpushed changes in your repo. This '
                          'should not happen. Something must be going wrong.')

            self.fail('Should not fail. Something must be going wrong.')


class ClogTest(CommandTestCase):

    create_repo_per_test = False

    def setUp(self):
        super(ClogTest, self).setUp()

        with open(os.path.join(self.cloned_repo_path, self.spec_file), 'w') as specfile:
            specfile.write('''
Summary: package demo
Name: pkgtool
Version: 0.1
Release: 1%{{?dist}}
License: GPL
%description
package demo for testing
%changelog
* {0} tester@example.com
- add %%changelog section
- add new spec

* {0} tester@example.com
- initial
'''.format(datetime.strftime(datetime.now(), '%a %b %d %Y')))

        self.clog_file = os.path.join(self.cloned_repo_path, 'clog')
        self.cmd = self.make_commands()
        self.checkout_branch(self.cmd.repo, 'eng-rhel-6')

    def test_clog(self):
        self.cmd.clog()

        with open(self.clog_file, 'r') as clog:
            clog_lines = clog.readlines()

        expected_lines = ['add %changelog section\n',
                          '\n',
                          'add new spec\n']
        self.assertEqual(expected_lines, clog_lines)

    def test_raw_clog(self):
        self.cmd.clog(raw=True)

        with open(self.clog_file, 'r') as clog:
            clog_lines = clog.readlines()

        expected_lines = ['- add %changelog section\n',
                          '\n',
                          '- add new spec\n']
        self.assertEqual(expected_lines, clog_lines)


class TestProperties(CommandTestCase):

    create_repo_per_test = False

    def setUp(self):
        super(TestProperties, self).setUp()
        self.invalid_repo = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.invalid_repo)
        super(TestProperties, self).tearDown()

    def test_target(self):
        cmd = self.make_commands()
        self.checkout_branch(cmd.repo, 'eng-rhel-6')
        self.assertEqual('eng-rhel-6-candidate', cmd.target)

    def test_spec(self):
        cmd = self.make_commands()
        self.assertEqual('docpkg.spec', cmd.spec)

    def test_no_spec_as_it_is_deadpackage(self):
        with patch('os.listdir', return_value=['dead.package']):
            cmd = self.make_commands()
            self.assertRaises(rpkgError, cmd.load_spec)

    def test_no_spec_there(self):
        with patch('os.listdir', return_value=['anyfile']):
            cmd = self.make_commands()
            self.assertRaises(rpkgError, cmd.load_spec)

    def test_nvr(self):
        cmd = self.make_commands(dist='eng-rhel-6')

        repo_name = os.path.basename(self.repo_path)
        self.assertEqual('{0}-1.2-2.el6'.format(repo_name), cmd.nvr)

    def test_nvr_cannot_get_repo_name_from_push_url(self):
        cmd = self.make_commands(path=self.repo_path, dist='eng-rhel-6')
        self.assertEqual('docpkg-1.2-2.el6', cmd.nvr)

    def test_localarch(self):
        expected_localarch = rpm.expandMacro('%{_arch}')
        cmd = self.make_commands()
        self.assertEqual(expected_localarch, cmd.localarch)

    def test_commithash(self):
        cmd = self.make_commands(path=self.cloned_repo_path)
        repo = git.Repo(self.cloned_repo_path)
        expected_commit_hash = str(six.next(repo.iter_commits()))
        self.assertEqual(expected_commit_hash, cmd.commithash)

    def test_dist(self):
        repo = git.Repo(self.cloned_repo_path)
        self.checkout_branch(repo, 'eng-rhel-7')

        cmd = self.make_commands(path=self.cloned_repo_path)
        self.assertEqual('el7', cmd.disttag)
        self.assertEqual('rhel', cmd.distvar)
        self.assertEqual('7', cmd.distval)
        self.assertEqual('0', cmd.epoch)

    def test_repo(self):
        cmd = self.make_commands(path=self.cloned_repo_path)
        cmd.load_repo()
        self.assertEqual(self.cloned_repo_path, os.path.dirname(cmd._repo.git_dir))

        cmd = self.make_commands(path=self.invalid_repo)
        self.assertRaises(rpkgError, cmd.load_repo)

        cmd = self.make_commands(path='some-dir')
        self.assertRaises(rpkgError, cmd.load_repo)

    def test_mockconfig(self):
        cmd = self.make_commands(path=self.cloned_repo_path)
        self.checkout_branch(cmd.repo, 'eng-rhel-7')
        expected_localarch = rpm.expandMacro('%{_arch}')
        self.assertEqual('eng-rhel-7-candidate-{0}'.format(expected_localarch), cmd.mockconfig)

    def test_get_ns_repo_name(self):
        cmd = self.make_commands(path=self.cloned_repo_path)

        tests = (
            ('http://localhost/rpms/docpkg.git', 'docpkg'),
            ('http://localhost/docker/docpkg.git', 'docpkg'),
            ('http://localhost/docpkg.git', 'docpkg'),
            ('http://localhost/rpms/docpkg', 'docpkg'),
        )
        for push_url, expected_ns_repo_name in tests:
            cmd._push_url = push_url
            cmd.load_ns()
            cmd.load_repo_name()
            self.assertEqual(expected_ns_repo_name, cmd.ns_repo_name)

        cmd.distgit_namespaced = True
        tests = (
            ('http://localhost/rpms/docpkg.git', 'rpms/docpkg'),
            ('http://localhost/docker/docpkg.git', 'docker/docpkg'),
            ('http://localhost/docpkg.git', 'rpms/docpkg'),
            ('http://localhost/rpms/docpkg', 'rpms/docpkg'),
        )
        for push_url, expected_ns_repo_name in tests:
            cmd._push_url = push_url
            cmd.load_ns()
            cmd.load_repo_name()
            self.assertEqual(expected_ns_repo_name, cmd.ns_repo_name)


class TestNamespaced(CommandTestCase):

    require_test_repos = False

    def test_get_namespace_giturl(self):
        cmd = self.make_commands(path='/path/to/repo')
        cmd.gitbaseurl = 'ssh://%(user)s@localhost/%(module)s'
        cmd.distgit_namespaced = False

        self.assertEqual(cmd.gitbaseurl % {'user': cmd.user, 'module': 'docpkg'},
                         cmd._get_namespace_giturl('docpkg'))
        self.assertEqual(cmd.gitbaseurl % {'user': cmd.user, 'module': 'docker/docpkg'},
                         cmd._get_namespace_giturl('docker/docpkg'))
        self.assertEqual(cmd.gitbaseurl % {'user': cmd.user, 'module': 'rpms/docpkg'},
                         cmd._get_namespace_giturl('rpms/docpkg'))

    def test_get_namespace_giturl_namespaced_is_enabled(self):
        cmd = self.make_commands(path='/path/to/repo')
        cmd.gitbaseurl = 'ssh://%(user)s@localhost/%(module)s'
        cmd.distgit_namespaced = True

        self.assertEqual(cmd.gitbaseurl % {'user': cmd.user, 'module': 'rpms/docpkg'},
                         cmd._get_namespace_giturl('docpkg'))
        self.assertEqual(cmd.gitbaseurl % {'user': cmd.user, 'module': 'docker/docpkg'},
                         cmd._get_namespace_giturl('docker/docpkg'))
        self.assertEqual(cmd.gitbaseurl % {'user': cmd.user, 'module': 'rpms/docpkg'},
                         cmd._get_namespace_giturl('rpms/docpkg'))

    def test_get_namespace_anongiturl(self):
        cmd = self.make_commands(path='/path/to/repo')
        cmd.anongiturl = 'git://localhost/%(module)s'
        cmd.distgit_namespaced = False

        self.assertEqual(cmd.anongiturl % {'module': 'docpkg'},
                         cmd._get_namespace_anongiturl('docpkg'))
        self.assertEqual(cmd.anongiturl % {'module': 'docker/docpkg'},
                         cmd._get_namespace_anongiturl('docker/docpkg'))
        self.assertEqual(cmd.anongiturl % {'module': 'rpms/docpkg'},
                         cmd._get_namespace_anongiturl('rpms/docpkg'))

    def test_get_namespace_anongiturl_namespaced_is_enabled(self):
        cmd = self.make_commands(path='/path/to/repo')
        cmd.anongiturl = 'git://localhost/%(module)s'
        cmd.distgit_namespaced = True

        self.assertEqual(cmd.anongiturl % {'module': 'rpms/docpkg'},
                         cmd._get_namespace_anongiturl('docpkg'))
        self.assertEqual(cmd.anongiturl % {'module': 'docker/docpkg'},
                         cmd._get_namespace_anongiturl('docker/docpkg'))
        self.assertEqual(cmd.anongiturl % {'module': 'rpms/docpkg'},
                         cmd._get_namespace_anongiturl('rpms/docpkg'))


class TestGetLatestCommit(CommandTestCase):

    def test_get_latest_commit(self):
        cmd = self.make_commands(path=self.cloned_repo_path)
        # Repos used for running tests locates in local filesyste, refer to
        # self.repo_path and self.cloned_repo_path.
        cmd.anongiturl = os.path.join(os.path.dirname(self.cloned_repo_path), "%(module)s")
        cmd.distgit_namespaced = False

        self.assertEqual(str(six.next(git.Repo(self.repo_path).iter_commits())),
                         cmd.get_latest_commit(os.path.basename(self.repo_path),
                                               'eng-rhel-6'))


def load_kojisession(self):
    self._kojisession = Mock()
    self._kojisession.getFullInheritance.return_value = [
        {'child_id': 342, 'currdepth': 1, 'filter': [], 'intransitive': False,
         'maxdepth': None, 'name': 'f25-override', 'nextdepth': None, 'noconfig': False,
         'parent_id': 341, 'pkg_filter': '', 'priority': 0},
        {'child_id': 341, 'currdepth': 2, 'filter': [], 'intransitive': False,
         'maxdepth': None, 'name': 'f25-updates', 'nextdepth': None, 'noconfig': False,
         'parent_id': 336, 'pkg_filter': '', 'priority': 0},
        {'child_id': 336, 'currdepth': 3, 'filter': [], 'intransitive': False,
         'maxdepth': None, 'name': 'f25', 'nextdepth': None, 'noconfig': False,
         'parent_id': 335, 'pkg_filter': '', 'priority': 0},
    ]


class TestTagInheritanceTag(CommandTestCase):

    @patch('pyrpkg.Commands.load_kojisession', new=load_kojisession)
    def test_error_if_not_inherit(self):
        build_target = {
            'build_tag': 342, 'build_tag_name': 'f25-build',
            'dest_tag': 337, 'dest_tag_name': 'f25-updates-candidate',
            'id': 167, 'name': 'f25-candidate',
        }
        dest_tag = {
            'arches': None, 'extra': {},
            'id': 337, 'locked': False,
            'maven_include_all': False, 'maven_support': False,
            'name': 'f25-updates-candidate',
            'perm': None, 'perm_id': None,
        }

        cmd = self.make_commands()
        self.assertRaises(rpkgError, cmd.check_inheritance, build_target, dest_tag)


class TestLoadRepoNameFromSpecialPushURL(CommandTestCase):
    """Test load repo name from a special push url that ends in /

    For issue: https://pagure.io/rpkg/issue/192
    """

    def setUp(self):
        super(TestLoadRepoNameFromSpecialPushURL, self).setUp()

        self.case_repo = tempfile.mkdtemp(prefix='case-test-load-repo-name-')
        cmd = ['git', 'clone', '{0}/'.format(self.repo_path), self.case_repo]
        self.run_cmd(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tearDown(self):
        shutil.rmtree(self.case_repo)
        super(TestLoadRepoNameFromSpecialPushURL, self).tearDown()

    def test_load_repo_name(self):
        cmd = self.make_commands(path=self.case_repo)
        self.assertEqual(os.path.basename(self.repo_path), cmd.repo_name)


class TestLoginKojiSession(CommandTestCase):
    """Test login_koji_session"""

    require_test_repos = False

    def setUp(self):
        super(TestLoginKojiSession, self).setUp()

        self.cmd = self.make_commands(path='/path/to/repo')
        self.cmd.log = Mock()
        self.koji_config = {
            'authtype': 'ssl',
            'server': 'http://localhost/kojihub',
            'cert': '/path/to/cert',
            'serverca': '/path/to/serverca',
        }
        self.session = Mock()

    @patch('pyrpkg.koji.is_requests_cert_error', return_value=True)
    def test_ssl_login_cert_revoked_or_expired(self, is_requests_cert_error):
        self.session.ssl_login.side_effect = Exception

        self.koji_config['authtype'] = 'ssl'

        self.assertRaises(rpkgError,
                          self.cmd.login_koji_session,
                          self.koji_config, self.session)
        self.cmd.log.info.assert_called_once_with(
            'Certificate is revoked or expired.')

    def test_ssl_login(self):
        self.koji_config['authtype'] = 'ssl'

        self.cmd.login_koji_session(self.koji_config, self.session)

        self.session.ssl_login.assert_called_once_with(
            self.koji_config['cert'],
            None,
            self.koji_config['serverca'],
            proxyuser=None,
        )

    def test_runas_option_cannot_be_set_for_password_auth(self):
        self.koji_config['authtype'] = 'password'
        self.cmd.runas = 'user'
        self.assertRaises(rpkgError,
                          self.cmd.login_koji_session,
                          self.koji_config, self.session)

    @patch('pyrpkg.Commands.user', new_callable=PropertyMock)
    def test_password_login(self, user):
        user.return_value = 'tester'
        self.session.opts = {}
        self.koji_config['authtype'] = 'password'

        self.cmd.login_koji_session(self.koji_config, self.session)

        self.assertEqual({'user': 'tester', 'password': None},
                         self.session.opts)
        self.session.login.assert_called_once()

    @patch('pyrpkg.Commands._load_krb_user', return_value=False)
    def test_gssapi_login_fails_if_no_valid_credential(self, _load_krb_user):
        self.koji_config['authtype'] = 'kerberos'
        self.cmd.realms = ['FEDORAPROJECT.ORG']

        self.cmd.login_koji_session(self.koji_config, self.session)

        self.session.gssapi_login.assert_not_called()
        self.assertEqual(2, self.cmd.log.warning.call_count)

    @patch('pyrpkg.Commands._load_krb_user', return_value=True)
    def test_gssapi_login_fails(self, _load_krb_user):
        self.koji_config['authtype'] = 'kerberos'
        # Simulate ClientSession.gssapi_login fails and error is raised.
        self.session.gssapi_login.side_effect = Exception

        self.cmd.login_koji_session(self.koji_config, self.session)

        self.session.gssapi_login.assert_called_once_with(proxyuser=None)
        self.cmd.log.error.assert_called_once()

    @patch('pyrpkg.Commands._load_krb_user', return_value=True)
    def test_successful_gssapi_login(self, _load_krb_user):
        self.koji_config['authtype'] = 'kerberos'

        self.cmd.login_koji_session(self.koji_config, self.session)

        self.session.gssapi_login.assert_called_once_with(proxyuser=None)


class TestConstructBuildURL(CommandTestCase):
    """Test Commands.construct_build_url"""

    require_test_repos = False

    def setUp(self):
        super(TestConstructBuildURL, self).setUp()
        self.cmd = self.make_commands(path='/path/to/repo')

    @patch('pyrpkg.Commands.ns_repo_name', new_callable=PropertyMock)
    @patch('pyrpkg.Commands.commithash', new_callable=PropertyMock)
    def test_construct_url(self, commithash, ns_repo_name):
        commithash.return_value = '12345'
        ns_repo_name.return_value = 'container/fedpkg'

        anongiturl = 'https://src.example.com/%(repo)s'
        with patch.object(self.cmd, 'anongiturl', new=anongiturl):
            url = self.cmd.construct_build_url()

        expected_url = '{0}#{1}'.format(
            anongiturl % {'repo': ns_repo_name.return_value},
            commithash.return_value)
        self.assertEqual(expected_url, url)

    def test_construct_with_given_repo_name_and_hash(self):
        anongiturl = 'https://src.example.com/%(repo)s'
        with patch.object(self.cmd, 'anongiturl', new=anongiturl):
            for repo_name in ('extra-cmake-modules', 'rpms/kf5-kfilemetadata'):
                url = self.cmd.construct_build_url(repo_name, '123456')

                expected_url = '{0}#{1}'.format(
                    anongiturl % {'repo': repo_name}, '123456')
                self.assertEqual(expected_url, url)


class TestCleanupTmpDir(CommandTestCase):
    """Test Commands._cleanup_tmp_dir for mockbuild command"""

    require_test_repos = False

    def setUp(self):
        super(TestCleanupTmpDir, self).setUp()
        self.tmp_dir_name = tempfile.mkdtemp(prefix='test-cleanup-tmp-dir-')
        self.cmd = self.make_commands(path='/path/to/repo')

    def tearDown(self):
        if os.path.exists(self.tmp_dir_name):
            os.rmdir(self.tmp_dir_name)
        super(TestCleanupTmpDir, self).tearDown()

    @patch('shutil.rmtree')
    def test_do_nothing_is_tmp_dir_is_invalid(self, rmtree):
        for invalid_dir in ('', None):
            self.cmd._cleanup_tmp_dir(invalid_dir)
            rmtree.assert_not_called()

    def test_remove_tmp_dir(self):
        self.cmd._cleanup_tmp_dir(self.tmp_dir_name)

        self.assertFalse(os.path.exists(self.tmp_dir_name))

    def test_keep_silient_if_tmp_dir_does_not_exist(self):
        tmp_dir = tempfile.mkdtemp()
        os.rmdir(tmp_dir)

        self.cmd._cleanup_tmp_dir(tmp_dir)

    def test_raise_error_if_other_non_no_such_file_dir_error(self):
        with patch('shutil.rmtree',
                   side_effect=OSError((errno.EEXIST), 'error message')):
            self.assertRaises(rpkgError, self.cmd._cleanup_tmp_dir, '/tempdir')


class TestConfigMockConfigDir(CommandTestCase):
    """Test Commands._config_dir_basic for mockbuild"""

    require_test_repos = False

    def setUp(self):
        super(TestConfigMockConfigDir, self).setUp()

        self.cmd = self.make_commands(path='/path/to/repo')
        self.temp_config_dir = tempfile.mkdtemp()

        self.fake_root = 'fedora-26-x86_64'
        self.mock_config_patcher = patch('pyrpkg.Commands.mock_config',
                                         return_value='mock config x86_64')
        self.mock_mock_config = self.mock_config_patcher.start()

        self.mkdtemp_patcher = patch('tempfile.mkdtemp',
                                     return_value=self.temp_config_dir)
        self.mock_mkdtemp = self.mkdtemp_patcher.start()

    def tearDown(self):
        shutil.rmtree(self.temp_config_dir)
        self.mkdtemp_patcher.stop()
        self.mock_config_patcher.stop()
        super(TestConfigMockConfigDir, self).tearDown()

    def test_config_in_created_config_dir(self):
        config_dir = self.cmd._config_dir_basic(root=self.fake_root)

        self.assertEqual(self.temp_config_dir, config_dir)

        config_file = '{0}.cfg'.format(
            os.path.join(self.temp_config_dir, self.fake_root))
        with io.open(config_file, 'r', encoding='utf-8') as f:
            self.assertEqual(self.mock_mock_config.return_value,
                             f.read().strip())

    def test_config_in_specified_config_dir(self):
        config_dir = self.cmd._config_dir_basic(
            config_dir=self.temp_config_dir,
            root=self.fake_root)

        self.assertEqual(self.temp_config_dir, config_dir)

        config_file = '{0}.cfg'.format(
            os.path.join(self.temp_config_dir, self.fake_root))
        with io.open(config_file, 'r', encoding='utf-8') as f:
            self.assertEqual(self.mock_mock_config.return_value,
                             f.read().strip())

    @patch('pyrpkg.Commands.mockconfig', new_callable=PropertyMock)
    def test_config_using_root_guessed_from_branch(self, mockconfig):
        mockconfig.return_value = 'f26-candidate-i686'

        config_dir = self.cmd._config_dir_basic()

        self.assertEqual(self.temp_config_dir, config_dir)

        config_file = '{0}.cfg'.format(
            os.path.join(self.temp_config_dir, mockconfig.return_value))
        with io.open(config_file, 'r', encoding='utf-8') as f:
            self.assertEqual(self.mock_mock_config.return_value,
                             f.read().strip())

    def test_fail_if_error_occurs_while_getting_mock_config(self):
        self.mock_mock_config.side_effect = rpkgError

        with patch('pyrpkg.Commands._cleanup_tmp_dir') as mock:
            self.assertRaises(
                rpkgError, self.cmd._config_dir_basic, root=self.fake_root)
            mock.assert_called_once_with(self.mock_mkdtemp.return_value)

        with patch('pyrpkg.Commands._cleanup_tmp_dir') as mock:
            self.assertRaises(rpkgError,
                              self.cmd._config_dir_basic,
                              config_dir='/path/to/fake/config-dir',
                              root=self.fake_root)
            mock.assert_called_once_with(None)

    def test_fail_if_error_occurs_while_writing_cfg_file(self):
        with patch.object(io, 'open') as m:
            m.return_value.__enter__.return_value.write.side_effect = IOError

            with patch('pyrpkg.Commands._cleanup_tmp_dir') as mock:
                self.assertRaises(rpkgError,
                                  self.cmd._config_dir_basic,
                                  root=self.fake_root)
                mock.assert_called_once_with(self.mock_mkdtemp.return_value)

            with patch('pyrpkg.Commands._cleanup_tmp_dir') as mock:
                self.assertRaises(rpkgError,
                                  self.cmd._config_dir_basic,
                                  config_dir='/path/to/fake/config-dir',
                                  root=self.fake_root)
                mock.assert_called_once_with(None)


class TestConfigMockConfigDirWithNecessaryFiles(CommandTestCase):
    """Test Commands._config_dir_other"""

    require_test_repos = False

    def setUp(self):
        super(TestConfigMockConfigDirWithNecessaryFiles, self).setUp()
        self.cmd = self.make_commands(path='/path/to/repo')

    @patch('shutil.copy2')
    @patch('os.path.exists', return_value=True)
    def test_copy_cfg_files_from_etc_mock_dir(self, exists, copy2):
        self.cmd._config_dir_other('/path/to/config-dir')

        exists.assert_has_calls([
            call('/etc/mock/site-defaults.cfg'),
            call('/etc/mock/logging.ini')
        ])
        copy2.assert_has_calls([
            call('/etc/mock/site-defaults.cfg',
                 '/path/to/config-dir/site-defaults.cfg'),
            call('/etc/mock/logging.ini',
                 '/path/to/config-dir/logging.ini'),
        ])

    @patch('os.path.exists', return_value=False)
    def test_create_empty_cfg_files_if_not_exist_in_system_mock(self, exists):
        with patch.object(six.moves.builtins, 'open', mock_open()) as m:
            self.cmd._config_dir_other('/path/to/config-dir')

            m.assert_has_calls([
                call('/path/to/config-dir/site-defaults.cfg', 'w'),
                call().close(),
                call('/path/to/config-dir/logging.ini', 'w'),
                call().close(),
            ])

        exists.assert_has_calls([
            call('/etc/mock/site-defaults.cfg'),
            call('/etc/mock/logging.ini')
        ])

    @patch('shutil.copy2')
    @patch('os.path.exists', return_value=True)
    def test_fail_when_copy_cfg_file(self, exists, copy2):
        copy2.side_effect = OSError

        self.assertRaises(
            rpkgError, self.cmd._config_dir_other, '/path/to/config-dir')

    @patch('os.path.exists', return_value=False)
    def test_fail_if_error_when_write_empty_cfg_files(self, exists):
        with patch.object(six.moves.builtins, 'open', mock_open()) as m:
            m.side_effect = IOError
            self.assertRaises(
                rpkgError, self.cmd._config_dir_other, '/path/to/config-dir')


class TestLint(CommandTestCase):
    @patch('glob.glob')
    @patch('os.path.exists')
    @patch('pyrpkg.Commands._run_command')
    @patch('pyrpkg.Commands.load_rpmdefines', new=mock_load_rpmdefines)
    @patch('pyrpkg.Commands.rel', new_callable=PropertyMock)
    def test_lint_each_file_once(self, rel, run, exists, glob):
        rel.return_value = '2.fc26'

        cmd = self.make_commands()
        srpm_path = os.path.join(cmd.path, 'docpkg-1.2-2.fc26.src.rpm')
        bin_path = os.path.join(cmd.path, 'x86_64', 'docpkg-1.2-2.fc26.x86_64.rpm')

        def _mock_exists(path):
            return path in [
                srpm_path,
                os.path.join(cmd.path, 'x86_64'),
            ]

        def _mock_glob(g):
            return {
                os.path.join(cmd.path, 'x86_64', '*.rpm'): [bin_path],
                srpm_path: [srpm_path],
            }[g]

        exists.side_effect = _mock_exists
        glob.side_effect = _mock_glob
        cmd._get_build_arches_from_spec = Mock(
            return_value=['x86_64', 'x86_64'])
        run.return_value = [0, "version 1.1", None]

        cmd.lint()

        self.assertEqual(
            run.call_args_list,
            [call(['rpmlint', '--version'],
                  return_stdout=True,
                  return_text=True),
             call(['rpmlint',
                   os.path.join(cmd.path, 'docpkg.spec'),
                   srpm_path,
                   bin_path,
                   ])])

    @patch('glob.glob')
    @patch('os.path.exists')
    @patch('pyrpkg.Commands._run_command')
    @patch('pyrpkg.Commands.load_rpmdefines', new=mock_load_rpmdefines)
    @patch('pyrpkg.Commands.rel', new_callable=PropertyMock)
    def test_lint_dist_git_results_layout(self, rel, run, exists, glob):
        rel.return_value = '2.fc26'

        cmd = self.make_commands(results_dir='subdir')
        srpm_path = os.path.join(cmd.path, 'results',
                                 'docpkg-1.2-2.fc26.src.rpm')
        bin_path = os.path.join(cmd.path, 'results',
                                'docpkg-1.2-2.fc26.x86_64.rpm')
        debuginfo_path = os.path.join(cmd.path, 'results',
                                      'docpkg-debuginfo-1.2-2.fc26.src.rpm')
        debugsource_path = os.path.join(cmd.path, 'results',
                                        'docpkg-debugsource-1.2-2.fc26.src.rpm')

        def _mock_exists(path):
            return path in [srpm_path, os.path.join(cmd.path, 'results')]

        def _mock_glob(g):
            return {
                os.path.join(cmd.path, 'results', '*.rpm'): [bin_path],
                srpm_path: [srpm_path, debuginfo_path, debugsource_path],
            }[g]

        exists.side_effect = _mock_exists
        glob.side_effect = _mock_glob
        run.return_value = [0, "version 1.1", None]

        cmd.lint()

        self.assertEqual(
            run.call_args_list,
            [call(['rpmlint', '--version'],
                  return_stdout=True,
                  return_text=True),
             call(['rpmlint',
                   os.path.join(cmd.path, 'docpkg.spec'),
                   srpm_path,
                   bin_path,
                   ])])

    @patch('glob.glob')
    @patch('os.path.exists')
    @patch('pyrpkg.Commands._run_command')
    @patch('pyrpkg.Commands.load_rpmdefines', new=mock_load_rpmdefines)
    @patch('pyrpkg.Commands.rel', new_callable=PropertyMock)
    def test_lint_mockbuild(self, rel, run, exists, glob):
        rel.return_value = '2.fc26'

        cmd = self.make_commands()
        mockdir = os.path.join(cmd.path,
                               'results_%s/1.2/2.fc26' % os.path.basename(self.repo_path))
        srpm_path = os.path.join(mockdir, 'docpkg-1.2-2.fc26.src.rpm')
        bin_path = os.path.join(mockdir, 'docpkg-1.2-2.fc26.x86_64.rpm')

        def _mock_exists(path):
            return path in mockdir

        def _mock_glob(g):
            return {os.path.join(mockdir, '*.rpm'): [srpm_path, bin_path]}[g]

        exists.side_effect = _mock_exists
        glob.side_effect = _mock_glob
        run.return_value = [0, "version 1.1", None]

        cmd.lint()

        self.assertEqual(
            run.call_args_list,
            [call(['rpmlint', '--version'],
                  return_stdout=True,
                  return_text=True),
             call(['rpmlint',
                   os.path.join(cmd.path, 'docpkg.spec'),
                   srpm_path,
                   bin_path,
                   ])])


class TestRunCommand(CommandTestCase):
    """Test _run_command"""

    require_test_repos = False

    def setUp(self):
        super(TestRunCommand, self).setUp()
        self.cmd = self.make_commands(path='/path/to/repo')

    # NOTE: this method will be removed once 'shell' parameter is removed from
    # _run_command method. Currently it is marked as deprecated.
    # Until then, shell=True is excluded from bandit scan.
    @patch('subprocess.Popen')
    def test_run_command_within_shell(self, Popen):
        Popen.return_value.wait.return_value = 0

        result = self.cmd._run_command(['rpmbuild'], shell=True)  # nosec

        self.assertEqual((0, None, None), result)
        Popen.assert_called_once_with(
            'rpmbuild', env=os.environ, shell=True, cwd=None,  # nosec
            stdout=None, stderr=None, universal_newlines=False)

    @patch('subprocess.Popen')
    def test_run_command_without_shell(self, Popen):
        Popen.return_value.wait.return_value = 0

        result = self.cmd._run_command(['rpmbuild'])

        self.assertEqual((0, None, None), result)
        Popen.assert_called_once_with(
            ['rpmbuild'], env=os.environ, shell=False, cwd=None,
            stdout=None, stderr=None, universal_newlines=False)

    @patch('subprocess.Popen')
    def test_return_stdout(self, Popen):
        Popen.return_value.wait.return_value = 0
        Popen.return_value.stdout.read.return_value = 'output'

        result = self.cmd._run_command(
            ['rpmbuild'], shell=False, return_stdout=True)

        self.assertEqual((0, 'output', None), result)
        Popen.assert_called_once_with(
            ['rpmbuild'], env=os.environ, shell=False, cwd=None,
            stdout=subprocess.PIPE, stderr=None, universal_newlines=False)

    @patch('subprocess.Popen')
    def test_return_stderr(self, Popen):
        Popen.return_value.wait.return_value = 0
        Popen.return_value.stderr.read.return_value = 'output'

        result = self.cmd._run_command(
            ['rpmbuild'], shell=False, return_stderr=True)

        self.assertEqual((0, None, 'output'), result)
        Popen.assert_called_once_with(
            ['rpmbuild'], env=os.environ, shell=False, cwd=None,
            stdout=None, stderr=subprocess.PIPE, universal_newlines=False)

    @patch('subprocess.Popen')
    def test_pipe(self, Popen):
        Popen.return_value.wait.return_value = 0

        first_proc = Mock()
        second_proc = Mock()
        second_proc.wait.return_value = 0

        Popen.side_effect = [first_proc, second_proc]

        result = self.cmd._run_command(
            ['rpmbuild'], pipe=['grep', 'src.rpm'])

        self.assertEqual((0, None, None), result)
        Popen.assert_has_calls([
            call(['rpmbuild'],
                 env=os.environ, shell=False, cwd=None,
                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT),
            call(['grep', 'src.rpm'],
                 env=os.environ, shell=False, cwd=None,
                 stdin=first_proc.stdout, stdout=None, stderr=None,
                 universal_newlines=False),
        ])

    @patch('subprocess.Popen')
    def test_raise_error_if_error_is_raised_from_subprocess(self, Popen):
        Popen.side_effect = OSError(1, "msg")

        six.assertRaisesRegex(
            self, rpkgError, 'msg', self.cmd._run_command, ['rpmbuild'])

    @patch('subprocess.Popen')
    def test_raise_error_if_command_returns_nonzeror(self, Popen):
        Popen.return_value.wait.return_value = 1
        Popen.return_value.stderr.read.return_value = ''

        six.assertRaisesRegex(
            self, rpkgError, 'Failed to execute command',
            self.cmd._run_command, ['rpmbuild'])

    @patch('subprocess.Popen')
    def test_return_error_msg_if_return_stderr_is_set(self, Popen):
        Popen.return_value.wait.return_value = 1
        Popen.return_value.stderr.read.return_value = 'something wrong'

        result = self.cmd._run_command(['rpmbuild'], return_stderr=True)
        self.assertEqual((1, None, 'something wrong'), result)

    @patch('subprocess.Popen')
    def test_set_envs(self, Popen):
        Popen.return_value.wait.return_value = 0

        with patch.dict('os.environ', {}, clear=True):
            result = self.cmd._run_command(['rpmbuild'], env={'myvar': 'test'})

            self.assertEqual((0, None, None), result)
            Popen.assert_called_once_with(
                ['rpmbuild'], env={'myvar': 'test'},
                shell=False, cwd=None, stdout=None, stderr=None,
                universal_newlines=False)

    @patch('subprocess.Popen')
    def test_run_command_in_a_directory(self, Popen):
        Popen.return_value.wait.return_value = 0

        tempdir = tempfile.mkdtemp(prefix='rpkg_test_')
        self.cmd._run_command(['rpmbuild'], cwd=tempdir)

        Popen.assert_called_once_with(
            ['rpmbuild'], env=os.environ, shell=False, cwd=tempdir,
            stdout=None, stderr=None, universal_newlines=False)

        shutil.rmtree(tempdir)

    @patch('subprocess.Popen')
    def test_return_output_as_text(self, Popen):
        Popen.return_value.wait.return_value = 0

        self.cmd._run_command(
            ['rpmbuild'], return_stdout=True, return_text=True)

        Popen.assert_called_once_with(
            ['rpmbuild'], env=os.environ, shell=False, cwd=None,
            stdout=subprocess.PIPE, stderr=None, universal_newlines=True)
