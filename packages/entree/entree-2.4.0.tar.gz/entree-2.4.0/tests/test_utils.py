#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for entree
"""

import datetime
import os
import shutil
import unittest

from jinja2.exceptions import UndefinedError
import entree
from utilities import TMPFile, random_string


class TestConfig(unittest.TestCase):
    """Testing if config file was imported"""

    def test_get_config_dir(self):
        """Test get_config_dir()"""
        username = os.getenv("SUDO_USER") or os.getenv("USER")
        homedir = os.path.expanduser("~" + username)
        configdir = os.path.join(homedir, ".config")
        self.assertEqual(configdir, entree.utils.get_config_dir())

    def test_get_config_file(self):
        """Test get_config_file()"""
        configdir = entree.utils.get_config_dir()
        configfile = os.path.join(configdir, entree.utils.CONFIG_FILE_NAME)
        self.assertEqual(configfile, entree.utils.get_config_file())

    def test_get_config_param_shen(self):
        """Test get_config_param()"""
        shenanigan = entree.utils.get_config_param("shenanigan", "BLAH")
        self.assertEqual(shenanigan, "BLAH")

    def test_get_config_param_author(self):
        """Test get_config_param()
        This is not properly tested.
        """

        configdir = entree.utils.get_config_dir()
        configfile = os.path.join(configdir, entree.utils.CONFIG_FILE_NAME)

        author = "Julien Spronick"

        old_config = {}

        if os.path.exists(configfile):
            old_config = entree.utils.read_config()
            os.remove(configfile)

        entree.utils.set_config(author=author)
        author = entree.utils.get_config_param("author", "BLAH")
        self.assertEqual(author, "Julien Spronick")

        os.remove(configfile)

        if old_config:
            entree.utils.set_config(**old_config)

    def test_get_config_param_project(self):
        """Test get_config_param()
        This is not properly tested.
        """

        configdir = entree.utils.get_config_dir()
        configfile = os.path.join(configdir, entree.utils.CONFIG_FILE_NAME)

        author = "Julien Spronick"

        old_config = {}

        if os.path.exists(configfile):
            old_config = entree.utils.read_config()
            os.remove(configfile)

        entree.utils.set_config(author=author, project_config={"Flask": {"author": "Spronick Julien"}})
        author = entree.utils.get_config_param("author", value="BLAH")
        self.assertEqual(author, "Julien Spronick")

        author = entree.utils.get_config_param("author", value="BLAH", project_type="Flask")
        self.assertEqual(author, "Spronick Julien")

        os.remove(configfile)

        if old_config:
            entree.utils.set_config(**old_config)

    def test_create_config_inexisting(self):
        """Test set_config() and read_config() when config file does not exist"""
        configdir = entree.utils.get_config_dir()
        configfile = os.path.join(configdir, entree.utils.CONFIG_FILE_NAME)

        author = "Julien Spronck"
        author_email_prefix = "github"
        author_email_suffix = "frenetic.be"
        author_url = "http://frenetic.be"

        old_config = {}

        if os.path.exists(configfile):
            old_config = entree.utils.read_config()
            os.remove(configfile)

        config = entree.utils.read_config()
        self.assertTrue(os.path.exists(configfile))
        self.assertEqual(config["author"], "<UNDEFINED>")
        self.assertEqual(config["author_email_prefix"], "<UNDEFINED>")
        self.assertEqual(config["author_email_suffix"], "<UNDEFINED>")
        self.assertEqual(config["author_url"], "<UNDEFINED>")
        os.remove(configfile)

        entree.utils.set_config(
            author=author,
            author_email_prefix=author_email_prefix,
            author_email_suffix=author_email_suffix,
            author_url=author_url,
        )
        self.assertTrue(os.path.exists(configfile))
        config = entree.utils.read_config()
        self.assertEqual(config["author"], author)
        self.assertEqual(config["author_email_prefix"], author_email_prefix)
        self.assertEqual(config["author_email_suffix"], author_email_suffix)
        self.assertEqual(config["author_url"], author_url)

        entree.utils.set_config(overwrite=True)
        self.assertTrue(os.path.exists(configfile))
        config = entree.utils.read_config()
        self.assertEqual(config["author"], "<UNDEFINED>")
        self.assertEqual(config["author_email_prefix"], "<UNDEFINED>")
        self.assertEqual(config["author_email_suffix"], "<UNDEFINED>")
        self.assertEqual(config["author_url"], "<UNDEFINED>")

        os.remove(configfile)

        if old_config:
            entree.utils.set_config(**old_config)


class TesProjectConfig(unittest.TestCase):
    """Testing project-specific configuration"""

    def setUp(self):
        """Create a fake file structure to test"""
        self.configdir = entree.utils.get_config_dir()
        self.configfile = os.path.join(self.configdir, entree.utils.CONFIG_FILE_NAME)

        self.old_config = {}

        if os.path.exists(self.configfile):
            self.old_config = entree.utils.read_config()
            os.remove(self.configfile)

        config = {
            "author": "aaa",
            "author_email_prefix": "bbb",
            "author_email_suffix": "ccc",
            "author_url": "ddd",
            "project_config": {
                "Flask": {},
                "FlaskLarge": {"author": "eee"},
                "SQLAlchemy": {"author": "fff", "newfield": "ggg"},
            },
        }
        entree.utils.set_config(**config)

    def test_general_config(self):
        """Test create_dirs()"""
        theclass = entree.projects.Python
        config = theclass.get_config()
        self.assertEqual(config["author"], "aaa")
        self.assertEqual(config["author_email_prefix"], "bbb")
        self.assertEqual(config["author_email_suffix"], "ccc")
        self.assertEqual(config["author_url"], "ddd")
        self.assertListEqual(
            sorted(config.keys()), ["author", "author_email_prefix", "author_email_suffix", "author_url"]
        )

    def test_empty_project_config(self):
        """Test create_dirs()"""
        theclass = entree.projects.Flask
        config = theclass.get_config()
        self.assertEqual(config["author"], "aaa")
        self.assertEqual(config["author_email_prefix"], "bbb")
        self.assertEqual(config["author_email_suffix"], "ccc")
        self.assertEqual(config["author_url"], "ddd")
        self.assertListEqual(
            sorted(config.keys()), ["author", "author_email_prefix", "author_email_suffix", "author_url"]
        )

    def test_project_config(self):
        """Test create_dirs()"""
        theclass = entree.projects.FlaskLarge
        config = theclass.get_config()
        self.assertEqual(config["author"], "eee")
        self.assertEqual(config["author_email_prefix"], "bbb")
        self.assertEqual(config["author_email_suffix"], "ccc")
        self.assertEqual(config["author_url"], "ddd")
        self.assertListEqual(
            sorted(config.keys()), ["author", "author_email_prefix", "author_email_suffix", "author_url"]
        )

    def test_project_config_newkey(self):
        """Test create_dirs()"""
        theclass = entree.projects.SQLAlchemy
        config = theclass.get_config()
        self.assertEqual(config["author"], "fff")
        self.assertEqual(config["author_email_prefix"], "bbb")
        self.assertEqual(config["author_email_suffix"], "ccc")
        self.assertEqual(config["author_url"], "ddd")
        self.assertEqual(config["newfield"], "ggg")
        self.assertListEqual(
            sorted(config.keys()), ["author", "author_email_prefix", "author_email_suffix", "author_url", "newfield"]
        )

    def tearDown(self):
        """Get rid of the temporary file structure"""
        if os.path.exists(self.configfile):
            os.remove(self.configfile)

        if self.old_config:
            entree.utils.set_config(**self.old_config)


class TestCreateDirsAndFiles(unittest.TestCase):
    """Testing file and directory creation"""

    def test_create_general_file(self):
        """Test create_dirs()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            entree.utils.create_general_file(path_a, "AAAAA")
            self.assertTrue(os.path.exists(path_a))
            with open(path_a) as fil:
                content = fil.read()
                self.assertEqual(content, "AAAAA")

    def test_create_general_file_nofile(self):
        """Test create_dirs()"""
        rootdir = random_string(16)
        path_a = os.path.join(rootdir, "a")
        with self.assertRaises(IOError):
            entree.utils.create_general_file(path_a, "AAAAA")
        self.assertFalse(os.path.exists(path_a))

    def test_create_dirs(self):
        """Test create_dirs()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            entree.utils.create_dirs(rootdir, path_a, path_b, path_c)
            self.assertTrue(os.path.exists(rootdir))
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))

    def test_create_dirs_norootdir(self):
        """Test create_dirs()"""
        rootdir = random_string(16)
        path_a = os.path.join(rootdir, "a")
        path_b = os.path.join(rootdir, "b")
        path_c = os.path.join(rootdir, "c")
        with self.assertRaises(IOError):
            entree.utils.create_dirs(rootdir, path_a, path_b, path_c)
        self.assertFalse(os.path.exists(rootdir))
        self.assertFalse(os.path.exists(path_a))
        self.assertFalse(os.path.exists(path_b))
        self.assertFalse(os.path.exists(path_c))

    def test_render_template(self):
        """Test render_template()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            template_string = (
                "My name is {{ name }}, I'm {{ blah['age'] }} " "years old. This is year " "{{ date.strftime('%Y') }}."
            )
            entree.utils.create_general_file(path_a, template_string)
            date = datetime.datetime(2018, 1, 1)
            content = entree.utils.render_template(path_a, name="Lily", blah={"age": 19}, date=date)
            self.assertEqual(content, "My name is Lily, I'm 19 years old. " "This is year 2018.")

    def test_create_single_file(self):
        """Test create_single_file()"""
        with TMPFile() as rootdir:
            newfilename = "newfilename"
            template_path = os.path.join(rootdir, "template_path")

            template_string = "My name is {{ name }}, I'm {{ blah['age'] }} " "years old"
            entree.utils.create_general_file(template_path, template_string)
            entree.utils.create_single_file(rootdir, newfilename, template_path, name="Lily", blah={"age": 19})
            self.assertTrue(os.path.exists(os.path.join(rootdir, newfilename)))
            with open(os.path.join(rootdir, newfilename)) as fil:
                content = fil.read()
                self.assertEqual(content, "My name is Lily, I'm 19 years old")

    def test_create_single_file_nofile(self):
        """Test create_single_file()"""
        rootdir = random_string(16)
        path_a = os.path.join(rootdir, "a")
        with self.assertRaises(IOError):
            entree.utils.create_single_file(path_a, "", "")


