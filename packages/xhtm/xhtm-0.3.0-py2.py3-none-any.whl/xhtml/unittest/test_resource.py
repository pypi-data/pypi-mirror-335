# coding:utf-8

import unittest

from xhtml.resource import FileResource
from xhtml.resource import Resource


class TestFileResource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_file_not_found(self):
        self.assertRaises(FileNotFoundError, FileResource, "test.txt")


class TestResource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res: Resource = Resource()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_favicon(self):
        self.assertIsInstance(self.res.favicon.loadb(), bytes)

    def test_favicon_ext(self):
        self.assertEqual(self.res.favicon.ext, ".ico")

    def test_seek(self):
        self.assertIsInstance(self.res.seek("logo.svg").loads(), str)

    def test_seek_file_not_found(self):
        self.assertRaises(FileNotFoundError, self.res.seek, "test.txt")


if __name__ == "__main__":
    unittest.main()
