import string

printable = set(string.printable)


def removesuffix(s, suffix):
    return s[: -len(suffix)] if s.endswith(suffix) else s


def remove_non_ascii(s):
    return ''.join(filter(lambda x: x in printable, s))


def split_string_by_bytes(s, n):
    segments = []
    current_segment = []
    current_bytes = 0
    for ch in s:
        ch_bytes = len(ch.encode('utf-8'))
        if current_bytes + ch_bytes > n:
            if current_segment:
                segments.append(''.join(current_segment))
            current_segment = [ch]
            current_bytes = ch_bytes
        else:
            current_segment.append(ch)
            current_bytes += ch_bytes
    if current_segment:
        segments.append(''.join(current_segment))
    return segments