class TestReplaceDirname(unittest.TestCase):
    """Testing entree.utils.replace_pathname"""

    def test_no_replace(self):
        """Testing entree.utils.replace_pathname when there is no replace
        dictionary
        """
        dirname = "blah"
        newdirname = entree.utils.replace_pathname(dirname)
        self.assertEqual(dirname, newdirname)

    def test_empty_replace(self):
        """Testing entree.utils.replace_pathname when replace is empty"""
        dirname = "blah"
        newdirname = entree.utils.replace_pathname(dirname, {})
        self.assertEqual(dirname, newdirname)

    def test_replace_no_match(self):
        """Testing entree.utils.replace_pathname when dirname is not in replace"""
        dirname = "blah"
        newdirname = entree.utils.replace_pathname(dirname, {"bloh": "yay"})
        self.assertEqual(dirname, newdirname)

    def test_replace_simple(self):
        """Testing entree.utils.replace_pathname when dirname is in replace"""
        dirname = "blah"
        newdirname = entree.utils.replace_pathname(dirname, {"blah": "yay"})
        self.assertEqual(newdirname, "yay")

    def test_replace_simple_template(self):
        """Testing entree.utils.replace_pathname when dirname is in replace
        but needs templating
        """
        dirname = "src"
        newdirname = entree.utils.replace_pathname(dirname, {"src": "{{ modname }}"}, modname="yay")
        self.assertEqual(newdirname, "yay")

    def test_replace_complex_template(self):
        """Testing entree.utils.replace_pathname when dirname is in replace
        but is complex and needs templating
        """
        dirname = os.path.join("src", "blah", "src", "blah", "src")
        newdirname = entree.utils.replace_pathname(dirname, {"src": "{{ modname }}"}, modname="yay")
        self.assertEqual(newdirname, os.path.join("yay", "blah", "yay", "blah", "yay"))

    def test_replace_python_file(self):
        """Testing entree.utils.replace_pathname when dirname is a python
        template
        """
        dirname = "yay_py.template"
        newdirname = entree.utils.replace_pathname(dirname, {"src": "{{ modname }}"}, modname="yay")
        self.assertEqual(newdirname, "yay.py")

    def test_replace_py_file_simple_dir(self):
        """Testing entree.utils.replace_pathname when dirname is a python
        template inside a dir
        """
        dirname = os.path.join("blah", "yay_py.template")
        newdirname = entree.utils.replace_pathname(dirname, {"src": "{{ modname }}"}, modname="yay")
        self.assertEqual(newdirname, os.path.join("blah", "yay.py"))

    def test_replace_py_file_in_dir(self):
        """Testing entree.utils.replace_pathname when dirname is a python
        template inside a dir
        """
        dirname = os.path.join("src", "blah", "src", "blah", "yay_py.template")
        newdirname = entree.utils.replace_pathname(dirname, {"src": "{{ modname }}"}, modname="yay")
        self.assertEqual(newdirname, os.path.join("yay", "blah", "yay", "blah", "yay.py"))


