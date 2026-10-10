"""Interface de discussion d'ArbitRAG. Lancer avec : streamlit run app.py"""
import html

import streamlit as st

from src import llm
from src.search import charger_passages, chercher, detecter_jeu

TOUS = "Tous les jeux"
EXEMPLES = [
    "Combien de cartes reçoit chaque joueur au Skyjo ?",
    "Que fait la Sorcière dans les Loups-Garous ?",
    "Comment sortir de prison au Monopoly ?",
]

st.set_page_config(page_title="ArbitRAG", page_icon="🎲")


@st.cache_data
def passages():
    return charger_passages()


JEUX = sorted(passages()["jeu"].unique())


def nom(jeu: str) -> str:
    return jeu if jeu == TOUS else jeu.replace("-", " ").title()


def repondre(question: str, jeu_choisi: str, avec_llm: bool) -> dict:
    jeu = detecter_jeu(question, JEUX) if jeu_choisi == TOUS else jeu_choisi
    resultats = chercher(passages(), question, jeu=jeu)
    sources = [
        {"numero": numero, "jeu": r.jeu, "page": r.page, "fichier": r.fichier, "texte": r.texte}
        for numero, r in enumerate(resultats.itertuples(), start=1)
    ]
    message = {"role": "assistant", "jeu": jeu, "sources": sources}
    if sources and avec_llm:
        # Une même question n'est envoyée qu'une fois au LLM pendant la session.
        cache = st.session_state.setdefault("cache", {})
        if (question, jeu) not in cache:
            try:
                cache[question, jeu] = llm.arbitrer(question, sources)
                st.session_state.appels = st.session_state.get("appels", 0) + 1
            except RuntimeError as erreur:
                message["erreur"] = str(erreur)
        message["arbitrage"] = cache.get((question, jeu))
    return message


def afficher(message: dict):
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["texte"])
            return
        if message["jeu"]:
            st.caption(f"Jeu : {nom(message['jeu'])}")
        arbitrage = message.get("arbitrage")
        if "erreur" in message:
            st.error(message["erreur"])
        if not message["sources"]:
            st.warning("Je ne trouve rien sur cette question dans les livrets.")
        elif arbitrage and arbitrage["trouve_dans_le_livret"]:
            st.subheader(arbitrage["verdict"])
            st.markdown(arbitrage["explication"])
        elif arbitrage:
            st.warning(f"Ce n'est pas dans le livret. {arbitrage['explication']}")
        else:
            st.markdown("Voici les passages du livret les plus proches de votre question.")
        cites = set(arbitrage["passages_utilises"]) if arbitrage else {1}
        for source in message["sources"]:
            cite = source["numero"] in cites
            titre = f"{nom(source['jeu'])} · page {source['page']}"
            with st.expander(f"📌 {titre}" if arbitrage and cite else titre, expanded=cite):
                # st.text coupe les lignes trop longues ; ce bloc les renvoie à la ligne.
                texte = html.escape(source["texte"])
                st.markdown(f"<div style='white-space: pre-wrap'>{texte}</div>", unsafe_allow_html=True)
                st.caption(f"Source : {source['fichier']}")


st.session_state.setdefault("messages", [])

with st.sidebar:
    st.header("Réglages")
    jeu_choisi = st.selectbox("Jeu", [TOUS, *JEUX], format_func=nom)
    avec_llm = st.toggle(
        "Réponse rédigée par le LLM",
        disabled=not llm.cle_presente(),
        help="Chaque nouvelle question consomme un appel à l'API.",
    )
    if not llm.cle_presente():
        st.caption("Clé d'API absente : ajoutez-la dans le fichier `.env`.")
    elif not avec_llm:
        st.caption("Recherche seule : l'arbitre montre les passages, sans appel à l'API.")
    st.caption(f"Appels au LLM pendant cette session : {st.session_state.get('appels', 0)}")
    if st.button("Effacer la discussion"):
        st.session_state.messages = []
    st.divider()
    st.caption(f"{len(JEUX)} jeux · {len(passages())} passages de livret")

st.title("🎲 ArbitRAG")
st.caption("L'arbitre des jeux de société : posez une question de règle, la réponse cite le livret.")

for message in st.session_state.messages:
    afficher(message)

question = st.chat_input("Posez une question de règle…")
if not st.session_state.messages:
    st.markdown("**Exemples de questions**")
    for exemple in EXEMPLES:
        if st.button(exemple):
            question = exemple

if question:
    st.session_state.messages.append({"role": "user", "texte": question})
    with st.spinner("L'arbitre consulte le livret…"):
        st.session_state.messages.append(repondre(question, jeu_choisi, avec_llm))
    st.rerun()
