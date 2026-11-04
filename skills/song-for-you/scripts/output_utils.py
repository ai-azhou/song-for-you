"""Keep diagnostic messages free of service links and commercial amounts."""
import re


def safe_text(value):
    text = re.sub(r'(?:https?://|www\.)[^\s<>\"\']+', '[链接已省略]', str(value))
    text = re.sub(r'(?i)(?:[$€£¥￥]\s*\d[\d,.]*|\d[\d,.]*\s*(?:credits?\b|积分|额度|美元|元)|(?:credits?|额度|价格)\s*[:：]?\s*\d[\d,.]*)', '[金额或额度已省略]', text)
    return text


class _FilteredStream:
    def __init__(self, stream):
        self.stream = stream

    def write(self, text):
        self.stream.write(safe_text(text))
        return len(text)

    def __getattr__(self, name):
        return getattr(self.stream, name)


def install_output_filter():
    """Also filter Python dependency logs sent to the standard streams."""
    import sys
    sys.stdout = _FilteredStream(sys.stdout)
    sys.stderr = _FilteredStream(sys.stderr)
