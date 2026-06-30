#!/usr/bin/env python3
"""
renumber_bookmarks.py — Réattribue des w:id uniques à tous les
<w:bookmarkStart>/<w:bookmarkEnd> d'un document.xml, en préservant
l'appariement start/end (y compris en cas de doublons préexistants
dans le document maître, ce qui arrive souvent après assemblage de
plusieurs briques Word).

Usage:
    python renumber_bookmarks.py unpacked/word/document.xml

Le fichier est modifié en place. Un .bak est conservé à côté.
"""
import re
import sys
import shutil


def renumber(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        content = f.read()

    shutil.copyfile(path, path + ".bak")

    next_id = [0]
    stack_by_old_id = {}

    pattern = re.compile(
        r'<w:bookmarkStart w:id="(\d+)"([^/]*)/>|<w:bookmarkEnd w:id="(\d+)"/>'
    )

    out = []
    last = 0
    for m in pattern.finditer(content):
        out.append(content[last:m.start()])
        if m.group(1) is not None:
            old_id = m.group(1)
            new_id = next_id[0]
            next_id[0] += 1
            stack_by_old_id.setdefault(old_id, []).append(new_id)
            out.append(f'<w:bookmarkStart w:id="{new_id}"{m.group(2)}/>')
        else:
            old_id = m.group(3)
            lst = stack_by_old_id.get(old_id)
            new_id = lst.pop() if lst else old_id
            out.append(f'<w:bookmarkEnd w:id="{new_id}"/>')
        last = m.end()
    out.append(content[last:])
    new_content = "".join(out)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return next_id[0]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python renumber_bookmarks.py <document.xml>")
        sys.exit(1)
    n = renumber(sys.argv[1])
    print(f"Renumbered {n} bookmark ids in {sys.argv[1]} (backup at {sys.argv[1]}.bak)")
