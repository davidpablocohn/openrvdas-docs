#!/usr/bin/env python3
"""Render the deck script Markdown into the styled HTML that gets published.

    ./_training/build_deck.py                      # -> _training/openrvdas_tech_deck.html
    ./_training/build_deck.py --check              # parse and report, write nothing
    ./_training/build_deck.py --slides-only        # -> _training/openrvdas_tech_deck_slides.html

Edit openrvdas_tech_deck.md, run this, publish the HTML. Slide numbers, the
contents list and the slide/section counts in the header are all generated, so
reordering slides means moving a block of text and nothing else.

The source format is plain Markdown plus a few ALL-CAPS block labels:

    TITLE / EYEBROW / STANDFIRST / FACTS   document header
    INTRO / COLOPHON                       the "how to use" note and the footer
    # Section heading                      starts a section; the line(s) under
                                           it are the section's blurb
    ## Slide title  {demo}                 starts a slide; the optional tag is
                                           one of demo, gotcha, drill, ref
    ON SLIDE                               what gets projected
    SAY                                    what the presenter says

Inside ON SLIDE and SAY you can use paragraphs, - bullets, 1. numbered lists,
``` code fences, ```mermaid diagram fences, ```svg fences for hand-drawn
inline SVG (passed through as-is), | pipe | tables |, `code`, **bold**,
*italic*, {{demo}} for an inline tag pill, a trailing \\ for a hard line break,
and a line starting with NOTE: for a presenter note.

No third-party dependencies: standard library only.
"""

import argparse
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC_LABELS = ('TITLE', 'EYEBROW', 'STANDFIRST', 'FACTS', 'INTRO', 'COLOPHON')
SLIDE_LABELS = ('ON SLIDE', 'SAY')
TAG_NAMES = {'demo': 'Demo', 'gotcha': 'Gotcha', 'drill': 'Drill', 'ref': 'Reference'}


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def parse(text):
    """Split the source into document blocks and a list of sections."""
    doc, sections = {}, []
    label = None
    buf = []
    slide = None

    def flush():
        """Attach the buffered lines to whatever we were last collecting."""
        nonlocal buf
        body = '\n'.join(buf).strip('\n')
        if label and body:
            if slide is not None and label in SLIDE_LABELS:
                slide[label] = body
            elif label in DOC_LABELS:
                doc[label] = body
            elif label == '#BLURB':
                sections[-1]['blurb'] = ' '.join(body.split())
        buf = []

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped in DOC_LABELS + SLIDE_LABELS:
            flush()
            label = stripped
            if stripped in SLIDE_LABELS and slide is None:
                sys.exit('error: "%s" appears before any "## slide" heading' % stripped)
            continue

        if line.startswith('# '):
            flush()
            slide = None
            sections.append({'title': line[2:].strip(), 'blurb': '', 'slides': []})
            label = '#BLURB'
            continue

        if line.startswith('## '):
            flush()
            if not sections:
                sys.exit('error: slide "%s" appears before any "# section" heading'
                         % line[3:].strip())
            head = line[3:].strip()
            tag = None
            m = re.search(r'\s*\{(\w+)\}\s*$', head)
            if m:
                tag = m.group(1).lower()
                if tag not in TAG_NAMES:
                    sys.exit('error: unknown tag {%s} on slide "%s" (use %s)'
                             % (tag, head, ', '.join(sorted(TAG_NAMES))))
                head = head[:m.start()].strip()
            slide = {'title': head, 'tag': tag}
            sections[-1]['slides'].append(slide)
            label = None
            continue

        buf.append(line)

    flush()
    return doc, sections


# --------------------------------------------------------------------------
# markdown rendering
# --------------------------------------------------------------------------

def inline(text):
    """Inline markdown -> HTML. Escapes first, so source stays plain text."""
    out = html.escape(text, quote=False)
    out = re.sub(r'`([^`]+)`', r'<code>\1</code>', out)
    out = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', out)
    out = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', out)
    out = re.sub(r'\{\{(\w+)\}\}',
                 lambda m: '<span class="tag tag-%s">%s</span>'
                           % (m.group(1), TAG_NAMES.get(m.group(1), m.group(1))),
                 out)
    # a trailing backslash is a hard line break
    out = re.sub(r'\\\n', '<br>\n', out)
    return out


