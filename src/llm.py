"""Réponse de l'arbitre rédigée par le LLM (Groq, API compatible OpenAI).

Chaque appel à arbitrer() consomme du quota : rien n'est appelé à l'import.
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

URL = "https://api.groq.com/openai/v1/chat/completions"
MODELE = "openai/gpt-oss-20b"
CONSIGNE = (
    "Tu es l'arbitre d'un jeu de société. Réponds à la question uniquement à partir "
    "des extraits du livret de règles fournis, jamais de mémoire. "
    "Si les extraits ne contiennent pas la réponse, dis-le. "
    'Réponds en JSON avec exactement ces champs : "verdict" (la réponse en quelques mots), '
    '"explication" (une ou deux phrases), "passages_utilises" (les numéros des extraits '
    'qui justifient la réponse), "trouve_dans_le_livret" (true ou false).'
)

load_dotenv(Path(__file__).parent.parent / ".env")


def cle_presente() -> bool:
    return bool(os.environ.get("GROQ_API_KEY"))


def construire_messages(question: str, passages: list[dict]) -> list[dict]:
    extraits = "\n\n".join(
        f"[{p['numero']}] {p['jeu']}, page {p['page']}\n{p['texte']}" for p in passages
    )
    return [
        {"role": "system", "content": CONSIGNE},
        {"role": "user", "content": f"Extraits du livret :\n\n{extraits}\n\nQuestion : {question}"},
    ]


def lire_reponse(contenu: str) -> dict:
    """Remet la réponse du LLM dans le format attendu, même si elle est mal formée."""
    try:
        brut = json.loads(contenu)
    except json.JSONDecodeError:
        brut = None
    if not isinstance(brut, dict):
        brut = {"explication": contenu}
    utilises = brut.get("passages_utilises")
    return {
        "verdict": str(brut.get("verdict", "")),
        "explication": str(brut.get("explication", "")),
        "passages_utilises": [n for n in utilises if isinstance(n, int)] if isinstance(utilises, list) else [],
        "trouve_dans_le_livret": brut.get("trouve_dans_le_livret") is True,
    }


def arbitrer(question: str, passages: list[dict]) -> dict:
    """Pose la question au LLM avec les passages retrouvés. Un appel à l'API."""
    corps = {
        "model": MODELE,
        "messages": construire_messages(question, passages),
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    requete = urllib.request.Request(
        URL,
        data=json.dumps(corps).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json",
            "User-Agent": "arbitrag",  # l'agent par défaut de Python peut être refusé
        },
    )
    try:
        with urllib.request.urlopen(requete, timeout=60) as reponse:
            donnees = json.load(reponse)
    except urllib.error.HTTPError as erreur:
        detail = erreur.read().decode(errors="replace")[:300]
        raise RuntimeError(f"L'API a répondu {erreur.code} : {detail}") from erreur
    except urllib.error.URLError as erreur:
        raise RuntimeError(f"API injoignable : {erreur.reason}") from erreur
    return lire_reponse(donnees["choices"][0]["message"]["content"])


if __name__ == "__main__":
    # Vérifications sans réseau : aucun appel à l'API.
    passages = [{"numero": 1, "jeu": "skyjo", "page": 2, "texte": "Chaque joueur reçoit 12 cartes."}]
    messages = construire_messages("Combien de cartes ?", passages)
    assert "[1] skyjo, page 2" in messages[1]["content"] and "Combien de cartes ?" in messages[1]["content"]
    bonne = lire_reponse('{"verdict": "12", "explication": "x", "passages_utilises": [1], "trouve_dans_le_livret": true}')
    assert bonne == {"verdict": "12", "explication": "x", "passages_utilises": [1], "trouve_dans_le_livret": True}
    cassee = lire_reponse("pas du JSON")
    assert cassee["explication"] == "pas du JSON" and cassee["trouve_dans_le_livret"] is False
    assert lire_reponse('{"passages_utilises": "1"}')["passages_utilises"] == []
    print("llm.py : vérifications passées, aucun appel à l'API")
