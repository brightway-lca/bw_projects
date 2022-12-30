import os
import random
import shutil
import string
import sys
import tempfile
import unittest

from pathlib import Path

from bw_projects.project import ProjectManager, ProjectDataset
from bw_projects.filesystem import maybe_path, create_dir, check_dir, safe_filename
from bw_projects import projects


class TestProjects(unittest.TestCase):
    def setUp(self):
        self.tempdir = projects._use_temp_directory()
        self.current = "".join(random.choices(string.ascii_lowercase, k=18))
        self.assertEqual("default", projects.current)
        projects.set_current(self.current)
        self.assertEqual(self.current, projects.current)
        self.projects = projects

    def tearDown(self):
        if hasattr(self.projects, "_lock"):
            try:
                self.projects._lock.release()
            except (RuntimeError):
                pass
        shutil.rmtree(self.tempdir)

    def test_project_default(self):
        self.assertTrue(self.projects.current)
        self.assertEqual(self.current, self.projects.current)
        self.assertTrue(check_dir(self.projects.dir.absolute()))
        self.assertTrue(check_dir(self.projects.logs_dir.absolute()))
        self.assertEqual(len(self.projects), 2)
        self.assertTrue("default" in self.projects)

    def test_create_project(self):
        self.assertEqual(len(self.projects), 2)
        self.projects.create_project("a-new-project")
        self.assertEqual(len(self.projects), 3)
        self.assertNotEqual(projects.current, "a-new-project")
        self.assertTrue("a-new-project" in self.projects)

    def test_set_current(self):
        new_project_name = "".join(random.choices(string.ascii_lowercase, k=18))
        self.assertNotEqual(projects.current, new_project_name)
        self.assertFalse(
            check_dir(
                f"{self.projects._base_data_dir}/{safe_filename(new_project_name)}"
            )
        )
        self.projects.set_current(new_project_name)
        self.assertTrue(
            check_dir(
                f"{self.projects._base_data_dir}/{safe_filename(new_project_name)}"
            )
        )

    @unittest.skip("Don't run this test. It will clean up existing projects")
    def test_project_creation(self):
        """No arguments, initializing project instance"""
        projects = ProjectManager()
        self.assertGreater(len(projects), 1)
        self.assertEqual(projects.current, "default")
        shutil.rmtree(projects.dir)

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_windows_path(self):
        """Logic to confirm we handle windows path length limitation"""
        pass

    def test_project_folder(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            projects = ProjectManager(tmpdirname)
            self.assertEqual(projects.current, "default")
            self.assertEqual(len(projects), 1)
            self.assertTrue(check_dir(projects.dir))
            self.assertTrue(projects.dir.is_relative_to(tmpdirname))

    def test_project_with_folder_priority(self):
        """Pass folder argument and confirm ENV variable doesn't get used"""
        os.environ["BRIGHTWAY_DIR"] = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdirname:
            projects = ProjectManager(tmpdirname)
            self.assertEqual(projects.current, "default")
            self.assertEqual(len(projects), 1)
            self.assertTrue(check_dir(projects.dir))
            self.assertTrue(projects.dir.is_relative_to(tmpdirname))
            self.assertFalse(projects.dir.is_relative_to(os.getenv("BRIGHTWAY_DIR")))
            self.assertFalse(
                check_dir(f"{os.getenv('BRIGHTWAY_DIR')}/{safe_filename('default')}")
            )
            del os.environ["BRIGHTWAY_DIR"]

    def test_project_with_env_variable(self):
        """Pass folder argument and confirm ENV variable doesn't get used"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            os.environ["BRIGHTWAY_DIR"] = tmpdirname
            projects = ProjectManager()
            self.assertTrue(
                check_dir(f"{os.getenv('BRIGHTWAY_DIR')}/{safe_filename('default')}")
            )
            self.assertEqual(projects.current, "default")
            self.assertEqual(len(projects), 1)
            self.assertTrue(check_dir(projects.dir))
            self.assertTrue(projects.dir.is_relative_to(tmpdirname))
            del os.environ["BRIGHTWAY_DIR"]

    def test_multiple_projects_different_location(self):
        folder_1 = "".join(random.choices(string.ascii_lowercase, k=8))
        self.assertFalse(check_dir(folder_1))
        project_1 = ProjectManager(folder_1)
        self.assertEqual(project_1.current, "default")

        folder_2 = "".join(random.choices(string.ascii_lowercase, k=8))
        self.assertFalse(check_dir(folder_2))
        project_2 = ProjectManager(folder_2)
        self.assertEqual(project_2.current, "default")

        self.assertNotEqual(
            project_1._base_data_dir.as_posix(), project_2._base_data_dir.as_posix()
        )

        # Cleanup
        self.assertIn(folder_1, project_1._base_data_dir.as_posix())
        shutil.rmtree(project_1._base_data_dir)
        self.assertIn(folder_2, project_2._base_data_dir.as_posix())
        shutil.rmtree(project_2._base_data_dir)


if __name__ == "__main__":
    unittest.main()
