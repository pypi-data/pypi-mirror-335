import os

import pytest

from itshire.add_sections import extract_headers


@pytest.fixture
def test_file_strong(tmp_path):
    test_file_path = tmp_path / "test_file_strong.md"
    with open(test_file_path, "w") as file:
        file.write("## **Section 1**\ntest")
    yield test_file_path
    os.remove(test_file_path)


@pytest.fixture
def test_file_italics(tmp_path):
    test_file_path = tmp_path / "test_file_italics.md"
    with open(test_file_path, "w") as file:
        file.write("## *Section 2*\ntest")
    yield test_file_path
    os.remove(test_file_path)


@pytest.fixture
def test_file_levels(tmp_path):
    test_file_path = tmp_path / "test_file_levels.md"
    with open(test_file_path, "w") as file:
        file.write(
            "# Level **1**\n## Level *2*\n### **Level** 3\n#### *Level* 4\n##### Level ***5***"
        )
    yield test_file_path
    os.remove(test_file_path)


@pytest.fixture
def test_file_inline_code(tmp_path):
    test_file_path = tmp_path / "test_file_inline_code.md"
    with open(test_file_path, "w") as file:
        file.write(
            "# Section `code`\n## Section *`code`*\n### Section **`code`**\n#### `Section` *code*\n##### **`Section`** `code`"
        )
    yield test_file_path
    os.remove(test_file_path)


def test_extract_headers_strong(test_file_strong):
    headers = extract_headers(test_file_strong)
    assert headers == ["Section 1"]


def test_extract_headers_italics(test_file_italics):
    headers = extract_headers(test_file_italics)
    assert headers == ["Section 2"]


def test_extract_headers_levels(test_file_levels):
    headers = extract_headers(test_file_levels)
    assert headers == ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]


def test_extract_headers_inline_code(test_file_inline_code):
    headers = extract_headers(test_file_inline_code)
    assert headers == [
        "Section code",
        "Section code",
        "Section code",
        "Section code",
        "Section code",
    ]


@pytest.fixture
def test_file_internal_links(tmp_path):
    test_file_path = tmp_path / "test_file_internal_links.md"
    with open(test_file_path, "w") as file:
        file.write(
            "# Section [[link1]]\n"
            "## Section [[link2]] with text\n"
            "### **Section** [[link3]] and *more* text\n"
            "#### Section with [[link4]] and `code`\n"
            "##### [[link5]] at the beginning"
        )
    yield test_file_path
    os.remove(test_file_path)


def test_extract_headers_internal_links(test_file_internal_links):
    headers = extract_headers(test_file_internal_links)
    assert headers == [
        "Section [[link1]]",
        "Section [[link2]] with text",
        "Section [[link3]] and more text",
        "Section with [[link4]] and code",
        "[[link5]] at the beginning",
    ]
