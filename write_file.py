import pathlib
content = pathlib.Path("~/git/agno/cookbook/teams/README.md").read_text()
print(f"Read {len(content)} chars")