def split_blocks(body):
    """Yield (kind, lines) for each top-level block in a chunk of markdown."""
    lines = body.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        if line.lstrip().startswith('```'):
            fence = line.strip()
            kind = ('mermaid' if fence.startswith('```mermaid')
                    else 'svg' if fence.startswith('```svg') else 'code')
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            yield kind, buf
            continue

        if line.lstrip().startswith('|'):
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                buf.append(lines[i].strip())
                i += 1
            yield 'table', buf
            continue

        if re.match(r'\s*-\s', line):
            buf = []
            while i < len(lines) and re.match(r'\s*-\s', lines[i]):
                buf.append(re.sub(r'^\s*-\s+', '', lines[i]))
                i += 1
            yield 'ul', buf
            continue

        if re.match(r'\s*\d+\.\s', line):
            buf = []
            while i < len(lines) and re.match(r'\s*\d+\.\s', lines[i]):
                buf.append(re.sub(r'^\s*\d+\.\s+', '', lines[i]))
                i += 1
            yield 'ol', buf
            continue

        buf = []
        while i < len(lines) and lines[i].strip() and not (
                lines[i].lstrip().startswith(('```', '|'))
                or re.match(r'\s*(-|\d+\.)\s', lines[i])):
            buf.append(lines[i])
            i += 1
        yield 'p', buf


def render(body, indent='  '):
    """Markdown chunk -> HTML fragment."""
    out = []
    for kind, buf in split_blocks(body):
        if kind == 'code':
            out.append('<pre><code>%s</code></pre>'
                       % html.escape('\n'.join(buf), quote=False))
        elif kind == 'svg':
            # hand-drawn inline SVG, passed through untouched
            out.append('<div class="art">\n%s\n</div>' % '\n'.join(buf))
        elif kind == 'mermaid':
            out.append('<div class="art">\n<pre class="mermaid">\n%s\n</pre>\n</div>'
                       % '\n'.join(buf))
        elif kind == 'table':
            rows = [[c.strip() for c in r.strip('|').split('|')] for r in buf]
            rows = [r for r in rows if not all(set(c) <= set('-: ') for c in r)]
            if not rows:
                continue
            head, rest = rows[0], rows[1:]
            cells = ''.join('<th>%s</th>' % inline(c) for c in head)
            trs = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r)
                          for r in rest)
            out.append('<div class="table-scroll">\n<table>\n<thead><tr>%s</tr></thead>\n'
                       '<tbody>%s</tbody>\n</table>\n</div>' % (cells, trs))
        elif kind in ('ul', 'ol'):
            items = ''.join('\n%s  <li>%s</li>' % (indent, inline(t)) for t in buf)
            out.append('<%s>%s\n%s</%s>' % (kind, items, indent, kind))
        else:
            text = '\n'.join(buf)
            if text.startswith('NOTE:'):
                out.append('<p><span class="kicker">Presenter note:</span> %s</p>'
                           % inline(text[5:].strip()))
            else:
                out.append('<p>%s</p>' % inline(text))
    return ('\n' + indent).join(out)


# --------------------------------------------------------------------------
# page assembly
# --------------------------------------------------------------------------

SLIDES_ONLY_EYEBROW = 'Tutorial deck · slides only · draft'
SLIDES_ONLY_STANDFIRST = ('What goes on screen, section by section. The speaker '
                          'script and presenter notes are left out of this version.')
SLIDES_ONLY_TITLE = 'OpenRVDAS Tutorial Slides'


