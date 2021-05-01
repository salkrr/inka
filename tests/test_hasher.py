import os

import pytest

from inka.models.hasher import Hasher


@pytest.fixture
def test_file(tmp_path) -> str:
    path = str(tmp_path / "file.md")
    with open(path, mode="wt", encoding="utf-8") as f:
        f.write("Hello, **WORLD**!")
    yield path
    os.remove(path)


@pytest.fixture
def file_with_hashes(tmp_path) -> str:
    path = str(tmp_path / "test_file_with_hashes.json")
    with open(path, mode="wt", encoding="utf-8") as f:
        f.write(
            "{\n"
            '"fake1.md": "724ae4e3bf11c04581daf1bb4de43161",\n'
            '"fake2.md": "123ae4a4bf1ac04581daf1bb4de43161"\n'
            "}"
        )

    yield path
    os.remove(path)


@pytest.fixture
def hasher(file_with_hashes: str) -> Hasher:
    return Hasher(file_with_hashes)


# calculate_hash
def test_calculate_hash_when_file_exists(test_file):
    expected = "724ae4e3bf11c04581daf1bb4de43161"

    assert Hasher.calculate_hash(test_file) == expected


def test_calculate_hash_when_file_does_not_exist_raises_error():
    with pytest.raises(FileNotFoundError):
        Hasher.calculate_hash("does_not_exist.json")


# has_changed
def test_has_changed_when_file_hash_exists_in_data_file_and_hash_same(hasher):
    assert not hasher.has_changed("fake1.md", "724ae4e3bf11c04581daf1bb4de43161")


def test_has_changed_when_file_hash_exists_in_data_file_and_hashes_different(hasher):
    assert hasher.has_changed("fake1.md", "111ae1e31111c04581daf1bb4de43161")


def test_has_changed_when_file_hash_does_not_exist_in_data_file(hasher):
    assert hasher.has_changed("oops.md", "111ae1e31111c04581daf1bb4de43161")


# update_hash
def test_update_hash_when_file_hash_exists_in_data_file(hasher, file_with_hashes):
    new_hash = "111ae1e31111c04581daf1bb4de43161"
    expected = (
        "{"
        f'"fake1.md": "{new_hash}", '
        '"fake2.md": "123ae4a4bf1ac04581daf1bb4de43161"'
        "}"
    )

    hasher.update_hash("fake1.md", new_hash)

    with open(file_with_hashes, mode="rt", encoding="utf-8") as f:
        assert f.read() == expected


def test_update_hash_when_file_hash_does_not_exist_in_data_file(
    hasher, file_with_hashes
):
    filename = "my_file_path.md"
    new_hash = "111ae1e31111c04581daf1bb4de43161"
    expected = (
        "{"
        '"fake1.md": "724ae4e3bf11c04581daf1bb4de43161", '
        '"fake2.md": "123ae4a4bf1ac04581daf1bb4de43161", '
        f'"{filename}": "{new_hash}"'
        "}"
    )

    hasher.update_hash(filename, new_hash)

    with open(file_with_hashes, mode="rt", encoding="utf-8") as f:
        assert f.read() == expected


# reset_hashes
def test_reset_hashes_when_data_file_does_not_exist():
    path = "some_random_path.json"
    hasher = Hasher(path)
    expected = "{}"

    hasher.reset_hashes()

    with open(path, mode="rt", encoding="utf-8") as f:
        assert f.read() == expected
    os.remove(path)


def test_reset_hashes_when_data_file_contains_hashes(hasher, file_with_hashes):
    expected = "{}"

    hasher.reset_hashes()

    with open(file_with_hashes, mode="rt", encoding="utf-8") as f:
        assert f.read() == expected
