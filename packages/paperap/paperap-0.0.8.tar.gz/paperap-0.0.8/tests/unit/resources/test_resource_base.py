"""




 ----------------------------------------------------------------------------

    METADATA:

        File:    test_base.py
        Project: paperap
        Created: 2025-03-13
        Version: 0.0.8
        Author:  Jess Mann
        Email:   jess@jmann.me
        Copyright (c) 2025 Jess Mann

 ----------------------------------------------------------------------------

    LAST MODIFIED:

        2025-03-13     By Jess Mann

"""
from string import Template
from typing import override
import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError
from paperap.models import StandardModel
from tests.lib import UnitTestCase
from paperap.resources.base import BaseResource

class ExampleModel(StandardModel):
    name : str | None = None

class TestBaseResource(UnitTestCase):
    # TODO: All methods in this class are AI Generated Tests (gpt 4oo). Will remove this comment when they are removed.

    @override
    def setUp(self):
        super().setUp()
        class TestResource(BaseResource):
            model_class = ExampleModel
            endpoints = {
                "list": Template("http://example.com")
            }

        self.resource = TestResource(self.client) # type: ignore

    def test_all(self):
        self.resource._meta.queryset = MagicMock(return_value="queryset") # type: ignore
        self.assertEqual(self.resource.all(), "queryset")

    def test_filter(self):
        self.resource._meta.queryset = MagicMock() # type: ignore
        self.resource._meta.queryset.return_value.filter.return_value = "filtered_queryset" # type: ignore
        result = self.resource.filter(name="test")
        self.assertEqual(result, "filtered_queryset")

    def test_create_model(self):
        model_instance = self.resource.create_model(name="TestModel")
        self.assertEqual(model_instance.name, "TestModel")

    def test_transform_data_output(self):
        transformed = self.resource.transform_data_output(name="TestModel")
        self.assertEqual(transformed["name"], "TestModel")

    def test_endpoints_converted_to_template_init(self):
        class FooResource(BaseResource):
            model_class = MagicMock()
            endpoints = {
                "list": "http://example.com/fooresource/" # type: ignore
            }

        resource = FooResource(self.client)
        self.assertIsInstance(resource.endpoints, dict)
        self.assertIsInstance(resource.endpoints["list"], Template) # type: ignore
        self.assertEqual(resource.endpoints["list"].safe_substitute(), "http://example.com/fooresource/") # type: ignore

    def test_endpoints_init_list_required(self):
        with self.assertRaises(ValueError):
            class BarResource(BaseResource): # type: ignore
                model_class = MagicMock()
                endpoints = {
                    "create": Template("http://example.com") # type: ignore
                }

if __name__ == "__main__":
    unittest.main()
