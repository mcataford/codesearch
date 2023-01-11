import pytest

from .prefix_tree import PrefixTree


@pytest.fixture
def prefix_tree():
    return PrefixTree.initialize()


def test_base_tree_has_a_root_node(prefix_tree, snapshot):
    assert prefix_tree.to_dict() == snapshot


def test_insert_single_string(prefix_tree, snapshot):
    mock_value = "abc"
    mock_key = "key_1"
    prefix_tree.insert(value=mock_value, key=mock_key)
    assert prefix_tree.to_dict() == snapshot
    assert prefix_tree.get(value=mock_value) == [mock_key]


def test_insert_single_character_(prefix_tree, snapshot):
    mock_value = "a"
    mock_key = "key_1"
    prefix_tree.insert(value=mock_value, key=mock_key)
    assert prefix_tree.to_dict() == snapshot
    assert prefix_tree.get(value=mock_value) == [mock_key]


def test_insert_overlapping_strings(prefix_tree, snapshot):
    mock_value_1 = "abcd"
    mock_key_1 = "key_1"
    mock_value_2 = "abce"
    mock_key_2 = "key_2"
    prefix_tree.insert(value=mock_value_1, key=mock_key_1)
    prefix_tree.insert(value=mock_value_2, key=mock_key_2)
    assert prefix_tree.to_dict() == snapshot
    assert prefix_tree.get(value=mock_value_1) == [mock_key_1]
    assert prefix_tree.get(value=mock_value_2) == [mock_key_2]


def test_insert_multiple_keys_same_string(prefix_tree, snapshot):
    mock_value = "abcd"
    mock_key_1 = "key_1"
    mock_key_2 = "key_2"
    prefix_tree.insert(value=mock_value, key=mock_key_1)
    prefix_tree.insert(value=mock_value, key=mock_key_2)
    assert prefix_tree.to_dict() == snapshot
    assert prefix_tree.get(value=mock_value) == [mock_key_1, mock_key_2]


def test_insert_strings_subsets_of_each_other(prefix_tree, snapshot):
    mock_value_1 = "abcd"
    mock_key_1 = "key_1"
    mock_value_2 = "abc"
    mock_key_2 = "key_2"
    prefix_tree.insert(value=mock_value_1, key=mock_key_1)
    prefix_tree.insert(value=mock_value_2, key=mock_key_2)
    assert prefix_tree.to_dict() == snapshot
    assert prefix_tree.get(value=mock_value_1) == [mock_key_1]
    assert prefix_tree.get(value=mock_value_2) == [mock_key_2]


def test_serializes_to_json(prefix_tree, snapshot):
    prefix_tree.insert(value="abcd", key="key_1")
    assert prefix_tree.to_json() == snapshot
