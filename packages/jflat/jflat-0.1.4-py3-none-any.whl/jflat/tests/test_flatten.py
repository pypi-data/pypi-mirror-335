import unittest

from jflat import flatten


class TestFlatten(unittest.TestCase):
    def test_flat(self):
        """Test flattening a simple flat dictionary"""
        nested = {"a": "foo", "b": 2, "c": True}
        expected = {"$.a": "foo", "$.b": 2, "$.c": True}
        self.assertEqual(flatten(nested), expected)

    def test_flat_with_none(self):
        """Test flattening a flat dictionary with None values"""
        nested = {"a": "foo", "b": None, "c": True}
        expected = {"$.a": "foo", "$.b": None, "$.c": True}
        self.assertEqual(flatten(nested), expected)

    def test_slice(self):
        """Test flattening a dictionary with a list"""
        nested = {"a": "foo", "b": ["bar", 2]}
        expected = {"$.a": "foo", "$.b[0]": "bar", "$.b[1]": 2}
        self.assertEqual(flatten(nested), expected)

    def test_nested_map(self):
        """Test flattening a dictionary with a nested dictionary"""
        nested = {"a": "foo", "b": {"c": "bar", "d": 2}}
        expected = {"$.a": "foo", "$.b.c": "bar", "$.b.d": 2}
        self.assertEqual(flatten(nested), expected)

    def test_slice_with_nested_maps(self):
        """Test flattening a dictionary with a list of dictionaries"""
        nested = {"a": "foo", "b": [{"c": "bar", "d": 2}, {"c": "baz", "d": 3}]}
        expected = {"$.a": "foo", "$.b[0].c": "bar", "$.b[0].d": 2, "$.b[1].c": "baz", "$.b[1].d": 3}
        self.assertEqual(flatten(nested), expected)

    def test_slice_with_nested_maps_with_nested_slice(self):
        """Test flattening a dictionary with a list of dictionaries containing lists"""
        nested = {"a": "foo", "b": [{"c": "bar", "d": [2, True]}, {"c": "baz", "d": [3, False]}]}
        expected = {
            "$.a": "foo",
            "$.b[0].c": "bar",
            "$.b[0].d[0]": 2,
            "$.b[0].d[1]": True,
            "$.b[1].c": "baz",
            "$.b[1].d[0]": 3,
            "$.b[1].d[1]": False,
        }
        self.assertEqual(flatten(nested), expected)

    def test_slice_with_nested_maps_with_nested_slice_with_nested_map(self):
        """Test flattening a complex nested structure"""
        nested = {"a": "foo", "b": [{"c": "bar", "d": [{"e": 2}, True]}, {"c": "baz", "d": [{"e": 3}, False]}]}
        expected = {
            "$.a": "foo",
            "$.b[0].c": "bar",
            "$.b[0].d[0].e": 2,
            "$.b[0].d[1]": True,
            "$.b[1].c": "baz",
            "$.b[1].d[0].e": 3,
            "$.b[1].d[1]": False,
        }
        self.assertEqual(flatten(nested), expected)

    def test_top_level_list(self):
        """Test flattening a top level list"""
        nested = [{"a": "foo", "b": 2}, {"a": "bar", "b": 3}]
        expected = {"$[0].a": "foo", "$[0].b": 2, "$[1].a": "bar", "$[1].b": 3}
        self.assertEqual(flatten(nested), expected)


if __name__ == "__main__":
    unittest.main()
