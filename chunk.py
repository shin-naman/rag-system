"""Pure chunking library: markdown text in, chunks out. No I/O, no side effects."""


def hard_split(text, cap, overlap):
    """Hard-slice an over-cap paragraph into overlapping windows.

    The overlap means a sentence guillotined at a window boundary still appears
    whole in the neighboring window.
    """
    if len(text) <= cap:
        return [text]
    step = cap - overlap
    return [text[i:i + cap] for i in range(0, len(text), step)]


def pack_paragraphs(text, cap, overlap):
    """Split on blank lines, greedily fill paragraphs into chunks up to `cap` chars.

    A paragraph longer than `cap` (which can never fit alongside anything) is
    hard-sliced into overlapping windows via `hard_split`.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        if len(para) > cap:
            # too big to ever fit: flush what we've packed, then hard-slice it
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(hard_split(para, cap, overlap))
            continue
        # +2 accounts for the "\n\n" separator we'd add between paragraphs
        if current and len(current) + len(para) + 2 > cap:
            chunks.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks


def split_sections(text):
    """Split markdown into (heading_path, body) sections, tracking the heading hierarchy.

    Fence-aware: `#` lines inside ``` / ~~~ code blocks are treated as body, not headings.
    """
    sections = []
    stack = []        # (level, title) for the current heading ancestry
    path = ""         # heading path that the accumulating body belongs to
    body_lines = []
    in_fence = False  # inside a fenced code block?

    def flush():
        body = "\n".join(body_lines).strip()
        if body:
            sections.append((path, body))

    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence       # toggle on the opening and closing fence
            body_lines.append(line)
            continue
        if not in_fence and stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip()
            flush()                       # body so far belongs to the previous heading path
            body_lines = []
            while stack and stack[-1][0] >= level:
                stack.pop()               # leave sibling/deeper sections
            stack.append((level, title))
            path = " > ".join(t for _, t in stack)
        else:
            body_lines.append(line)
    flush()
    return sections


def chunk_markdown(text, cap, overlap):
    """Chunk by heading section, pack paragraphs within, and staple the heading path on.

    Returns a list of (chunk_text, heading_path) tuples.
    """
    chunks = []
    for path, body in split_sections(text):
        for packed in pack_paragraphs(body, cap, overlap):
            stapled = f"{path}\n\n{packed}" if path else packed
            chunks.append((stapled, path))
    return chunks
