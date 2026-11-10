# Daily Wellness Notes

Pinterest affiliate editorial site published at https://dailywellnessnotes.github.io/notes/.

## Current batch

- 42 distinct 1000 × 1500 JPG pins, scheduled over seven days in America/New_York time.
- Three boards: Glow Skin Routine Ideas, Healthy Hair Care Tips, Calm Evening Rituals.
- Nine original articles, three per product, with visible affiliate disclosure and supplement disclaimer.
- Pins link to articles, never directly to affiliate destinations.
- `gecmis.json` is append-only. It records pin metadata, image hashes, prompts, destinations, and CSV files.

## Next batch

1. Read `gecmis.json`; begin the day after the latest scheduled date.
2. Create 42 new concepts and separate original image generations. Do not reuse a theme for the same product within seven days, a near-duplicate heading or scene, any description, or an image hash.
3. Put new specifications in `pin_specs.json` and source PNG paths in the untracked `asset_sources.json`.
4. Run `python build_site.py` if articles change, then `python assemble_batch.py`. For an empty history only, pass `--first-date YYYY-MM-DD`.
5. Commit and push images, pages, and `gecmis.json`. Wait for GitHub Pages.
6. Run `python publish_csv.py`. It refuses to write the CSV unless all article and image URLs return the expected content type. Commit and push the CSV.

The Pinterest CSV is also copied to `C:\Users\ik_ej\Documents\pinterest-csv`.
