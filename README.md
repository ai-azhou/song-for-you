# 只属于你的歌 · song-for-you

## 能做什么

帮你从歌单、歌手、一个题目、一件想写的事或自己写的歌词出发，写出一首完整的歌：定立意和结构，写词和风格说明，最后给出 Suno、海绵音乐能直接粘贴的提示词，告诉你下一步怎么用。你出了歌回来说哪里不对，它帮你改提示词。

它只做到提示词为止：不安装、不运行任何生成模型，歌在你自己选的工具里生成。

## 两种用法

- **Skill**（推荐）：装进 Claude Code、Codex 这类能在你电脑上干活的 AI 助手（Agent），它会按你给的东西一步步问、一步步写。
- **网页版**：不装任何东西，把 [`prompt-standalone.md`](prompt-standalone.md) 里的提示词粘进 DeepSeek、Kimi、豆包、千问这类网页 AI，最后一行写你手上有的东西。

提示词不等于 Skill：网页版只有一段话；Skill 版带着完整的写词规则、写歌说明和导出脚本，效果更稳。

## 安装

把这句话发给你的 Agent，它会自己装好：

```text
帮我装上 song-for-you 这个 Skill：https://github.com/ai-azhou/song-for-you
```

也可以自己在终端装：

```bash
npx skills add ai-azhou/song-for-you
```

- 加 `-g` 装到全局，所有项目都能用。
- 加 `-a claude-code`（或 `codex`、`cursor`、`gemini-cli` 等）只装给指定的 AI 助手。

## 用法

装好以后直接对它说，例如：

- 「这是我的歌单截图，照我的口味写首歌。」
- 「写首歌送我妈，她今年退休。」
- 「帮这段歌词做成歌：……」

没说「你定」时，它先给 2–3 个方向让你选，选好再写词；想省事就回「你定」。

## 它不会做的事

- 不假装听过歌。它听不到音频，口味是凭它对歌手的了解、查到的描述和你的话写的。
- 生成用的标题、风格和歌词里不出现真实歌手名、乐队名和歌名，不抄、不化用别人的歌词，不模仿任何人的声音。
- 不承诺这首歌能火、能赚钱。交付时会提醒你：发出去之前按所在地规定和平台要求标注 AI 生成；工具允许使用不等于拥有独占版权。

## 你会拿到什么

- **写歌说明**（JSON）：立意、结构、歌词、风格都在里面。后面要改，就从它改。格式见 `skills/song-for-you/references/brief-format.md`。
- **粘贴稿**：Suno 的 Title、Styles、Exclude、人声和完整歌词，附 Custom 模式的操作步骤；海绵音乐的中文风格描述和完整歌词。

## 粘贴稿

```bash
python3 skills/song-for-you/scripts/to_suno.py 写歌说明.json --out Suno-粘贴.md
```

只用 Python 3.11 以上的标准库。按写歌说明的首数导出，操作步骤跟着歌词语言切换中文或英文。选项名称和费用以 Suno 界面为准。

导出前先校验语言代码和段落标签（以 `references/writing.md` 的表为准）。标签行 `]` 后面有字时默认拒绝，加 `--fix` 会把提示搬进方括号，只改这一次，不覆盖原 JSON。`fixed_lines` 每一句都要一字不差地在歌词里。段落表和歌词对不上、长歌副歌不到两遍又没说明是刻意的，只提醒不拒绝。这些校验不评价歌词质量。旧的写歌说明里叫 `ace_step`、`suno` 的字段照样认。

## 测过的 AI 助手

发布前在 Claude Code、Codex、OpenCode（Kimi 模型）和 DeepSeek Harness 上各跑了两轮全量测试（每家 11 道题），网页版在 Kimi、DeepSeek 上跑过，两轮都没有出现越过底线的问题。已知：Codex 有时会在回复里提到它在用这个 Skill，或者解释它为什么停下来等你选，不影响结果。

## 许可与致谢

本仓库脚本及文档采用 [MIT](LICENSE)。

写词规则中「先写钩子、再做段落规划」的思路参考了 [regiellis/suno-songwriter-agent-skill](https://github.com/regiellis/suno-songwriter-agent-skill)（[MIT License](https://github.com/regiellis/suno-songwriter-agent-skill/blob/main/LICENSE)），「写完逐行审稿再修改」的思路参考了 [jedliuai/SUNO-AI-Music-Skills](https://github.com/jedliuai/SUNO-AI-Music-Skills)（[CC0-1.0](https://github.com/jedliuai/SUNO-AI-Music-Skills/blob/main/LICENSE)）。本项目的规则文字为自行撰写，未复制上述项目的内容。

立意五问、押韵安排、重复与变化的思路参考了 [jtydhr88/lyric-writing-skills](https://github.com/jtydhr88/lyric-writing-skills)（MIT；其 NOTICE 说明书籍、歌词、访谈和译文等第三方材料不在该许可覆盖内）；「用户指定文字不改」的思路参考了 [bq1998-dot/lyric-writing](https://github.com/bq1998-dot/lyric-writing)（MIT）。本项目的规则文字为自行撰写，未复制上述项目的内容。
