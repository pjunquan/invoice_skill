# invoice_skill

本工具用于把发票图片批量贴到 PPT（每张图片一页），可选导出 PDF。

## 目录结构

- `input/`：本地待处理图片目录（默认不入库）。
- `output/`：生成的 PPT/PDF（默认不入库）。
- `examples/`：脱敏示例数据，可用于冒烟测试。
- `run.py`：一键入口。
- `create_invoice_ppt.py`：一图一页版式。
- `create_sheet_ppt.py`：A4 多图一页版式（按图片方向自动排布）。
- `scripts/quick_validate.py`：`SKILL.md` 快速校验。
- `scripts/block_sensitive_paths.py`：pre-commit 提交防呆。
- `tests/`：pytest 自动化测试。

## 输入结构

支持以下三种结构：

1. `input/<姓名>/<图片>`
2. `input/<分组>/<姓名>/<图片>`
3. `input/<图片>`（复制到临时目录处理，不移动原文件）
4. `input/<大类>/<项目>/<姓名>/<图片>`（会自动递归识别到“姓名目录”）

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python3 run.py
```

可选参数：

- `python3 run.py --pdf`：同时导出 PDF（需 LibreOffice / `soffice`）。
- `python3 run.py --input-root <path>`：指定输入目录。
- `python3 run.py --output-name <name>.pptx`：自定义输出文件名。
- `python3 run.py --layout sheet`：A4 多图一页，并且**每个人单独出一册**。
- `python3 run.py --layout sheet --captions <file>.csv`：给每张图加标注。

运行时会自动做数量校验：`single` 版式校验 `发票数 == 生成页数`，`sheet` 版式校验 `发票数 == 已贴图片数`，不符则返回非 0 并报错。

## 两种版式

| | `single`（默认） | `sheet` |
|---|---|---|
| 页面 | 10×7.5in | A4 |
| 每页 | 1 张 | 竖版 6 张（3×2）／横版 2 张（上下） |
| 标题 | 完整文件名 | 页眉 + 每图下方标注 |
| 输出 | 全部人合成一个文件 | 每人一册 |

`sheet` 的排布是**按宽高比自动决定**的，不用手工指定：

- 竖版手机截图受限于高度，横排三列并不会让单张变小，所以排 3×2；
- 横版发票受限于宽度，上下两张同样不会变小，所以排 1×2；
- 夹在横版里的竖版图（例如几十行商品明细的超市发票）会**独占整页**，否则明细会糊掉。

### 标注 CSV 格式

第一列是文件名，其余列依次作为该图下方的标注行：

```csv
20260903_No06_34.30元_晚餐.png,No06　¥34.30,09-03　IP老师晚餐,真票1·商品餐费
```

### 单独调用版式引擎

```bash
python3 create_sheet_ppt.py <图片文件夹> --output out.pptx --captions captions.csv
```

## 发布安全

- 不要把真实发票或个人信息提交到仓库。
- `input/`、`output/`、`__pycache__/` 已在 `.gitignore` 中忽略。
- 提交前建议启用 pre-commit 防呆：

```bash
pip install pre-commit
pre-commit install
```

启用后会拦截：

- `input/`、`output/`、`__pycache__/` 下文件
- `.pyc` 文件
- 非 `examples/` / `assets/` 目录下的图片与 PDF

## 自动化校验

本地执行：

```bash
python3 scripts/quick_validate.py .
python3 -m py_compile run.py create_invoice_ppt.py scripts/quick_validate.py scripts/block_sensitive_paths.py
pytest -q
```

GitHub Actions 已配置同等 CI 校验：`.github/workflows/ci.yml`。
