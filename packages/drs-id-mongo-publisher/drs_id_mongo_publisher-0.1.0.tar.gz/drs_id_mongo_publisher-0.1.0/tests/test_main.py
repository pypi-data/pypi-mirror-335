from drs_id_mongo_publisher.main import _get_ids_list


def test_get_ids_list_none():
    assert _get_ids_list(None) is None


def test_get_ids_list_empty_file(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("")
    assert _get_ids_list(empty_file) == []


def test_get_ids_list_with_ids(tmp_path):
    ids_file = tmp_path / "ids.txt"
    ids_file.write_text("id1\nid2\nid3\n")
    assert _get_ids_list(ids_file) == ["id1", "id2", "id3"]


def test_get_ids_list_with_blank_lines(tmp_path):
    ids_file = tmp_path / "ids_with_blanks.txt"
    ids_file.write_text("id1\n\nid2\n\nid3\n")
    assert _get_ids_list(ids_file) == ["id1", "id2", "id3"]