class TestGetAllDirsAndFiles(unittest.TestCase):
    """Testing entree.utils.get_all_dirs_and_files"""

    def test_get_all_dirs_and_files(self):
        """Testing entree.utils.get_all_dirs_and_files"""
        dirs = ["src", "src/static", "src/static/css", "src/static/js", "src/templates", "tests"]
        files = [
            ".gitignore",
            "License.md",
            "README.md",
            "requirements.txt",
            "setup_py.template",
            "src/__init___py.template",
            "src/models_py.template",
            "src/static/css/style.css",
            "src/static/js/app.js",
            "src/templates/index.html",
            "src/views_py.template",
            "tests/unittest_py.template",
        ]
        tpath = entree.projects.FlaskLarge.template_path()
        fldirs, flfiles = entree.utils.get_all_dirs_and_files(tpath)
        self.assertEqual(dirs, sorted(fldirs))
        self.assertEqual(files, sorted(flfiles))

    def test_get_all_dirs_and_files2(self):
        """Testing entree.utils.get_all_dirs_and_files"""
        dirs = ["src", "tests"]
        files = [
            ".gitignore",
            "License.md",
            "README.md",
            "requirements.txt",
            "setup_py.template",
            "src/__init___py.template",
            "tests/unittest_py.template",
        ]
        tpath = entree.projects.Python.template_path()
        fldirs, flfiles = entree.utils.get_all_dirs_and_files(tpath)
        self.assertEqual(dirs, sorted(fldirs))
        self.assertEqual(files, sorted(flfiles))

    def test_get_all_files_ignore(self):
        """Testing entree.utils.get_all_dirs_and_files
        with files_to_ignore
        """
        dirs = ["src", "tests"]
        files = [
            ".gitignore",
            "License.md",
            "README.md",
            "requirements.txt",
            "setup_py.template",
            "src/__init___py.template",
            "tests/unittest_py.template",
        ]
        files_to_ignore = [".DS_Store"]
        tpath = entree.projects.Python.template_path()
        fldirs, flfiles = entree.utils.get_all_dirs_and_files(tpath, files_to_ignore=files_to_ignore)
        self.assertEqual(dirs, sorted(fldirs))
        self.assertEqual(files, sorted(flfiles))

    def test_get_all_files_ignore2(self):
        """Testing entree.utils.get_all_dirs_and_files
        with files_to_ignore
        """
        dirs = ["src", "tests"]
        files = [
            ".gitignore",
            "README.md",
            "requirements.txt",
            "setup_py.template",
            "src/__init___py.template",
            "tests/unittest_py.template",
        ]
        files_to_ignore = [".DS_Store", "License.md"]
        tpath = entree.projects.Python.template_path()
        fldirs, flfiles = entree.utils.get_all_dirs_and_files(tpath, files_to_ignore=files_to_ignore)
        self.assertEqual(dirs, sorted(fldirs))
        self.assertEqual(files, sorted(flfiles))

    def test_get_all_files_ignore3(self):
        """Testing entree.utils.get_all_dirs_and_files
        with files_to_ignore
        """
        dirs = ["src", "tests"]
        files = [
            ".gitignore",
            "README.md",
            "setup_py.template",
            "src/__init___py.template",
            "tests/unittest_py.template",
        ]
        files_to_ignore = [".DS_Store", "License.md", "req*"]
        tpath = entree.projects.Python.template_path()
        fldirs, flfiles = entree.utils.get_all_dirs_and_files(tpath, files_to_ignore=files_to_ignore)
        self.assertEqual(dirs, sorted(fldirs))
        self.assertEqual(files, sorted(flfiles))

    def test_get_all_files_ignore4(self):
        """Testing entree.utils.get_all_dirs_and_files
        with files_to_ignore
        """
        dirs = ["src", "tests"]
        files = [
            ".gitignore",
            "requirements.txt",
            "setup_py.template",
            "src/__init___py.template",
            "tests/unittest_py.template",
        ]
        files_to_ignore = [".DS_Store", "*.md"]
        tpath = entree.projects.Python.template_path()
        fldirs, flfiles = entree.utils.get_all_dirs_and_files(tpath, files_to_ignore=files_to_ignore)
        self.assertEqual(dirs, sorted(fldirs))
        self.assertEqual(files, sorted(flfiles))

    def test_get_all_files_ignore5(self):
        """Testing entree.utils.get_all_dirs_and_files
        with files_to_ignore
        """
        dirs = ["src", "tests"]
        files = [
            ".gitignore",
            "License.md",
            "README.md",
            "requirements.txt",
            "setup_py.template",
            "tests/unittest_py.template",
        ]
        files_to_ignore = [".DS_Store", "src/*"]
        tpath = entree.projects.Python.template_path()
        fldirs, flfiles = entree.utils.get_all_dirs_and_files(tpath, files_to_ignore=files_to_ignore)
        self.assertEqual(dirs, sorted(fldirs))
        self.assertEqual(files, sorted(flfiles))

    def test_get_all_files_ignore6(self):
        """Testing entree.utils.get_all_dirs_and_files
        with files_to_ignore
        """
        dirs = ["tests"]
        files = [
            ".gitignore",
            "License.md",
            "README.md",
            "requirements.txt",
            "setup_py.template",
            "tests/unittest_py.template",
        ]
        files_to_ignore = [".DS_Store", "src"]
        tpath = entree.projects.Python.template_path()
        fldirs, flfiles = entree.utils.get_all_dirs_and_files(tpath, files_to_ignore=files_to_ignore)
        self.assertEqual(dirs, sorted(fldirs))
        self.assertEqual(files, sorted(flfiles))


