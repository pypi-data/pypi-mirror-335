"""Test the high level SSG operations.

SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-only
"""
import os
import tempfile

import incorporealcms.ssg as ssg
from incorporealcms import init_instance

HERE = os.path.dirname(os.path.abspath(__file__))

instance_dir = os.path.join(HERE, 'instance')
init_instance(instance_dir)


def test_file_copy():
    """Test the ability to sync a file to the output dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generator = ssg.StaticSiteGenerator(src_dir, tmpdir)
        os.chdir(os.path.join(instance_dir, 'pages'))
        generator.build_file_in_destination(os.path.join(instance_dir, 'pages'), '', 'no-title.md', tmpdir,
                                            True)
        assert os.path.exists(os.path.join(tmpdir, 'no-title.md'))
        assert os.path.exists(os.path.join(tmpdir, 'no-title.html'))


def test_file_copy_no_markdown():
    """Test the ability to sync a file to the output dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generator = ssg.StaticSiteGenerator(src_dir, tmpdir)
        os.chdir(os.path.join(instance_dir, 'pages'))
        generator.build_file_in_destination(os.path.join(instance_dir, 'pages'), '', 'no-title.md', tmpdir,
                                            False)
        assert os.path.exists(os.path.join(tmpdir, 'no-title.md'))
        assert not os.path.exists(os.path.join(tmpdir, 'no-title.html'))


def test_file_copy_symlink():
    """Test the ability to sync a file to the output dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generator = ssg.StaticSiteGenerator(src_dir, tmpdir)
        os.chdir(os.path.join(instance_dir, 'pages'))
        generator.build_file_in_destination(os.path.join(instance_dir, 'pages'), '', 'symlink-to-foo.txt', tmpdir)
        # need to copy the destination for os.path.exists to be happy with this
        generator.build_file_in_destination(os.path.join(instance_dir, 'pages'), '', 'foo.txt', tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'symlink-to-foo.txt'))
        assert os.path.islink(os.path.join(tmpdir, 'symlink-to-foo.txt'))


def test_dir_copy():
    """Test the ability to sync a directory to the output dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generator = ssg.StaticSiteGenerator(src_dir, tmpdir)
        os.chdir(os.path.join(instance_dir, 'pages'))
        generator.build_subdir_in_destination(os.path.join(instance_dir, 'pages'), '', 'media', tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'media'))
        assert os.path.isdir(os.path.join(tmpdir, 'media'))


def test_dir_copy_symlink():
    """Test the ability to sync a directory to the output dir."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generator = ssg.StaticSiteGenerator(src_dir, tmpdir)
        os.chdir(os.path.join(instance_dir, 'pages'))
        generator.build_subdir_in_destination(os.path.join(instance_dir, 'pages'), '', 'symlink-to-subdir', tmpdir)
        # need to copy the destination for os.path.exists to be happy with this
        generator.build_subdir_in_destination(os.path.join(instance_dir, 'pages'), '', 'subdir', tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'symlink-to-subdir'))
        assert os.path.isdir(os.path.join(tmpdir, 'symlink-to-subdir'))
        assert os.path.islink(os.path.join(tmpdir, 'symlink-to-subdir'))


def test_build_in_destination():
    """Test the ability to walk a source and populate the destination."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generator = ssg.StaticSiteGenerator(src_dir, tmpdir)
        generator.build_in_destination(os.path.join(src_dir, 'pages'), tmpdir)

        assert os.path.exists(os.path.join(tmpdir, 'index.md'))
        assert os.path.exists(os.path.join(tmpdir, 'index.html'))
        assert os.path.exists(os.path.join(tmpdir, 'subdir', 'index.md'))
        assert os.path.exists(os.path.join(tmpdir, 'subdir', 'index.html'))


def test_build_in_destination_ignores_dot_files():
    """Test the ability to walk a source and populate the destination."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generator = ssg.StaticSiteGenerator(src_dir, tmpdir)
        generator.build_in_destination(os.path.join(src_dir, 'pages'), tmpdir)

        assert not os.path.exists(os.path.join(tmpdir, '.ignored-file.md'))
