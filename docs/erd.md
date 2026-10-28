# WildFIndia database relationships

This diagram describes the implemented application. Django's built-in User
model owns private identification history and journal entries. Wildlife and
protected-area records form the public catalogue.

```mermaid
erDiagram
    USER ||--o{ IDENTIFICATION : uploads
    IDENTIFICATION ||--o{ IDENTIFICATION_RESULT : returns
    SPECIES o|--o{ IDENTIFICATION_RESULT : matches
    USER ||--o{ WILDDEX_ENTRY : owns
    SPECIES ||--o{ WILDDEX_ENTRY : records
    IDENTIFICATION o|--o{ WILDDEX_ENTRY : source
    CATEGORY ||--o{ SPECIES : categorises
    CONSERVATION_STATUS ||--o{ SPECIES : describes
    SPECIES }o--o{ HABITAT : inhabits
    SPECIES ||--o{ SPECIES_IMAGE : illustrates
    SPECIES ||--o{ SPECIES_SOUND : records
    SPECIES ||--o{ SPECIES_DISTRIBUTION : occurs
    STATE ||--o{ SPECIES_DISTRIBUTION : contains
    STATE ||--o{ NATIONAL_PARK : contains
    NATIONAL_PARK }o--o{ SPECIES : records
    NATIONAL_PARK }o--o{ PARK_FACILITY : offers
    NATIONAL_PARK ||--o{ PARK_IMAGE : illustrates
    NATIONAL_PARK ||--o{ PARK_ROUTE : accesses
    NATIONAL_PARK ||--o{ PARK_REVIEW : receives
    USER o|--o{ PARK_REVIEW : submits

    WILDDEX_ENTRY {
        bigint id PK
        bigint user_id FK
        uuid species_id FK
        bigint source_identification_id FK
        datetime discovered_at
        date observed_on
        string location
        text notes
    }
    PARK_REVIEW {
        uuid id PK
        uuid park_id FK
        bigint user_id FK
        string reviewer_name
        smallint rating
        text review
        date visit_date
        boolean is_verified
    }
    IDENTIFICATION_RESULT {
        bigint id PK
        bigint identification_id FK
        uuid species_id FK
        string label
        float score
        smallint rank
    }
```

- A user can have one WildDex entry per species. XP is calculated from entries,
  so confirming the same species twice does not award extra XP.
- A user can submit one review per park. Reviews remain private until moderated.
- Deleting an identification leaves the WildDex entry and clears its source link.
- A prediction may have no matching species in the curated catalogue.
- A species/state combination has one distribution record.
- A protected area's name, state and type together identify its directory record.
- Catalogue photos downloaded for the project are static assets. Their source
  metadata is in `datasets/catalogue_media.json`; user/admin uploads use the
  relevant database image fields.
