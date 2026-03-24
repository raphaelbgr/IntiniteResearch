import pathlib
content = pathlib.Path("C:/Users/rbgnr/git/agno/cookbook/teams/README.md").read_text()
print(f"Read {len(content)} chars")
