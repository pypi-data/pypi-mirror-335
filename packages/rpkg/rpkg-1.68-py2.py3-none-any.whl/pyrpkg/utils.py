# Copyright (c) 2015 - Red Hat Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.


"""Miscellaneous utilities

This module contains a bunch of utilities used elsewhere in pyrpkg.
"""

from __future__ import print_function

import argparse
import os
import subprocess
import sys

import git
import six

if six.PY3:
    def u(s):
        return s

    def validate_path(s):
        abspath = os.path.abspath(s)
        if os.path.exists(abspath):
            return s
        else:
            raise argparse.ArgumentTypeError('given path \'{0}\' doesn\'t exist'.format(abspath))

    getcwd = os.getcwd
else:
    def u(s):
        return s.decode('utf-8')

    def validate_path(s):
        abspath = os.path.abspath(s.decode('utf-8'))
        if os.path.exists(abspath):
            return s.decode('utf-8')
        else:
            raise argparse.ArgumentTypeError('given path \'{0}\' doesn\'t exist'.format(abspath))

    getcwd = os.getcwdu


class cached_property(property):
    """A property caching its return value

    This is pretty much the same as a normal Python property, except that the
    decorated function is called only once. Its return value is then saved,
    subsequent calls will return it without executing the function any more.

    Example:
        >>> class Foo(object):
        ...     @cached_property
        ...     def bar(self):
        ...         print("Executing Foo.bar...")
        ...         return 42
        ...
        >>> f = Foo()
        >>> f.bar
        Executing Foo.bar...
        42
        >>> f.bar
        42
    """
    def __get__(self, inst, type=None):
        try:
            return getattr(inst, '_%s' % self.fget.__name__)
        except AttributeError:
            v = super(cached_property, self).__get__(inst, type)
            setattr(inst, '_%s' % self.fget.__name__, v)
            return v


def warn_deprecated(clsname, oldname, newname):
    """Emit a deprecation warning

    :param str clsname: The name of the class which has its attribute
        deprecated.
    :param str oldname: The name of the deprecated attribute.
    :param str newname: The name of the new attribute, which should be used
        instead.
    """
    sys.stderr.write(
        "DeprecationWarning: %s.%s is deprecated and will be removed eventually.\n"
        "Please use %s.%s instead.\n" % (clsname, oldname, clsname, newname))


def _log_value(log_func, value, level, indent, suffix=''):
    offset = ' ' * level * indent
    log_func(''.join([offset, str(value), suffix]))


def log_result(log_func, result, level=0, indent=2):
    if isinstance(result, list):
        for item in result:
            log_result(log_func, item, level)
    elif isinstance(result, dict):
        for key, value in result.items():
            _log_value(log_func, key, level, indent, ':')
            log_result(log_func, value, level + 1)
    else:
        _log_value(log_func, result, level, indent)


def find_me():
    """Find the way to call the same binary/config as is being called now"""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-C', '--config', help='Specify a config file to use')
    (args, other) = parser.parse_known_args()

    binary = os.path.abspath(sys.argv[0])

    cmd = [binary]
    if args.config:
        cmd += ['--config', args.config]

    return cmd


def validate_module_dep_override(dep):
    """Validate the passed-in module dependency override."""
    try:
        return dep.split(':', 1)
    except (ValueError, AttributeError):
        raise argparse.ArgumentTypeError('This option must be in the format of "name:stream"')


def validate_module_build_optional(optional_arg):
    """Validate the passed-in optional argument to the module-build command."""
    try:
        key, value = optional_arg.split('=', 1)
    except (ValueError, AttributeError):
        raise argparse.ArgumentTypeError('This option must be in the format of "key=value"')

    if key in ('branch', 'buildrequire_overrides', 'require_overrides', 'scmurl'):
        raise argparse.ArgumentTypeError(
            'The "{0}" optional argument is reserved to built-in arguments'.format(key))

    # If the user passed in an integer such as a module build ID, then the type
    # should be an integer when sent to MBS
    try:
        value = int(value)
    except ValueError:
        pass

    return (key, value)


