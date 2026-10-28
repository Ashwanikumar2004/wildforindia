# Catalogue content and photographs

`protected_areas.json` records the source and dates of the 106 national parks
and 574 wildlife sanctuaries in this project's directory. This snapshot is not
a live official register. Similar names in different states represent separate
directory records.

`species_catalogue.json` contains researched species descriptions and source
links. The `seed_species_catalogue` command creates additional species and fills
empty biological details on the original six records. It preserves existing
species edits, AI labels, confidence thresholds and discovery history.

`catalogue_media.json` contains the source article, retrieval date, image author,
license and source file page for cached media. Short Wikipedia introduction
excerpts retain their attribution and CC BY-SA 4.0 license. Photographs retain
the individual license recorded beside each image. Images are resized and
encoded as WebP; card layouts may crop them for display. The About page and
individual detail pages display credits.

The media import uses matching Wikipedia article titles/redirects and checks
state context for protected areas. A missing match is left as an illustration;
it is never substituted with a photograph of a different protected area.
Imported coordinates are approximate display points, not gates or surveyed
boundaries. Sources should be reviewed before using these data for research.

To resume interrupted downloads:

```powershell
.\.venv\Scripts\python.exe manage.py download_catalogue_media
```

To retry entries that did not have a downloadable image:

```powershell
.\.venv\Scripts\python.exe manage.py download_catalogue_media --retry-missing
```

This is an optional maintenance command. Visitors' requests never initiate
downloads. Commit `catalogue_media.json` and `static/images/catalogue/` together.
Uploaded user photos remain in private storage and must not be committed.
