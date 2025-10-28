# Stocky

Application FastAPI de gestion de stock, commandes, numéros de série et attributions inspirée du cahier des charges fourni.

## Démarrage rapide

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

L'API expose la documentation interactive sur `http://localhost:8000/docs`.

## Données de démonstration

Au démarrage, la base SQLite `stocky.db` est initialisée et peuplée avec un jeu de données réaliste (matériels, fournisseurs, commandes, numéros de série et attributions) facilitant la prise en main.

Définissez la variable d'environnement `DATABASE_URL` avant de lancer l'application pour utiliser un autre SGBD pris en charge par SQLAlchemy (PostgreSQL, MySQL, etc.).

## Pièces jointes stockées en base

Les documents (PDF, images, etc.) sont persistés directement en base via le point d'API `POST /files`.
La route accepte un formulaire multipart contenant `entity_type`, `entity_id` et le fichier (`attachment`).
Les téléchargements se font via `GET /files/{id}/download` et les fichiers liés sont exposés dans les réponses des entités (ex : `GET /orders/{id}`).

## Rôles et permissions

Les appels HTTP doivent fournir l'en-tête `X-User-Role` avec l'une des valeurs :

- `admin`
- `storekeeper`
- `buyer`
- `viewer`

Certaines routes (création de commande, réception, attribution, etc.) sont limitées aux rôles décrits.

## Jeux de widgets et rapports

Le dashboard (`GET /dashboard/widgets`) regroupe les widgets demandés :

- Stock par catégorie.
- Livraisons en attente.
- Garanties à échéance (< 90 jours).
- Attributions récentes.
- Valeur de stock.
- Alertes (seuils de stock, garanties expirées).

Les rapports sont disponibles via :

- `GET /reports/stock-by-site`
- `GET /reports/orders-by-status`
- `GET /reports/assignments-by-department`

## Tests

```bash
pytest
```

## Interface utilisateur React

Une interface moderne en React/JS est disponible dans le dossier `frontend`.

```bash
cd frontend
npm install
npm run dev
```

### Accéder au dashboard

1. Démarrez l'API FastAPI (voir section "Démarrage rapide").
2. Lancez le serveur de développement React avec `npm run dev`.
3. Ouvrez le navigateur sur `http://localhost:5173` pour afficher le dashboard.

L'application démarre sur `http://localhost:5173` avec :

- un dashboard modulaire regroupant les widgets demandés ;
- les vues Commandes, Matériels, Détail matériel et Attributions avec filtres, recherche et actions rapides ;
- une base de données locale simulée (données de démonstration stockées côté client) respectant le modèle fourni.
