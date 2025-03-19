import os
import shutil
import tempfile
import unittest
import warnings

try:
    import rpmautospec
except ImportError:
    rpmautospec = None

try:
    from unittest import mock
except ImportError:
    import mock

from pyrpkg.utils import (cached_property, is_file_in_directory,
                          is_file_tracked, log_result,
                          spec_file_undo_rpmautospec, warn_deprecated)

from utils import CommandTestCase


class CachedPropertyTestCase(unittest.TestCase):
    def test_computed_only_once(self):
        class Foo(object):
            @cached_property
            def foo(self):
                runs.append("run once")
                return 42

        runs = []

        f = Foo()
        self.assertEqual(len(runs), 0)
        self.assertEqual(f.foo, 42)
        self.assertEqual(len(runs), 1)
        self.assertEqual(f.foo, 42)
        self.assertEqual(len(runs), 1)

    def test_not_shared_between_properties(self):
        class Foo(object):
            @cached_property
            def foo(self):
                foo_runs.append("run once")
                return 42

            @cached_property
            def bar(self):
                bar_runs.append("run once")
                return 43

        foo_runs = []
        bar_runs = []

        f = Foo()
        self.assertEqual(len(foo_runs), 0)
        self.assertEqual(f.foo, 42)
        self.assertEqual(len(foo_runs), 1)
        self.assertEqual(f.foo, 42)
        self.assertEqual(len(foo_runs), 1)

        self.assertEqual(len(bar_runs), 0)
        self.assertEqual(f.bar, 43)
        self.assertEqual(len(bar_runs), 1)
        self.assertEqual(f.bar, 43)
        self.assertEqual(len(bar_runs), 1)

    def test_not_shared_between_instances(self):
        class Foo(object):
            @cached_property
            def foo(self):
                foo_runs.append("run once")
                return 42

        class Bar(object):
            @cached_property
            def foo(self):
                bar_runs.append("run once")
                return 43

        foo_runs = []
        bar_runs = []

        f = Foo()
        self.assertEqual(len(foo_runs), 0)
        self.assertEqual(f.foo, 42)
        self.assertEqual(len(foo_runs), 1)
        self.assertEqual(f.foo, 42)
        self.assertEqual(len(foo_runs), 1)

        b = Bar()
        self.assertEqual(len(bar_runs), 0)
        self.assertEqual(b.foo, 43)
        self.assertEqual(len(bar_runs), 1)
        self.assertEqual(b.foo, 43)
        self.assertEqual(len(bar_runs), 1)

    def test_not_shared_when_inheriting(self):
        class Foo(object):
            @cached_property
            def foo(self):
                foo_runs.append("run once")
                return 42

        class Bar(Foo):
            @cached_property
            def foo(self):
                bar_runs.append("run once")
                return 43

        foo_runs = []
        bar_runs = []

        b = Bar()
        self.assertEqual(len(bar_runs), 0)
        self.assertEqual(b.foo, 43)
        self.assertEqual(len(bar_runs), 1)
        self.assertEqual(b.foo, 43)
        self.assertEqual(len(bar_runs), 1)

        f = Foo()
        self.assertEqual(len(foo_runs), 0)
        self.assertEqual(f.foo, 42)
        self.assertEqual(len(foo_runs), 1)
        self.assertEqual(f.foo, 42)
        self.assertEqual(len(foo_runs), 1)

        bar_runs = []
        b = Bar()
        self.assertEqual(len(bar_runs), 0)
        self.assertEqual(b.foo, 43)
        self.assertEqual(len(bar_runs), 1)
        self.assertEqual(b.foo, 43)
        self.assertEqual(len(bar_runs), 1)


