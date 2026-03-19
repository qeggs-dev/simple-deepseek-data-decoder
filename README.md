# DeepSeek Data Decoder

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: CC0 1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

一个用于解码 DeepSeek 导出数据的工具，将 JSON 格式的聊天数据转换为结构化的 Markdown 文件。

## 📖 简介

DeepSeek Data Decoder 可以将 DeepSeek 平台导出的数据（ZIP 文件）转换为易于阅读和管理的 Markdown 文件。它会将会话树拆分为多条独立的路径，每条路径生成一个 Markdown 文件，支持自定义输出格式和文件名模板。

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/deepseek-data-decoder.git
cd deepseek-data-decoder

# 安装依赖
pip install -r requirements.txt
```

### 使用方法

```bash
python deepseek_data_decoder.py -i <input.zip> -f <format_package.zip> -o <output_dir>
```

#### 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--input` | `-i` | 输入的 DeepSeek 数据 ZIP 文件 | 必填 |
| `--format` | `-f` | 格式模板包 ZIP 文件 | 必填 |
| `--output` | `-o` | 输出目录 | 必填 |
| `--file-name` | `-fn` | 文件名模板 | `{{file_name}}` |
| `--dir-name` | `-dn` | 目录名模板 | `{{dir_name}}` |

### 示例

```bash
python deepseek_data_decoder.py \
  -i ./data/deepseek_export.zip \
  -f ./templates/default_format.zip \
  -o ./output \
  -fn "{{file_name}}" \
  -dn "{{dir_name}}"
```

## 📦 格式模板包

格式模板包是一个 ZIP 文件，包含以下 Markdown 模板文件：

| 文件 | 说明 |
|------|------|
| `session.md` | 会话主模板 |
| `node.md` | 节点模板 |
| `message.md` | 消息模板 |
| `file.md` | 文件模板 |
| `user_input.md` | 用户输入模板 |
| `read_link.md` | 阅读链接模板 |
| `search.md` | 搜索结果模板 |
| `search_unit.md` | 单个搜索结果模板 |
| `thinking.md` | 思考过程模板 |
| `ai_answer.md` | AI 回答模板 |

每个模板使用 Jinja2 语法，可以访问相应的数据模型。

## 🏗️ 项目结构

```
deepseek_data_decoder/
├── __init__.py          # 模块入口
├── core.py              # 核心解码器
├── format_pkg.py        # 格式包数据模型
├── load_format_package.py # 加载格式包
├── models.py            # 数据模型定义
├── parser.py            # 会话解析器
├── parse_args.py        # 命令行参数解析
└── deepseek_data_decoder.py # 主入口脚本
```

## 📄 许可证

CC0 1.0 通用 (CC0 1.0) 公共领域贡献

本项目采用 CC0 1.0 通用 许可证。任何人可以随意将本项目用于任何目的，无需任何限制，也无需注明原作者。

> 在法律允许的范围内，作者已将本项目贡献至公共领域，放弃所有在全球范围内基于版权法对该作品享有的权利。您可以复制、修改、发行和使用本作品，甚至用于商业目的，都无需征得许可。

详情请参阅 [https://creativecommons.org/publicdomain/zero/1.0/legalcode](https://creativecommons.org/publicdomain/zero/1.0/legalcode)

[查看完整的许可证文本](https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt)或该仓库存储的副本[LICENSE](LICENSE)

*PS: CC0 生效范围仅限于本实现，第三方仓库与 Deepseek 的数据格式版权不在此范围内。*