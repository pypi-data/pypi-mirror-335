import logging
import pathlib

import frontmatter
import mistletoe


def extract_headers(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        markdown_content = file.read()
    parsed_markdown = mistletoe.Document(markdown_content)
    headers = []

    def _traverse(node):
        if isinstance(node, mistletoe.block_token.Heading):
            header_text = "".join(_extract_text(child) for child in node.children)
            headers.append(header_text.strip())
        for child in getattr(node, "children", []):
            if child is not None:
                _traverse(child)

    def _extract_text(node):
        if node is None:
            return ""
        if isinstance(node, mistletoe.span_token.RawText):
            return node.content
        elif isinstance(node, mistletoe.span_token.InlineCode):
            return node.children[0].content if node.children else ""
        else:
            return "".join(
                _extract_text(child)
                for child in getattr(node, "children", [])
                if child is not None
            )

    try:
        _traverse(parsed_markdown)
    except Exception as e:
        logging.error(f"Error extracting headers from {file_path}: {str(e)}")
        return []

    return headers


def add_sections(file_path, section_names):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            markdown_content = file.read()

        original_content = markdown_content

        for section_name in section_names:
            if section_name not in markdown_content:
                markdown_content += f"\n## [[{section_name}]]\n- [x] shopping\n"

        if markdown_content != original_content:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(markdown_content)
    except Exception as e:
        logging.error(f"Error adding sections to {file_path}: {str(e)}")


def find_markdown_files(directory):
    return list(pathlib.Path(directory).rglob("*.md"))


def filter_markdown_files(files):
    filtered_files = []
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
                if post.get("filetype") == "product":
                    filtered_files.append(file)
        except Exception as e:
            logging.error(f"Error processing file {file}: {str(e)}")
    return filtered_files


def main(directory):
    markdown_files = find_markdown_files(directory)
    filtered_files = filter_markdown_files(markdown_files)
    logging.debug(f"Filtered files: {filtered_files}")

    stores = [
        "Amazon Fresh",
        "Amazon.com",
        "Central Co-op",
        "Chef's Store",
        "Costco",
        "Dong Hing Market",
        "Fred Meyer",
        "Grocery Outlet",
        "H Mart",
        "Hau Hau Market",
        "Lam's Seafood Asian Market",
        "M2M",
        "Pacific Supply",
        "PCC",
        "QFC",
        "Safeway",
        "Target",
        "Trader Joes",
        "Uwajimaya",
        "Walgreens",
        "Walmart",
        "Whole Foods",
    ]

    for file_path in filtered_files:
        logging.info(f"Processing file: {file_path}")
        try:
            existing_headers = extract_headers(file_path)
            missing_sections = [
                store_name
                for store_name in stores
                if store_name not in existing_headers
            ]
            if missing_sections:
                add_sections(file_path, missing_sections)
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")

    print("Sections added successfully.")
