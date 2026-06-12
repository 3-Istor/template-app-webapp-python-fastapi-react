# AI Context - FastAPI Template

Ce document est destiné à être lu par une IA avant toute modification du backend. Il décrit les règles d’architecture, les conventions de code et la procédure standard pour ajouter une fonctionnalité.

## 1. Règles d’architecture

Le projet suit une séparation stricte des responsabilités.

- Les routers FastAPI exposent uniquement les endpoints HTTP. Ils ne doivent pas contenir de logique métier importante.
- Les schémas Pydantic servent à valider les entrées et à normaliser les sorties de l’API.
- Les modèles ORM décrivent la structure persistée en base de données.
- Les services contiennent la logique métier réutilisable et les opérations complexes.
- La configuration applicative vit dans un module de settings unique, basé sur les variables d’environnement.

Structure cible à respecter pour les nouvelles fonctionnalités :

```text
backend/app/
├── core/
├── database/
├── models/
├── schemas/
├── routers/
├── services/
└── main.py
```

Si un fichier ou un dossier n’existe pas encore, l’IA doit créer la couche manquante au bon endroit plutôt que d’étendre `main.py` avec de la logique métier.

## 2. Conventions de code

- Utiliser `async def` pour les routes qui peuvent bénéficier d’un I/O non bloquant ou qui s’intègrent à une stack asynchrone.
- Garder `def` uniquement pour une fonction purement synchrone et sans attente réseau ou base de données asynchrone.
- Centraliser les variables d’environnement dans une classe héritant de `BaseSettings` de Pydantic Settings.
- Exposer les valeurs de configuration via une fonction cacheable, afin d’éviter de recréer les settings à chaque requête.
- Utiliser le typage strict avec `typing` ou les types natifs Python 3.10+.
- Préférer les annotations explicites sur les paramètres, les retours de fonctions, les collections et les modèles.

Conventions recommandées :

- Les routes doivent retourner des objets JSON simples, des schémas Pydantic ou lever une exception HTTP.
- Les fonctions de service doivent avoir des signatures claires et testables.
- Les effets de bord doivent être isolés dans des couches dédiées.

## 3. Gestion des erreurs et réponses

- Lever `HTTPException` pour toute erreur métier ou technique exposable à l’utilisateur.
- Choisir un code HTTP précis : 400 pour une requête invalide, 401 pour une authentification absente, 403 pour un accès interdit, 404 pour une ressource inexistante, 409 pour un conflit, 422 pour une validation gérée par FastAPI, 500 pour une erreur inattendue.
- Ne jamais masquer une erreur de validation en renvoyant une réponse 200 avec un champ `error` si l’erreur doit être traitée comme un échec HTTP.
- Les réponses réussies doivent rester cohérentes et prévisibles, avec des clés stables et un schéma de sortie documentable.

Format attendu pour les erreurs applicatives exposées par l’API :

```json
{
  "detail": "Message lisible par un humain"
}
```

## 4. Injection de dépendances

Utiliser `Depends()` pour injecter les dépendances transverses.

- Injection de la session de base de données pour les opérations de lecture et d’écriture.
- Injection de la sécurité pour JWT, OAuth2, API keys ou récupération de l’utilisateur courant.
- Injection de services ou de repositories si la logique devient réutilisable ou complexe.

Règles importantes :

- Ne pas instancier la session DB directement dans les routes.
- Ne pas mélanger l’accès base de données, l’authentification et la logique métier dans le même endpoint.
- Préférer une dépendance dédiée par responsabilité, réutilisable dans plusieurs routers.

## 5. Guide d’action pour l’IA : ajouter un nouvel endpoint ou une nouvelle entité

### Étape 1 - Créer le modèle

- Ajouter le modèle ORM dans `models/`.
- Définir la table, les colonnes, les clés primaires, les relations et les contraintes.
- Garder les noms explicites et alignés sur le domaine métier.

### Étape 2 - Créer les schémas In/Out

- Ajouter un schéma d’entrée pour la création ou la mise à jour.
- Ajouter un schéma de sortie pour la réponse API.
- Séparer clairement les champs requis, optionnels et calculés.

### Étape 3 - Créer le router

- Ajouter un router dans `routers/`.
- Déclarer un `APIRouter` avec un préfixe, des tags et, si nécessaire, des dépendances communes.
- Garder le endpoint mince : validation, appel au service, retour de la réponse ou levée d’une exception.

### Étape 4 - Brancher la logique métier

- Créer ou compléter le service correspondant dans `services/`.
- Déplacer la logique métier, les règles de domaine et les transformations hors du router.
- Centraliser l’accès aux données si plusieurs endpoints utilisent la même mécanique.

### Étape 5 - Intégrer le router dans `main.py`

- Importer le router.
- L’enregistrer avec `app.include_router(...)`.
- Vérifier que le tag, le préfixe et les dépendances sont cohérents avec le reste de l’API.

### Étape 6 - Vérifier la cohérence

- Ajouter ou mettre à jour les tests.
- Vérifier que les schémas OpenAPI sont propres dans `/docs` et `/redoc`.
- Contrôler que les nouvelles routes respectent les conventions d’erreurs et de typage.

## 6. Ce que l’IA doit éviter

- Ne pas mettre de logique métier dans `main.py`.
- Ne pas utiliser des structures de retour incohérentes d’un endpoint à l’autre.
- Ne pas contourner les schémas Pydantic pour manipuler des dictionnaires non typés quand un schéma est possible.
- Ne pas créer une dépendance DB globale utilisée directement sans injection contrôlée.
- Ne pas ajouter de nouveau pattern architectural sans le faire correspondre à l’existant ou sans l’isoler clairement.

## 7. Règle de décision rapide

Si une modification touche l’API, poser systématiquement cette question : la logique appartient-elle au router, au schéma, au service, au modèle ou à la configuration ?

La bonne réponse est presque toujours : configuration dans `settings`, validation dans `schemas`, persistance dans `models` et `database`, orchestration dans `services`, exposition HTTP dans `routers`.