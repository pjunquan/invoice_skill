from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import create_sheet_ppt as sheet
import run


def write_image(path: Path, width: int, height: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (width, height), "white").save(path)
    return path


def test_choose_layout_grid_for_tall_screenshots(tmp_path: Path) -> None:
    images = [write_image(tmp_path / f"s{i}.png", 1080, 2400) for i in range(3)]
    assert sheet.choose_layout(images) == "grid"


def test_choose_layout_pairs_for_landscape_invoices(tmp_path: Path) -> None:
    images = [write_image(tmp_path / f"i{i}.png", 990, 660) for i in range(3)]
    assert sheet.choose_layout(images) == "pairs"


def test_grid_packs_six_per_page(tmp_path: Path) -> None:
    images = [write_image(tmp_path / f"s{i}.png", 1080, 2400) for i in range(7)]
    slides, placed = sheet.build_deck(images, tmp_path / "out.pptx", "tester")
    assert placed == 7
    assert slides == 2


def test_pairs_stack_two_per_page(tmp_path: Path) -> None:
    images = [write_image(tmp_path / f"i{i}.png", 990, 660) for i in range(4)]
    slides, placed = sheet.build_deck(images, tmp_path / "out.pptx", "tester")
    assert placed == 4
    assert slides == 2


def test_portrait_invoice_gets_its_own_page(tmp_path: Path) -> None:
    images = [
        write_image(tmp_path / "a.png", 990, 660),
        write_image(tmp_path / "b.png", 700, 990),  # 竖版，应独占一页
        write_image(tmp_path / "c.png", 990, 660),
    ]
    slides, placed = sheet.build_deck(images, tmp_path / "out.pptx", "tester", layout="pairs")
    assert placed == 3
    assert slides == 3


def test_manifest_page_is_appended(tmp_path: Path) -> None:
    images = [write_image(tmp_path / "a.png", 990, 660)]
    manifest = {
        "headers": ["序号", "金额"],
        "widths": [1.0, 1.0],
        "rows": [["1", "47.50"]],
        "footer": ["合计", "47.50"],
    }
    slides, placed = sheet.build_deck(images, tmp_path / "out.pptx", "tester", manifest=manifest)
    assert placed == 1
    assert slides == 2


def test_load_captions_maps_filename_to_lines(tmp_path: Path) -> None:
    csv_path = tmp_path / "captions.csv"
    csv_path.write_text("a.png,No01 ¥47.50,08-19 顺丰寄件\n", encoding="utf-8-sig")
    assert sheet.load_captions(csv_path) == {"a.png": ["No01 ¥47.50", "08-19 顺丰寄件"]}


def test_run_main_sheet_layout_emits_one_deck_per_person(tmp_path: Path, monkeypatch) -> None:
    input_dir = tmp_path / "input"
    for i in range(3):
        write_image(input_dir / "alice" / f"s{i}.png", 1080, 2400)
    write_image(input_dir / "bob" / "s0.png", 1080, 2400)
    output_dir = tmp_path / "output"
    monkeypatch.setattr(run, "OUTPUT", output_dir)
    monkeypatch.setattr(sys, "argv", ["run.py", "--input-root", str(input_dir), "--layout", "sheet"])

    assert run.main() == 0
    assert (output_dir / "alice.pptx").exists()
    assert (output_dir / "bob.pptx").exists()
