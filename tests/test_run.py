from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import create_invoice_ppt
import run


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc`\x00\x00"
    b"\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
)


def write_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(PNG_1X1)


def test_discover_layout_person_dirs(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    write_png(input_dir / "alice" / "invoice.png")

    root, persons = run.discover_input_layout(input_dir)

    assert root == input_dir
    assert persons == ["alice"]


def test_discover_layout_group_person_dirs(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    write_png(input_dir / "PPT贴发票" / "alice" / "invoice.png")

    root, persons = run.discover_input_layout(input_dir)

    assert root == input_dir
    assert persons == [str(Path("PPT贴发票") / "alice")]


def test_discover_layout_three_level_project_dirs(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    write_png(input_dir / "PPT贴发票" / "20260128-0210新高阶拍摄" / "alice" / "invoice.png")

    root, persons = run.discover_input_layout(input_dir)

    assert root == input_dir
    assert persons == [str(Path("PPT贴发票") / "20260128-0210新高阶拍摄" / "alice")]


def test_discover_layout_top_level_images_copy_not_move(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    image = input_dir / "invoice.png"
    write_png(image)

    root, persons = run.discover_input_layout(input_dir)

    assert root == input_dir
    assert persons == [run.STAGING_PERSON]
    assert image.exists()
    assert (input_dir / run.STAGING_PERSON / "invoice.png").exists()


def test_count_expected_invoices(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    write_png(input_dir / "proj" / "alice" / "a.png")
    write_png(input_dir / "proj" / "alice" / "b.png")
    write_png(input_dir / "proj" / "bob" / "c.png")

    _, persons = run.discover_input_layout(input_dir)
    assert run.count_expected_invoices(input_dir, persons) == 3


def test_run_main_empty_input_returns_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir(parents=True)
    monkeypatch.setattr(run, "OUTPUT", tmp_path / "output")
    monkeypatch.setattr(sys, "argv", ["run.py", "--input-root", str(input_dir), "--output-name", "x.pptx"])

    assert run.main() == 1


def test_run_main_zero_slides_returns_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_dir = tmp_path / "input"
    person_dir = input_dir / "alice"
    person_dir.mkdir(parents=True)
    (person_dir / "note.txt").write_text("not an image", encoding="utf-8")
    monkeypatch.setattr(run, "OUTPUT", tmp_path / "output")
    monkeypatch.setattr(sys, "argv", ["run.py", "--input-root", str(input_dir), "--output-name", "x.pptx"])

    assert run.main() == 1


def test_run_main_single_group_layout_succeeds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_dir = tmp_path / "input"
    write_png(input_dir / "PPT贴发票" / "alice" / "invoice.png")
    output_dir = tmp_path / "output"
    monkeypatch.setattr(run, "OUTPUT", output_dir)
    monkeypatch.setattr(sys, "argv", ["run.py", "--input-root", str(input_dir), "--output-name", "ok.pptx"])

    assert run.main() == 0
    assert (output_dir / "ok.pptx").exists()


def test_run_main_count_mismatch_returns_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_dir = tmp_path / "input"
    write_png(input_dir / "PPT贴发票" / "alice" / "invoice.png")
    output_dir = tmp_path / "output"
    monkeypatch.setattr(run, "OUTPUT", output_dir)
    monkeypatch.setattr(sys, "argv", ["run.py", "--input-root", str(input_dir), "--output-name", "bad.pptx"])
    monkeypatch.setattr(create_invoice_ppt, "create_ppt", lambda *_args, **_kwargs: 2)

    assert run.main() == 1


def test_convert_to_pdf_without_soffice_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(create_invoice_ppt.shutil, "which", lambda _: None)
    monkeypatch.setattr(create_invoice_ppt.os.path, "exists", lambda _: False)

    assert create_invoice_ppt.convert_to_pdf("a.pptx", ".") is False
