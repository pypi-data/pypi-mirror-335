"""Test the conversion of Markdown pages.

SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-only
"""
import os
from unittest.mock import patch

import pytest

from incorporealcms.markdown import (generate_parent_navs, handle_markdown_file_path,
                                     instance_resource_path_to_request_path, parse_md,
                                     request_path_to_breadcrumb_display)

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, 'instance/', 'pages/'))


def test_generate_page_navs_index():
    """Test that the index page has navs to the root (itself)."""
    assert generate_parent_navs('index.md') == [('example.org', '/')]


def test_generate_page_navs_subdir_index():
    """Test that dir pages have navs to the root and themselves."""
    assert generate_parent_navs('subdir/index.md') == [('example.org', '/'), ('subdir', '/subdir/')]


def test_generate_page_navs_subdir_real_page():
    """Test that real pages have navs to the root, their parent, and themselves."""
    assert generate_parent_navs('subdir/page.md') == [('example.org', '/'), ('subdir', '/subdir/'),
                                                      ('Page', '/subdir/page')]


def test_generate_page_navs_subdir_with_title_parsing_real_page():
    """Test that title metadata is used in the nav text."""
    assert generate_parent_navs('subdir-with-title/page.md') == [
        ('example.org', '/'),
        ('SUB!', '/subdir-with-title/'),
        ('page', '/subdir-with-title/page')
    ]


def test_generate_page_navs_subdir_with_no_index():
    """Test that breadcrumbs still generate even if a subdir doesn't have an index.md."""
    assert generate_parent_navs('no-index-dir/page.md') == [
        ('example.org', '/'),
        ('/no-index-dir/', '/no-index-dir/'),
        ('page', '/no-index-dir/page')
    ]


def test_page_includes_themes_with_default():
    """Test that a request contains the configured themes and sets the default as appropriate."""
    assert '<link rel="stylesheet" type="text/css" title="light" href="/static/css/light.css">'\
        in handle_markdown_file_path('index.md')
    assert '<link rel="alternate stylesheet" type="text/css" title="dark" href="/static/css/dark.css">'\
        in handle_markdown_file_path('index.md')
    assert '<a href="" onclick="setStyle(\'light\'); return false;">[light]</a>'\
        in handle_markdown_file_path('index.md')
    assert '<a href="" onclick="setStyle(\'dark\'); return false;">[dark]</a>'\
        in handle_markdown_file_path('index.md')


def test_render_with_style_overrides():
    """Test that the default can be changed."""
    with patch('incorporealcms.Config.DEFAULT_PAGE_STYLE', 'dark'):
        assert '<link rel="stylesheet" type="text/css" title="dark" href="/static/css/dark.css">'\
            in handle_markdown_file_path('index.md')
        assert '<link rel="alternate stylesheet" type="text/css" title="light" href="/static/css/light.css">'\
            in handle_markdown_file_path('index.md')
    assert '<a href="" onclick="setStyle(\'light\'); return false;">[light]</a>'\
        in handle_markdown_file_path('index.md')
    assert '<a href="" onclick="setStyle(\'dark\'); return false;">[dark]</a>'\
        in handle_markdown_file_path('index.md')


def test_render_with_default_style_override():
    """Test that theme overrides work, and if a requested theme doesn't exist, the default is loaded."""
    with patch('incorporealcms.Config.PAGE_STYLES', {'cool': '/static/css/cool.css',
                                                     'warm': '/static/css/warm.css'}):
        with patch('incorporealcms.Config.DEFAULT_PAGE_STYLE', 'warm'):
            assert '<link rel="stylesheet" type="text/css" title="warm" href="/static/css/warm.css">'\
                in handle_markdown_file_path('index.md')
            assert '<link rel="alternate stylesheet" type="text/css" title="cool" href="/static/css/cool.css">'\
                in handle_markdown_file_path('index.md')
            assert '<link rel="alternate stylesheet" type="text/css" title="light" href="/static/css/light.css">'\
                not in handle_markdown_file_path('index.md')
            assert '<a href="" onclick="setStyle(\'warm\'); return false;">[warm]</a>'\
                in handle_markdown_file_path('index.md')
            assert '<a href="" onclick="setStyle(\'cool\'); return false;">[cool]</a>'\
                in handle_markdown_file_path('index.md')


def test_redirects_error_unsupported():
    """Test that we throw a warning about the barely-used Markdown redirect tag, which we can't support via SSG."""
    os.chdir(os.path.join(HERE, 'instance/', 'broken/'))
    with pytest.raises(NotImplementedError):
        handle_markdown_file_path('redirect.md')
    os.chdir(os.path.join(HERE, 'instance/', 'pages/'))


def test_instance_resource_path_to_request_path_on_index():
    """Test index.md -> /."""
    assert instance_resource_path_to_request_path('index.md') == '/'


def test_instance_resource_path_to_request_path_on_page():
    """Test no-title.md -> no-title."""
    assert instance_resource_path_to_request_path('no-title.md') == '/no-title'


def test_instance_resource_path_to_request_path_on_subdir():
    """Test subdir/index.md -> subdir/."""
    assert instance_resource_path_to_request_path('subdir/index.md') == '/subdir/'


def test_instance_resource_path_to_request_path_on_subdir_and_page():
    """Test subdir/page.md -> subdir/page."""
    assert instance_resource_path_to_request_path('subdir/page.md') == '/subdir/page'


def test_request_path_to_breadcrumb_display_patterns():
    """Test various conversions from request path to leaf nodes for display in the breadcrumbs."""
    assert request_path_to_breadcrumb_display('/foo') == 'foo'
    assert request_path_to_breadcrumb_display('/foo/') == 'foo'
    assert request_path_to_breadcrumb_display('/foo/bar') == 'bar'
    assert request_path_to_breadcrumb_display('/foo/bar/') == 'bar'
    assert request_path_to_breadcrumb_display('/') == ''


def test_parse_md_metadata():
    """Test the direct results of parsing a markdown file."""
    content, md, page_name, page_title, mtime = parse_md('more-metadata.md')
    assert page_name == 'title for the page'
    assert page_title == 'title for the page - example.org'


def test_parse_md_metadata_forced_no_title():
    """Test the direct results of parsing a markdown file."""
    content, md, page_name, page_title, mtime = parse_md('forced-no-title.md')
    assert page_name == ''
    assert page_title == 'example.org'


def test_parse_md_metadata_no_title_so_path():
    """Test the direct results of parsing a markdown file."""
    content, md, page_name, page_title, mtime = parse_md('subdir/index.md')
    assert page_name == '/subdir/'
    assert page_title == '/subdir/ - example.org'


def test_parse_md_no_file():
    """Test the direct results of parsing a markdown file."""
    with pytest.raises(FileNotFoundError):
        content, md, page_name, page_title, mtime = parse_md('nope.md')


def test_parse_md_bad_file():
    """Test the direct results of parsing a markdown file."""
    with pytest.raises(ValueError):
        content, md, page_name, page_title, mtime = parse_md('actually-a-png.md')
