import unittest

from jflat import unflatten


class TestUnflatten(unittest.TestCase):
    def test_flat(self):
        """Test unflattening a simple flat dictionary"""
        flattened = {"$.a": "foo", "$.b": 2, "$.c": True}
        expected = {"a": "foo", "b": 2, "c": True}
        self.assertEqual(unflatten(flattened), expected)

    def test_flat_with_none(self):
        """Test unflattening a flat dictionary with None values"""
        flattened = {"$.a": "foo", "$.b": None, "$.c": True}
        expected = {"a": "foo", "b": None, "c": True}
        self.assertEqual(unflatten(flattened), expected)

    def test_slice(self):
        """Test unflattening a dictionary with list notation"""
        flattened = {"$.a": "foo", "$.b[0]": "bar", "$.b[1]": 2}
        expected = {"a": "foo", "b": ["bar", 2]}
        self.assertEqual(unflatten(flattened), expected)

    def test_nested_map(self):
        """Test unflattening a dictionary with nested notation"""
        flattened = {"$.a": "foo", "$.b.c": "bar", "$.b.d": 2}
        expected = {"a": "foo", "b": {"c": "bar", "d": 2}}
        self.assertEqual(unflatten(flattened), expected)

    def test_slice_with_nested_maps(self):
        """Test unflattening a dictionary with list and nested dictionary notation"""
        flattened = {"$.a": "foo", "$.b[0].c": "bar", "$.b[0].d": 2, "$.b[1].c": "baz", "$.b[1].d": 3}
        expected = {"a": "foo", "b": [{"c": "bar", "d": 2}, {"c": "baz", "d": 3}]}
        self.assertEqual(unflatten(flattened), expected)

    def test_slice_with_nested_maps_with_nested_slice(self):
        """Test unflattening a complex structure with nested lists"""
        flattened = {
            "$.a": "foo",
            "$.b[0].c": "bar",
            "$.b[0].d[0]": 2,
            "$.b[0].d[1]": True,
            "$.b[1].c": "baz",
            "$.b[1].d[0]": 3,
            "$.b[1].d[1]": False,
        }
        expected = {"a": "foo", "b": [{"c": "bar", "d": [2, True]}, {"c": "baz", "d": [3, False]}]}
        self.assertEqual(unflatten(flattened), expected)

    def test_slice_with_nested_maps_with_nested_slice_with_nested_map(self):
        """Test unflattening a highly complex nested structure"""
        flattened = {
            "$.a": "foo",
            "$.b[0].c": "bar",
            "$.b[0].d[0].e": 2,
            "$.b[0].d[1]": True,
            "$.b[1].c": "baz",
            "$.b[1].d[0].e": 3,
            "$.b[1].d[1]": False,
        }
        expected = {"a": "foo", "b": [{"c": "bar", "d": [{"e": 2}, True]}, {"c": "baz", "d": [{"e": 3}, False]}]}
        self.assertEqual(unflatten(flattened), expected)

    def test_top_level_list(self):
        """Test unflattening a top-level list"""
        flattened = {"$[0]": "foo", "$[1]": 2, "$[2]": {"a": "bar"}}
        expected = ["foo", 2, {"a": "bar"}]
        self.assertEqual(unflatten(flattened), expected)


if __name__ == "__main__":
    unittest.main()
