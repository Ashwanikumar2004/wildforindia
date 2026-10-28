# WildFIndia

A Django wildlife guide for India, with an image identifier, a personal WildDex,
a protected-area directory and an interactive map.

## Open the project again

In the VS Code terminal, inside this project folder:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. Press **Ctrl+C** in that terminal to stop.
You do not need to recreate the environment or reload the catalogue each time.

## What is included

- A searchable species guide with category, habitat and recorded-state filters.
- Thirteen researched species, descriptions, biological facts, conservation
  status, photographs, source links and related protected areas.
- A directory snapshot with 106 national parks and 574 wildlife sanctuaries.
  Search, state/type/safari filters, sorting and pagination work together.
- Park profiles with sourced introductions and available attributed photos,
  visit-planning links and moderated visitor reviews.
- A 3D map using approximate park positions. Species appear only when explicitly
  linked to that park, rather than being inferred from a state-wide range.
- Registration, login, logout, profile editing and password changes.
- Private WildDex entries with observation dates, locations, notes, collection
  search and filters, XP, level tracking and CSV export.
- Existing SpeciesNet image identification and private photo history.
- Image attribution, responsive layouts, accessible forms and custom error pages.

Not every protected area has a suitable freely licensed photograph or a full
visitor profile. Missing photographs use an illustration. The project never
labels a photograph of another location as that protected area's photograph.
Directory and conservation data are snapshots, not live official registers.

## Install on another Windows computer

Use a supported Python installation (the project's original setup used Python
3.12). Create an environment and install the web dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Open `.env`, keep `DJANGO_DEBUG=True`, and replace the example secret with a
long private random value. Do not commit this file.

Prepare the database:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_database
.\.venv\Scripts\python.exe manage.py seed_species_catalogue
.\.venv\Scripts\python.exe manage.py seed_protected_areas
.\.venv\Scripts\python.exe manage.py seed_park_locations
.\.venv\Scripts\python.exe manage.py runserver
```

The basic seed command updates the original six starter species. The extended
species seed only creates missing species and fills empty facts. Park seeds
preserve curated details and use existing records instead of duplicating them.

Photographs already included under `static/images/catalogue/` work without a
network connection to Wikimedia. To download or resume missing catalogue media:

```powershell
.\.venv\Scripts\python.exe manage.py download_catalogue_media
```

This optional maintenance command needs internet access. It stores attribution
in `datasets/catalogue_media.json`. It never runs during a visitor's request.
The map and the current Bootstrap/fonts use external libraries, so those parts
of the interface still require internet access.

## Use WildDex

1. Register or log in.
2. Open **AI Identifier** and upload a clear animal photograph.
3. Review the suggestion and confirm a matching catalogue species.
4. Open **WildDex**, then **Open journal**, to save notes and an observation date.
5. Use **Export my journal** to download your own entries.

Each species earns XP once. Removing a discovery recalculates XP; it does not
delete the original identification. Deleting an identification photo from
history keeps an already confirmed journal entry.

## Administration

Create an administrator account:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Visit `/admin/` to edit catalogue records, upload photos, link species to parks,
and moderate reviews. In **Park reviews**, approve a reviewed submission by
enabling **is verified**. New or edited reviews remain unpublished until then.
Do not publish invented visitor reviews or unverified park/species associations.

## Data and storage

Development uses `db.sqlite3` for accounts, catalogue records, reviews, journal
entries and saved prediction results. Uploaded files are stored under `media/`.
Both are excluded from Git. Passwords are stored by Django using password
hashing; they are not stored as readable text.

Cached catalogue photos are public static assets. User identification images
are served through an account ownership check; production storage is private.
Do not share the development database, `.env`, or users' uploaded photographs.

See [catalogue sources](datasets/CATALOGUE-SOURCES.md) for the data and image
licenses, and [map sources](static/data/README.md) for boundary attribution.
The site's **About & image credits** page includes photograph credits.

## Project structure

- `accounts/`: registration, login, account details and password management.
- `wildlife/`: species catalogue, home page, search, map and data import commands.
- `parks/`: protected areas, facilities, photos, routes and moderated reviews.
- `wilddex/`: private discovery journal and XP.
- `ai_identifier/`: the existing working SpeciesNet upload and prediction flow.
- `config/`: Django settings, URLs and storage.
- `templates/`, `static/`: page templates, CSS, JavaScript and public assets.
- `datasets/`: reproducible catalogue records, source metadata and model notes.
- `sightings/`, `dashboard/`, `chatbot/`: original scaffolding, with no public
  routes. Current account and journal features live in the apps above.

## Checks

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test --noinput
```

Tests cover accounts, catalogue filters, private journal access, XP, exports,
review moderation, first-run seeding and mocked AI workflows. They do not
measure the real model's recognition accuracy.

## Existing AI model

The AI model and its runtime implementation have been retained. For a new
installation only, install its optional dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-local-ai.txt
```

SpeciesNet downloads model files on first use and reuses them afterwards.
Identification happens on the computer running Django. Scores are suggestions,
not guarantees; the person using the app confirms any WildDex addition.
Model training photos are not required or included; see `datasets/README.md`.

## Hosting and Vercel

Pushing to GitHub saves code; it does not host the website or run the AI.

The current web configuration supports PostgreSQL and Vercel Blob. Set:

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY`: a new production secret
- `DJANGO_ALLOWED_HOSTS`: your deployment and domain hostnames
- `DJANGO_CSRF_TRUSTED_ORIGINS`: full HTTPS origins
- `DATABASE_URL`: your PostgreSQL connection URL
- `BLOB_PUBLIC_READ_WRITE_TOKEN`: a public Blob store token
- `BLOB_PRIVATE_READ_WRITE_TOKEN`: a separate private Blob store token

Apply the database migrations and catalogue seed commands against the production
database from a trusted environment. Keep secrets in hosting environment
settings. Back up the production database and storage.

**The current local SpeciesNet model is not configured to run on Vercel.**
Its large dependencies are deliberately separate from the web requirements.
Running the complete identifier online needs a compatible server with enough
memory for the existing model, or a separately hosted inference service. That
connection has not been changed as part of the catalogue and journal work.
Do not present the Vercel web deployment alone as a working hosted identifier.
