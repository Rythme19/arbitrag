"""Extrait le texte des livrets de data/raw/ vers data/processed/pages.parquet (une ligne par page).

Formats lus : .pdf, .txt, .md. Les autres fichiers sont signalés et ignorés.
Nom des fichiers : <jeu>.pdf, ou <jeu>__<document>.pdf s'il y a plusieurs
documents pour un même jeu (ex. loups-garous__extension.pdf).
"""
import subprocess
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).parent.parent
RAW = RACINE / "data" / "raw"
SORTIE = RACINE / "data" / "processed" / "pages.parquet"


def extraire_pages(pdf: Path) -> list[str]:
    # Un fichier texte compte pour une seule page, sauf s'il contient des sauts
    # de page (\f), comme ceux produits par src/ocr.swift.
    if pdf.suffix.lower() in {".txt", ".md"}:
        return [page.strip() for page in pdf.read_text(encoding="utf-8").split("\f")]
    # pdftotext sépare les pages par un saut de page (\f) et en ajoute un à la fin.
    # ponytail: texte brut dans l'ordre de lecture, les tableaux et les icônes
    # sont perdus ; passer à pdfplumber ou à un OCR si ça gêne.
    texte = subprocess.run(
        ["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout
    return [page.strip() for page in texte.removesuffix("\f").split("\f")]


def main():
    fichiers = sorted(f for f in RAW.iterdir() if f.is_file() and not f.name.startswith("."))
    lisibles = [f for f in fichiers if f.suffix.lower() in {".pdf", ".txt", ".md"}]
    for ignore in set(fichiers) - set(lisibles):
        print(f"IGNORÉ (format non géré) : {ignore.name}")

    lignes = [
        {"jeu": pdf.stem.split("__")[0], "fichier": pdf.name, "page": numero, "texte": texte}
        for pdf in lisibles
        for numero, texte in enumerate(extraire_pages(pdf), start=1)
    ]
    if not lignes:
        raise SystemExit(f"Aucun fichier lisible (.pdf, .txt, .md) dans {RAW}")

    pages = pd.DataFrame(lignes)
    pages["nb_caracteres"] = pages["texte"].str.len()
    pages.to_parquet(SORTIE, index=False)

    # Une page presque vide est en général une image ou un scan : à noter dans JOURNAL.md.
    resume = pages.groupby("fichier").agg(
        pages=("page", "count"),
        caracteres=("nb_caracteres", "sum"),
        pages_presque_vides=("nb_caracteres", lambda n: int((n < 100).sum())),
    )
    print(resume.to_string())
    print(f"\n{len(pages)} pages écrites dans {SORTIE}")


if __name__ == "__main__":
    main()
