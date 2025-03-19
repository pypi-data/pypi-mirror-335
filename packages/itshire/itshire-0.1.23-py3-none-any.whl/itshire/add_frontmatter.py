import os

import frontmatter

with open("filelist.txt", "r") as file:
    ingredients_foods = [line.strip() for line in file]

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
