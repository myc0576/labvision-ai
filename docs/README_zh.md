# LabVision AI 中文说明

LabVision AI 当前是一个可公开浏览、安装和测试的 MIT 开源核心包。这个版本不包含 AI 功能，只提供经过测试的通用实验图像处理能力：图像读取、预处理、归一化、ROI 裁剪、伪彩色、叠加图、三联图、运行清单和 Markdown 摘要。

## 范围

- 导入包名：`labvision`。
- 本地构建包名：`labvision-ai`。
- 顶层 API 只导出稳定核心入口。
- 领域专用工作流、论文图排版导出、托管 AI、付费授权、包索引上传均暂缓。
- 示例只使用合成数据，不提交真实实验数据或生成产物。

## 安装

```powershell
python -m pip install .
python -m pip install .[image,viz]
python -m pip install .[all,dev]
```

## 本地验证

```powershell
python -m pip install -e .[all,dev]
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest
python scripts/check_import_boundaries.py
python -m compileall -q src tests examples scripts
powershell -ExecutionPolicy Bypass -File scripts/run_examples.ps1
python -m build
```

示例脚本位于 `examples/`，均支持 `--output-dir` 指定输出目录。
