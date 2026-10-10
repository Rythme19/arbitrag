# ArbitRAG

Un arbitre pour les jeux de société. On pose une question de règle, le système
répond en citant le passage du livret officiel. Projet du cours NLP 2026 (ESGI,
5IABD).

## Installation

Il faut Python 3.12 ou plus, et `pdftotext` (fourni par poppler :
`brew install poppler` sur macOS).

```bash
pip install -r requirements.txt
```

Les livrets ne sont pas dans le dépôt, car ils sont protégés par le droit
d'auteur. Chacun dépose les siens dans `data/raw/`, puis lance :

```bash
python3 src/extract.py
```

## Structure

```
arbitrag/
├── data/
│   ├── originaux/    scans et fichiers à convertir avant usage (non versionnés)
│   ├── raw/          livrets lus par l'extraction : PDF ou texte (non versionnés)
│   └── processed/    texte découpé, au format parquet
├── eval/
│   └── questions.csv base de tests : question, réponse et source attendues
├── src/              code : extraction, RAG, évaluation
├── results/          scores de chaque version du pipeline
├── JOURNAL.md        rapport d'avancement : ce qui a été testé, ce qui a raté
└── README.md
```

Le contenu de `data/` et tous les PDF sont ignorés par git (voir `.gitignore`).
Le parquet est à remettre au prof à part.

## Corpus

État au 11/10/2026 : 8 jeux, tous en français, 94 pages. Les problèmes sont
détaillés dans `JOURNAL.md`.

| Fichier (`data/raw/`) | Jeu | Pages | Origine du texte | Source |
|-----------------------|-----|-------|------------------|--------|
| `catan.txt` | Catan, le jeu de base | 12 | scan, reconnaissance de texte | à compléter |
| `dobble.pdf` | Dobble | 16 | texte du PDF | à compléter |
| `loups-garous.pdf` | Loups-Garous de Thiercelieux, jeu de base | 4 | texte du PDF | à compléter |
| `loups-garous__le-village.pdf` | Loups-Garous, extension Le Village | 8 | texte du PDF | à compléter |
| `monopoly.txt` | Monopoly, édition canadienne de 1961 | 4 | scan, reconnaissance de texte | à compléter |
| `root.pdf` | Root, livret d'apprentissage | 32 | texte du PDF | à compléter |
| `skyjo.txt` | Skyjo | 4 | image, reconnaissance de texte | à compléter |
| `uno-express.txt` | UNO Express | 1 | colonne française de la fiche Mattel | à compléter |
| `wingspan.pdf` | Wingspan | 12 | texte du PDF | 1jour-1jeu.com |

Les fichiers qui ont dû être convertis sont conservés dans `data/originaux/`,
avec le livret anglais de Catan, mis de côté. Pour refaire une conversion :

```bash
swift src/ocr.swift data/originaux/monopoly.pdf > data/raw/monopoly.txt
```

## Étapes

| # | Étape | Échéance |
|---|-------|----------|
| 0 | Faire valider le sujet par le prof | fait |
| 1 | Choisir les jeux et la langue, récupérer les livrets dans `data/raw/` | |
| 2 | Extraire le texte, vérifier sa qualité, l'enregistrer en parquet | |
| 3 | Écrire la base de tests dans `eval/questions.csv` | |
| 4 | Pipeline de base : découpage fixe, embeddings, top-k, génération | |
| 5 | Évaluer le LLM seul et le pipeline de base, noter les échecs | **01/12/2026 12h** |
| 6 | Améliorations, testées une par une et mesurées à chaque fois | |
| 7 | Rapport et slides (soutenance de 10 min) | **07/01/2027 9h** |

Étape 2 : déposer les livrets dans `data/raw/` sous le nom `<jeu>.pdf`, puis
lancer `python3 src/extract.py`. Le script écrit `data/processed/pages.parquet`
(une ligne par page) et signale les pages presque vides, qui sont en général
des images.

Améliorations prévues à l'étape 6 : découpage par section, filtre par jeu,
recherche hybride (BM25 + embeddings), reranker.

## Évaluation

Deux mesures, calculées sur `eval/questions.csv` :

- **Recherche** : le passage attendu fait-il partie des k passages retrouvés ?
- **Réponse** : la réponse est-elle correcte par rapport à la réponse attendue ?

Colonne `difficulte` : `direct`, `cas_limite`, `combinaison` (deux règles à
croiser), `hors_livret` (la réponse n'est pas dans le livret, le système doit
le dire).

Chaque version est comparée au LLM seul, sans recherche.

### Le LLM connaît-il déjà les règles ?

Remarque du prof : de bons résultats ne prouvent rien si le LLM répond de
mémoire. Trois garde-fous :

1. **LLM seul** : on mesure d'abord ce qu'il sait sans aucun livret. Les jeux
   où il a déjà tout bon ne servent que de témoin.
2. **Recherche mesurée à part** : retrouver le bon passage ne dépend pas de la
   mémoire du LLM.
3. **Livrets modifiés** : dans une copie du livret, on change quelques règles
   (un nombre de cartes, une condition de victoire). Si le système donne la
   valeur modifiée, il lit le livret ; s'il donne la valeur d'origine, il
   récite.

Si les résultats restent trop bons, étape suivante proposée par le prof :
l'arbitre devient un joueur. Le LLM reçoit ses cartes et l'historique des
coups, et joue son coup en s'appuyant sur les règles retrouvées par le RAG
(détail à confirmer avec lui). Variante plus simple : des règles maison ou des
extensions fournies par l'utilisateur, qui contredisent le livret de base.

## Sortie

Pour chaque question, le système renvoie :

```json
{
  "reponse": "Non",
  "explication": "Une carte +2 ne peut pas être posée sur une autre carte +2.",
  "sources": [{"jeu": "Uno", "page": 2, "extrait": "..."}],
  "trouve_dans_le_livret": true
}
```

Quand la règle n'est pas dans le livret, `trouve_dans_le_livret` vaut `false`
et le système le dit au lieu d'inventer.

## Exigences du prof

- Pouvoir dire objectivement que ça marche.
- Un rapport d'avancement avec les échecs et les erreurs (`JOURNAL.md`).
- Ne pas reposer que sur du prompt engineering : le travail porte sur la
  recherche, pas sur la formulation du prompt.
