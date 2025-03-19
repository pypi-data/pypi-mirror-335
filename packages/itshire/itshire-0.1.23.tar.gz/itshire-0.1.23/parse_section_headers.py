import mistletoe


def extract_headers(file_path):
    with open(file_path, "r") as file:
        markdown_content = file.read()

    parsed_markdown = mistletoe.Document(markdown_content)
    headers = []

    def _traverse(node):
        if isinstance(node, mistletoe.block_token.Heading):
            headers.append(node.children[0].content)
        for child in getattr(node, "children", []):
            _traverse(child)

    _traverse(parsed_markdown)
    return headers


file_path = "/Users/mtm/Documents/Obsidian Vault/Lime.md"
headers = extract_headers(file_path)
sorted_headers = sorted(headers)

print("Sorted headers:")
for header in sorted_headers:
    print(header)
