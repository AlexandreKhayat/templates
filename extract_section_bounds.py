#!/usr/bin/env python3
"""
extract_section_bounds.py — Calcule automatiquement les paraId de
début/fin de chaque section "corps" dans W1_Vendeur.docx (unpacked)
et W2_Cas_acquereurs.docx (unpacked), pour mettre à jour la table de
bornes figées dans le prompt maître si ces fichiers venaient à changer.

Usage:
    python /mnt/skills/public/docx/scripts/office/unpack.py W1_Vendeur.docx unpacked_W1/
    python /mnt/skills/public/docx/scripts/office/unpack.py W2_Cas_acquereurs.docx unpacked_W2/
    python extract_section_bounds.py w1 unpacked_W1/word/document.xml
    python extract_section_bounds.py w2 unpacked_W2/word/document.xml

W1 repose sur des marqueurs explicites [[W1:CODE]] / [[/W1:CODE]] déjà
présents dans le template — fiable et sans ambiguïté.

W2 n'a pas de marqueurs explicites : la détection se fait par repérage
des paragraphes d'en-tête (style gras + texte de titre). Si W2 change
de structure, mettre à jour la liste HEADERS_W2 ci-dessous avec les
nouveaux intitulés exacts, dans l'ordre d'apparition.
"""
import re
import sys

HEADERS_W2 = [
    "Personne physique célibataire (sans PACS)",
    "Personne physique célibataire (avec PACS)",
    "Sans contrat de mariage",
    "Avec contrat de mariage",
    "agit seul",                 # fragment distinctif, insensible aux variantes d'apostrophe
    "précédent mariage",         # fragment distinctif, insensible aux variantes d'apostrophe
    "CAS 3",      # veuve
    "CAS 4",      # divorcée
]


def load_para_starts(lines):
    para_starts = []
    for i, line in enumerate(lines):
        if re.search(r"<w:p[ >]", line):
            pid_m = re.search(r'w14:paraId="([0-9A-Fa-f]+)"', line)
            para_starts.append((i, pid_m.group(1) if pid_m else None))
    return para_starts


def first_para_after(para_starts, idx0):
    for idx, pid in para_starts:
        if idx > idx0:
            return idx
    return None


def last_meaningful_para_before(para_starts, idx0):
    candidates = [idx for idx, pid in para_starts if idx < idx0 and pid is not None]
    return candidates[-1] if candidates else None


def para_start_idx_for_line(para_starts, line_no_0idx):
    best = None
    for idx, pid in para_starts:
        if idx <= line_no_0idx:
            best = idx
        else:
            break
    return best


def extract_w1(path):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    para_starts = load_para_starts(lines)

    markers = []
    for i, line in enumerate(lines):
        om = re.search(r"\[\[W1:(\w+)\]\]", line)
        cm = re.search(r"\[\[/W1:(\w+)\]\]", line)
        if om:
            markers.append(("OPEN", om.group(1), i))
        if cm:
            markers.append(("CLOSE", cm.group(1), i))

    print("| Section W1 | paraId premier (corps) | paraId dernier (corps utile) |")
    print("|---|---|---|")
    for j in range(0, len(markers), 2):
        _, name, ln1 = markers[j]
        _, name2, ln2 = markers[j + 1]
        assert name == name2, f"Marqueurs déséquilibrés autour de {name}/{name2}"
        first_idx = first_para_after(para_starts, ln1)
        last_idx = last_meaningful_para_before(para_starts, ln2)
        fp = re.search(r'w14:paraId="([0-9A-Fa-f]+)"', lines[first_idx]).group(1)
        lp = re.search(r'w14:paraId="([0-9A-Fa-f]+)"', lines[last_idx]).group(1)
        print(f"| {name} | {fp} | {lp} |")


def extract_w2(path):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    para_starts = load_para_starts(lines)

    header_lines_0idx = []
    for h in HEADERS_W2:
        found = None
        for i, line in enumerate(lines):
            if h in line and "<w:t>" in line:
                found = i
                break
        if found is None:
            print(f"  ATTENTION: en-tête introuvable, à vérifier manuellement: {h}")
        header_lines_0idx.append(found)

    print("| Cas W2 | paraId premier (corps) | paraId dernier (corps utile) |")
    print("|---|---|---|")
    for i, (label, hl0) in enumerate(zip(HEADERS_W2, header_lines_0idx)):
        if hl0 is None:
            print(f"| {label} | ? | ? |")
            continue
        header_para_start = para_start_idx_for_line(para_starts, hl0)
        body_first_idx = first_para_after(para_starts, header_para_start)
        if i + 1 < len(HEADERS_W2) and header_lines_0idx[i + 1] is not None:
            next_header_para_start = para_start_idx_for_line(para_starts, header_lines_0idx[i + 1])
            body_last_idx = last_meaningful_para_before(para_starts, next_header_para_start)
        else:
            candidates = [idx for idx, pid in para_starts if pid is not None]
            body_last_idx = candidates[-1]
        fp = re.search(r'w14:paraId="([0-9A-Fa-f]+)"', lines[body_first_idx])
        lp = re.search(r'w14:paraId="([0-9A-Fa-f]+)"', lines[body_last_idx])
        fp = fp.group(1) if fp else "?"
        lp = lp.group(1) if lp else "?"
        print(f"| {label} | {fp} | {lp} |")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("w1", "w2"):
        print("Usage: python extract_section_bounds.py [w1|w2] <document.xml>")
        sys.exit(1)
    if sys.argv[1] == "w1":
        extract_w1(sys.argv[2])
    else:
        extract_w2(sys.argv[2])