def make_koji_watch_tasks_handler(progname):
    def koji_watch_tasks_handler(_, tasks, quiet):
        """
        Displays information about running tasks and says how to watch them.
        Unlike the default version at koji library it overrides progname
        to show brew, koji or other build client.
        """
        if not quiet:
            tlist = ['%s: %s' % (t.str(), t.display_state(t.info))
                     for t in tasks.values() if not t.is_done()]
            print("Tasks still running. You can continue to watch with the '%s watch-task' command."
                  "\nRunning Tasks: %s" % (progname, '\n'.join(tlist)))

    # Save reference of the handler during first time use.
    # It guarantees that the same object is always returned (it allows unittest to pass).
    global handler_reference
    if 'handler_reference' not in globals():
        handler_reference = koji_watch_tasks_handler
    return handler_reference


def is_file_tracked(file_path, repo_path):
    """
    Finds out whether input file is currently tracked in the Git repository

    :param file_path: path to a file that should be checked (relative or absolute)
    :type file_path: str
    :param repo_path: path to Git repository (relative or absolute)
    :type repo_path: str
    :return: is file staged in git repo
    :rtype: bool
    """
    if not file_path:
        raise ValueError("empty file path")
    if not repo_path:
        raise ValueError("empty repo path")

    # file can be external and file like this is not tracked
    relative_file_path = is_file_in_directory(file_path, repo_path)
    if not relative_file_path:
        return False

    # create a repo object from our path
    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        # repo_path is not a valid repo - input file is not tracked
        return False
    except git.NoSuchPathError:
        raise RuntimeError("%s is not a valid path" % repo_path)

    if relative_file_path in repo.untracked_files:
        return False

    # search entries for the file name
    for entry in repo.index.entries.keys():
        (entry_file_name, _) = entry
        if entry_file_name == relative_file_path:
            return True

    return False


def is_file_in_directory(file_path, dir_path):
    """
    Compares two different paths - file and dictionary.
    Method doesn't check whether files exist.
    :param file_path: relative or absolute path to the file
    :type file_path: str
    :param dir_path: relative or absolute path to the directory
    :type dir_path: str
    :return: file path relative to the dictionary if the file is inside
        of the directory otherwise None
    :rtype: str or None
    """
    try:
        real_file_path = os.path.realpath(file_path)
        real_dir_path = os.path.realpath(dir_path)
    except TypeError:
        print(
            "Wrong value of the file name(s): ({0}, {1})".format(
                file_path, dir_path
            ),
            file=sys.stderr
        )
        raise

    # file is definitely outside of the repository
    if len(real_dir_path) > len(real_file_path):
        return

    # this case is not defined
    if real_file_path == real_dir_path:
        raise ValueError("Wrong input, paths are the same.")

    # paths have common prefix that equals to dir path -> file is inside the directory
    # NOTE: there is more suitable method 'os.path.commonpath' since Python 3.5.
    # It returns valid path.
    if os.path.commonprefix((real_file_path, real_dir_path)) == real_dir_path:
        # what is the file name relative to the directory
        # (length of filename is safely longer than length of directory)
        return real_file_path[len(real_dir_path):].strip("/")
    return


