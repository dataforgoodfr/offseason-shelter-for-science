# 📡 Dispatcher API

Une API REST développée avec **FastAPI** pour gérer l’allocation, la libération et la priorisation d'assets à partir de données CKAN, avec une mise à jour automatique toutes les 2 minutes via **APScheduler**.

---

## 🧩 Fonctionnalités principales

- 🔄 Mise à jour automatique des priorités CKAN
- 📦 Allocation intelligente d’assets
- 🔓 Libération manuelle d’assets
- ⚙️ Mise à jour manuelle des priorités CKAN
- 📊 Monitoring de l’état global via endpoint

---

## 🚀 Lancement rapide

### Prérequis

- Python 3.8+
- `pip install -r requirements.txt`

### Lancer le serveur localement

```bash
uvicorn main:app --reload
```

---

## 📁 Structure du projet

```
dispatcher-api/
├── main.py                   # Application FastAPI principale
├── dispatcher/
│   ├── logic.py              # Logique d'allocation et gestion des données
│   ├── schemas.py            # Schémas Pydantic pour la validation
│   data/
│       ├── allocations.json  # Allocations actives
│       └── ckan_data.json    # Données d’assets avec priorités
```

---

## 🔌 Endpoints API

### 📥 `POST /allocate`

Alloue des assets à un nœud selon l’espace disque disponible.

#### 🔸 Requête

```json
{
  "free_space_gb": 10,
  "node_id": "node-123"
}
```

#### 🔸 Réponse

```json
[
  {
    "id": "asset-1",
    "url": "http://example.com/file1.zip",
    "size_mb": 500,
    "priority": 6,
    "name": "file1.zip"
  }
]
```

#### 🔸 Erreur possible

```json
{
  "detail": "No available assets matching the criteria"
}
```

---

### 🔁 `POST /release`

Libère un asset précédemment alloué.

#### 🔸 Requête

```json
{
  "asset_id": "asset-1",
  "node_id": "node-123"
}
```

#### 🔸 Réponse

```json
{
  "status": "success"
}
```

---

### ⚙️ `POST /update-ckan`

Met à jour manuellement la priorité d’un ou plusieurs assets CKAN.

#### 🔸 Requête

```json
{
  "updates": [
    {
      "asset_id": "asset-1",
      "new_priority": 9
    }
  ]
}
```

#### 🔸 Réponse

```json
{
  "status": "success",
  "updated_items": 1
}
```

#### 🔸 Erreur possible

```json
{
  "detail": "Error message..."
}
```

---

### 📈 `GET /status`

Retourne l’état global du système.

#### 🔸 Réponse

```json
{
  "ckan_datasets": 42,
  "active_allocations": 5,
  "next_auto_update": "2025-07-26T14:00:00"
}
```

---

## 🔄 Mise à jour automatique

Le script démarre un **BackgroundScheduler** qui :

- Nettoie les allocations expirées (> 24h)
- Modifie les priorités des datasets CKAN de façon aléatoire (±1 dans la plage [1, 10])
- Sauvegarde les changements dans les fichiers JSON

🕑 Par défaut : toutes les **2 minutes**

---

## 🔐 Sécurité & Déploiement

> Cette API est pensée pour des environnements de test ou des prototypes de microservices.  
Pour un usage en production, il est recommandé de :
- Ajouter une authentification/API key
- Remplacer les fichiers JSON par une base de données (PostgreSQL, MongoDB…)
- Gérer la concurrence et les accès aux fichiers avec des verrous ou une file d’attente

---

## 📃 Licence

Open Source — Utilisation libre sous licence MIT.

---

## 👤 Auteur

Slim