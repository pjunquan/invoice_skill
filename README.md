# invoice_skill

本工具用于把发票图片批量贴到 PPT（每张图片一页），可选导出 PDF。

## 目录结构

- `input/`：本地待处理图片目录（默认不入库）。
- `output/`：生成的 PPT/PDF（默认不入库）。
- `examples/`：脱敏示例数据，可用于冒烟测试。
- `run.py`：一键入口。
- `create_invoice_ppt.py`：核心逻辑。
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

运行时会自动做数量校验：`目标目录发票数` 必须等于 `生成PPT页数`，否则返回非 0 并报错。

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
