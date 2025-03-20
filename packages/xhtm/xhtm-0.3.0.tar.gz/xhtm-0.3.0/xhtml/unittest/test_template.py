# coding:utf-8

import os
import unittest

from xhtml.template import LocaleTemplate


class TestLocaleTemplate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base: str = os.path.dirname(os.path.abspath(__file__))
        cls.template: LocaleTemplate = LocaleTemplate(cls.base)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_search(self):
        self.assertEqual(self.template.search("zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6", "login").lang.tag, "zh-Hans")  # noqa:E501
        self.assertEqual(self.template.search("en", "login").lang.tag, "en")
        self.assertEqual(self.template.search("fr", "login").lang.tag, "en")


if __name__ == "__main__":
    unittest.main()
