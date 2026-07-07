# 🌿 WildFIndia - Database Entity Relationship Diagram (ERD)

## Overview

WildFIndia is a full-stack wildlife conservation and exploration platform featuring:

- Wildlife Information
- AI Species Identification
- National Parks
- Citizen Science
- WildDex (Gamification)
- Interactive Maps
- Three.js Visualization

---

# Wildlife Module

```mermaid
erDiagram

CATEGORY ||--o{ SPECIES : contains
HABITAT ||--o{ SPECIES : lives_in
CONSERVATION_STATUS ||--o{ SPECIES : status

CATEGORY {
    int id PK
    string name
    string slug
    string description
    string icon
    string cover_image
    string color
    int display_order
    boolean is_active
    datetime created_at
    datetime updated_at
}

HABITAT {
    int id PK
    string name
    string slug
    string climate
    string vegetation
    float average_temperature
    float rainfall
    string hero_image
}

CONSERVATION_STATUS {
    int id PK
    string name
    string code
    string badge_color
    int priority
}

SPECIES {
    uuid id PK
    string common_name
    string scientific_name
    string slug
    text description
    float weight
    float height
    float length
    float speed
    int lifespan
    string diet
    string behaviour
    boolean endemic_to_india
    string thumbnail
    string hero_image
    string sound
    string three_model
    string ar_model
    boolean is_featured
    boolean is_verified
}
```

---

# Parks Module

```mermaid
erDiagram

STATE ||--o{ NATIONAL_PARK : contains

NATIONAL_PARK }o--o{ SPECIES : protects

STATE{
    int id PK
    string name
    string slug
    string capital
    string region
}

NATIONAL_PARK{
    uuid id PK
    string name
    string slug
    int established_year
    float area_sq_km
    float latitude
    float longitude
    string hero_image
    string best_visit_month
}
```

---

# Accounts Module

```mermaid
erDiagram

USER ||--|| USER_PROFILE : owns

USER_PROFILE{
    uuid id PK
    string profile_photo
    string bio
    string location
    int total_xp
    int total_species_discovered
    int total_parks_visited
}
```

---

# WildDex Module

```mermaid
erDiagram

USER_PROFILE ||--o{ USER_COLLECTION : owns

SPECIES ||--o{ USER_COLLECTION : collected

USER_COLLECTION }o--o{ ACHIEVEMENT : unlocks

USER_COLLECTION{
    uuid id PK
    datetime discovered_date
    int xp_earned
    boolean verified
}

ACHIEVEMENT{
    int id PK
    string title
    int xp_required
    string badge
}
```

---

# Sightings Module

```mermaid
erDiagram

USER_PROFILE ||--o{ WILDLIFE_SIGHTING : reports

SPECIES ||--o{ WILDLIFE_SIGHTING : identified

NATIONAL_PARK ||--o{ WILDLIFE_SIGHTING : occurs_at

WILDLIFE_SIGHTING{
    uuid id PK
    float latitude
    float longitude
    string uploaded_photo
    float confidence
    boolean verified
    datetime sighting_date
}
```

---

# AI Identifier Module

```mermaid
erDiagram

SPECIES ||--o{ AI_PREDICTION : predicted_as

AI_PREDICTION{
    uuid id PK
    string uploaded_image
    float confidence
    float inference_time
    string model_version
    datetime prediction_date
}
```

---

# Complete Database Overview

```mermaid
erDiagram

CATEGORY ||--o{ SPECIES : contains
HABITAT ||--o{ SPECIES : habitat
CONSERVATION_STATUS ||--o{ SPECIES : status

STATE ||--o{ NATIONAL_PARK : contains

SPECIES }o--o{ NATIONAL_PARK : found_in

USER ||--|| USER_PROFILE : owns

USER_PROFILE ||--o{ USER_COLLECTION : collects
USER_PROFILE ||--o{ WILDLIFE_SIGHTING : reports

SPECIES ||--o{ USER_COLLECTION : unlocked
SPECIES ||--o{ WILDLIFE_SIGHTING : observed
SPECIES ||--o{ AI_PREDICTION : predicted

NATIONAL_PARK ||--o{ WILDLIFE_SIGHTING : location
```

---

# Legend

| Symbol | Meaning |
|---------|----------|
| `||` | Exactly One |
| `o{` | Zero or Many |
| `}|` | One or Many |
| `}o--o{` | Many-to-Many |

---

# Status

- ✅ Database Planning
- ✅ ER Diagram
- ⏳ Django Models
- ⏳ Admin Panel
- ⏳ Migrations
- ⏳ Sample Data
- ⏳ REST API
- ⏳ AI Integration