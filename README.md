# Meriel Thermique

Application web **Django** pour la gestion de bâtiments et l’évaluation d’un indicateur de performance énergétique simplifié : déperditions thermiques à partir de coefficients surfaciques **k**, consommation normalisée (kWh/m²/an) et **classe énergétique** de A à G.

Le dépôt correspond au projet Django `meriel` et à l’application métier `thermo`. L’interface est en **français** ; la zone horaire par défaut est **Africa/Algiers**.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Pile technique](#pile-technique)
- [Modèle métier et calculs](#modèle-métier-et-calculs)
- [Structure du dépôt](#structure-du-dépôt)
- [Prérequis](#prérequis)
- [Installation et exécution](#installation-et-exécution)
- [Comptes utilisateurs initiaux](#comptes-utilisateurs-initiaux)
- [Navigation et URLs principales](#navigation-et-urls-principales)
- [Données de démonstration](#données-de-démonstration)
- [Interface d’administration](#interface-dadministration)
- [Configuration](#configuration)
- [Mise en production (rappels)](#mise-en-production-rappels)
- [Tests automatisés](#tests-automatisés)

---

## Fonctionnalités

### Authentification

- Connexion / déconnexion Django (`LoginView` / `LogoutView`).
- Formulaire de connexion personnalisé (`thermo.auth_forms.ConnexionForm`) avec classes CSS alignées sur le reste du site.
- Pages métier protégées par `@login_required` : tableau de bord, bâtiments, matériaux.

### Bâtiments

- **Tableau de bord** : aperçu des derniers bâtiments et total.
- **Liste** avec recherche textuelle, filtre par catégorie, filtre par classe énergétique, tri (nom, consommation, déperdition, classe, date) et **pagination** (12 par page).
- **Création / modification / suppression** avec formulaires `ModelForm`.
- **Fiche détail** : affichage des surfaces, types choisis, coefficients **k**, déperditions par composant, total, consommation kWh/m²/an et classe.

### Référentiels « matériaux »

Page hub **`/materiaux/`** pour centraliser :

- **Types de bâtiment** (`CategorieBatiment`) : nom + actif/inactif (sans coefficient).
- **Types de plancher, mur, toiture, ouvrant** : nom, **k**, actif/inactif.

Opérations CRUD dédiées (création, modification, suppression). Les types utilisés par au moins un bâtiment ne peuvent pas être supprimés (`ProtectedError` géré avec message utilisateur). Les libellés des types sont **uniques** ; une collision affiche une erreur de validation.

### Charte graphique

- Mise en page commune (`templates/base.html`), styles dans `static/css/app.css` (navigation, cartes, tableaux, boutons, messages flash).

---

## Pile technique

| Élément | Détail |
|--------|--------|
| Langage | Python (3.12 utilisé en développement) |
| Framework | Django **6.0.x** |
| Base de données | **SQLite** (`db.sqlite3` à la racine) |
| Templates | Moteur Django, répertoire global `templates/` |
| Fichiers statiques | `STATICFILES_DIRS` → dossier `static/` |

Il n’y a pas encore de fichier `requirements.txt` dans le dépôt ; voir la section [Prérequis](#prérequis) pour installer Django explicitement.

---

## Modèle métier et calculs

### Entités principales (`thermo/models.py`)

- **`CoefficientBase`** (modèle abstrait) : `nom`, `k` (≥ 0), `actif`.
- **`TypePlancher`, `TypeMur`, `TypeToiture`, `TypeOuvrant`** : héritent de `CoefficientBase` (tables séparées).
- **`CategorieBatiment`** : catégorie fonctionnelle du bâtiment (école, hôpital, etc.).
- **`Batiment`** :
  - lien obligatoire vers une `CategorieBatiment` ;
  - surfaces : habitable, plancher, murs, toiture, ouvrants ;
  - quatre clés étrangères vers les types (plancher, mur, toiture, ouvrant), avec suppression protégée (`PROTECT`).

### Déperditions et classe

Pour chaque enveloppe :

\[
\text{déperdition} = k \times \text{surface}
\]

La **déperdition totale** est la somme plancher + murs + toiture + ouvrants. La **consommation normalisée** utilisée pour l’affichage et la classe est :

\[
\text{consommation (kWh/m²/an)} = \frac{\text{déperdition totale}}{\text{surface habitable}}
\]

Les **seuils de classe** (`Batiment.classe_depuis_conso`) :

| Classe | Condition sur la consommation normalisée |
|--------|------------------------------------------|
| A | &lt; 70 |
| B | ≤ 110 |
| C | ≤ 180 |
| D | ≤ 250 |
| E | ≤ 330 |
| F | ≤ 420 |
| G | &gt; 420 |

Ces règles sont implémentées en `Decimal` pour limiter les erreurs d’arrondi.

---

## Structure du dépôt

```
Meriel_Website/
├── manage.py                 # Point d’entrée Django
├── db.sqlite3                # Base SQLite (git ne doit pas versionner les données sensibles en prod)
├── meriel/                   # Projet Django
│   ├── settings.py           # Configuration (DEBUG, DB, static, auth redirects, i18n)
│   ├── urls.py               # Routage racine + auth + inclusion de thermo.urls
│   ├── wsgi.py / asgi.py
├── thermo/                   # Application métier
│   ├── models.py             # Modèles et propriétés de calcul
│   ├── views.py              # Vues CRUD et tableau de bord
│   ├── urls.py               # Routes namespacées app_name = "thermo"
│   ├── forms.py              # Formulaires bâtiments et types
│   ├── admin.py              # Enregistrement dans l’admin Django
│   ├── auth_forms.py         # Formulaire de connexion
│   └── migrations/           # Schéma + données initiales (seed)
├── templates/
│   ├── base.html
│   ├── auth/connexion.html
│   └── thermo/               # Pages bâtiments, tableau de bord, matériaux
└── static/
    └── css/app.css
```

L’application `thermo` est déclarée dans `INSTALLED_APPS`. Les URLs applicatives utilisent le **namespace** `thermo:` (important pour `{% url %}` et `reverse()`).

---

## Prérequis

- **Python** 3.10+ recommandé (le projet a été utilisé avec **3.12**).
- **pip** pour installer Django.

Exemple d’installation minimale :

```bash
pip install "Django>=6.0,<7"
```

(adaptez selon votre environnement virtuel ou vos contraintes universitaires.)

---

## Installation et exécution

À la racine du dépôt :

```bash
# Créer et activer un environnement virtuel (recommandé)
python -m venv .venv
# Windows PowerShell :
.\.venv\Scripts\Activate.ps1

pip install "Django>=6.0,<7"

# Appliquer les migrations (crée/met à jour db.sqlite3)
python manage.py migrate

# Lancer le serveur de développement
python manage.py runserver
```

Puis ouvrir dans le navigateur : **http://127.0.0.1:8000/**

- La racine du site correspond aux URLs définies dans `thermo/urls.py` (pas de préfixe supplémentaire dans `meriel/urls.py`).
- Connexion : **http://127.0.0.1:8000/connexion/**

---

## Comptes utilisateurs initiaux

La migration **`0002_seed_comptes_et_types`** crée ou met à jour deux utilisateurs Django :

| Utilisateur | Mot de passe | Rôle |
|-------------|--------------|------|
| `admin` | `admin` | Superutilisateur et staff |
| `user` | `user` | Utilisateur standard |

**Important :** ces identifiants sont adaptés au **développement local uniquement**. Changez les mots de passe avant toute exposition réseau et ne commitez pas de secrets.

---

## Navigation et URLs principales

Rappels : routes d’auth au niveau projet (`name="login"`, `name="logout"`) ; routes métier sous le namespace **`thermo:`**.

| URL | Nom Django | Description |
|-----|------------|-------------|
| `/` | `thermo:tableau_de_bord` | Tableau de bord |
| `/connexion/` | `login` | Connexion |
| `/deconnexion/` | `logout` | Déconnexion |
| `/batiments/` | `thermo:batiment_liste` | Liste paginée et filtres |
| `/batiments/nouveau/` | `thermo:batiment_creer` | Création |
| `/batiments/<id>/` | `thermo:batiment_detail` | Détail |
| `/batiments/<id>/modifier/` | `thermo:batiment_modifier` | Modification |
| `/batiments/<id>/supprimer/` | `thermo:batiment_supprimer` | Suppression |
| `/materiaux/` | `thermo:materiaux_hub` | Hub matériaux & catégories |
| `/materiaux/categories/...` | `thermo:categorie_batiment_*` | CRUD catégories |
| `/materiaux/planchers/...` | `thermo:materiau_plancher_*` | CRUD planchers |
| `/materiaux/murs/...` | `thermo:materiau_mur_*` | CRUD murs |
| `/materiaux/toitures/...` | `thermo:materiau_toiture_*` | CRUD toitures |
| `/materiaux/ouvrants/...` | `thermo:materiau_ouvrant_*` | CRUD ouvrants |
| `/admin/` | (admin Django) | Back-office |

---

## Données de démonstration

- **`0002_seed_comptes_et_types`** : utilisateurs ci-dessus + exemples de types (planchers, murs, toitures, ouvrants) avec des **k** réalistes mais simplifiés.
- **`0003_categorie_batiment`** : modèle `CategorieBatiment` + catégories par défaut (École, Hôpital, Immeuble, Bureau, Commerce, Industriel) + rattachement des anciens bâtiments sans catégorie à « Immeuble » si besoin.

---

## Interface d’administration

Superutilisateur `admin` / `admin` peut accéder à **`/admin/`** pour gérer utilisateurs, groupes et modèles `thermo` (configuration dans `thermo/admin.py` : recherche, filtres, colonnes calculées classe et consommation pour `Batiment`).

---

## Configuration

Fichier principal : **`meriel/settings.py`**.

| Variable | Valeur actuelle (dev) | Commentaire |
|----------|----------------------|-------------|
| `DEBUG` | `True` | À désactiver en production |
| `SECRET_KEY` | valeur par défaut générée | **À remplacer** en production |
| `ALLOWED_HOSTS` | `127.0.0.1`, `localhost` | Étendre selon le nom de domaine |
| `DATABASES` | SQLite fichier `db.sqlite3` | Postgres/MySQL possibles pour la prod |
| `LANGUAGE_CODE` | `fr` | Français |
| `TIME_ZONE` | `Africa/Algiers` | Fuseau horaire affichage |
| `STATIC_URL` / `STATICFILES_DIRS` | `static/` et dossier `static/` | CSS et assets statiques |
| `LOGIN_URL` | `login` | Page de connexion projet |
| `LOGIN_REDIRECT_URL` | `thermo:tableau_de_bord` | Après connexion réussie |
| `LOGOUT_REDIRECT_URL` | `login` | Après déconnexion |

---

## Mise en production (rappels)

Ce dépôt est configuré comme **projet étudiant / développement**. Pour un déploiement réel :

1. `DEBUG = False`, `ALLOWED_HOSTS` corrects, `SECRET_KEY` fort et hors dépôt.
2. Servir les fichiers statiques avec un serveur web ou `collectstatic` + stockage adapté.
3. Base de données dédiée et sauvegardes.
4. HTTPS et politique de mots de passe renforcée pour les comptes admin.

---

## Tests automatisés

Le fichier `thermo/tests.py` est pour l’instant vide (stub Django). Vous pouvez lancer :

```bash
python manage.py test
```

pour valider la configuration ; l’ajout de tests unitaires (modèle `Batiment`, vues protégées, reversing des URLs) reste une évolution naturelle du projet.

---

## Licence et contexte

Projet réalisé dans un cadre **académique** (« Meriel Thermique », calcul et classification énergétique simplifiés). Pour toute réutilisation ou citation du dépôt, respectez les règles de votre établissement concernant le plagiat et le partage du code source.
