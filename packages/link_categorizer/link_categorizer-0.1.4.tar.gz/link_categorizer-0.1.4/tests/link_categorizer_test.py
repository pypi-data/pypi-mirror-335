# setup unit test for link_categorizer.py

import unittest
import yaml
from src.link_categorizer.categorizer import categorize_links, categorize_link


class TestLinkCategorizer(unittest.TestCase):
    def setUp(self):
        # read from test_data.yml into self.data
        with open("test_data_url_schemes.yml", "r") as file:
            self.data_schemes = yaml.safe_load(file)

        with open("test_data_domains.yml", "r") as file:
            self.data_domains = yaml.safe_load(file)

        with open("test_data_paths.yml", "r") as file:
            self.data_paths = yaml.safe_load(file)

        with open("test_data_titles.yml", "r") as file:
            self.data_titles = yaml.safe_load(file)

    def test_categorize_link_schemes(self):
        for test in self.data_schemes:
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])

    def test_categorize_link_domains(self):
        for test in self.data_domains:
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])

    def test_categorize_link_paths(self):
        for test in self.data_paths:
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])

    def test_categorize_link_titles(self):
        for test in self.data_titles:
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])

    def test_categorize_link_text(self):
        for test in self.data_titles:
            test["text"] = test["title"]
            del test["title"]
            with self.subTest(test=test):
                self.assertEqual(categorize_link(test), test["expected"])
