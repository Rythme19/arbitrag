# Journal d'avancement

Ce fichier sert de base au rapport : on y note chaque problème rencontré et
chaque essai, y compris ceux qui ont raté.

## Problèmes rencontrés

Une ligne par problème, même s'il n'est pas encore résolu.

| Date | Problème | Cause | Solution essayée | Résultat | Statut |
|------|----------|-------|------------------|----------|--------|
| 10/10/2026 | Remarque du prof à la validation du sujet : de bons résultats ne prouvent rien si le LLM connaît déjà les règles et répond de mémoire, sans se servir de la recherche. | Les règles des jeux connus font partie de ce que les LLM ont appris. | Prévu : mesurer le LLM seul, mesurer la recherche à part, tester avec des livrets modifiés (voir README, partie Évaluation). Si ça marche trop bien, le prof propose de passer à l'étape suivante : l'arbitre devient un joueur. | Pas encore testé | Ouvert |
| 10/10/2026 | Monopoly : l'extraction donne 0 caractère sur les 4 pages. | Le PDF est un scan (des images, pas du texte). | Reconnaissance de texte avec l'outil intégré à macOS (`src/ocr.swift`), le 11/10. | 4 pages, 20 590 caractères. Quelques fautes isolées (« dèpart », un « \| » parasite). | Résolu |
| 10/10/2026 | Monopoly : le livret est une vieille édition canadienne (Parker Brothers, 1961 : dollars, « GO », « Caisse Commune »), différente du Monopoly français actuel. | C'est le seul livret en français trouvé. | À décider : le garder en le disant clairement, ou chercher l'édition française actuelle. | – | Ouvert |
| 10/10/2026 | Uno : le texte extrait mélange 7 langues, et les 2 pages sont identiques. | La fiche Mattel met les 7 langues côte à côte sur la même page. | Extraction de la seule colonne française, sur une seule page (`pdftotext -l 1 -x 686 -y 0 -W 406 -H 1138`), le 11/10. | 5 553 caractères, aucun mot d'une autre langue repéré. Les numéros des listes sont perdus. | Résolu |
| 10/10/2026 | Uno : la fiche est celle de UNO Express (56 cartes), pas du Uno classique. | C'est la fiche trouvée. | À décider : la garder sous le nom UNO Express, ou chercher la fiche du Uno classique. | – | Ouvert |
| 10/10/2026 | Catan : le livret trouvé sur catan.com est en anglais alors que les autres sont en français. | Le site de l'éditeur ne propose que l'anglais. | Remplacé le 11/10 par un livret français, qui est un scan : reconnaissance de texte avec `src/ocr.swift`. Le livret anglais est mis de côté dans `data/originaux/catan-en.pdf`. | 12 pages, 47 406 caractères. Les pages sont des doubles pages à plusieurs colonnes : l'ordre des paragraphes reste à vérifier. | À vérifier |
| 10/10/2026 | Les règles de base des Loups-Garous sont présentes deux fois. | `loups-garous__le-village.pdf` reprend les règles de base (p. 2 à 5) avant celles de l'extension (p. 6 à 8). | À faire au découpage : ne garder que les pages 6 à 8 du fichier « Le Village ». | Pas encore testé | Ouvert |
| 10/10/2026 | Pages presque vides dans plusieurs livrets (couvertures, dos). | Ces pages sont des images sans texte utile. | À faire au découpage : ignorer les pages de moins de 100 caractères. | Pas encore testé | Ouvert |
| 11/10/2026 | Skyjo : l'extraction donne 0 caractère sur les 4 pages. | Le PDF officiel a été « imprimé en PDF » : le texte y est sous forme d'image. | Reconnaissance de texte avec `src/ocr.swift`. | 4 pages, 4 406 caractères, texte propre. | Résolu |
| 11/10/2026 | Les livrets de Wingspan et de Catan en français étaient des téléchargements non confirmés par Chrome (fichiers `.crdownload`). | Chrome attend une confirmation avant de finaliser certains téléchargements. | Vérifié que les deux fichiers sont des PDF complets (12 pages chacun) avant de les copier. | Les deux sont utilisables. | Résolu |

## Essais

Une ligne par version du pipeline testée.

| Date | Version | Ce qu'on a testé | Résultat (recherche / réponse) | Échecs observés | Décision |
|------|---------|------------------|--------------------------------|-----------------|----------|
|      |         |                  |                                |                 |          |