def build(doc, sections, slides_only=False):
    """Render the page. slides_only drops everything meant for the presenter:
    the SAY blocks (and the notes inside them), section blurbs, the intro and
    the colophon."""
    n_slides = sum(len(s['slides']) for s in sections)

    # Slide numbers and per-section ranges are derived, never written by hand.
    number = 0
    ranges = []
    for sec in sections:
        first = number + 1
        for slide in sec['slides']:
            number += 1
            slide['num'] = '%02d' % number
        ranges.append('Slides %02d–%02d' % (first, number) if sec['slides']
                      else 'No slides yet')

    facts = []
    for n, line in enumerate(doc.get('FACTS', '').split('\n')):
        if ':' not in line:
            continue
        key, val = line.split(':', 1)
        facts.append((key.strip(), val.strip()))
        if n == 0:  # auto counts sit right after the first declared fact
            facts.append(('Slides', str(n_slides)))
            facts.append(('Sections', str(len(sections))))

    parts = []
    title = SLIDES_ONLY_TITLE if slides_only else doc.get('TITLE', 'Deck')
    parts.append('<title>%s</title>' % html.escape(title, quote=False))
    parts.append('<style>\n%s\n</style>\n' % (HERE / 'deck.css').read_text().rstrip())
    parts.append('<div class="wrap">\n')

    parts.append('  <header class="masthead">')
    eyebrow = SLIDES_ONLY_EYEBROW if slides_only else doc.get('EYEBROW', '')
    standfirst = SLIDES_ONLY_STANDFIRST if slides_only else doc.get('STANDFIRST', '')
    parts.append('    <p class="eyebrow">%s</p>' % inline(eyebrow))
    parts.append('    <h1>%s</h1>' % inline(doc.get('TITLE', '')))
    parts.append('    <p class="standfirst">\n      %s\n    </p>'
                 % inline(standfirst))
    parts.append('    <dl class="facts">')
    for key, val in facts:
        parts.append('      <div class="fact"><dt>%s</dt><dd>%s</dd></div>'
                     % (inline(key), inline(val)))
    parts.append('    </dl>\n  </header>\n')

    if doc.get('INTRO') and not slides_only:
        parts.append('  <div class="note-box">\n    %s\n  </div>\n'
                     % render(doc['INTRO'], indent='    '))

    parts.append('  <nav class="contents">\n    <h2>Contents</h2>\n    <ol class="toc">')
    for i, sec in enumerate(sections, 1):
        parts.append('      <li><a href="#part-%d">%s<span class="range">%s</span></a></li>'
                     % (i, inline(sec['title']), ranges[i - 1]))
    parts.append('    </ol>\n  </nav>\n')

    words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
             'nine', 'ten', 'eleven', 'twelve']
    for i, sec in enumerate(sections, 1):
        parts.append('  <section class="part" id="part-%d">' % i)
        parts.append('    <div class="section-band">')
        label = 'Part %s' % (words[i - 1] if i <= len(words) else i)
        parts.append('      <span class="part-num">%s</span>' % label)
        parts.append('      <h2>%s</h2>' % inline(sec['title']))
        if sec['blurb'] and not slides_only:
            parts.append('      <p>%s</p>' % inline(sec['blurb']))
        parts.append('    </div>\n')
        parts.append('    <div class="slides">\n')
        for slide in sec['slides']:
            tag = ''
            if slide['tag']:
                tag = '<span class="tag tag-%s">%s</span>' % (slide['tag'],
                                                             TAG_NAMES[slide['tag']])
            parts.append('      <article class="slide">')
            parts.append('        <div class="slide-head"><span class="num">%s</span>'
                         '<h3>%s</h3>%s</div>' % (slide['num'], inline(slide['title']), tag))
            parts.append('        <div class="slide-body">')
            if slide.get('ON SLIDE'):
                parts.append('          <div class="onslide">')
                if not slides_only:
                    parts.append('            <p class="label">On the slide</p>')
                parts.append('            %s' % render(slide['ON SLIDE'], indent='            '))
                parts.append('          </div>')
            if slide.get('SAY') and not slides_only:
                parts.append('          <div class="say">')
                parts.append('            <p class="label">What you say</p>')
                parts.append('            %s' % render(slide['SAY'], indent='            '))
                parts.append('          </div>')
            parts.append('        </div>\n      </article>\n')
        parts.append('    </div>\n  </section>\n')

    if doc.get('COLOPHON') and not slides_only:
        parts.append('  <footer class="colophon">\n    %s\n  </footer>\n'
                     % render(doc['COLOPHON'], indent='    '))

    parts.append('</div>')
    return '\n'.join(parts) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', nargs='?', default=str(HERE / 'openrvdas_tech_deck.md'))
    ap.add_argument('-o', '--output', default=None)
    ap.add_argument('--slides-only', action='store_true',
                    help='leave out the speaker script, presenter notes and section '
                    'blurbs; writes <source>_slides.html')
    ap.add_argument('--check', action='store_true',
                    help='parse and report structure, write nothing')
    args = ap.parse_args()

    src = Path(args.source)
    doc, sections = parse(src.read_text())
    n_slides = sum(len(s['slides']) for s in sections)

    if not sections:
        sys.exit('error: no sections found — every slide needs a "# Section" above it')

    if args.check:
        print('%s: %d sections, %d slides' % (src.name, len(sections), n_slides))
        num = 0
        for sec in sections:
            print('\n  %s' % sec['title'])
            for slide in sec['slides']:
                num += 1
                missing = [b for b in SLIDE_LABELS if not slide.get(b)]
                flag = '  <-- missing %s' % ', '.join(missing) if missing else ''
                print('    %02d  %-52s %-8s%s'
                      % (num, slide['title'][:52],
                         '{%s}' % slide['tag'] if slide['tag'] else '', flag))
        return

    if args.output:
        out = Path(args.output)
    elif args.slides_only:
        out = src.with_name(src.stem + '_slides.html')
    else:
        out = src.with_suffix('.html')
    out.write_text(build(doc, sections, slides_only=args.slides_only))
    print('wrote %s — %d sections, %d slides' % (out, len(sections), n_slides))


if __name__ == '__main__':
    main()
