---
name: invoice-skill
description: Generate reimbursement PowerPoint decks from local invoice and payment-screenshot images, one image per slide or auto-packed multiple per A4 page, and optionally export PDF. Use when users ask to batch place invoice images into slides, organize invoices by person folder, add a per-deck manifest page, or produce reimbursement-ready PPT/PDF outputs.
---

# Invoice Skill

Generate reimbursement slides from local images in this folder.

## Run Workflow

1. Install dependencies with `pip install -r requirements.txt`.
2. Place invoice images under `input/`.
3. Run `python3 run.py` to generate `output/发票汇总.pptx`.
4. Add `--pdf` when PDF export is required.
5. Add `--layout sheet` to pack several images per A4 page and emit one deck per person.

## Supported Input Layouts

- `input/<person>/*.png`
- `input/<group>/<person>/*.png`
- `input/<category>/<project>/<person>/*.png` (recursively auto-detected)
- `input/*.png` (copied to a temporary processing folder without moving originals)

## Layout Modes

- `single` (default): one image per slide on a 10x7.5in page, slide title is the file name.
- `sheet`: A4 pages, layout chosen from image aspect ratio. Tall screenshots go into a 3x2 grid;
  landscape invoices are stacked two per page; a portrait image among landscape ones takes a full
  page so dense line items stay readable. Emits one deck per person folder.

## Operational Rules

- Return non-zero exit code when no slides are generated.
- Verify invoice count against generated slide count (`single`) or placed image count (`sheet`); fail fast on mismatch.
- Use `soffice` from `PATH` for PDF conversion; fallback to macOS default LibreOffice path.
- Keep source images unchanged during processing.
