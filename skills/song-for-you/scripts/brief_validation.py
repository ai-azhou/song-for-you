"""读入写歌说明并校验歌词边界；不覆盖输入文件。"""
import json
import re
import sys
from pathlib import Path


def normalize(data):
    """新字段是 song、style；旧说明里的 ace_step、suno 照样认。"""
    for cluster in data.get('clusters') or []:
        if not isinstance(cluster, dict):
            continue
        old = cluster.get('ace_step')
        if 'song' not in cluster and isinstance(old, dict):
            cluster['song'] = {k: old[k] for k in ('lyrics', 'vocal_language', 'duration') if k in old}
        suno = cluster.get('suno')
        if 'style' not in cluster and isinstance(suno, dict):
            cluster['style'] = {'tags': suno.get('styles', ''), 'exclude': suno.get('exclude', ''), 'vocal': suno.get('vocal', '')}
    return data


def load_brief(path, fix=False):
    """to_suno.py 的读入入口：读入、改成新字段名、校验标签和指定文字、提醒结构问题。"""
    from output_utils import safe_text
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('status') != 'ok':
        reason = data.get('question') if isinstance(data, dict) else None
        raise ValueError('写歌说明还没准备好（status 必须是 ok）：' + (reason or '请先补齐材料，再重新生成说明。'))
    if not isinstance(data.get('clusters'), list) or not data['clusters']:
        raise ValueError('clusters 必须包含至少一首。')
    normalize(data)
    for i, c in enumerate(data['clusters'], 1):
        song = c.get('song') if isinstance(c, dict) else None
        if not isinstance(song, dict) or not isinstance(song.get('lyrics'), str) or not song['lyrics'].strip():
            raise ValueError(f'第 {i} 首缺少有效的 song.lyrics。')
        if song.get('duration') is not None and not 10 <= float(song['duration']) <= 600:
            raise ValueError(f'第 {i} 首 song.duration 要在 10–600 秒之间。')
    changes = validate_lyrics(data, fix=fix)
    for change in changes:
        print(safe_text("已修正（仅本次使用，不覆盖原文件）：" + change), file=sys.stderr)
    for message in structure_messages(data):
        print(safe_text(message), file=sys.stderr)
    return data


def section_name(value):
    return str(value).strip().strip('[]').split(' - ', 1)[0].strip()


def structure_messages(data):
    """结构问题只提醒；无法确定是否刻意安排时仍请用户确认。"""
    messages = []
    if data.get('base') in ('市场', '混合') and not str(data.get('market_note') or '').strip():
        messages.append('市场或混合基底没有 market_note，请补充依据。')
    for i, cluster in enumerate(data['clusters'], 1):
        song = cluster['song']
        structure = cluster.get('structure') or []
        actual = [section_name(m[1]) for line in song['lyrics'].splitlines()
                  if (m := re.fullmatch(r'\s*\[([^\]]+)\]\s*', line))]
        planned = [section_name(row.get('section', '')) for row in structure]
        if not structure:
            messages.append(f'第 {i} 首没有段落表。')
        elif planned != actual:
            messages.append(f'第 {i} 首段落表与歌词不一致：段落表 {planned}；歌词 {actual}。')
        # 只认明确的单次副歌说明，不能从一般的“变化”措辞推断意图。
        intentional = any(re.search(r'(?:刻意|有意|故意).{0,12}副歌.{0,8}(?:一次|一遍)|副歌.{0,8}(?:一次|一遍).{0,12}(?:刻意|有意|故意)',
                                    ' '.join(str(row.get(k, '')) for k in ('job', 'difference')))
                          for row in structure)
        # 没有写副歌的歌（比如靠 Drop 或叠句）说明过结构就不提醒。
        no_chorus_form = 'Chorus' not in actual and str(cluster.get('form_note', '')).strip()
        if actual.count('Chorus') < 2 and float(song.get('duration') or 210) >= 150 and not intentional and not no_chorus_form:
            messages.append(f'第 {i} 首：副歌只回来一次，确认这是这首歌要的。')
    return messages


