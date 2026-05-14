# FoodExpress-CI

**MVP de livraison de repas a Abidjan, Cote d'Ivoire**

API backend FastAPI + PostgreSQL/SQLite + Auth JWT pour une application de commande et livraison de repas.

---

## Stack Technique

| Couche | Technologie |
|--------|-------------|
| Framework | FastAPI |
| Base de donnees | PostgreSQL (prod) / SQLite (dev) |
| ORM | SQLAlchemy |
| Auth | JWT (jose + passlib) |
| Docs auto | Swagger UI / ReDoc |

---

## Fonctionnalites MVP

- [x] **Authentification JWT** — Inscription, connexion, profil utilisateur
- [x] **Restaurants** — Liste geolocalisee, menus par restaurant
- [x] **Commandes** — Creation, suivi, mise a jour du statut
- [x] **Livraisons** — Assignation livreur, tracking GPS en temps reel
- [x] **Paiement** — Statut de paiement simule (pret pour integration mobile money)

---

## Installation

```bash
# 1. Cloner le repo
git clone https://github.com/gnoujeanpierre/foodexpress-ci.git
cd foodexpress-ci/backend

# 2. Creer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Installer les dependances
pip install -r requirements.txt

# 4. Lancer le serveur
uvicorn app.main:app --reload --port 8000