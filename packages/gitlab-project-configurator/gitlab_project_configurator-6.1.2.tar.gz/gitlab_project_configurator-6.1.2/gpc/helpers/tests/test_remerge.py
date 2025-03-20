# Standard Library
from pprint import pprint

# Gitlab-Project-Configurator Modules
from gpc.helpers.remerge import ListOverrideBehavior
from gpc.helpers.remerge import remerge
from gpc.helpers.remerge import sourced_remerge


def test_override_string():
    defaults = {"key_to_override": "value_from_defaults"}

    first_override = {"key_to_override": "value_from_first_override"}

    merged, source_map = sourced_remerge(
        [
            ("defaults", defaults),
            ("first_override", first_override),
        ]
    )

    expected_merged = {"key_to_override": "value_from_first_override"}
    assert merged == expected_merged
    assert source_map == {("key_to_override",): "first_override"}

    merged = remerge([defaults, first_override])
    assert merged == expected_merged


def test_override_item_in_subdict():
    defaults = {
        "do_no_touch_me": 42,
        "subdict": {
            "other_subdict": {
                "key_to_override": "value_from_defaults",
                "integer_to_override": 2222,
            }
        },
    }

    first_override = {
        "subdict": {
            "other_subdict": {
                "key_to_override": "value_from_first_override",
                "integer_to_override": 5555,
            }
        }
    }

    expected_merge = {
        "do_no_touch_me": 42,
        "subdict": {
            "other_subdict": {
                "key_to_override": "value_from_first_override",
                "integer_to_override": 5555,
            }
        },
    }

    merged, source_map = sourced_remerge(
        [
            ("defaults", defaults),
            ("first_override", first_override),
        ]
    )
    assert merged == expected_merge

    assert source_map == {
        ("do_no_touch_me",): "defaults",
        ("subdict",): "first_override",
        ("subdict", "other_subdict"): "first_override",
        ("subdict", "other_subdict", "integer_to_override"): "first_override",
        ("subdict", "other_subdict", "key_to_override"): "first_override",
    }

    merged = remerge([defaults, first_override])
    assert merged == expected_merge


def test_override_with_list_append_flag():
    list_update_behavior = ListOverrideBehavior.APPEND

    defaults = {
        "list_to_append": [{"a": 1}],
        "list_to_keep_as_it_is": [{"x": 1}],
        "list_to_set_to_none": [{"o": 1}],
    }
    first_override = {
        "list_to_append": [{"b": 1}],
        "list_to_keep_as_it_is": [],
        "list_to_set_to_none": None,
    }

    merged, source_map = sourced_remerge(
        [("defaults", defaults), ("first_override", first_override)],
        list_update_behavior=list_update_behavior,
    )

    expected_merged = {
        "list_to_append": [{"a": 1}, {"b": 1}],
        "list_to_keep_as_it_is": [{"x": 1}],
        "list_to_set_to_none": None,
    }

    assert merged == expected_merged
    assert source_map == {
        ("list_to_keep_as_it_is",): "first_override",  # TODO: should be defaults, but not fixed yet
        ("list_to_append",): "first_override",
        ("list_to_set_to_none",): "first_override",
    }

    merged = remerge([defaults, first_override], list_update_behavior=list_update_behavior)
    assert merged == expected_merged


def test_override_with_list_replace_flag():
    list_update_behavior = ListOverrideBehavior.REPLACE

    defaults = {
        "list_to_replace": [{"a": 1}],
        "list_to_clear": [{"x": 1}],
        "list_to_set_to_none": [{"o": 1}],
    }
    first_override = {
        "list_to_replace": [{"b": 1}],
        "list_to_clear": [],
        "list_to_set_to_none": None,
    }

    merged, source_map = sourced_remerge(
        [("defaults", defaults), ("first_override", first_override)],
        list_update_behavior=list_update_behavior,
    )

    expected_merged = {
        "list_to_replace": [{"b": 1}],
        "list_to_clear": [],
        "list_to_set_to_none": None,
    }

    assert merged == expected_merged
    assert source_map == {
        ("list_to_clear",): "first_override",
        ("list_to_replace",): "first_override",
        ("list_to_set_to_none",): "first_override",
    }

    merged = remerge([defaults, first_override], list_update_behavior=list_update_behavior)
    assert merged == expected_merged


def test_override_with_list_append_with_empty_means_clear_flag():
    list_update_behavior = ListOverrideBehavior.APPEND_WITH_EMPTY_MEANS_RESET
    defaults = {
        "list_to_append": [{"a": 1}],
        "list_to_clear": [{"x": 1}],
        "list_to_set_to_none": [{"o": 1}],
    }
    first_override = {
        "list_to_append": [{"b": 1}],
        "list_to_clear": [],
        "list_to_set_to_none": None,
    }

    merged, source_map = sourced_remerge(
        [("defaults", defaults), ("first_override", first_override)],
        list_update_behavior=list_update_behavior,
    )

    expected_merged = {
        "list_to_append": [{"a": 1}, {"b": 1}],
        "list_to_clear": [],
        "list_to_set_to_none": None,
    }

    assert merged == expected_merged
    assert source_map == {
        ("list_to_clear",): "first_override",
        ("list_to_append",): "first_override",
        ("list_to_set_to_none",): "first_override",
    }

    merged = remerge([defaults, first_override], list_update_behavior=list_update_behavior)
    assert merged == expected_merged


def test_complex_dict():
    list_update_behavior = ListOverrideBehavior.APPEND

    defaults = {
        "key_to_override": "value_from_defaults",
        "integer_to_override": 1111,
        "list_to_append": [{"a": 1}],
        "subdict": {
            "other_subdict": {
                "key_to_override": "value_from_defaults",
                "integer_to_override": 2222,
            },
            "second_subdict": {
                "key_to_override": "value_from_defaults",
                "integer_to_override": 3333,
            },
        },
    }

    first_override = {
        "key_to_override": "value_from_first_override",
        "integer_to_override": 4444,
        "list_to_append": [{"b": 2}],
        "subdict": {
            "other_subdict": {
                "key_to_override": "value_from_first_override",
                "integer_to_override": 5555,
            }
        },
        "added_in_first_override": "some_string",
    }

    second_override = {
        "subdict": {"second_subdict": {"key_to_override": "value_from_second_override"}}
    }

    merged, source_map = sourced_remerge(
        [
            ("defaults", defaults),
            ("first_override", first_override),
            ("second_override", second_override),
        ],
        list_update_behavior=list_update_behavior,
    )
    print("")
    print("'merged' dictionary:")
    pprint(merged)
    print("")
    pprint(source_map)
    print(len(source_map), "paths")

    assert merged["key_to_override"] == "value_from_first_override"
    assert merged["integer_to_override"] == 4444
    assert merged["subdict"]["other_subdict"]["key_to_override"] == "value_from_first_override"
    assert merged["subdict"]["other_subdict"]["integer_to_override"] == 5555
    assert merged["subdict"]["second_subdict"]["key_to_override"] == "value_from_second_override"
    assert merged["subdict"]["second_subdict"]["integer_to_override"] == 3333
    assert merged["added_in_first_override"] == "some_string"
    assert merged["list_to_append"] == [{"a": 1}, {"b": 2}]
