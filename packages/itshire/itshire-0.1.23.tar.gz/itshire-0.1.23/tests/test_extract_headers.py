import logging

import pytest

from itshire.add_sections import extract_headers


@pytest.fixture
def problematic_file(tmp_path):
    content = """---
filetype: product
---
![[Pasted image 20240218165711.png]]
## [[PCC]]
- [x] shopping
## [[Safeway]]
- [x] shopping
[Poblano/Pasilla Peppers - Safeway](https://www.safeway.com/shop/product-details.184490016.html)
## [[Trader Joes]]
- [x] shopping
## [[Central Co-op]]
- [x] shopping
## [[Hau Hau Market]]
- [x] shopping
## [[M2M]]
- [x] shopping
## [[Uwajimaya]]
- [x] shopping
## [[QFC]]
- [x] shopping
## [[Whole Foods]]
- [x] shopping
## [[Grocery Outlet]]
- [x] shopping
## [[Amazon.com]]
- [x] shopping
## [[H Mart]]
- [x] shopping
## [[Lam's Seafood Asian Market]]
- [x] shopping
## [[Pacific Supply]]
- [x] shopping
## [[Walgreens]]
- [x] shopping
## [[Target]]
- [x] shopping
## [[Chef's Store]]
- [x] shopping
## [[Walmart]]
- [x] shopping
"""
    file_path = tmp_path / "poblano_chiles.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def test_file_levels(tmp_path):
    content = """# Level **1**
## Level *2*
### **Level** 3
#### *Level* 4
##### Level ***5***"""
    file_path = tmp_path / "test_file_levels.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def problematic_oats_file(tmp_path):
    content = """---
filetype: product
---
# Old Fashioned Oats
[[Problematic Content]]
"""
    file_path = tmp_path / "old_fashioned_oats.md"
    file_path.write_text(content)
    return file_path


def test_extract_headers_problematic_file(problematic_file):
    headers = extract_headers(problematic_file)
    expected_headers = [
        "[[Amazon.com]]",
        "[[Central Co-op]]",
        "[[Chef's Store]]",
        "[[Fred Meyer]]",
        "[[Grocery Outlet]]",
        "[[H Mart]]",
        "[[Hau Hau Market]]",
        "[[Lam's Seafood Asian Market]]",
        "[[M2M]]",
        "[[Pacific Supply]]",
        "[[PCC]]",
        "[[QFC]]",
        "[[Safeway]]",
        "[[Target]]",
        "[[Trader Joes]]",
        "[[Uwajimaya]]",
        "[[Walgreens]]",
        "[[Walmart]]",
        "[[Whole Foods]]",
    ]
    assert headers == expected_headers


def test_extract_headers_levels(test_file_levels):
    headers = extract_headers(test_file_levels)
    expected_headers = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
    assert headers == expected_headers


def test_extract_headers_error_handling(problematic_oats_file, caplog):
    caplog.set_level(logging.ERROR)
    headers = extract_headers(problematic_oats_file)
    assert headers == []
    assert "'NoneType' object is not iterable" in caplog.text
    assert "Error extracting headers from" in caplog.text
