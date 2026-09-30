#!/usr/bin/env python3
"""Draw the deck's diagrams as inline SVG and splice them into the deck source.

    ./_training/diagrams.py            # regenerate every diagram in openrvdas_tech_deck.md
    ./_training/diagrams.py --list     # list the diagrams this file knows about
    ./_training/build_deck.py          # then rebuild the HTML as usual

Each diagram is a function below that places boxes, text and arrows on a
fixed grid. The result replaces the ```svg block whose <svg> carries the same
id, so editing a diagram means editing its function here, never the SVG in the
Markdown. Colours come from the deck's CSS variables and currentColor, so the
figures follow the page's light and dark themes.

Conventions shared by every figure:
  - data flows top to bottom
  - a logger is one box: its name as a header, then one component per line,
    with writers side by side on the last row when there is more than one
  - dotted arrows carry data; solid arrows are control (starts, writes configuration)
  - components are written by class name (SerialReader, not "serial reader")

Standard library only.
"""

import argparse
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = HERE / 'openrvdas_tech_deck.md'

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'
LINE = 20          # spacing between component lines in a logger box
HEAD = 32          # height of a logger box's header band


class Figure:
    """One SVG figure. Coordinates are in viewBox units."""

    def __init__(self, fig_id, width, height, aria):
        self.id, self.width, self.height, self.aria = fig_id, width, height, aria
        self.parts = []

    # -- primitives ---------------------------------------------------------

    def text(self, x, y, s, size=11, anchor='middle', mono=False, bold=False):
        attrs = ['x="%g"' % x, 'y="%g"' % y, 'font-size="%d"' % size]
        if anchor != 'start':
            attrs.append('text-anchor="%s"' % anchor)
        if mono:
            attrs.append('font-family="%s"' % MONO)
        if bold:
            attrs.append('font-weight="700"')
        self.parts.append('  <text %s fill="currentColor" stroke="none">%s</text>'
                          % (' '.join(attrs), html.escape(s)))

    def rect(self, x, y, w, h, fill='surface', accent=False):
        style = 'fill: var(--%s)' % fill
        if accent:
            style += '; stroke: var(--accent); stroke-width: 2.5'
        self.parts.append('  <rect x="%g" y="%g" width="%g" height="%g" rx="4" style="%s"/>'
                          % (x, y, w, h, style))

    def rule(self, x1, y1, x2, y2, faint=False):
        extra = ' stroke-opacity="0.4"' if faint else ''
        self.parts.append('  <line x1="%g" y1="%g" x2="%g" y2="%g"%s/>' % (x1, y1, x2, y2, extra))

    def arrow(self, *points, dashed=False, label=None, at=None, anchor='middle'):
        """Arrow through points [(x, y), ...]; the head is on the last point."""
        dash = ' stroke-dasharray="5 4"' if dashed else ''
        marker = ' marker-end="url(#%s-arrow)"' % self.id
        if len(points) == 2:
            (x1, y1), (x2, y2) = points
            self.parts.append('  <line x1="%g" y1="%g" x2="%g" y2="%g"%s%s/>'
                              % (x1, y1, x2, y2, dash, marker))
        else:
            pts = ' '.join('%g,%g' % p for p in points)
            self.parts.append('  <polyline points="%s"%s%s/>' % (pts, dash, marker))
        if label:
            self.text(at[0], at[1], label, anchor=anchor)

    # -- composite shapes ---------------------------------------------------

    def box(self, x, y, w, h, lines, mono=False, bold_first=False, fill='surface',
            accent=False, size=12):
        """A box with one or more centred lines of text."""
        self.rect(x, y, w, h, fill=fill, accent=accent)
        first = y + h / 2 - (len(lines) - 1) * 9 + 4
        for i, s in enumerate(lines):
            bold = bold_first and i == 0
            self.text(x + w / 2, first + i * 18, s, size=14 if bold else size,
                      mono=mono and not bold, bold=bold)
        return {'top': (x + w / 2, y), 'bottom': (x + w / 2, y + h),
                'left': (x, y + h / 2), 'right': (x + w, y + h / 2)}

    def logger(self, x, y, w, name, components, writers=()):
        """A logger box: name header, one component per line, then writers.

        Writers given separately are drawn side by side on a last row. Returns
        anchor points, including 'writers': the centre-bottom of each writer.
        """
        h = HEAD + 8 + LINE * len(components) + (30 if writers else 0)
        self.rect(x, y, w, h)
        self.text(x + w / 2, y + 22, name, size=14, bold=True)
        self.rule(x, y + HEAD, x + w, y + HEAD)
        for i, comp in enumerate(components):
            self.text(x + w / 2, y + HEAD + 20 + LINE * i, comp, size=12, mono=True)
        out = []
        if writers:
            row = y + h - 30
            self.rule(x, row, x + w, row, faint=True)
            cell = w / len(writers)
            for i, wr in enumerate(writers):
                if i:
                    self.rule(x + cell * i, row, x + cell * i, y + h, faint=True)
                cx = x + cell * (i + 0.5)
                self.text(cx, row + 20, wr, size=12, mono=True)
                out.append((cx, y + h))
        return {'top': (x + w / 2, y), 'bottom': (x + w / 2, y + h),
                'left': (x, y + h / 2), 'right': (x + w, y + h / 2),
                'height': h, 'writers': out}

    # -- output -------------------------------------------------------------

    def svg(self):
        head = ('<svg id="%s" viewBox="0 0 %d %d" role="img" aria-label="%s" '
                'font-family="%s" fill="none" stroke="currentColor" stroke-width="1.5">'
                % (self.id, self.width, self.height, html.escape(self.aria), SANS))
        defs = ['  <defs>',
                '    <marker id="%s-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
                'markerWidth="7" markerHeight="7" orient="auto-start-reverse">' % self.id,
                '      <path d="M0,0 L10,5 L0,10 z" fill="currentColor" stroke="none"/>',
                '    </marker>',
                '  </defs>']
        return '\n'.join([head] + defs + self.parts + ['</svg>'])


