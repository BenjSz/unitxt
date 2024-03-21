from src.unitxt.dict_utils import dict_delete, dict_get, dict_set
from tests.utils import UnitxtTestCase


class TestDictUtils(UnitxtTestCase):
    def test_simple_get(self):
        dic = {"a": 1, "b": 2, "d": [3, 4]}
        self.assertEqual(dict_get(dic, "a"), 1)
        self.assertEqual(dict_get(dic, "b"), 2)
        self.assertEqual(dict_get(dic, "c", not_exist_ok=True), None)
        with self.assertRaises(ValueError):
            dict_get(dic, "c")
        self.assertEqual(dict_get(dic, "d/1"), 4)
        with self.assertRaises(ValueError):
            dict_get(dic, "d/2")

    def test_nested_get(self):
        dic = {"a": {"b": 1, "c": 2}}
        self.assertEqual(dict_get(dic, "a/b", use_dpath=True), 1)
        self.assertEqual(dict_get(dic, "a/c", use_dpath=True), 2)
        self.assertEqual(dict_get(dic, "a/d", use_dpath=True, not_exist_ok=True), None)
        with self.assertRaises(ValueError):
            dict_get(dic, "a/d", use_dpath=True)

    def test_query_get(self):
        dic = {"a": [{"b": 1}, {"b": 2}]}
        self.assertEqual(dict_get(dic, "a/*/b", use_dpath=True), [1, 2])
        dic = {"a": [{"b": 1}, {"b": 2}], "c": [{"b": 3}, {"b": 4}]}
        self.assertEqual(dict_get(dic, "*/1/b", use_dpath=True), [2, 4])
        dic = {"references": ["r1", "r2", "r3"]}
        self.assertEqual(
            dict_get(dic, "references/*", use_dpath=True), ["r1", "r2", "r3"]
        )
        self.assertEqual(
            dict_get(dic, "references/", use_dpath=True), ["r1", "r2", "r3"]
        )
        self.assertEqual(
            dict_get(dic, "references", use_dpath=True), ["r1", "r2", "r3"]
        )
        with self.assertRaises(ValueError):
            dict_get(dic, "references+#/^!", use_dpath=True)

    def test_query_delete(self):
        dic = {"a": [{"b": 1}, {"b": 2, "c": 3}]}
        dict_delete(dic, "a/*/b", remove_empty_ancestors=True)
        self.assertEqual({"a": [{"c": 3}]}, dic)

        dic = {"references": ["r1", "r2", "r3"]}
        dict_delete(dic, "references/*")
        self.assertEqual({"references": []}, dic)

        dic = {"references": ["r1", "r2", "r3"]}
        dict_delete(dic, "references/*", remove_empty_ancestors=True)
        self.assertEqual({}, dic)

        dic = {"references": ["r1", "r2", "r3"]}
        dict_delete(dic, "references/*")
        self.assertEqual({"references": []}, dic)

        dic = {"references": ["r1", "r2", "r3"]}
        dict_delete(dic, "references/")
        self.assertEqual({"references": []}, dic)

        dic = {"references": ["r1", "r2", "r3"]}
        dict_delete(dic, "references/1")
        self.assertEqual({"references": ["r1", "r3"]}, dic)

        dic = {"references": ["r1", "r2", "r3"]}
        dict_delete(dic, "references", remove_empty_ancestors=True)
        self.assertEqual({}, dic)
        with self.assertRaises(ValueError):
            dict_delete(dic, "references+#/^!", remove_empty_ancestors=True)

        dic = {"a": [[["i1", "i2"], ["i3", "i4"]], [["i5", "i6"], ["i7", "i8"]]]}
        dict_delete(dic, "a/1/0/1")
        self.assertEqual(
            {"a": [[["i1", "i2"], ["i3", "i4"]], [["i5"], ["i7", "i8"]]]}, dic
        )
        dict_delete(dic, "a/1/0/0")
        self.assertEqual({"a": [[["i1", "i2"], ["i3", "i4"]], [[], ["i7", "i8"]]]}, dic)
        dict_delete(dic, "a/1/1")
        self.assertEqual({"a": [[["i1", "i2"], ["i3", "i4"]], [[]]]}, dic)
        dict_delete(dic, "a/1/0", remove_empty_ancestors=True)
        self.assertEqual({"a": [[["i1", "i2"], ["i3", "i4"]]]}, dic)

        with self.assertRaises(ValueError):
            dict_delete(dic, "aaa")
        with self.assertRaises(ValueError):
            dict_delete(dic, "a/2/3")

        self.assertEqual("i", dict_get(dic, "a/0/0/0/0", use_dpath=True))
        self.assertEqual("i", dict_get(dic, "a/0/0/0/0/0/0/0", use_dpath=True))
        with self.assertRaises(ValueError):
            dict_get(dic, "a/0/0/0/*/0")

    def test_simple_set(self):
        dic = {"a": 1, "b": 2}
        dict_set(dic, "a", 3)
        self.assertDictEqual(dic, {"a": 3, "b": 2})
        dict_set(dic, "b", 4)
        self.assertDictEqual(dic, {"a": 3, "b": 4})
        with self.assertRaises(ValueError):
            dict_set(dic, "c", 5, not_exist_ok=False)
        dict_set(dic, "c", 5)
        self.assertDictEqual(dic, {"a": 3, "b": 4, "c": 5})

    def test_nested_set(self):
        dic = {"a": {"b": 1, "c": 2}}
        dict_set(dic, "a/b", 3, use_dpath=True)
        self.assertDictEqual(dic, {"a": {"b": 3, "c": 2}})
        dict_set(dic, "a/c", 4, use_dpath=True)
        self.assertDictEqual(dic, {"a": {"b": 3, "c": 4}})
        with self.assertRaises(ValueError):
            dict_set(dic, "a/d", 5, use_dpath=True, not_exist_ok=False)
        dict_set(dic, "a/d", 5, use_dpath=True)
        self.assertDictEqual(dic, {"a": {"b": 3, "c": 4, "d": 5}})

    def test_query_set(self):
        dic = {"a": [{"b": 1}, {"b": 2}]}
        dict_set(dic, "a/*/b", [3, 4], use_dpath=True, set_multiple=True)
        self.assertDictEqual(dic, {"a": [{"b": 3}, {"b": 4}]})
        with self.assertRaises(ValueError):
            dict_set(dic, "a/0/b/c/*/d/*/e", [3, 4], use_dpath=True, set_multiple=True)
        with self.assertRaises(ValueError):
            dict_set(dic, "a/0/b/c/*/d", [3, 4], use_dpath=True, set_multiple=False)

        # dic = {"a": [{"b": 1}, {"b": 2}], "c": [{"b": 3}, {"b": 4}]}
        # dict_set(dic, "*/1/b", [5, 6], use_dpath=True, set_multiple=True)
        # self.assertDictEqual(
        #     dic, {"a": [{"b": 1}, {"b": 5}], "c": [{"b": 3}, {"b": 6}]}
        # )

        dic = {"a": {"b": []}}
        dict_set(dic, "a/b/2/c", [3, 4], use_dpath=True)
        self.assertDictEqual(dic, {"a": {"b": [None, None, {"c": [3, 4]}]}})

        dic = {"a": {"b": []}}
        with self.assertRaises(ValueError):
            dict_set(dic, "a/b/2/c", [3, 4], use_dpath=True, not_exist_ok=False)

    def test_query_set_with_multiple_non_existing(self):
        dic = {"a": [{"b": 1}, {"b": 2}]}
        dict_set(dic, "a/*/c", [3, 4], use_dpath=True, set_multiple=True)
        self.assertDictEqual({"a": [{"b": 1, "c": 3}, {"b": 2, "c": 4}]}, dic)
        dict_set(
            dic,
            "a/*/c",
            [3, 4],
            use_dpath=True,
            set_multiple=False,
            not_exist_ok=True,
        )
        self.assertEqual({"a": [{"b": 1, "c": [3, 4]}, {"b": 2, "c": [3, 4]}]}, dic)

        dic = {"a": [{"b": 1}, {"b": 2}]}
        with self.assertRaises(ValueError):
            dict_set(dic, "a/*/d", [3, 4, 5], use_dpath=True, set_multiple=True)

    def test_adding_one_new_field(self):
        dic = {"a": {"b": {"c": 0}}}
        dict_set(dic, "a/b/d", 1, use_dpath=True)
        self.assertDictEqual(dic, {"a": {"b": {"c": 0, "d": 1}}})

    def test_adding_one_new_field_nested(self):
        dic = {"d": 0}
        dict_set(dic, "/a/b/d", 1, use_dpath=True)
        self.assertDictEqual(dic, {"a": {"b": {"d": 1}}, "d": 0})
