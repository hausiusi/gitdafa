import json
import os
import sys

sys.path.append("./")

import loc


def _clear_ignore_lists():
    loc.ignored_extensions_clear()
    loc.ignored_directories_clear()
    # loc.ignored_subdirectories_clear()
    # loc.ignored_filenames_clear()


def _check_files_in_list_exist(file_list, *files_to_check):
    for file in files_to_check:
        assert file in [os.path.basename(f) for f in file_list]


def _check_files_in_list_not_exist(file_list, *files_to_check):
    for file in files_to_check:
        assert file not in [os.path.basename(f) for f in file_list]


def _check_extensions_in_list_exist(file_list, *extensions):
    for ext in extensions:
        assert ext in [os.path.splitext(f)[1] for f in file_list]


def _check_extensions_in_list_not_exist(file_list, *extensions):
    for ext in extensions:
        assert ext not in [os.path.splitext(f)[1] for f in file_list]


def test_nothing_ignored():
    _clear_ignore_lists()
    file_names = loc.get_file_names('tests/data/samples')
    assert len(file_names) == 8


def test_txt_ext_ignored():
    _clear_ignore_lists()
    loc.ignored_extensions_extend(['.txt'])
    file_names = loc.get_file_names('tests/data/samples')
    assert len(file_names) == 4
    _check_extensions_in_list_not_exist(file_names, '.txt')
    _check_extensions_in_list_exist(file_names, '.c', '.json', '.py', '.js')


def test_foo_dir_ignored():
    _clear_ignore_lists()
    loc.ignored_directories_extend(['foo'])
    file_names = loc.get_file_names('tests/data/samples')
    assert len(file_names) == 6
    _check_files_in_list_not_exist(file_names, 'baz2.txt', 'foo.txt')
    _check_files_in_list_exist(file_names, 'bar.TXT')


def test_bar_dir_ignored():
    _clear_ignore_lists()
    loc.ignored_directories_extend(['bar'])
    file_names = loc.get_file_names('tests/data/samples')
    assert len(file_names) == 6
    _check_files_in_list_not_exist(file_names, 'bar.TXT', 'baz1.txt')
    _check_files_in_list_exist(file_names, 'foo.txt')


def test_bar_baz_dir_ignored():
    _clear_ignore_lists()
    loc.ignored_directories_extend(['bar/baz'])
    file_names = loc.get_file_names('tests/data/samples')
    assert len(file_names) == 7
    _check_files_in_list_not_exist(file_names, 'baz1.txt')
    _check_files_in_list_exist(file_names, 'bar.TXT', 'foo.txt', 'baz2.txt')


def test_baz_subdir_ignored():
    _clear_ignore_lists()
    loc.ignored_subdirectories_extend(['baz'])
    file_names = loc.get_file_names('tests/data/samples')
    assert len(file_names) == 6
    _check_files_in_list_not_exist(file_names, 'baz1.txt', 'baz2.txt')
    _check_files_in_list_exist(file_names, 'bar.TXT', 'foo.txt')


def test_line_counter():
    _clear_ignore_lists()
    file_names = loc.get_file_names('tests/data/samples')
    with open('tests/data/expects/expect_loc.json') as f:
        expects = json.load(f)
    for file_name in file_names:
        counter = loc.LineCounter(file_name)
        cfi = counter.count()
        reference = expects[os.path.basename(file_name)]
        assert cfi.language == reference['language']
        assert cfi.comment_lines == reference['comment_lines']
        assert cfi.file_ext == reference['file_ext']
        assert cfi.code_lines == reference['code_lines']
        assert cfi.empty_lines == reference['empty_lines']
