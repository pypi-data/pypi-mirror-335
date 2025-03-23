#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for entree.projects
"""

import os
import unittest

import entree.utils
import entree.projects.base as base
from utilities import get_file_content, TMPFile, print_header

CLASSES = base.ProjectBase.__subclasses__()


class TestFileCreation(unittest.TestCase):
    """Testing if files are successfully created"""

    def setUp(self):
        """Setting up"""
        self.cfile = entree.utils.CONFIG_FILE_NAME
        self.cdir = entree.utils.CONFIG_DIR
        entree.utils.CONFIG_FILE_NAME = "entree_config_test.json"
        entree.utils.CONFIG_DIR = "tests/"

    def test_directory_creation(self):
        """Test that all directories are created where they should be
        for all child classes of the ProjectBase class.
        """
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            # Create temporary rootdir
            with TMPFile() as rootdir:
                # Create temporary project directory
                with TMPFile(root=rootdir) as project:
                    print_header("Testing directory creation for class " "`{0}`".format(project_cls.__name__))
                    project_cls.create_all(rootdir, project)
                    gendir = os.path.join(rootdir, project)

                    tpath = project_cls.template_path()
                    dirs, _ = entree.utils.get_all_dirs_and_files(tpath)
                    dirmap = entree.utils.filemap(dirs, replace=project_cls.replace, modname=project)

                    for _, dname in dirmap.items():
                        print("- Testing directory `{0}`".format(dname))
                        path = os.path.join(gendir, dname)
                        try:
                            self.assertTrue(os.path.exists(path))
                        except AssertionError:
                            print("\nERROR: Path does not exist: " "{0}".format(path))
                            raise

    def test_file_creation(self):
        """Test that all files are created where they should be
        for all child classes of the ProjectBase class.
        """
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            # Create temporary rootdir
            with TMPFile() as rootdir:
                # Create temporary project directory
                with TMPFile(root=rootdir) as project:
                    print_header("Testing file creation for class " "`{0}`".format(project_cls.__name__))
                    project_cls.create_all(rootdir, project)
                    gendir = os.path.join(rootdir, project)

                    tpath = project_cls.template_path()
                    _, files = entree.utils.get_all_dirs_and_files(tpath)
                    filmap = entree.utils.filemap(files, replace=project_cls.replace, modname=project)
                    for _, fname in filmap.items():
                        print("- Testing file `{0}`".format(fname))
                        path = os.path.join(gendir, fname)
                        try:
                            self.assertTrue(os.path.exists(path))
                        except AssertionError:
                            print("\nERROR: Path does not exist: " "{0}".format(path))
                            raise

    def test_partial_file_creation(self):
        """Test that all files are created where they should be
        for all child classes of the ProjectBase class.
        """
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            # Create temporary rootdir
            config = project_cls.get_config()
            if "partial_builds" in config:
                for partial_build in config["partial_builds"]:
                    with TMPFile() as rootdir:
                        # Create temporary project directory
                        with TMPFile(root=rootdir) as project:
                            print_header(
                                "Testing partial file creation for " "class " "`{0}`".format(project_cls.__name__)
                            )
                            project_cls.create_all(rootdir, project, partial=partial_build)
                            gendir = os.path.join(rootdir, project)

                            tpath = project_cls.template_path()
                            files = entree.utils.get_all_dirs_and_files(tpath)
                            filmap = entree.utils.filemap(files[1], replace=project_cls.replace, modname=project)
                            partials = config["partial_builds"][partial_build]
                            for tname, fname in filmap.items():
                                path = os.path.join(gendir, fname)
                                if tname in partials:
                                    print("- Testing file " "`{0}`: IN".format(fname))
                                    try:
                                        self.assertTrue(os.path.exists(path))
                                    except AssertionError:
                                        print("\nERROR: Path does not " "exist: {0}".format(path))
                                        raise
                                else:
                                    print("- Testing file " "`{0}`: OUT".format(fname))
                                    try:
                                        self.assertFalse(os.path.exists(path))
                                    except AssertionError:
                                        print("\nERROR: Path does " "exist: {0}".format(path))
                                        raise

    def test_partial_file_creation_noconfig(self):
        """Test that all files are created where they should be
        for all child classes of the ProjectBase class.
        """
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            # Create temporary rootdir
            config = project_cls.get_config()
            with TMPFile() as rootdir:
                # Create temporary project directory
                with TMPFile(root=rootdir) as project:
                    if "partial_builds" not in config:
                        with self.assertRaises(ValueError):
                            project_cls.create_all(rootdir, project, partial="blah")
                    else:
                        with self.assertRaises(ValueError):
                            project_cls.create_all(rootdir, project, partial=project)

    def test_single_file_creation(self):
        """Test file creation in single-file mode
        for all child classes of the ProjectBase class.
        """
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            if project_cls.single_file:
                # Create temporary rootdir
                with TMPFile() as rootdir:
                    # Create temporary project directory
                    with TMPFile(root=rootdir) as project:
                        print_header("Testing single-file creation for class " "`{0}`".format(project_cls.__name__))
                        gendir = os.path.join(rootdir, project)
                        project_cls.create_one(gendir, "somefile.txt")
                        path = os.path.join(gendir, "somefile.txt")
                        try:
                            self.assertTrue(os.path.exists(path))
                        except AssertionError:
                            print("\nERROR: Path does not exist: " "{0}".format(path))
                            raise

    def test_file_content(self):
        """Test file content for all files for all child classes of the
        ProjectBase class.
        """

        for project_cls in CLASSES:
            with TMPFile() as rootdir:
                with TMPFile(root=rootdir) as project:
                    print_header("Testing file content for class " "`{0}`".format(project_cls.__name__))
                    project_cls.create_all(rootdir, project)

                    gendir = os.path.join(rootdir, project)
                    tpath = project_cls.template_path()
                    _, files = entree.utils.get_all_dirs_and_files(tpath)
                    filmap = entree.utils.filemap(files, replace=project_cls.replace, modname=project)
                    for tname, fname in filmap.items():
                        print("- Testing file content for " "`{0}`".format(fname))
                        filepath = os.path.join(gendir, fname)
                        templatepath = project_cls.template_path()
                        templatepath = os.path.join(templatepath, tname)
                        content1, content2 = get_file_content(project, filepath, templatepath, project_cls=project_cls)
                        self.assertEqual(content1, content2)

    def test_single_file_content(self):
        """Test file content in single-file mode
        for all child classes of the ProjectBase class.
        """
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            if project_cls.single_file:
                # Create temporary rootdir
                with TMPFile() as rootdir:
                    # Create temporary project directory
                    with TMPFile(root=rootdir) as project:
                        print_header("Testing single-file content for class " "`{0}`".format(project_cls.__name__))
                        gendir = os.path.join(rootdir, project)
                        project_cls.create_one(gendir, "somefile.txt")
                        filepath = os.path.join(gendir, "somefile.txt")
                        templatepath = project_cls.single_file_path()
                        content1, content2 = get_file_content(
                            "somefile", filepath, templatepath, project_cls=project_cls
                        )
                        self.assertEqual(content1, content2)

    def tearDown(self):
        """Tearing down"""
        entree.utils.CONFIG_FILE_NAME = self.cfile
        entree.utils.CONFIG_DIR = self.cdir


class TestFileCreationIgnore(unittest.TestCase):
    """Testing if files are successfully created"""

    def setUp(self):
        """Setting up"""
        self.cfile = entree.utils.CONFIG_FILE_NAME
        self.cdir = entree.utils.CONFIG_DIR
        entree.utils.CONFIG_FILE_NAME = "entree_config_test_ignore.json"
        entree.utils.CONFIG_DIR = "tests/"

    def test_directory_creation(self):
        """Test that all directories are created where they should be
        for all child classes of the ProjectBase class.
        """
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            # Create temporary rootdir
            with TMPFile() as rootdir:
                # Create temporary project directory
                with TMPFile(root=rootdir) as project:
                    print_header(
                        "Testing directory creation for class " "`{0}` with files to " "ignore".format(
                            project_cls.__name__
                        )
                    )
                    project_cls.create_all(rootdir, project)
                    config = project_cls.get_config()
                    files_to_ignore = []
                    if "files_to_ignore" in config:
                        files_to_ignore = config["files_to_ignore"]
                    print("Files to ignore: ", files_to_ignore)

                    gendir = os.path.join(rootdir, project)

                    tpath = project_cls.template_path()
                    dirs, _ = entree.utils.get_all_dirs_and_files(tpath, files_to_ignore=files_to_ignore)
                    dirmap = entree.utils.filemap(dirs, replace=project_cls.replace, modname=project)

                    for _, dname in dirmap.items():
                        print("- Testing directory `{0}`".format(dname))
                        path = os.path.join(gendir, dname)
                        try:
                            self.assertTrue(os.path.exists(path))
                        except AssertionError:
                            print("\nERROR: Path does not exist: " "{0}".format(path))
                            raise

    def test_file_creation(self):
        """Test that all files are created where they should be
        for all child classes of the ProjectBase class.
        """
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            # Create temporary rootdir
            with TMPFile() as rootdir:
                # Create temporary project directory
                with TMPFile(root=rootdir) as project:
                    print_header(
                        "Testing file creation for class " "`{0}` with files to " "ignore".format(project_cls.__name__)
                    )
                    project_cls.create_all(rootdir, project)
                    config = project_cls.get_config()
                    files_to_ignore = []
                    if "files_to_ignore" in config:
                        files_to_ignore = config["files_to_ignore"]
                    print("Files to ignore: ", files_to_ignore)

                    gendir = os.path.join(rootdir, project)

                    tpath = project_cls.template_path()
                    _, files = entree.utils.get_all_dirs_and_files(tpath, files_to_ignore=files_to_ignore)
                    filmap = entree.utils.filemap(files, replace=project_cls.replace, modname=project)
                    for _, fname in filmap.items():
                        print("- Testing file `{0}`".format(fname))
                        path = os.path.join(gendir, fname)
                        try:
                            self.assertTrue(os.path.exists(path))
                        except AssertionError:
                            print("\nERROR: Path does not exist: " "{0}".format(path))
                            raise

    def tearDown(self):
        """Tearing down"""
        entree.utils.CONFIG_FILE_NAME = self.cfile
        entree.utils.CONFIG_DIR = self.cdir


class TestProjectPaths(unittest.TestCase):
    """Testing if the template path, the single-file path
    files path exists
    """

    def test_template_path(self):
        """Testing template path"""
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            self.assertTrue(os.path.exists(project_cls.template_path()))

    def test_singlefile_path(self):
        """Testing single-file path"""
        # Loop through all classes available in entree.projects
        for project_cls in CLASSES:
            if project_cls.single_file:
                self.assertTrue(os.path.exists(project_cls.single_file_path()))


if __name__ == "__main__":
    unittest.main()
