# Protected area catalogue

`protected_areas.json` contains the names and state or union territory for 106
national parks and 574 wildlife sanctuaries. The counts match the Wildlife
Institute of India's published protected-area totals. The names are transcribed
from the [state-wise protected-area list](https://wildlifesafaris.in/list-of-national-parks-and-wildlife-sanctuaries/),
which attributes its sanctuary list to the WII National Wildlife Database
(February 2025) and its national park list to WII and government sources
(August 2026).

The source list does not provide a complete, consistent set of areas, opening
details, species, or coordinates. Those fields are left blank in the app rather
than filled with guesses. Please check current notifications with the relevant
state forest department before treating this as an official operational
directory; protected-area names and status can change.

To load these records after applying migrations, run:

```powershell
python manage.py seed_protected_areas
```

The command can be run more than once. It adds missing records and keeps
existing descriptions, photos, and other administrator-entered details.
