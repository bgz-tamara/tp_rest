# TP-REST

Application de réservation de cinéma composée de quatre microservices REST (Flask) :

| Service  | Dossier     | Port | Rôle                          | Dépend de       |
|----------|-------------|------|-------------------------------|-----------------|
| Movie    | `movie/`    | 3200 | Catalogue des films           | -               |
| Booking  | `booking/`  | 3201 | Réservations des utilisateurs | Movie, Schedule |
| Schedule | `schedule/` | 3202 | Programmation des séances     | Movie           |
| User     | `user/`     | 3203 | Utilisateurs et connexion     | -               |

## Prérequis

- Python 3.10 ou plus récent
- Git

## Installation

À faire une seule fois, depuis la racine du projet.

Créer l'environnement virtuel :

    python -m venv venv

Sous Linux ou macOS, la commande peut être `python3`.

L'activer, selon le terminal utilisé :

    .\venv\Scripts\Activate.ps1     # Windows, PowerShell
    source venv/Scripts/activate    # Windows, Git Bash
    source venv/bin/activate        # Linux / macOS

Installer les dépendances :

    pip install -r requirements.txt

## Lancement

Chaque service tourne dans son propre terminal. Ouvrir quatre terminaux à la racine du projet, **activer l'environnement virtuel dans chacun**, puis lancer un service par terminal :

    cd movie
    pymon movie.py

    cd schedule
    pymon schedule.py

    cd booking
    pymon booking.py

    cd user
    pymon user.py

`pymon` redémarre le service à chaque modification du code. `python movie.py` (etc.) fonctionne aussi, sans ce rechargement.

Il faut lancer chaque service **depuis son dossier**, car les chemins vers les fichiers de `databases/` sont relatifs.

Pour vérifier qu'un service répond, ouvrir son adresse dans un navigateur, par exemple <http://localhost:3200> pour Movie. Un message de bienvenue doit s'afficher.

Pour arrêter un service : `Ctrl+C` dans son terminal.

## Authentification

Les routes protégées attendent un token JWT, délivré par le service User et valable une heure.

1. Envoyer une requête `POST http://localhost:3203/login` avec le corps JSON :

        { "id": "<identifiant>", "password": "<mot de passe>" }

2. Ajouter le `access_token` reçu à l'en-tête des requêtes suivantes :

        Authorization: Bearer <access_token>

Comptes de test :

| Rôle               | id            | password   |
|--------------------|---------------|------------|
| Administrateur     | `pam_beesly`  | `pam123`   |
| Utilisateur simple | `jim_halpert` | `jim123`   |

Tous les comptes sont listés dans `user/databases/users.json`, où les mots de passe ne sont stockés que sous forme de hash.

La clé de signature se définit avec la variable d'environnement `JWT_SECRET_KEY`. Sans elle, une clé de développement est utilisée. Si vous la définissez, elle doit être identique dans les quatre terminaux.

## Documentation des API

Chaque service est décrit par un fichier OpenAPI dans son dossier (`movie/movie.yaml`, `booking/booking.yaml`, `schedule/schedule.yaml`, `user/user.yaml`), à ouvrir par exemple dans [Swagger Editor](https://editor.swagger.io/).

## Données

Les données sont stockées dans les fichiers JSON des dossiers `databases/`. Les ajouts, modifications et suppressions les réécrivent : `git restore <fichier>` permet de revenir à la dernière version commitée.

## Docker

La conteneurisation n'est pas encore terminée : les `Dockerfile` sont incomplets et `docker-compose.yml` ne déclare que Movie. Utiliser le lancement manuel ci-dessus.