# --------------------------------------------------------------------------
# the diagrams
# --------------------------------------------------------------------------

def where_openrvdas_sits():
    """Slide: Where OpenRVDAS sits."""
    f = Figure('where-openrvdas-sits', 720, 396,
               'Instruments feed OpenRVDAS. CORIOLIX sits beside OpenRVDAS and writes its '
               'configuration. OpenRVDAS writes to files and the network, to databases such '
               'as InfluxDB that Grafana reads, and through CORIOLIXWriter to the CX database '
               'backend, which CX reads.')
    inst = f.box(140, 16, 180, 40, ['Instruments'], size=13)
    ordv = f.box(120, 100, 220, 60, ['OpenRVDAS', 'read · process · write'],
                 bold_first=True, accent=True)
    cx = f.box(480, 100, 220, 60, ['CORIOLIX (CX)', 'keeps OpenRVDAS running'], bold_first=True)
    f.box(20, 240, 180, 50, ['Files and network', '(UDP)'])
    f.box(240, 240, 180, 50, ['Databases', 'such as InfluxDB'])
    f.box(500, 240, 180, 50, ['CX database backend'])
    f.box(240, 340, 180, 40, ['Grafana dashboards'])

    f.arrow(inst['bottom'], (230, 98), dashed=True)
    f.arrow(cx['left'], (342, 130), label='writes configuration', at=(411, 121))
    f.arrow((170, 160), (115, 238), dashed=True)
    f.arrow((250, 160), (320, 238), dashed=True)
    f.arrow((320, 160), (530, 238), dashed=True, label='CORIOLIXWriter', at=(428, 182))
    f.arrow((640, 240), (640, 162), dashed=True, label='reads', at=(648, 205), anchor='start')
    f.arrow((330, 290), (330, 338), dashed=True, label='reads', at=(338, 318), anchor='start')
    return f


def snapping_together():
    """Slide: Snapping them together — the inside of one logger."""
    f = Figure('snapping-together', 720, 356,
               'Inside one logger: a SerialReader reads the gyro serial port; '
               'TimestampTransform then PrefixTransform are applied in order; the result goes '
               'to LogfileWriter and UDPWriter at the same time, which write a data file and '
               'broadcast on UDP port 6224.')
    f.text(360, 24, 'gyro serial port', size=12)
    reader = f.box(270, 60, 180, 36, ['SerialReader'], mono=True)
    stamp = f.box(270, 124, 180, 36, ['TimestampTransform'], mono=True)
    prefix = f.box(270, 188, 180, 36, ['PrefixTransform'], mono=True)
    logw = f.box(170, 262, 180, 36, ['LogfileWriter'], mono=True)
    udpw = f.box(370, 262, 180, 36, ['UDPWriter'], mono=True)
    f.text(260, 342, 'data file', size=12)
    f.text(460, 342, 'UDP port 6224', size=12)

    # side notes on the three stages
    f.text(256, 82, 'readers', anchor='end')
    f.text(256, 178, 'transforms, in order', anchor='end')
    f.text(156, 284, 'writers, all at once', anchor='end')

    f.arrow((360, 32), (360, 58), dashed=True)
    f.arrow(reader['bottom'], (360, 122), dashed=True)
    f.arrow(stamp['bottom'], (360, 186), dashed=True)
    f.arrow((340, 224), (262, 260), dashed=True)
    f.arrow((380, 224), (458, 260), dashed=True)
    f.arrow(logw['bottom'], (260, 326), dashed=True)
    f.arrow(udpw['bottom'], (460, 326), dashed=True)
    return f


