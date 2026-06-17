# podcast-extended-reading

> Turn one podcast episode into anchored, source-linked, cross-domain knowledge units organized around your own way of thinking.

`podcast-extended-reading` 的目的是让我像向量数据库一样去思考跨领域的问题，找出多领域的共同点，构建自己的知识树干，以下readme由AI生成

## Why

普通播客笔记常见的问题是：

- 只有摘要，没有原文锚点
- 有观点，没有来源分层
- 有延伸阅读，但和播客原文的桥接关系不清楚
- 有一些“相关内容”，但无法稳定进入长期知识库

这个 skill 的目的，是把播客内容变成更像“可持续积累的思维单元”：

- 有原文抓手
- 有来源链接
- 有研究拆解
- 有跨领域桥接
- 有统一结构，方便切块、召回、关联和二次扩写

## At A Glance

| Stage | What happens |
| --- | --- |
| Input | Xiaoyuzhou 链接、音频、转录稿、ASR JSON |
| Anchor | 从原文中提取 `4-8` 个高价值抓手 |
| Expand | 围绕播客主题做第一轮高置信度延展阅读 |
| Link | 按指定领域做第二轮跨领域连接 |
| Structure | 输出统一字段，贴近你的思考方式，也兼容后续向量化检索 |

## What It Produces

每一条输出都尽量保持为一个结构化知识单元，而不是松散笔记。常见字段包括：

- 原播客锚点
- 原文短引
- 主题标题
- 来源链接
- 核心问题
- 假设 / 方法 / 结果 / 局限性
- 关键数据
- 关键图表
- `研究本质`
- `哲学式启发`
- 跨领域桥接理由

这类结构的价值在于：

- 语义更完整：不只保留结论，还保留条件、证据和反驳对象
- 联想更自然：更容易围绕你关心的问题、对比方式和思路路径继续展开
- 检索更稳定：可以按主题、问题、学科、案例、方法或原文触发点召回

## Core Features

- 从 Xiaoyuzhou 或其他播客内容中提取带原文锚点的知识抓手
- 对播客主题做第一轮高置信度延展阅读
- 对指定外部领域做第二轮跨领域 linking
- 对论文做结构化拆解：
  - 假设
  - 实验 / 方法
  - 结果
  - 驳斥或修正了什么观点
  - 局限性
  - 置信度
- 为每条新内容补充：
  - `研究本质`
  - `哲学式启发`
  - `关键数据`
  - `关键图表`
- 在初学者模式下提供更适合复杂知识入门的解释顺序与类比
- 支持自动从 PDF 中抽取关键图表，帮助快速理解论文证据

## Workflow

1. 准备播客内容  
   输入 Xiaoyuzhou 链接、音频、转录稿或 ASR JSON。

2. 提取原文锚点  
   从播客中抽出 `4-8` 个真正值得延展的抓手，每个抓手尽量包含标题、位置、短引和重要性说明。

3. 第一轮延展阅读  
   围绕播客本身的核心问题，优先找高置信度来源：
   - 论文
   - 官方机构材料
   - 历史档案
   - 高置信度报道
   - 可溯源文章或书籍入口

4. 第二轮跨领域连接  
   把播客内容 link 到外部领域，例如神经科学、认知科学、行为经济学、消费者心理、量化交易、历史或技术史。

5. 提取关键证据  
   如果来源里有决定理解的数字、对比或图表，就单独抽出来，而不是埋在解释段落里。

6. 输出成统一格式  
   最终结果适合导入 Obsidian、做跨笔记召回、继续扩写，也方便未来接入 embedding 或向量化检索体系。

## Typical Use Cases

- 想把播客变成长期可检索的知识资产
- 想围绕一段播客内容做高质量延展阅读
- 想系统地建立跨领域知识连接
- 想把笔记整理成更贴近自己思考模式、同时适合 embedding 和召回的结构
- 想让知识积累更像“可被联想和检索的思维网络”，而不是只堆积零散收藏

## Quick Start

把这个目录放到：

```bash
~/.codex/skills/podcast-extended-reading
```

然后在 Codex 中使用类似请求：

```text
Use $podcast-extended-reading to turn this podcast into anchored extended reading, then link it to neuroscience in beginner mode.
```

如果你处理的是 Xiaoyuzhou 链接，这个 skill 会先复用转录流程，再继续做延展阅读和跨领域 linking。

## Repository Layout

- `SKILL.md`: 主技能说明
- `agents/openai.yaml`: skill 的入口配置
- `references/source-ladder.md`: 来源分层与置信度规则
- `references/output-template.md`: 默认输出模板
- `references/novice-explanation-patterns.md`: 初学者解释模式
- `references/visual-evidence.md`: 关键数据与图表规则
- `scripts/extract_key_figures.py`: 自动抽取论文图表的脚本

## Design Goal

这个 skill 服务的不是“一次性的阅读体验”，而是“长期可复用的个人思维基础设施”。

它希望你最后积累下来的，不只是“听过什么”，而是：

- 哪些问题值得继续挖
- 哪些学科会给出不同解释
- 哪些观点彼此冲突
- 哪些内容值得进入长期知识库

它更像是在帮你慢慢长出一套围绕自己问题意识、判断路径和联想方式的知识网络。  
如果未来你要把这些内容接到向量数据库，那会很顺；但这个 skill 本身的重点，始终是思考结构，而不是数据库工程。

## Notes

- 图表抽取脚本会在第一次运行时自动安装本地依赖
- `scripts/_vendor/` 是脚本运行时生成的本地依赖目录，不应提交到仓库
- 这个 skill 的重点不是“尽量多列资料”，也不是“真的去建数据库”，而是把资料组织成长期可复用、贴近你思考方式的知识结构
