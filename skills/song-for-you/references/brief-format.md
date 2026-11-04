# 写歌说明（brief）JSON

写歌说明就是这份 JSON 文件，属于交付物，不换成别的格式，也不要删。`scripts/to_suno.py` 读它出粘贴稿，用户回来改提示词时也从它改。字段名、层级、取值写法照下面写。存成 UTF-8 的 `.json` 文件，写完自己用 JSON 解析器读一遍，读不通就改到读通。

## 结构

```json
{
  "status": "ok|need_input",
  "question": "",
  "tier": "放手|选择|共创|自带",
  "base": "口味|市场|混合",
  "market_note": "",
  "material_check": {
    "items": [{"name": "", "familiarity": "熟悉|大概知道|不认识", "source": "印象|联网|用户补充|无"}],
    "note": ""
  },
  "shared_base": "",
  "clusters": [
    {
      "label": "", "share": "",
      "taste_profile": {
        "genre": "", "era": "", "tempo": "", "mode_mood": "", "instruments": "",
        "vocal": "", "production": "", "lyric_themes": "", "lyric_style": "", "avoid": ""
      },
      "intent": {"type": "", "one_thing": "", "to_whom": "", "moment": "", "anchor": ""},
      "form_note": "",
      "structure": [{"section": "", "job": "", "length": "", "energy": "", "difference": ""}],
      "title": "",
      "lyrics_source": "agent|user|mixed",
      "fixed_lines": [],
      "human_contribution": "",
      "song": {"vocal_language": "zh", "duration": 210, "lyrics": ""},
      "style": {"tags": "", "exclude": "", "vocal": ""}
    }
  ]
}
```

所有粘贴内容都用同一份歌词（`song.lyrics`）和同一段风格短语（`style.tags`）。旧的写歌说明里叫 `ace_step`、`suno` 的，脚本照样认；新写一律用 `song`、`style`。

## 哪些字段能出现真实名字

- **可以**：`question`、`market_note`、`material_check`、`share`、`human_contribution`。这些是给用户看的。
- **不行**：`label`、`shared_base`、`taste_profile`、`intent`、`structure`、`title`、`song`、`style`。`exclude` 里也不写「不要像某某」。
- **例外**：`lyrics_source` 是 `user` 或 `mixed` 时，用户自己写的词原样放在 `song.lyrics` 里，里面有真实名字也不改，在回复里提示。

## 顶层

| 字段 | 要求 |
|---|---|
| `status` | `ok`：写好了，可以生成。`need_input`：触发了「停下来问」，这时 `clusters` 是空数组。 |
| `question` | `need_input` 时必填，用用户的语言，一次问完；`ok` 时留空字符串。不引用本 Skill 的规则。 |
| `tier` | 用户的参与档位，四选一。 |
| `base` | 风格基底，三选一。 |
| `market_note` | `base` 是市场或混合时必填：查到了什么、是哪种热、哪里哪段时间、证据多硬、哪些没查到。口味基底留空字符串。 |
| `material_check.items` | 每位歌手一项（歌单按歌手合并）。没有歌手材料时是空数组。 |
| `material_check.note` | 用户的语言。有画像就写明它是凭印象、查到的描述和用户的话写的，不是听出来的。有才写：哪些歌手没用上、名字按哪一位理解、其他没写成歌的方向。 |
| `shared_base` | 这首歌最核心的底色，一句话。 |

## 每首歌（`clusters[]`）

| 字段 | 要求 |
|---|---|
| `label` | 短名，描述声音，不用人名。 |
| `share` | 这一类大约占多少、主要来自哪几位；市场基底写来自哪个方向。 |
| `taste_profile` | 十项，见 `writing.md` 第二节。`avoid` 必填。 |
| `intent` | 五项，见 `writing.md` 第四节。自带档从用户的词里读出来。 |
| `form_note` | 一两句：这种风格、这个用途的结构特点，这首歌取了什么、没取什么。见 `writing.md` 第五节。 |
| `structure` | 段落表，见 `writing.md` 第五节。`section` 只写标签表里的段落名，不带方括号和提示，顺序和个数要和 `song.lyrics` 里的标签对上。`length` 写大约几行或「器乐」；`energy` 写高中低这类相对描述；`difference` 写这一遍和上一遍差在哪，第一次出现就写「首次」。 |
| `title` | 短；和歌词同一种语言；不撞你知道的真实歌名，不含人名。用户自己定的标题不改，撞名只提示。 |
| `lyrics_source` | `agent` 你写的；`user` 用户写的；`mixed` 两者都有。 |
| `fixed_lines` | 只放用户写的或改过的句子，逐句一项，一字不差。他只说「可以」的你写的句子不算。脚本会核对它们都在歌词里。没有就是空数组。 |
| `human_contribution` | 如实写用户做了什么：选了方向、改了哪几句、写了哪些词。放手档写还没有参与，之后听歌时会挑。 |
| `song.vocal_language` | 歌词语言的两位代码，比如 `zh`、`en`、`ja`。用户指定了照办；没指定用用户提问的语言。 |
| `song.duration` | 目标时长（秒，整数），见 `writing.md` 第五节。粘贴稿里写给用户看，生成工具不保证照它控制。 |
| `song.lyrics` | 一整段字符串，段落之间空一行（JSON 里写成 `\n\n`）。只有歌词和段落标签。 |
| `style.tags` | 英文短语，逗号分隔：流派、情绪、核心配器、人声（写明男声女声）、制作。就是 Suno 的 Styles；海绵音乐的中文风格描述照它翻。见 `writing.md` 第七节。 |
| `style.exclude` | 英文短语，逗号分隔。只有 Suno 用。 |
| `style.vocal` | `female`、`male`、`mixed`、`duet`、`group` 五选一。 |

## 自查

- 能被 JSON 解析器读通；`status` 和 `clusters` 对得上。
- 不能出现真名的字段里，搜一遍 `material_check.items` 的每个名字和你知道的原歌名。
- `structure` 和歌词里的标签顺序一致。
- `fixed_lines` 每一句都一字不差地在歌词里。
- 每个标签行的最后一个字符都是右方括号。