def check_rpm2archive():
    """
    Check if rpm2archive exists, and if it supports the required argument.
    """

    try:
        popen = subprocess.Popen(["rpm2archive", "--help"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        return "--nocompression" in popen.communicate()[0].decode("utf8")
    except OSError:
        pass
    return False


def extract_srpm(srpm_path, target_dir=None):
    """
    Extract srpm file into target directory. Target directory is a current
    directory if not specified
    """
    if not os.path.isfile(srpm_path):
        raise IOError("Input file doesn't exist: {0}".format(srpm_path))
    if target_dir and not os.path.isdir(target_dir):
        raise IOError("Target directory doesn't exist: {0}".format(target_dir))

    # We prefer using the newer rpm2archive utility over rpm2cpio for extraction
    # because it supports SRPMs >= 4GB (as long as it is available, i.e. epel8+)
    use_rpm2archive = check_rpm2archive()

    # Use one of those:
    # rpm2archive -n - < SRPM_PATH | tar xf -
    # rpm2cpio - < SRPM_PATH | cpio -iud --quiet
    cmd = ['rpm2archive', '-n', '-'] if use_rpm2archive else ['rpm2cpio', '-']
    # Overwrite existing files (tar's default, cpio -u), because git messes with
    # timestamps.
    cmd2 = ['tar', 'xf', '-'] if use_rpm2archive else ['cpio', '-iud', '--quiet']

    with open(srpm_path, 'r') as stdin:
        rpmcall = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=stdin,
                                   universal_newlines=True)
        cpiocall = subprocess.Popen(cmd2, stdin=rpmcall.stdout,
                                    universal_newlines=True, cwd=target_dir)
        output, err = cpiocall.communicate()
    return output, err


def is_lookaside_eligible_file(file_name, dir_path=None):
    """
    Binary files are eligible to be uploaded to the lookaside cache.
    File size and file extension doesn't matter.
    """
    file_path = os.path.join(dir_path or "", file_name)
    if os.path.isdir(file_path):
        # ignore dirs; do not upload them
        return False
    if not os.path.isfile(file_path):
        raise IOError("Input file doesn't exist: {0}".format(file_path))

    p = subprocess.Popen(
        # parameter '-b' causes brief output - without filename in the output
        ['file', '-b', '--mime-encoding', file_name],
        cwd=dir_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    output, errors = p.communicate()
    if errors:
        raise RuntimeError("Mime encoding detection of the file '{0}' has failed: {1}".format(
            file_path,
            errors
        ))
    # output contains encoding ("binary", "us-ascii", ...)
    encoding = output.strip()  # strip newline at the end
    return encoding == "binary"


def _replace_lines(lines, startline, endline, replacement_lines=None, strip_endline=False):
    replacement_lines = replacement_lines or []
    try:
        start = lines.index(startline)
        end = lines.index(endline, start)
    except ValueError:
        # if both are missing, nothing to do, all good
        # if only one of them is present, we better not touch it
        return lines, False
    else:
        # rpmautospec adds an empty line after the end
        # we want to remove it, but only if it is actually empty
        if strip_endline and lines[end + 1] == "\n":
            end += 1
        lines = lines[:start] + replacement_lines + lines[end + 1:]
        return lines, True


def spec_file_undo_rpmautospec(file_name, dir_path=None):
    """
    Given a path to specfile, undo changes generated by rpmautospec.
    Iff there is something to undo, the specfile will be overwritten.

    Namely:

     1. Removes everything between the following lines:
          ## START: Set by rpmautospec
          ## END: Set by rpmautospec
     2. Replaces everything between the following lines with %autochangelog:
          ## START: Generated by rpmautospec
          ## END: Generated by rpmautospec

    Both of the steps only happen once. If the specfile contains multiple such sections,
    only the first one is removed/replaced.

    The saved spec file is not guaranteed to be bit-by-bit identical with the original
    spec file used as an input to rpmautospec.
    However, subsequent repeated conversions there and back should be quite stable.

    The return value says whether the specfile was overwritten.
    """
    file_path = os.path.join(dir_path or "", file_name)

    try:
        with open(file_path) as f:
            contents = f.readlines()
    except Exception:
        # if we can't read it, let's do nothing
        return False

    # remove the generated macro section near the beginning of the specfile
    contents, was_removed = _replace_lines(
        contents,
        '## START: Set by rpmautospec\n',
        '## END: Set by rpmautospec\n',
        strip_endline=True)

    # replace the generated changelog with %autochangelog
    # note that this does not generally produce content identical to the original
    # e.g. the macro could have been conditionalized or in curly brackets
    # most importantly, the %changelog section might have been omitted entirely
    # however, this should be Good Enough for most of us
    contents, was_replaced = _replace_lines(
        contents,
        '## START: Generated by rpmautospec\n',
        '## END: Generated by rpmautospec\n',
        ['%autochangelog\n'])

    # finally, replace the spec if needed
    # if we cannot write it, better blow up
    if was_removed or was_replaced:
        with open(file_path, 'w') as f:
            f.writelines(contents)
        return True

    return False
