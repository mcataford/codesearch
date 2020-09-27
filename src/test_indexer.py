import pytest

from indexer import Indexer


@pytest.fixture()
def indexer():
    return Indexer()


def test_indexer_builds_trigram_set_for_given_document(indexer):
    mock_document = "now that's a doc"
    mock_path = "/home/documents/cool_doc"

    indexer.index(path=mock_path, content=mock_document)

    expected_trigrams = [
        "now",
        "ow ",
        "w t",
        " th",
        "tha",
        "hat",
        "at'",
        "t's",
        "'s ",
        "s a",
        " a ",
        "a d",
        " do",
        "doc",
    ]

    assert indexer.trigrams == {mock_path: set(expected_trigrams)}


def test_indexer_preserves_previous_trigram_sets_on_index(indexer):
    mock_document_1 = "wow"
    mock_document_2 = "woa"
    mock_path_1 = "/home"
    mock_path_2 = "/somewhere_else"

    indexer.index(path=mock_path_1, content=mock_document_1)

    assert indexer.trigrams == {mock_path_1: set(["wow"])}

    indexer.index(path=mock_path_2, content=mock_document_2)

    assert indexer.trigrams == {mock_path_1: set(["wow"]), mock_path_2: set(["woa"])}
