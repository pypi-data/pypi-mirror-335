import os
import shutil
import unittest
import tempfile

from pyrpkg import spec
from pyrpkg.errors import rpkgError


class SpecFileTestCase(unittest.TestCase):
    def setUp(self):
        self.workdir = tempfile.mkdtemp(prefix='rpkg-tests.')
        self.rpmdefines = ["--define", "_sourcedir %s" % self.workdir,
                           "--define", "_specdir %s" % self.workdir,
                           "--define", "_builddir %s" % self.workdir,
                           "--eval", "%%undefine rhel"]
        self.specfile = os.path.join(self.workdir, self._testMethodName)

        # Write common header
        spec_fd = open(self.specfile, "w")
        spec_fd.write(
            "Name: test-spec\n"
            "Version: 0.0.1\n"
            "Release: 1\n"
            "Summary: test specfile\n"
            "License: BSD\n"
            "\n"
            "%description\n"
            "foo\n"
            "\n")
        spec_fd.close()

    def tearDown(self):
        shutil.rmtree(self.workdir)
        return

    def test_parse(self):
        # Write some sources
        spec_fd = open(self.specfile, "a")
        spec_fd.write(
            "Source0: https://example.com/tarball.tar.gz\n"
            "Source1: https://example.com/subdir/LICENSE.txt\n"
            "source2: https://another.domain.com/source.tar.gz\n"
            "SOURCE3: local.txt\n"
            "\n"
            "patch0: local.patch\n"
            "PAtch999: https://remote.patch-sourcce.org/another-patch.bz2\n")
        spec_fd.close()

        s = spec.SpecFile(self.specfile, self.rpmdefines)
        actual = s.sources
        expected = [
            "tarball.tar.gz",
            "LICENSE.txt",
            "source.tar.gz",
            "local.txt",
            "local.patch",
            "another-patch.bz2"]
        self.assertEqual(len(actual), len(expected))
        self.assertTrue(all([a == b for a, b in zip(actual, expected)]))

    def test_invalid_specfile(self):
        # Overwrite the specfile, removing mandatory fields
        # Parsing such invalid specfile fails
        spec_fd = open(self.specfile, "w")
        spec_fd.write("Foo: Bar\n")
        spec_fd.close()

        self.assertRaises(rpkgError,
                          spec.SpecFile,
                          self.specfile,
                          self.rpmdefines)
