---
name: invoice-skill
description: Generate an invoice summary PowerPoint (one image per slide) from local invoice images and optionally export PDF. Use when users ask to batch place invoice images into slides, organize invoices by person folder, or produce reimbursement-ready PPT/PDF outputs.
---

# Invoice Skill

Generate reimbursement slides from local images in this folder.

## Run Workflow

1. Install dependencies with `pip install -r requirements.txt`.
2. Place invoice images under `input/`.
3. Run `python3 run.py` to generate `output/发票汇总.pptx`.
4. Add `--pdf` when PDF export is required.

## Supported Input Layouts

- `input/<person>/*.png`
- `input/<group>/<person>/*.png`
- `input/<category>/<project>/<person>/*.png` (recursively auto-detected)
- `input/*.png` (copied to a temporary processing folder without moving originals)

## Operational Rules

- Return non-zero exit code when no slides are generated.
- Verify invoice count against generated slide count; fail fast on mismatch.
- Use `soffice` from `PATH` for PDF conversion; fallback to macOS default LibreOffice path.
- Keep source images unchanged during processing.
