BLOCK_MATH = r"(?<!\\)\$\$" r"([\s\S]*?)" r"(?<!\\)\$\$"

INLINE_MATH = r"(?<![\\])\$" r"(.*?)" r"(?<![\\])\$"


def parse_inline_mathjax(inline, m, state):
    content = m.group(1)
    return "mathjax_inline", content


def parse_block_mathjax(block, m, state):
    content = m.group(1)
    return "mathjax_block", content


def render_html_inline_mathjax(content):
    return f"\\({content}\\)"


def render_html_block_mathjax(content):
    return f"\\[{content}\\]"


def plugin_mathjax(md):
    md.inline.register_rule("mathjax_block", BLOCK_MATH, parse_block_mathjax)
    md.inline.register_rule("mathjax_inline", INLINE_MATH, parse_inline_mathjax)

    md.inline.rules.append("mathjax_block")
    md.inline.rules.append("mathjax_inline")

    if md.renderer.NAME == "html":
        md.renderer.register("mathjax_block", render_html_block_mathjax)
        md.renderer.register("mathjax_inline", render_html_inline_mathjax)