class TestCopyFileStructure(unittest.TestCase):
    """Testing copy_file_structure"""

    def setUp(self):
        """Create a fake file structure to test"""
        self.template_dir = random_string(16)
        os.makedirs(self.template_dir)

        self.path_a = os.path.join(self.template_dir, "a")
        self.path_b = os.path.join(self.template_dir, "b")
        self.path_c = os.path.join(self.template_dir, "c")

        entree.utils.create_dirs(self.template_dir, self.path_a, self.path_b, self.path_c)

        self.file_a = os.path.join(self.path_a, "a.txt")
        self.file_b = os.path.join(self.path_b, "b.md")
        self.file_c = os.path.join(self.path_c, "c_py.template")

        entree.utils.create_general_file(self.file_a, "My name is")
        entree.utils.create_general_file(self.file_b, "{{ name }}")
        entree.utils.create_general_file(self.file_c, "I'm {{ blah['age'] }} years old.")

    def test_cfs_missing_dictionary(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            with self.assertRaises(UndefinedError):
                entree.utils.copy_file_structure(rootdir, self.template_dir)

    def test_cfs_with_blah_dictionary(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            file_a = os.path.join(path_a, "a.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            entree.utils.copy_file_structure(rootdir, self.template_dir, blah={"age": 19})
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertTrue(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))
            with open(file_a) as fil:
                content = fil.read()
                self.assertEqual(content, "My name is")
            with open(file_b) as fil:
                content = fil.read()
                self.assertEqual(content, "")
            with open(file_c) as fil:
                content = fil.read()
                self.assertEqual(content, "I'm 19 years old.")

    def test_cfs_with_blah_and_name(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            file_a = os.path.join(path_a, "a.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            entree.utils.copy_file_structure(rootdir, self.template_dir, blah={"age": 19}, name="Lily")
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertTrue(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))
            with open(file_a) as fil:
                content = fil.read()
                self.assertEqual(content, "My name is")
            with open(file_b) as fil:
                content = fil.read()
                self.assertEqual(content, "Lily")
            with open(file_c) as fil:
                content = fil.read()
                self.assertEqual(content, "I'm 19 years old.")

    def test_cfs_with_replace(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            file_a = os.path.join(path_a, "new.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            entree.utils.copy_file_structure(
                rootdir, self.template_dir, replace={"a.txt": "new.txt"}, blah={"age": 19}, name="Lily"
            )
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertTrue(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))
            with open(file_a) as fil:
                content = fil.read()
                self.assertEqual(content, "My name is")
            with open(file_b) as fil:
                content = fil.read()
                self.assertEqual(content, "Lily")
            with open(file_c) as fil:
                content = fil.read()
                self.assertEqual(content, "I'm 19 years old.")

    def test_cfs_with_replace_dir(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "newdir")
            file_a = os.path.join(path_a, "new.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            entree.utils.copy_file_structure(
                rootdir, self.template_dir, replace={"a.txt": "new.txt", "c": "newdir"}, blah={"age": 19}, name="Lily"
            )
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertTrue(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))
            with open(file_a) as fil:
                content = fil.read()
                self.assertEqual(content, "My name is")
            with open(file_b) as fil:
                content = fil.read()
                self.assertEqual(content, "Lily")
            with open(file_c) as fil:
                content = fil.read()
                self.assertEqual(content, "I'm 19 years old.")

    def test_cfs_with_replace_dir_templ(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "Lily")
            file_a = os.path.join(path_a, "new.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            entree.utils.copy_file_structure(
                rootdir,
                self.template_dir,
                replace={"a.txt": "new.txt", "c": "{{ name }}"},
                blah={"age": 19},
                name="Lily",
            )
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertTrue(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))
            with open(file_a) as fil:
                content = fil.read()
                self.assertEqual(content, "My name is")
            with open(file_b) as fil:
                content = fil.read()
                self.assertEqual(content, "Lily")
            with open(file_c) as fil:
                content = fil.read()
                self.assertEqual(content, "I'm 19 years old.")

    def test_cfs_partial(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            file_a = os.path.join(path_a, "a.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            partial = ["a", "a/a.txt", "c"]
            partial = [os.path.join(self.template_dir, name) for name in partial]
            entree.utils.copy_file_structure(rootdir, self.template_dir, partial=partial, blah={"age": 19})
            self.assertTrue(os.path.exists(path_a))
            self.assertFalse(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertTrue(os.path.exists(file_a))
            self.assertFalse(os.path.exists(file_b))
            self.assertFalse(os.path.exists(file_c))
            with open(file_a) as fil:
                content = fil.read()
                self.assertEqual(content, "My name is")

    def test_cfs_ignore(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            file_a = os.path.join(path_a, "a.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            ignore = ["a.txt"]
            entree.utils.copy_file_structure(rootdir, self.template_dir, files_to_ignore=ignore, blah={"age": 19})
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertFalse(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))

    def test_cfs_ignore2(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            file_a = os.path.join(path_a, "a.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            ignore = ["*.txt"]
            entree.utils.copy_file_structure(rootdir, self.template_dir, files_to_ignore=ignore, blah={"age": 19})
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertFalse(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))

    def test_cfs_ignore3(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            file_a = os.path.join(path_a, "a.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            ignore = ["a/*.txt"]
            entree.utils.copy_file_structure(rootdir, self.template_dir, files_to_ignore=ignore, blah={"age": 19})
            self.assertTrue(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertFalse(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))

    def test_cfs_ignore4(self):
        """Test copy_file_structure()"""
        with TMPFile() as rootdir:
            path_a = os.path.join(rootdir, "a")
            path_b = os.path.join(rootdir, "b")
            path_c = os.path.join(rootdir, "c")
            file_a = os.path.join(path_a, "a.txt")
            file_b = os.path.join(path_b, "b.md")
            file_c = os.path.join(path_c, "c.py")
            ignore = ["a"]
            entree.utils.copy_file_structure(rootdir, self.template_dir, files_to_ignore=ignore, blah={"age": 19})
            self.assertFalse(os.path.exists(path_a))
            self.assertTrue(os.path.exists(path_b))
            self.assertTrue(os.path.exists(path_c))
            self.assertFalse(os.path.exists(file_a))
            self.assertTrue(os.path.exists(file_b))
            self.assertTrue(os.path.exists(file_c))

    def tearDown(self):
        """Get rid of the temporary file structure"""
        if os.path.exists(self.template_dir):
            shutil.rmtree(self.template_dir)


if __name__ == "__main__":
    unittest.main()
