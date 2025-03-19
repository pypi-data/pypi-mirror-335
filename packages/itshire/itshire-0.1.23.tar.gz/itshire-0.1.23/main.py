import os

import frontmatter

ingredients_foods = [
    "/Users/mtm/Documents/Obsidian Vault/beef bouillon.md",
    "/Users/mtm/Documents/Obsidian Vault/couscous.md",
    "/Users/mtm/Documents/Obsidian Vault/Dino Kale.md",
    "/Users/mtm/Documents/Obsidian Vault/dried cranberries.md",
    "/Users/mtm/Documents/Obsidian Vault/extra virgin olive oil.md",
    "/Users/mtm/Documents/Obsidian Vault/Farro Wheat.md",
    "/Users/mtm/Documents/Obsidian Vault/Farro Wheat.sync-conflict-20240315-221725-G6QCYAQ.md",
    "/Users/mtm/Documents/Obsidian Vault/Green Beans.md",
    "/Users/mtm/Documents/Obsidian Vault/Green Chili.md",
    "/Users/mtm/Documents/Obsidian Vault/Lemon.md",
    "/Users/mtm/Documents/Obsidian Vault/Lime.md",
    "/Users/mtm/Documents/Obsidian Vault/Medjool dates.md",
    "/Users/mtm/Documents/Obsidian Vault/Organic Russet Potato.md",
    "/Users/mtm/Documents/Obsidian Vault/pecans.md",
    "/Users/mtm/Documents/Obsidian Vault/potato starch.md",
    "/Users/mtm/Documents/Obsidian Vault/Red Potatoes.md",
    "/Users/mtm/Documents/Obsidian Vault/Seafood Mushroom.md",
    "/Users/mtm/Documents/Obsidian Vault/Yukon Gold Potato.md",
]

for file_path in ingredients_foods:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        post = frontmatter.loads(content)

    if "filetype" not in post.metadata:
        post.metadata["filetype"] = "product"
        new_content = frontmatter.dumps(post)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(new_content)

    print(f"Processed: {os.path.basename(file_path)}")