def loggers_feed_loggers():
    """Slide: Loggers that feed loggers."""
    f = Figure('loggers-feed-loggers', 720, 600,
               'Two instrument loggers, knud-net and s330-net, each run SerialReader, '
               'TimestampTransform, PrefixTransform and UDPWriter, and broadcast to UDP port '
               '6224. The parse_data logger reads that port with UDPReader, parses with '
               'ParseTransform, and writes with CachedDataWriter to cached_data_server and with '
               'InfluxDBWriter to InfluxDB. The true_winds logger reads from '
               'cached_data_server, computes true winds, and writes them back to '
               'cached_data_server.')
    instrument = ['SerialReader', 'TimestampTransform', 'PrefixTransform', 'UDPWriter']
    knud = f.logger(110, 16, 200, 'knud-net', instrument)
    s330 = f.logger(410, 16, 200, 's330-net', instrument)
    parse = f.logger(200, 200, 320, 'parse_data', ['UDPReader', 'ParseTransform'],
                     writers=['CachedDataWriter', 'InfluxDBWriter'])
    cds = f.box(190, 360, 180, 40, ['cached_data_server'], mono=True, fill='surface-2')
    influx = f.box(380, 360, 120, 40, ['InfluxDB'], fill='surface-2')
    tw = f.logger(190, 450, 180, 'true_winds',
                  ['CachedDataReader', 'TrueWindsTransform', 'CachedDataWriter'])

    f.arrow((210, knud['bottom'][1]), (330, 198), dashed=True)
    f.arrow((510, s330['bottom'][1]), (390, 198), dashed=True)
    f.text(360, 176, 'UDP port 6224')
    (cw, cb), (iw, ib) = parse['writers']
    f.arrow((cw, cb), (cw, 358), dashed=True)
    f.arrow((iw, ib), (iw, 358), dashed=True)
    f.arrow(cds['bottom'], (280, 448), dashed=True)
    tb = tw['bottom'][1]
    f.arrow((280, tb), (280, tb + 22), (150, tb + 22), (150, 380), (188, 380), dashed=True,
            label='true winds', at=(142, 470), anchor='end')
    return f


def moving_parts():
    """Slide: The moving parts — what supervisord runs."""
    f = Figure('moving-parts', 720, 290,
               'supervisord starts logger_manager, cached_data_server and nginx with uwsgi. '
               'logger_manager starts one logger process per active configuration. '
               'cached_data_server feeds live data to the built-in displays and to the Django '
               'web console, which nginx and uwsgi serve.')
    sup = f.box(270, 16, 180, 40, ['supervisord (:9001)'], mono=True)
    lm = f.box(40, 110, 180, 40, ['logger_manager'], mono=True)
    cds = f.box(270, 110, 180, 40, ['cached_data_server (:8766)'], mono=True, size=11)
    web = f.box(500, 110, 180, 40, ['nginx + uwsgi'], mono=True)
    procs = [f.box(x, 210, 78, 50, ['logger', 'process']) for x in (10, 94, 178)]
    disp = f.box(285, 210, 150, 50, ['displays and', 'widgets'])
    gui = f.box(480, 210, 200, 50, ['Django web console'])

    f.arrow((330, 56), lm['top'], label='starts', at=(232, 76))
    f.arrow(sup['bottom'], cds['top'])
    f.arrow((390, 56), web['top'])
    for p in procs:
        f.arrow((130, 150), p['top'])
    f.text(206, 186, 'starts', anchor='start')
    f.arrow(cds['bottom'], disp['top'], dashed=True, label='live data', at=(368, 186),
            anchor='start')
    f.arrow((420, 150), (540, 208), dashed=True)
    f.arrow(web['bottom'], (600, 208), label='serves', at=(628, 186), anchor='start')
    return f


DIAGRAMS = [where_openrvdas_sits, snapping_together, loggers_feed_loggers, moving_parts]


# --------------------------------------------------------------------------
# splicing
# --------------------------------------------------------------------------

def splice(text, fig):
    """Replace the ```svg block whose <svg> has fig's id. Returns (text, found)."""
    pat = re.compile(r'```svg\n<svg id="%s".*?\n```' % re.escape(fig.id), re.S)
    block = '```svg\n%s\n```' % fig.svg()
    new, n = pat.subn(lambda m: block, text)
    return new, n == 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', nargs='?', default=str(DECK))
    ap.add_argument('--list', action='store_true', help='list diagram ids and exit')
    args = ap.parse_args()

    figs = [build() for build in DIAGRAMS]
    if args.list:
        for build, fig in zip(DIAGRAMS, figs):
            print('%-24s %s' % (fig.id, build.__doc__.strip()))
        return

    src = Path(args.source)
    text = src.read_text()
    missing = []
    for fig in figs:
        text, found = splice(text, fig)
        if not found:
            missing.append(fig.id)
    src.write_text(text)
    print('updated %d diagram(s) in %s' % (len(figs) - len(missing), src.name))
    if missing:
        sys.exit('no ```svg block with id %s — add a placeholder '
                 '"```svg\\n<svg id=\\"ID\\">\\n```" where it belongs'
                 % ', '.join(missing))


if __name__ == '__main__':
    main()
