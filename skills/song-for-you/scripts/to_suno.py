#!/usr/bin/env python3
"""只整理文本，不调用平台生成接口。"""
import argparse
import sys
from pathlib import Path
from brief_validation import load_brief
from output_utils import safe_text

STEPS = {
    'zh': '''打开 Suno Create，切到 Custom 模式。
把 Lyrics 完整粘进歌词框，把 Styles 粘进风格框。
展开 Advanced Options，把 Exclude 粘进排除框；按下面的说明设置人声。
有改写风格词的选项（Variety）时关掉，其余先用默认。
选项名称和位置以 Suno 界面为准。
如果界面有保持全曲一致的选项，长歌可以试，费用看界面。
生成后先听，再按需要调整。''',
    'en': '''Open Suno Create and switch to Custom mode.
Paste all of Lyrics into the lyrics box and Styles into the style box.
Open Advanced Options, paste Exclude into the exclusion box, and set vocals as described below.
If there is an option that rewrites your styles (Variety), turn it off; leave the rest at their defaults.
Option names and locations depend on the Suno interface.
If the interface offers an option to keep the whole song consistent, try it for long songs; check the interface for costs.
Listen to the result, then adjust as needed.''',
}


def fenced(text):
    fence = '`' * max(3, max((len(x) for x in __import__('re').findall(r'`+', text)), default=0) + 1)
    return f'{fence}\n{text}\n{fence}\n'


def main():
    p = argparse.ArgumentParser(description='把 status=ok 的写歌说明整理为 Suno Custom 模式粘贴稿。')
    p.add_argument('brief', nargs='?', help='写歌说明 JSON')
    p.add_argument('--brief', dest='brief_option', help='写歌说明 JSON（与位置参数二选一）')
    p.add_argument('--out', help='输出 Markdown 路径，不填则输出到终端')
    p.add_argument('--fix', action='store_true', help='把标签行方括号外的提示移入括号；不覆盖输入 JSON')
    a = p.parse_args()
    if bool(a.brief) == bool(a.brief_option):
        p.error('请提供一个写歌说明：位置参数或 --brief，二选一。')
    a.brief = a.brief or a.brief_option
    try:
        # 读入入口：校验标签、指定文字，并核对结构；旧字段名照样认。
        data = load_brief(a.brief, fix=a.fix)
        english = all(str(c['song'].get('vocal_language', '')).lower() == 'en' for c in data['clusters'])
        chunks = ['# Suno paste guide' if english else '# Suno 粘贴稿']
        for i, c in enumerate(data['clusters'], 1):
            lang = 'en' if str(c['song'].get('vocal_language', '')).lower() == 'en' else 'zh'
            s = c.get('style', {})
            if not all(isinstance(s.get(k), str) for k in ('tags', 'exclude', 'vocal')) or not s['tags'].strip():
                raise ValueError(f'Song {i}: missing style tags / exclude / vocal.' if lang == 'en' else f'第 {i} 首缺少 style 的 tags / exclude / vocal 字段。')
            vocal = s['vocal']
            if vocal not in ('female', 'male', 'mixed', 'duet', 'group'):
                raise ValueError(f'Song {i}: unsupported vocal setting: {vocal}' if lang == 'en' else f'第 {i} 首人声字段不支持：{vocal}')
            if lang == 'en':
                instruction = {'female':'Select Female', 'male':'Select Male', 'mixed':'Mixed vocals', 'duet':'Duet', 'group':'Group vocals'}[vocal]
                if vocal not in ('female', 'male'):
                    instruction += '; describe this in Styles. If no matching vocal option exists, leave the gender selection unset.'
                heading, voice = f'Song {i}', 'Vocals'
            else:
                instruction = {'female':'选 Female（女声）', 'male':'选 Male（男声）', 'mixed':'混合人声', 'duet':'对唱', 'group':'群唱'}[vocal]
                if vocal not in ('female', 'male'):
                    instruction += '；将此要求写入 Styles，界面没有对应选项时不强选单一性别。'
                heading, voice = f'第 {i} 首', '人声'
            minutes, seconds = divmod(int(c['song'].get('duration') or 210), 60)
            duration_note = (f'Target duration: {minutes}:{seconds:02d}; not guaranteed by the generator.' if lang == 'en'
                             else f'目标时长：{minutes} 分 {seconds:02d} 秒，生成器不保证。')
            chunks.append(f"\n## {heading}：{c.get('title', '')}\n\n{duration_note}\n\n{STEPS[lang]}\n\n**Title**\n\n{fenced(str(c.get('title', '')))}\n**Styles**\n\n{fenced(s['tags'])}\n**Exclude**\n\n{fenced(s['exclude'])}\n**{voice}**：{instruction}\n\n**Lyrics**\n\n{fenced(c['song']['lyrics'])}")
        text = safe_text('\n'.join(chunks))
        if a.out:
            dest = Path(a.out).expanduser(); dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding='utf-8')
            print(safe_text(f'Paste guide saved: {dest}' if english else f'已生成粘贴稿：{dest}'))
        else:
            print(text)
        return 0
    except Exception as exc:
        print(f'没有导出 / Export failed: {safe_text(exc)}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    from output_utils import install_output_filter
    install_output_filter()
    raise SystemExit(main())
