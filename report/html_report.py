#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds a self-contained HTML report from a Gitdafa statistics log (stats.txt).

The log is parsed generically: section headings are recognised, every
``tabulate`` table is split into columns by its dash separator line, and
``Key: value`` lines become key/value pairs. Anything the parser does not
recognise is kept as plain text, and the complete raw log is embedded at the
end of the page, so no data from the log is ever lost.
"""

import ast
import html
import math
import os
import re
from datetime import datetime

# Section headings as written by ``Statistics.__str__``
SECTION_PATTERNS = [
    ('statistics', 'Overview', re.compile(r'^STATISTICS\s*$')),
    ('authors', 'Authors', re.compile(r'^AUTHORS\((\d+)\)\s*$')),
    ('authors_per_month', 'Authors contribution per month',
     re.compile(r'^AUTHORS CONTRIBUTION PER MONTH\s*$')),
    ('monthly', 'All monthly contribution',
     re.compile(r'^ALL MONTHLY CONTRIBUTION\s*$')),
    ('tags', 'Tags', re.compile(r'^TAGS\((\d+)\)\s*$')),
    ('loc', 'Lines of code', re.compile(r'^LOC\((\d+) language types\)\s*$')),
    ('files', 'Analyzed files',
     re.compile(r'^Analyzed (\d+) different files\s*$')),
    ('errors', 'Errors', re.compile(r'^ERRORS (\[.*)$')),
]

DASH_LINE = re.compile(r'^\s*-+(?: +-+)*\s*$')
KEY_VALUE = re.compile(r'^([A-Za-z][\w ]*?):\s+(.*)$')
NUMBER = re.compile(r'^-?\d+(?:\.\d+)?$')

# Categorical / sequential series colours (light, dark)
SERIES = [('#2a78d6', '#3987e5'), ('#eb6834', '#d95926')]


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def _column_spans(dash_line):
    return [(m.start(), m.end()) for m in re.finditer(r'-+', dash_line)]


def _split_row(line, spans):
    """Cuts a fixed width tabulate row into cells using the dash spans."""
    cells = []
    for i in range(len(spans)):
        start = spans[i - 1][1] if i > 0 else 0
        end = spans[i + 1][0] if i + 1 < len(spans) else len(line)
        cells.append(line[start:end].strip())
    return cells


def _is_table_start(lines, i):
    return (i + 1 < len(lines) and lines[i].strip() != ''
            and DASH_LINE.match(lines[i + 1]) is not None
            and not DASH_LINE.match(lines[i]))


def _parse_blocks(lines):
    """Turns the body lines of a section into a list of typed blocks."""
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        stripped = line.strip()
        if stripped == '':
            i += 1
            continue
        # A title underlined with dashes and followed by a table (month name)
        if (_is_table_start(lines, i) and len(_column_spans(lines[i + 1])) == 1
                and _is_table_start(lines, i + 2)):
            blocks.append({'type': 'subheading', 'text': stripped})
            i += 2
            continue
        if _is_table_start(lines, i):
            spans = _column_spans(lines[i + 1])
            headers = _split_row(line, spans)
            rows = []
            i += 2
            while i < len(lines):
                row_line = lines[i].rstrip('\n')
                if row_line.strip() == '' or row_line.startswith('Duration: '):
                    break
                rows.append(_split_row(row_line, spans))
                i += 1
            blocks.append({'type': 'table', 'headers': headers, 'rows': rows})
            continue
        if stripped == 'N/A':
            blocks.append({'type': 'na'})
            i += 1
            continue
        kv = KEY_VALUE.match(stripped)
        if kv:
            blocks.append({'type': 'kv', 'key': kv.group(1),
                           'value': kv.group(2).strip()})
        else:
            blocks.append({'type': 'text', 'text': line})
        i += 1
    return blocks


def _parse_errors(text):
    text = text.strip()
    if text == '':
        return []
    try:
        value = ast.literal_eval(text)
        if isinstance(value, (list, tuple)):
            return [str(v) for v in value]
    except (ValueError, SyntaxError):
        pass
    return [text]


def parse_stats_log(text):
    """
    Parses the statistics log text.

    Returns a dict with ``sections`` (ordered list) and ``raw`` (original text).
    Each section has ``key``, ``title``, ``heading`` (line as in the log),
    ``count`` (number in the heading or None) and ``blocks``.
    """
    lines = text.replace('\r\n', '\n').split('\n')
    sections = []
    current = {'key': 'preamble', 'title': 'Run', 'heading': '',
               'count': None, 'lines': []}
    i = 0
    while i < len(lines):
        line = lines[i]
        matched = None
        for key, title, pattern in SECTION_PATTERNS:
            m = pattern.match(line)
            if m:
                matched = (key, title, m)
                break
        if matched is None:
            current['lines'].append(line)
            i += 1
            continue
        sections.append(current)
        key, title, m = matched
        current = {'key': key, 'title': title, 'heading': line.strip(),
                   'count': None, 'lines': []}
        if key == 'errors':
            # Everything to the end of the log belongs to the error list
            rest = '\n'.join([m.group(1)] + lines[i + 1:])
            current['errors'] = _parse_errors(rest)
            current['count'] = len(current['errors'])
            break
        if m.groups() and m.group(1) is not None:
            current['count'] = int(m.group(1))
        i += 1
    sections.append(current)

    for section in sections:
        section['blocks'] = _parse_blocks(section.pop('lines'))
    return {'sections': sections, 'raw': text}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _esc(value):
    return html.escape(str(value), quote=True)


def _to_number(value):
    value = str(value).strip()
    if NUMBER.match(value):
        return float(value)
    return None


def _fmt_number(value):
    if value is None:
        return ''
    if float(value).is_integer():
        return '{:,}'.format(int(value))
    return '{:,.3f}'.format(value).rstrip('0').rstrip('.')


def _fmt_axis(value):
    value = float(value)
    for limit, suffix in ((1e9, 'B'), (1e6, 'M'), (1e3, 'k')):
        if abs(value) >= limit:
            short = value / limit
            text = ('%.1f' % short).rstrip('0').rstrip('.')
            return text + suffix
    return _fmt_number(value)


def _nice_step(max_value, ticks=4):
    if max_value <= 0:
        return 1
    raw = max_value / float(ticks)
    magnitude = 10 ** math.floor(math.log10(raw))
    for mult in (1, 2, 2.5, 5, 10):
        if raw <= mult * magnitude:
            return mult * magnitude
    return 10 * magnitude


def _find_column(headers, *names):
    lowered = [h.strip().lower() for h in headers]
    for name in names:
        if name.lower() in lowered:
            return lowered.index(name.lower())
    return None


def _first(blocks, block_type):
    for block in blocks:
        if block['type'] == block_type:
            return block
    return None


def _kv(blocks, key):
    for block in blocks:
        if block['type'] == 'kv' and block['key'].lower() == key.lower():
            return block['value']
    return None


# --------------------------------------------------------------------------
# Rendering: tables and charts
# --------------------------------------------------------------------------

def _render_table(table, filterable=False, caption=None):
    headers = table['headers']
    rows = table['rows']
    numeric = []
    for col in range(len(headers)):
        values = [r[col] for r in rows if col < len(r) and r[col] != '']
        numeric.append(bool(values) and all(
            _to_number(v) is not None for v in values))
    out = []
    if filterable:
        out.append('<input class="filter" type="search" '
                   'placeholder="Filter rows..." aria-label="Filter rows">')
    out.append('<div class="table-wrap"><table class="data sortable">')
    if caption:
        out.append('<caption>%s</caption>' % _esc(caption))
    out.append('<thead><tr>')
    for col, header in enumerate(headers):
        cls = ' class="num"' if numeric[col] else ''
        label = header if header else '&nbsp;'
        out.append('<th%s scope="col" tabindex="0">%s</th>' % (
            cls, _esc(label) if header else label))
    out.append('</tr></thead><tbody>')
    for row in rows:
        out.append('<tr>')
        for col in range(len(headers)):
            cell = row[col] if col < len(row) else ''
            if numeric[col]:
                out.append('<td class="num" data-v="%s">%s</td>' % (
                    _esc(cell), _esc(cell)))
            else:
                out.append('<td>%s</td>' % _esc(cell))
        out.append('</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def _render_hbars(title, items, note=None, value_suffix=''):
    """Horizontal bar list: items = [(label, value, tooltip)]."""
    if not items:
        return ''
    max_value = max(v for _, v, _ in items) or 1
    out = ['<figure class="chart"><figcaption>%s</figcaption>'
           '<div class="hbars">' % _esc(title)]
    for label, value, tooltip in items:
        width = max(0.0, value / max_value * 100.0)
        out.append(
            '<div class="hbar" title="%s"><span class="hbar-label">%s</span>'
            '<span class="hbar-track"><span class="hbar-fill" '
            'style="width:%.3f%%"></span></span>'
            '<span class="hbar-value">%s%s</span></div>' % (
                _esc(tooltip), _esc(label), width, _esc(_fmt_number(value)),
                _esc(value_suffix)))
    out.append('</div>')
    if note:
        out.append('<p class="note">%s</p>' % _esc(note))
    out.append('</figure>')
    return ''.join(out)


def _bar_path(x, y, w, h, r=4):
    """Bar anchored to the baseline with rounded top corners."""
    if h <= 0:
        return ''
    r = min(r, w / 2.0, h)
    return ('M%.2f,%.2f V%.2f Q%.2f,%.2f %.2f,%.2f H%.2f Q%.2f,%.2f %.2f,%.2f '
            'V%.2f Z' % (x, y + h, y + r, x, y, x + r, y, x + w - r,
                         x + w, y, x + w, y + r, y + h))


def _render_columns(title, categories, series, legend=True):
    """
    Vertical bar chart. series = [(name, [values]), ...] (one or two series,
    same unit, one axis). Values of each category are drawn side by side.
    """
    if not categories:
        return ''
    k = len(series)
    slot = 30 + 14 * k
    bar_w = 12
    gap = 2
    left, right, top, bottom = 56, 16, 12, 72
    plot_h = 220
    width = left + slot * len(categories) + right
    height = top + plot_h + bottom
    max_value = max([max(vals) if vals else 0 for _, vals in series] + [0])
    step = _nice_step(max_value)
    y_max = step * max(1, math.ceil(max_value / step))

    def y_of(v):
        return top + plot_h - (v / y_max) * plot_h

    svg = ['<svg class="cols" width="%d" height="%d" viewBox="0 0 %d %d" '
           'role="img" aria-label="%s">' % (width, height, width, height,
                                             _esc(title))]
    tick = 0.0
    while tick <= y_max + 1e-9:
        y = y_of(tick)
        svg.append('<line class="grid%s" x1="%d" x2="%d" y1="%.2f" y2="%.2f"/>'
                   % (' base' if tick == 0 else '', left, width - right, y, y))
        svg.append('<text class="tick" x="%d" y="%.2f" text-anchor="end" '
                   'dy="0.32em">%s</text>' % (left - 8, y, _fmt_axis(tick)))
        tick += step
    group_w = k * bar_w + (k - 1) * gap
    for ci, category in enumerate(categories):
        x0 = left + ci * slot + (slot - group_w) / 2.0
        tip = [category] + ['%s: %s' % (name, _fmt_number(vals[ci]))
                            for name, vals in series]
        svg.append('<g class="col"><title>%s</title>' % _esc('\n'.join(tip)))
        svg.append('<rect class="hit" x="%.2f" y="%d" width="%d" height="%d"/>'
                   % (left + ci * slot, top, slot, plot_h))
        for si, (_, vals) in enumerate(series):
            value = vals[ci]
            y = y_of(value)
            path = _bar_path(x0 + si * (bar_w + gap), y, bar_w,
                             top + plot_h - y)
            if path:
                svg.append('<path class="s%d" d="%s"/>' % (si + 1, path))
        svg.append('</g>')
        cx = left + ci * slot + slot / 2.0
        ly = top + plot_h + 14
        svg.append('<text class="tick" x="%.2f" y="%d" text-anchor="end" '
                   'transform="rotate(-35 %.2f %d)">%s</text>' % (
                       cx, ly, cx, ly, _esc(category)))
    svg.append('</svg>')

    out = ['<figure class="chart"><figcaption>%s</figcaption>' % _esc(title)]
    if legend and k > 1:
        out.append('<div class="legend">')
        for si, (name, _) in enumerate(series):
            out.append('<span><i class="sw s%d"></i>%s</span>' % (
                si + 1, _esc(name)))
        out.append('</div>')
    out.append('<div class="scroll-x">%s</div></figure>' % ''.join(svg))
    return ''.join(out)


def _column_values(table, *names):
    col = _find_column(table['headers'], *names)
    if col is None:
        return None
    values = []
    for row in table['rows']:
        number = _to_number(row[col]) if col < len(row) else None
        values.append(number if number is not None else 0.0)
    return values


# --------------------------------------------------------------------------
# Rendering: sections
# --------------------------------------------------------------------------

def _render_generic_blocks(blocks, skip_keys=()):
    """Renders any block not consumed by a specialised renderer."""
    out = []
    kvs = [b for b in blocks if b['type'] == 'kv'
           and b['key'].lower() not in skip_keys]
    if kvs:
        out.append('<dl class="kv">')
        for b in kvs:
            out.append('<div><dt>%s</dt><dd>%s</dd></div>' % (
                _esc(b['key']), _esc(b['value'])))
        out.append('</dl>')
    for b in blocks:
        if b['type'] == 'text':
            out.append('<pre class="text">%s</pre>' % _esc(b['text']))
    return ''.join(out)


def _section_meta(section):
    parts = []
    duration = _kv(section['blocks'], 'Duration')
    if duration is not None:
        parts.append('Collected in %s' % duration)
    if section['heading']:
        parts.append('Log heading: %s' % section['heading'])
    return ' · '.join(parts)


def _section_open(section, count_label=None):
    count = ''
    if section.get('count') is not None:
        count = ' <span class="count">%s%s</span>' % (
            _fmt_number(section['count']),
            ' ' + count_label if count_label else '')
    meta = _section_meta(section)
    return ('<section id="%s"><h2>%s%s</h2>%s' % (
        _esc(section['key']), _esc(section['title']), count,
        '<p class="meta">%s</p>' % _esc(meta) if meta else ''))


def _empty(text):
    return '<p class="empty">%s</p>' % _esc(text)


def _render_authors(section):
    out = [_section_open(section)]
    table = _first(section['blocks'], 'table')
    if table:
        commits = _column_values(table, 'Commits')
        name_col = _find_column(table['headers'], 'Name')
        email_col = _find_column(table['headers'], 'Email')
        if commits is not None and name_col is not None:
            items = []
            for row, value in zip(table['rows'], commits):
                email = row[email_col] if email_col is not None else ''
                tip = '\n'.join('%s: %s' % (h, c) for h, c in
                                zip(table['headers'], row))
                label = row[name_col] or email
                items.append((label, value, tip))
            items.sort(key=lambda item: -item[1])
            limit = 25
            note = None
            if len(items) > limit:
                note = 'Top %d of %d authors; all authors are in the table.' % (
                    limit, len(items))
            out.append(_render_hbars('Commits per author', items[:limit],
                                     note))
        out.append(_render_table(table, filterable=len(table['rows']) > 10))
    elif _first(section['blocks'], 'na'):
        out.append(_empty('No author data collected.'))
    out.append(_render_generic_blocks(section['blocks'], ('duration',)))
    out.append('</section>')
    return ''.join(out)


def _render_authors_per_month(section):
    out = [_section_open(section)]
    blocks = section['blocks']
    months = []
    current = None
    for block in blocks:
        if block['type'] == 'subheading':
            current = {'title': block['text'], 'tables': []}
            months.append(current)
        elif block['type'] == 'table':
            if current is None:
                current = {'title': '', 'tables': []}
                months.append(current)
            current['tables'].append(block)
    if not months:
        out.append(_empty('No monthly author data collected.'))
    else:
        out.append('<div class="toolbar"><button type="button" '
                   'data-toggle="open">Expand all</button><button '
                   'type="button" data-toggle="close">Collapse all</button>'
                   '</div>')
        for month in months:
            authors = sum(len(t['rows']) for t in month['tables'])
            commits = sum(sum(_column_values(t, 'Commits') or [0])
                          for t in month['tables'])
            out.append('<details class="month"><summary><strong>%s</strong>'
                       '<span>%s author%s · %s commits</span></summary>' % (
                           _esc(month['title']), _fmt_number(authors),
                           '' if authors == 1 else 's', _fmt_number(commits)))
            for t in month['tables']:
                out.append(_render_table(t))
            out.append('</details>')
    out.append(_render_generic_blocks(blocks))
    out.append('</section>')
    return ''.join(out)


def _render_monthly(section):
    out = [_section_open(section)]
    table = _first(section['blocks'], 'table')
    if table:
        if table['headers'] and table['headers'][0] == '':
            table = dict(table, headers=['Month'] + table['headers'][1:])
        months = [r[0] for r in table['rows']]
        commits = _column_values(table, 'Commits')
        added = _column_values(table, 'Lines added')
        deleted = _column_values(table, 'Lines deleted')
        if commits is not None:
            out.append(_render_columns('Commits per month', months,
                                       [('Commits', commits)]))
        if added is not None and deleted is not None:
            out.append(_render_columns(
                'Lines added and deleted per month', months,
                [('Lines added', added), ('Lines deleted', deleted)]))
        out.append(_render_table(table))
    elif _first(section['blocks'], 'na'):
        out.append(_empty('No monthly contribution data collected.'))
    out.append(_render_generic_blocks(section['blocks']))
    out.append('</section>')
    return ''.join(out)


def _render_tags(section):
    out = [_section_open(section)]
    table = _first(section['blocks'], 'table')
    if table:
        commits = _column_values(table, 'Commits')
        name_col = _find_column(table['headers'], 'Name')
        if commits is not None and name_col is not None and table['rows']:
            out.append(_render_columns(
                'Commits per tag', [r[name_col] for r in table['rows']],
                [('Commits', commits)]))
        out.append(_render_table(table, filterable=len(table['rows']) > 10))
    else:
        out.append(_empty('No tags found.'))
    out.append(_render_generic_blocks(section['blocks'], ('duration',)))
    out.append('</section>')
    return ''.join(out)


def _render_loc(section):
    out = [_section_open(section, 'language types')]
    table = _first(section['blocks'], 'table')
    if table:
        lang_col = _find_column(table['headers'], 'Language')
        share = _column_values(table, 'total%')
        if lang_col is not None and share is not None:
            items = []
            for row, value in zip(table['rows'], share):
                tip = '\n'.join('%s: %s' % (h, c) for h, c in
                                zip(table['headers'], row))
                items.append((row[lang_col], value, tip))
            items.sort(key=lambda item: -item[1])
            out.append(_render_hbars('Share of all lines by language', items,
                                     value_suffix='%'))
        code = _column_values(table, 'Code lines')
        if lang_col is not None and code is not None:
            items = [(row[lang_col], value, '%s: %s code lines' % (
                row[lang_col], _fmt_number(value)))
                for row, value in zip(table['rows'], code) if value > 0]
            items.sort(key=lambda item: -item[1])
            out.append(_render_hbars('Code lines by language', items))
        out.append(_render_table(table))
    elif _first(section['blocks'], 'na'):
        out.append(_empty('No lines of code were counted.'))
    out.append(_render_generic_blocks(section['blocks'], ('duration',)))
    out.append('</section>')
    return ''.join(out)


def _render_files(section):
    out = [_section_open(section, 'files')]
    table = _first(section['blocks'], 'table')
    if table:
        out.append(_render_table(table, filterable=True))
    else:
        out.append(_empty('No files were analyzed.'))
    out.append(_render_generic_blocks(section['blocks']))
    out.append('</section>')
    return ''.join(out)


def _render_errors(section):
    out = [_section_open(section)]
    errors = section.get('errors', [])
    if errors:
        out.append('<ol class="errors">')
        for error in errors:
            out.append('<li><pre>%s</pre></li>' % _esc(error))
        out.append('</ol>')
    else:
        out.append(_empty('No errors reported.'))
    out.append(_render_generic_blocks(section['blocks']))
    out.append('</section>')
    return ''.join(out)


def _render_overview(sections, statistics, preamble, run_config):
    by_key = dict((s['key'], s) for s in sections)
    tiles = []
    if statistics is not None:
        for b in statistics['blocks']:
            if b['type'] == 'kv':
                tiles.append((b['key'], b['value']))
    for key, label in (('authors', 'Authors'), ('tags', 'Tags'),
                       ('loc', 'Language types'), ('files', 'Analyzed files'),
                       ('errors', 'Errors')):
        if key in by_key and by_key[key].get('count') is not None:
            tiles.append((label, _fmt_number(by_key[key]['count'])))
    if preamble is not None:
        duration = _kv(preamble['blocks'], 'Duration')
        if duration is not None:
            tiles.append(('Run duration', duration))
    out = ['<section id="overview"><h2>Overview</h2><div class="tiles">']
    for label, value in tiles:
        out.append('<div class="tile"><span class="tile-label">%s</span>'
                   '<span class="tile-value">%s</span></div>' % (
                       _esc(label), _esc(value)))
    out.append('</div>')
    if statistics is not None:
        rest = [b for b in statistics['blocks'] if b['type'] != 'kv']
        out.append(_render_generic_blocks(rest))
    if preamble is not None:
        out.append(_render_generic_blocks(preamble['blocks'], ('duration',)))
    if run_config:
        out.append('<details class="runconf"><summary>Runtime arguments'
                   '</summary><dl class="kv">')
        for key, value in run_config:
            out.append('<div><dt>%s</dt><dd>%s</dd></div>' % (
                _esc(key), _esc(value)))
        out.append('</dl></details>')
    out.append('</section>')
    return ''.join(out)


RENDERERS = {
    'authors': _render_authors,
    'authors_per_month': _render_authors_per_month,
    'monthly': _render_monthly,
    'tags': _render_tags,
    'loc': _render_loc,
    'files': _render_files,
    'errors': _render_errors,
}


def parse_runtime_conf(text):
    """Parses runtime.conf lines in the form ``name = value,``."""
    pairs = []
    for line in text.splitlines():
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        pairs.append((key.strip(), value.strip().rstrip(',')))
    return pairs


def render_html(parsed, title='Gitdafa statistics', generated=None,
                run_config=None):
    """Renders the parsed log (see :func:`parse_stats_log`) as HTML text."""
    sections = parsed['sections']
    preamble = None
    statistics = None
    body = []
    nav = [('overview', 'Overview')]
    for section in sections:
        if section['key'] == 'preamble':
            preamble = section
        elif section['key'] == 'statistics':
            statistics = section
    for section in sections:
        renderer = RENDERERS.get(section['key'])
        if renderer is None:
            continue
        body.append(renderer(section))
        nav.append((section['key'], section['title']))

    generated = generated or datetime.now()
    nav_html = ''.join('<a href="#%s">%s</a>' % (_esc(k), _esc(t))
                       for k, t in nav)
    raw = ('<section id="raw"><h2>Raw statistics log</h2><details>'
           '<summary>Show the original log</summary><pre class="raw">%s</pre>'
           '</details></section>' % _esc(parsed['raw']))
    return HTML_TEMPLATE.format(
        title=_esc(title),
        generated=_esc(generated.strftime('%Y-%m-%d %H:%M:%S')),
        nav=nav_html,
        overview=_render_overview(sections, statistics, preamble, run_config),
        body=''.join(body),
        raw=raw,
        css=CSS,
        js=JS,
    )


def generate_html_report(stats_file, html_file=None, title=None,
                         runtime_conf=None):
    """
    Reads ``stats_file`` and writes the HTML report next to it (or to
    ``html_file``). ``runtime.conf`` in the same directory is included when
    present. Returns the path of the written HTML file.
    """
    with open(stats_file, encoding='utf-8', errors='replace') as f:
        text = f.read()
    results_dir = os.path.dirname(os.path.abspath(stats_file))
    if html_file is None:
        html_file = os.path.join(results_dir, 'stats.html')
    if title is None:
        folder = os.path.basename(results_dir)
        project = folder.split('_', 1)[1] if '_' in folder else folder
        title = 'Gitdafa statistics: %s' % project
    if runtime_conf is None:
        candidate = os.path.join(results_dir, 'runtime.conf')
        runtime_conf = candidate if os.path.isfile(candidate) else None
    run_config = None
    if runtime_conf:
        with open(runtime_conf, encoding='utf-8', errors='replace') as f:
            run_config = parse_runtime_conf(f.read())
    page = render_html(parse_stats_log(text), title=title,
                       run_config=run_config)
    with open(html_file, encoding='utf-8', mode='w', errors='replace') as f:
        f.write(page)
    return html_file


# --------------------------------------------------------------------------
# Page template
# --------------------------------------------------------------------------

CSS = """
:root {
  color-scheme: light;
  --bg: #f6f6f4; --surface: #fcfcfb; --border: #e2e1dc; --grid: #ebeae6;
  --text: #0b0b0b; --text-2: #52514e; --muted: #7a7974; --accent: #2a78d6;
  --s1: %s; --s2: %s; --track: #ecebe7; --danger: #b42318;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #111110; --surface: #1a1a19; --border: #2f2f2d; --grid: #2a2a28;
    --text: #f0efec; --text-2: #c3c2b7; --muted: #8f8e88; --accent: #3987e5;
    --s1: %s; --s2: %s; --track: #262624; --danger: #f97066;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #111110; --surface: #1a1a19; --border: #2f2f2d; --grid: #2a2a28;
  --text: #f0efec; --text-2: #c3c2b7; --muted: #8f8e88; --accent: #3987e5;
  --s1: %s; --s2: %s; --track: #262624; --danger: #f97066;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
header { padding: 24px 16px 8px; max-width: 1200px; margin: 0 auto; }
header h1 { margin: 0; font-size: 22px; }
header p { margin: 4px 0 0; color: var(--text-2); }
nav { position: sticky; top: 0; z-index: 2; background: var(--bg);
  border-bottom: 1px solid var(--border); }
nav .inner { max-width: 1200px; margin: 0 auto; padding: 8px 16px;
  display: flex; gap: 4px 16px; flex-wrap: wrap; }
nav a { color: var(--text-2); text-decoration: none; font-size: 13px; }
nav a:hover { color: var(--accent); }
main { max-width: 1200px; margin: 0 auto; padding: 8px 16px 48px; }
section { background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 16px 20px; margin: 16px 0; min-width: 0;
  scroll-margin-top: 48px; }
h2 { margin: 0 0 4px; font-size: 17px; }
.count { color: var(--muted); font-weight: 500; font-size: 14px; }
.meta, .note, .empty { color: var(--muted); font-size: 12px; margin: 0 0 12px; }
.empty { font-size: 14px; font-style: italic; }
.tiles { display: grid; gap: 12px; margin-top: 12px;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
.tile { border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; }
.tile-label { display: block; color: var(--text-2); font-size: 12px; }
.tile-value { display: block; font-size: 20px; font-weight: 600;
  overflow-wrap: anywhere; }
dl.kv { display: grid; gap: 4px 16px; margin: 12px 0;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
dl.kv div { display: flex; gap: 8px; min-width: 0; }
dl.kv dt { color: var(--text-2); }
dl.kv dd { margin: 0; overflow-wrap: anywhere; }
.chart { margin: 12px 0 20px; }
.chart figcaption { font-weight: 600; margin-bottom: 8px; }
.legend { display: flex; gap: 16px; color: var(--text-2); font-size: 12px;
  margin-bottom: 4px; }
.sw { display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  margin-right: 6px; vertical-align: -1px; }
.sw.s1, path.s1 { background: var(--s1); fill: var(--s1); }
.sw.s2, path.s2 { background: var(--s2); fill: var(--s2); }
.scroll-x { overflow-x: auto; }
svg.cols { display: block; }
svg .grid { stroke: var(--grid); stroke-width: 1; }
svg .grid.base { stroke: var(--muted); }
svg .tick { fill: var(--text-2); font-size: 11px; }
svg .hit { fill: transparent; }
svg .col:hover .hit { fill: var(--grid); }
.hbars { display: grid; gap: 6px; }
.hbar { display: grid; grid-template-columns: minmax(80px, 200px) 1fr auto;
  gap: 12px; align-items: center; }
.hbar:hover .hbar-label { color: var(--text); }
.hbar-label { color: var(--text-2); overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; font-size: 13px; }
.hbar-track { height: 12px; background: var(--track); border-radius: 0 4px 4px 0; }
.hbar-fill { display: block; height: 100%%; background: var(--s1);
  border-radius: 0 4px 4px 0; min-width: 1px; }
.hbar-value { font-variant-numeric: tabular-nums; font-size: 13px;
  min-width: 56px; text-align: right; }
.table-wrap { overflow-x: auto; border: 1px solid var(--border);
  border-radius: 6px; margin: 8px 0; max-height: 640px; overflow-y: auto; }
table.data { border-collapse: collapse; width: 100%%; font-size: 13px; }
table.data th, table.data td { padding: 6px 10px; text-align: left;
  border-bottom: 1px solid var(--grid); white-space: nowrap; }
table.data th { position: sticky; top: 0; background: var(--surface);
  color: var(--text-2); font-weight: 600; cursor: pointer; user-select: none; }
table.data th:hover { color: var(--text); }
table.data th[aria-sort="ascending"]::after { content: " \\25B2"; font-size: 9px; }
table.data th[aria-sort="descending"]::after { content: " \\25BC"; font-size: 9px; }
table.data .num { text-align: right; font-variant-numeric: tabular-nums; }
table.data tbody tr:hover { background: var(--bg); }
table.data caption { text-align: left; padding: 6px 10px; color: var(--text-2); }
.filter { width: 100%%; max-width: 360px; padding: 6px 10px; margin: 4px 0;
  border: 1px solid var(--border); border-radius: 6px; background: var(--bg);
  color: var(--text); font: inherit; }
.toolbar { display: flex; gap: 8px; margin: 8px 0; }
button { font: inherit; font-size: 12px; padding: 4px 10px; cursor: pointer;
  border: 1px solid var(--border); border-radius: 6px; background: var(--bg);
  color: var(--text); }
details.month { border: 1px solid var(--border); border-radius: 6px;
  padding: 6px 12px; margin: 6px 0; }
details.month summary { cursor: pointer; display: flex; gap: 12px;
  flex-wrap: wrap; align-items: baseline; }
details.month summary span { color: var(--muted); font-size: 12px; }
details summary { cursor: pointer; }
.runconf { margin-top: 12px; }
ol.errors { margin: 8px 0; padding-left: 24px; color: var(--danger); }
ol.errors pre { margin: 0; white-space: pre-wrap; color: var(--text); }
pre.text, pre.raw { white-space: pre; overflow-x: auto; font-size: 12px;
  background: var(--bg); border-radius: 6px; padding: 10px; }
pre.raw { max-height: 640px; }
footer { color: var(--muted); font-size: 12px; text-align: center;
  padding: 0 16px 24px; }
@media (max-width: 600px) {
  section { padding: 12px; }
  .hbar { grid-template-columns: 96px 1fr auto; gap: 8px; }
}
""" % (SERIES[0][0], SERIES[1][0], SERIES[0][1], SERIES[1][1],
       SERIES[0][1], SERIES[1][1])

JS = """
(function () {
  function cellValue(row, index, numeric) {
    var cell = row.cells[index];
    if (!cell) { return numeric ? -Infinity : ''; }
    if (numeric) {
      var v = parseFloat(cell.getAttribute('data-v'));
      return isNaN(v) ? -Infinity : v;
    }
    return cell.textContent.toLowerCase();
  }
  function sortTable(th) {
    var table = th.closest('table');
    var tbody = table.tBodies[0];
    var index = Array.prototype.indexOf.call(th.parentNode.children, th);
    var numeric = th.classList.contains('num');
    var asc = th.getAttribute('aria-sort') !== 'ascending';
    Array.prototype.forEach.call(th.parentNode.children, function (h) {
      h.removeAttribute('aria-sort');
    });
    th.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
    var rows = Array.prototype.slice.call(tbody.rows);
    rows.sort(function (a, b) {
      var x = cellValue(a, index, numeric), y = cellValue(b, index, numeric);
      if (x < y) { return asc ? -1 : 1; }
      if (x > y) { return asc ? 1 : -1; }
      return 0;
    });
    rows.forEach(function (r) { tbody.appendChild(r); });
  }
  document.querySelectorAll('table.sortable th').forEach(function (th) {
    th.addEventListener('click', function () { sortTable(th); });
    th.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); sortTable(th); }
    });
  });
  document.querySelectorAll('input.filter').forEach(function (input) {
    var table = input.nextElementSibling.querySelector('table');
    input.addEventListener('input', function () {
      var q = input.value.toLowerCase();
      Array.prototype.forEach.call(table.tBodies[0].rows, function (r) {
        r.style.display = r.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
      });
    });
  });
  document.querySelectorAll('[data-toggle]').forEach(function (button) {
    button.addEventListener('click', function () {
      var open = button.getAttribute('data-toggle') === 'open';
      button.closest('section').querySelectorAll('details.month')
        .forEach(function (d) { d.open = open; });
    });
  });
})();
"""

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<header>
<h1>{title}</h1>
<p>Report generated by Gitdafa on {generated}</p>
</header>
<nav><div class="inner">{nav}<a href="#raw">Raw log</a></div></nav>
<main>
{overview}
{body}
{raw}
</main>
<footer>Generated from the Gitdafa statistics log.</footer>
<script>{js}</script>
</body>
</html>
"""