def allowed_tags():
    # 从唯一的标签表取值，避免脚本与写作规则各维护一份清单。
    writing = Path(__file__).resolve().parents[1] / 'references' / 'writing.md'
    rows = [line for line in writing.read_text(encoding='utf-8').splitlines()
            if line.lstrip().startswith('|')]
    tags = set(re.findall(r'`\[([^\]]+)\]`', '\n'.join(rows)))
    if not tags:
        raise ValueError('读不到 writing.md 的段落标签表，请恢复该文件后再运行。')
    return tags


def validate_lyrics(data, fix=False):
    tags = allowed_tags()
    errors, changes, pending = [], [], []
    for field, choices in (('tier', ('放手', '选择', '共创', '自带')), ('base', ('口味', '市场', '混合'))):
        if field in data and data[field] not in choices:
            errors.append(f'{field} 取值无效：{data[field]!r}；请选择 {choices}。')
    for i, cluster in enumerate(data['clusters'], 1):
        song = cluster['song']
        fixed = cluster.get('fixed_lines', [])
        if not isinstance(fixed, list):
            errors.append(f'第 {i} 首 fixed_lines 必须是数组。')
        else:
            lyric_lines = {line.strip() for line in song['lyrics'].splitlines()}
            for line in fixed:
                if not isinstance(line, str) or line.strip() not in lyric_lines:
                    errors.append(f'第 {i} 首 fixed_lines 中指定的句子不在歌词里：{line!r}')
        if not re.fullmatch(r'[a-z]{2}', str(song.get('vocal_language', ''))):
            errors.append(f'第 {i} 首 song.vocal_language 字段（不是歌词行）：'
                          f'目前为 {song.get("vocal_language")!r}；请写歌词语言的两位代码，比如 zh、en、ja。')
        lines = song['lyrics'].splitlines(keepends=True)
        for n, raw in enumerate(lines, 1):
            line = raw.rstrip('\r\n')
            match = re.match(r'^(\s*)\[([^\]]+)\](.*)$', line)
            if not match:
                if line.lstrip().startswith('['):
                    errors.append(f'第 {i} 首歌词第 {n} 行：标签缺少闭合方括号，请按 [Verse] 等格式填写。')
                continue
            indent, inside, tail = match.groups()
            tag = inside.split(' - ', 1)[0].strip()
            # 标签表允许风格描述中已有乐器的 Solo；以英文风格短语核对。
            solo = re.fullmatch(r'([A-Za-z][A-Za-z -]*) Solo', tag)
            style = str(cluster.get('style', {}).get('tags', '')) + ' ' + str(cluster.get('ace_step', {}).get('caption', ''))
            valid_solo = solo and re.search(r'(?<!\w)' + re.escape(solo[1]) + r'(?!\w)', style, re.I)
            if tag not in tags and not valid_solo:
                errors.append(f'第 {i} 首歌词第 {n} 行：[{tag}] 不在允许的段落标签表中；'
                              '请改用 writing.md 表内标签（例如 [Chorus]），Solo 的乐器须出现在风格描述中。')
            if tail.strip():
                if fix:
                    hint = tail.strip()
                    if hint.startswith('-'):
                        hint = hint[1:].strip()
                    if not hint or '[' in hint or ']' in hint:
                        errors.append(f'第 {i} 首歌词第 {n} 行：方括号外内容无法确定性搬移，请手动合并成一个标签。')
                        continue
                    revised = f'{indent}[{inside.rstrip()} - {hint}]'
                    lines[n-1] = revised + raw[len(line):]
                    changes.append(f'第 {i} 首歌词第 {n} 行：{line} → {revised}')
                else:
                    errors.append(f'第 {i} 首歌词第 {n} 行：] 后还有内容 {tail.strip()!r}，会被当成歌词；'
                                  '请把提示移进方括号，如 [Chorus - softly]，或加 --fix 自动搬移。')
        pending.append((song, ''.join(lines)))
    if errors:
        raise ValueError('写歌说明校验未通过：\n' + '\n'.join(errors))
    for song, lyrics in pending:
        song['lyrics'] = lyrics
    return changes
