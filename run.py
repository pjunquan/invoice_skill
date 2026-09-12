#!/usr/bin/env python3
"""轻量运行器：把 `invoice_skill/input` 下的发票处理成 PPT，结果放到 `invoice_skill/output` """

import argparse
import shutil
from pathlib import Path
import sys

BASE = Path(__file__).parent
INPUT = BASE / "input"
OUTPUT = BASE / "output"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}
STAGING_PERSON = "__TOP_LEVEL_IMAGES__"


def is_image_file(path: Path) -> bool:
    return path.is_file() and (not path.name.startswith(".")) and path.suffix.lower() in IMAGE_EXTENSIONS


def has_hidden_part(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    return any(part.startswith(".") for part in rel.parts)


def discover_person_dirs(input_dir: Path) -> list[str]:
    persons: list[str] = []
    for directory in sorted(input_dir.rglob("*")):
        if not directory.is_dir():
            continue
        if directory.name == STAGING_PERSON:
            continue
        if has_hidden_part(directory, input_dir):
            continue
        if any(is_image_file(p) for p in directory.iterdir()):
            persons.append(str(directory.relative_to(input_dir)))
    return persons


def discover_input_layout(input_dir: Path) -> tuple[Path, list[str]]:
    entries = [p for p in sorted(input_dir.iterdir()) if not p.name.startswith(".")]
    image_files = [p for p in entries if is_image_file(p)]
    persons = discover_person_dirs(input_dir)

    # 顶层直接放图片时，复制到临时目录处理，避免修改原始输入结构。
    if image_files:
        staging_dir = input_dir / STAGING_PERSON
        staging_dir.mkdir(exist_ok=True)
        for existing in staging_dir.iterdir():
            if is_image_file(existing):
                existing.unlink()
        for src in image_files:
            shutil.copy2(src, staging_dir / src.name)
        persons.append(STAGING_PERSON)

    return input_dir, sorted(set(persons))


def count_person_images(input_root: Path, person_dir: str) -> int:
    folder = input_root / person_dir
    if not folder.is_dir():
        return 0
    return sum(1 for p in folder.iterdir() if is_image_file(p))


def count_expected_invoices(input_root: Path, persons: list[str]) -> int:
    return sum(count_person_images(input_root, person_dir) for person_dir in persons)


def run_sheet_layout(input_root: Path, persons: list[str], captions_csv: str | None, page: str) -> tuple[int, list[Path]]:
    """每个人单独出一册，按图片方向自动排版。返回 (已贴图片数, 输出文件列表)。"""
    from create_sheet_ppt import build_deck, list_images, load_captions

    captions = load_captions(captions_csv) if captions_csv else {}
    placed_total = 0
    outputs: list[Path] = []
    for person_dir in persons:
        images = list_images(input_root / person_dir)
        if not images:
            continue
        name = Path(person_dir).name
        output_path = OUTPUT / f"{name}.pptx"
        slides, placed = build_deck(images, output_path, name, captions=captions, page=page)
        placed_total += placed
        outputs.append(output_path)
        print(f"已生成: {output_path.name}（{placed} 张图片 / {slides} 页）")
    return placed_total, outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="处理 invoice_skill/input 并在 output 中生成 PPT")
    parser.add_argument("--input-root", default=str(INPUT), help="输入目录，默认使用 invoice_skill/input")
    parser.add_argument("--pdf", action="store_true", help="同时生成 PDF（需 LibreOffice）")
    parser.add_argument("--output-name", default="发票汇总.pptx", help="输出文件名（放在 output 文件夹）")
    parser.add_argument(
        "--layout",
        choices=["single", "sheet"],
        default="single",
        help="single=一图一页汇总成一个文件；sheet=按图片方向多图一页，每人单独一册",
    )
    parser.add_argument("--captions", help="sheet 版式的标注 CSV：文件名,第一行,第二行,...")
    parser.add_argument("--page", default="A4", help="sheet 版式的页面尺寸，默认 A4")
    args = parser.parse_args()

    input_dir = Path(args.input_root).expanduser().resolve()
    if not input_dir.exists():
        print(f"请先创建输入文件夹并放入图片：{input_dir}", file=sys.stderr)
        return 1
    OUTPUT.mkdir(parents=True, exist_ok=True)

    input_root, persons = discover_input_layout(input_dir)
    if not persons:
        print(f"未在 {input_dir} 下发现可处理的图片或人员子目录", file=sys.stderr)
        return 1

    # 调用处理脚本（位于同一文件夹）
    sys.path.insert(0, str(BASE))
    from create_invoice_ppt import create_ppt, convert_to_pdf

    expected_count = count_expected_invoices(input_root, persons)

    if args.layout == "sheet":
        placed, outputs = run_sheet_layout(input_root, persons, args.captions, args.page)
        if not outputs:
            print("未生成任何册子，请检查输入目录结构或图片格式", file=sys.stderr)
            return 1
        if placed != expected_count:
            print(f"数量校验失败：目标发票数={expected_count}，已贴图片数={placed}", file=sys.stderr)
            return 1
        print(f"数量校验通过：目标发票数={expected_count}，已贴图片数={placed}")
        if args.pdf:
            for output_path in outputs:
                if not convert_to_pdf(str(output_path), str(OUTPUT)):
                    return 1
        print(f"输出文件位于: {OUTPUT}")
        return 0

    output_path = OUTPUT / args.output_name
    slide_count = create_ppt(str(input_root), persons, str(output_path))
    if slide_count == 0:
        print("未生成任何幻灯片，请检查输入目录结构或图片格式", file=sys.stderr)
        return 1
    if slide_count != expected_count:
        print(
            f"数量校验失败：目标发票数={expected_count}，生成幻灯片数={slide_count}",
            file=sys.stderr,
        )
        return 1
    print(f"数量校验通过：目标发票数={expected_count}，生成幻灯片数={slide_count}")

    if args.pdf:
        if not convert_to_pdf(str(output_path), str(OUTPUT)):
            return 1

    print(f"输出文件位于: {output_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