class DeprecationUtilsTestCase(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('always', DeprecationWarning)

    @mock.patch('sys.stderr')
    def test_warn_deprecated(self, mock_stderr):
        class Foo(object):
            def old_method(self):
                warn_deprecated(self.__class__.__name__, 'old_method',
                                'new_method')
                return self.new_method()

            def new_method(self):
                return "Yay!"

        def mock_write(msg):
            written_lines.append(msg)

        written_lines = []
        mock_stderr.write.side_effect = mock_write

        foo = Foo()
        self.assertEqual(foo.old_method(), foo.new_method())
        self.assertEqual(len(written_lines), 1)
        self.assertTrue('DeprecationWarning' in written_lines[0])
        self.assertTrue('Foo.old_method' in written_lines[0])
        self.assertTrue('Foo.new_method' in written_lines[0])


class LogResultTestCase(unittest.TestCase):
    def setUp(self):
        self.logs = []

        def info(msg):
            self.logs.append(msg)

        self.log_func = info

    def test_dict_result(self):
        obj = {'spam': 'maps'}
        expected = [
            'spam:',
            '  maps',
        ]
        log_result(self.log_func, obj)
        self.assertEqual(self.logs, expected)

    def test_list_result(self):
        obj = ['eggs', 'bacon', 'hash']
        expected = [
            'eggs',
            'bacon',
            'hash',
        ]
        log_result(self.log_func, obj)
        self.assertEqual(self.logs, expected)

    def test_str_result(self):
        obj = 'spam'
        expected = [
            'spam',
        ]
        log_result(self.log_func, obj)
        self.assertEqual(self.logs, expected)

    def test_complex_result(self):
        obj = {'breakfast': ['eggs', 'bacon', {'spam': 'maps'}]}
        expected = [
            'breakfast:',
            '  eggs',
            '  bacon',
            '  spam:',
            '    maps',
        ]
        log_result(self.log_func, obj)
        self.assertEqual(self.logs, expected)


class FileInDirectoryTestCase(unittest.TestCase):
    def test_is_file_in_directory(self):
        expected = (
            # file, directory, expected result
            ("/repo/fedpkg/sources", "/repo/fedpkg", "sources"),
            ("/repo/fedpkg/subdir/sources", "/repo/fedpkg", "subdir/sources"),
            ("/repo/fedpkg/sources/", "/repo/fedpkg", "sources"),
            ("/repo/fedpkg/sources", "/repo/fedpkg/", "sources"),
            ("/repo/file", "/", "repo/file"),
            ("/file", "/", "file"),
            ("sources", ".", "sources"),
            ("data/file", ".", "data/file"),
            ("dir/myrepo/sources", "dir/myrepo", "sources"),

            ("/sources", "/repo/fedpkg", None),
            ("/", "bad_dir_name", None),
            ("./", "./a", None),
            ("./b", "./a/", None),
            ("sources", "./dir", None),
            ("f", "./dir", None),
            ("file", "dir/myrepo", None),
            ("a/bbb", "/a/b", None),
            ("a/b", "/a/bbb", None),
        )
        for num, case in enumerate(expected):
            (file_path, dir_path, expected_result) = case
            self.assertEqual(
                is_file_in_directory(file_path, dir_path),
                expected_result,
                "The case num {0} has failed".format(num),
            )


class FileTrackedTestCase(CommandTestCase):
    def test_file_outside_of_repo(self):
        # check file outside of the test repo
        self.assertFalse(
            is_file_tracked("external_filename", self.repo_path)
        )

    def test_actual_file_in_repo(self):
        # check actual file from the test repo
        self.assertTrue(
            is_file_tracked(
                os.path.join(self.repo_path, "sources"),
                self.repo_path
            )
        )

    def test_newly_created_file_in_repo(self):
        # check newly created file in the test repo
        temp_file = tempfile.NamedTemporaryFile(dir=self.repo_path)
        self.assertFalse(
            is_file_tracked(temp_file.name, self.repo_path)
        )
        temp_file.close()

    def test_newly_added_file_to_stage(self):
        # check newly added file to stage in the test repo
        temp_file = tempfile.NamedTemporaryFile(dir=self.repo_path)
        temp_file_basename = os.path.basename(temp_file.name)
        self.run_cmd(["git", "add", temp_file_basename], cwd=self.repo_path)
        self.assertTrue(
            is_file_tracked(temp_file.name, self.repo_path)
        )
        temp_file.close()

    def test_not_existing_file(self):
        # check not existing file
        self.assertFalse(
            is_file_tracked("/file_doesnt_exist", self.repo_path)
        )

    def test_not_existing_file_should_belong_to_repo(self):
        # check not existing file that should belong to the test repo
        self.assertFalse(
            is_file_tracked(
                os.path.join(self.repo_path, "file_doesnt_exist"),
                self.repo_path
            )
        )


@unittest.skipIf(
    rpmautospec is None,
    "Skip test on releases where rpmautospec is not available (RHEL)")
class SpecFileUndoRpmautospec(CommandTestCase):
    def test_remove_autospec_from_specfile(self):
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures", "docpkg")

        specfile_without_rpmautospec = os.path.join(fixtures_dir, "docpkg.spec")
        specfile_without_rpmautospec_copy = os.path.join(self.repo_path, "docpkg.spec")
        shutil.copy2(specfile_without_rpmautospec, specfile_without_rpmautospec_copy)
        self.assertFalse(rpmautospec.specfile_uses_rpmautospec(specfile_without_rpmautospec_copy))
        self.assertFalse(spec_file_undo_rpmautospec(specfile_without_rpmautospec_copy))
        self.assertFalse(rpmautospec.specfile_uses_rpmautospec(specfile_without_rpmautospec_copy))
        os.remove(specfile_without_rpmautospec_copy)

        specfile_with_rpmautospec = os.path.join(fixtures_dir, "docpkg-rpmautospec.spec")
        specfile_with_rpmautospec_copy = os.path.join(self.repo_path, "docpkg-rpmautospec.spec")
        shutil.copy2(specfile_with_rpmautospec, specfile_with_rpmautospec_copy)
        # returns True if the specfile was modified
        self.assertTrue(spec_file_undo_rpmautospec(specfile_with_rpmautospec_copy))
        self.assertFalse(rpmautospec.specfile_uses_rpmautospec(
            specfile_with_rpmautospec_copy, check_autochangelog=False, check_autorelease=True))
        self.assertTrue(rpmautospec.specfile_uses_rpmautospec(
            specfile_with_rpmautospec_copy, check_autochangelog=True, check_autorelease=False))
        os.remove(specfile_with_rpmautospec_copy)
