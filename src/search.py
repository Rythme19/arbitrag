"""Recherche des passages de livret les plus proches d'une question, sans LLM."""
import re
import unicodedata
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

PAGES = Path(__file__).parent.parent / "data" / "processed" / "pages.parquet"
TAILLE_PASSAGE = 800  # caractères


def decouper(texte: str, taille: int = TAILLE_PASSAGE) -> list[str]:
    # ponytail: on empile les lignes jusqu'à la taille voulue, sans recouvrement
    # et sans tenir compte des titres ; à remplacer par un découpage par section.
    passages, courant = [], ""
    for ligne in texte.splitlines():
        if courant and len(courant) + len(ligne) > taille:
            passages.append(courant.strip())
            courant = ""
        courant += ligne + "\n"
    if courant.strip():
        passages.append(courant.strip())
    return passages


def charger_passages() -> pd.DataFrame:
    pages = pd.read_parquet(PAGES)
    pages = pages[pages["nb_caracteres"] >= 100]  # couvertures et dos de livret
    # Le livret « Le Village » reprend les règles de base aux pages 2 à 5.
    doublon = (pages["fichier"] == "loups-garous__le-village.pdf") & pages["page"].between(2, 5)
    passages = pages[~doublon].assign(texte=lambda p: p["texte"].map(decouper)).explode("texte")
    return passages[["jeu", "fichier", "page", "texte"]].reset_index(drop=True)


def detecter_jeu(question: str, jeux: list[str]) -> str | None:
    """Le jeu dont le nom apparaît dans la question (« loup » suffit pour loups-garous)."""
    question = unicodedata.normalize("NFKD", question).encode("ascii", "ignore").decode().lower()
    for jeu in jeux:
        racine = jeu.split("-")[0].rstrip("s")
        if re.search(rf"\b{racine}", question):
            return jeu
    return None


def chercher(passages: pd.DataFrame, question: str, jeu: str | None = None, k: int = 4) -> pd.DataFrame:
    # ponytail: recherche par mots (TF-IDF) ; à comparer avec des embeddings.
    if jeu:
        passages = passages[passages["jeu"] == jeu]
    vectoriseur = TfidfVectorizer(strip_accents="unicode", sublinear_tf=True)
    matrice = vectoriseur.fit_transform(passages["texte"])
    scores = (matrice @ vectoriseur.transform([question]).T).toarray().ravel()
    return passages.assign(score=scores).nlargest(k, "score").query("score > 0")


if __name__ == "__main__":
    assert decouper("a\n" * 5, taille=4) == ["a\na", "a\na", "a"]
    passages = charger_passages()
    jeux = sorted(passages["jeu"].unique())
    assert detecter_jeu("Que fait la Sorcière au Loup-Garou ?", jeux) == "loups-garous"
    assert detecter_jeu("Comment gagner ?", jeux) is None
    resultat = chercher(passages, "Combien de cartes reçoit chaque joueur ?", jeu="skyjo")
    assert 2 in resultat["page"].values, resultat[["fichier", "page", "score"]]
    assert chercher(passages, "xyzzy").empty
    print(len(passages), "passages,", len(jeux), "jeux")
    print(resultat[["jeu", "fichier", "page", "score"]].to_string())
