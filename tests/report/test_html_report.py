import html
import re
import sys

sys.path.append('./')

from report import generate_html_report, parse_stats_log, render_html

SAMPLE_LOG = """Duration: 0:00:01.500000



STATISTICS
Branch: main
All commits: 4
Total days: 40

AUTHORS(2)
Name    Email                Commits    Lines added    Lines deleted
------  -----------------  ---------  -------------  ---------------
Alice   alice@example.com          3            120               10
Bob     bob@example.com            1              5                2
Duration: 00:00:00.010000


AUTHORS CONTRIBUTION PER MONTH

2021 January
-------------
Name    Email                Commits    Lines added    Lines deleted
------  -----------------  ---------  -------------  ---------------
Alice   alice@example.com          2            100                0


2021 February
-------------
Name    Email                Commits    Lines added    Lines deleted
------  -----------------  ---------  -------------  ---------------
Alice   alice@example.com          1             20               10
Bob     bob@example.com            1              5                2





ALL MONTHLY CONTRIBUTION

               Name    Email      Commits    Lines added    Lines deleted
-------------  ------  -------  ---------  -------------  ---------------
2021 January   All     all              2            100                0
2021 February  All     all              2             25               12



TAGS(1)
Name    SHA        Index    Commits
------  -------  -------  ---------
v1.0    abc1234        0          4
Duration: 00:00:00.020000

LOC(2 language types)
Language      Code lines    Comment lines    Empty lines    Text lines    Files count    code%    code+comments%    total%  Extensions found
----------  ------------  ---------------  -------------  ------------  -------------  -------  ----------------  --------  ------------------
Python                90               10              5             0              2       90                90        75  ['.py']
Unknown               10                0              0            30              1       10                10        25  ['', '.cfg']
Duration: 00:00:00.030000

Analyzed 3 different files
File name                Extension    Language      Code lines    Comment lines    Empty lines
-----------------------  -----------  ----------  ------------  ---------------  -------------
/project/my file.py      .py          Python                60                5              3
/project/ERRORS.py       .py          Python                30                5              2
/project/Makefile                     Unknown               10                0              0

ERRORS ['Could not read <binary> & co', "second 'error'"]"""


def _section(parsed, key):
    return [s for s in parsed['sections'] if s['key'] == key][0]


def test_parse_sections_and_counts():
    parsed = parse_stats_log(SAMPLE_LOG)
    keys = [s['key'] for s in parsed['sections']]
    assert keys == ['preamble', 'statistics', 'authors', 'authors_per_month',
                    'monthly', 'tags', 'loc', 'files', 'errors']
    assert _section(parsed, 'authors')['count'] == 2
    assert _section(parsed, 'tags')['count'] == 1
    assert _section(parsed, 'loc')['count'] == 2
    assert _section(parsed, 'files')['count'] == 3
    assert _section(parsed, 'errors')['errors'] == [
        'Could not read <binary> & co', "second 'error'"]


def test_parse_tables_keep_empty_cells_and_spaces():
    parsed = parse_stats_log(SAMPLE_LOG)
    files = _section(parsed, 'files')['blocks'][0]
    assert files['headers'][0] == 'File name'
    assert files['rows'][0][0] == '/project/my file.py'
    assert files['rows'][2] == ['/project/Makefile', '', 'Unknown', '10', '0',
                                '0']
    loc = _section(parsed, 'loc')['blocks'][0]
    assert loc['rows'][1][-1] == "['', '.cfg']"


def test_parse_month_subheadings():
    blocks = _section(parse_stats_log(SAMPLE_LOG), 'authors_per_month')['blocks']
    assert [b['type'] for b in blocks] == ['subheading', 'table',
                                           'subheading', 'table']
    assert blocks[2]['text'] == '2021 February'
    assert len(blocks[3]['rows']) == 2


def test_html_contains_every_value_from_log():
    page = render_html(parse_stats_log(SAMPLE_LOG))
    page = page.split('<section id="raw">')[0]
    visible = html.unescape(re.sub(r'<[^>]+>', ' ', page))
    labels = {'STATISTICS', 'Branch:', 'All', 'commits:', 'Total', 'days:',
              'Duration:'}
    for line in SAMPLE_LOG.splitlines():
        if re.match(r'^\s*-+( +-+)*\s*$', line):
            continue
        for token in line.split():
            if token in labels or token.startswith(('AUTHORS', 'ERRORS',
                                                    'LOC(', 'TAGS(')):
                continue
            assert token in visible, token


def test_html_escapes_and_embeds_raw_log():
    page = render_html(parse_stats_log(SAMPLE_LOG))
    assert 'Could not read <binary>' not in page
    assert 'Could not read &lt;binary&gt; &amp; co' in page
    assert '<section id="raw">' in page


def test_empty_sections_render():
    log = ("Duration: 0:00:00.1\n\n\n\nSTATISTICS\nBranch: main\n"
           "All commits: 1\nTotal days: 0\n\nAUTHORS(0)\nN/A\n"
           "Duration: 00:00:00.000001\n\n\nAUTHORS CONTRIBUTION PER MONTH \n\n"
           "\n\n\nALL MONTHLY CONTRIBUTION \n\nN/A\n\n\n\nTAGS(0)\nN/A\n"
           "Duration: 00:00:00.000001\n\nLOC(0 language types)\nN/A\n"
           "Duration: 00:00:00.000001\n\nAnalyzed 0 different files\nN/A\n\n"
           "ERRORS []")
    page = render_html(parse_stats_log(log))
    assert 'No author data collected.' in page
    assert 'No tags found.' in page
    assert 'No errors reported.' in page


def test_generate_html_report_writes_file(tmp_path):
    results = tmp_path / '2021-01-01-00-00-00_demo'
    results.mkdir()
    stats = results / 'stats.txt'
    stats.write_text(SAMPLE_LOG, encoding='utf-8')
    (results / 'runtime.conf').write_text('projdir = /project,\nhtml = True,\n',
                                          encoding='utf-8')
    out = generate_html_report(str(stats))
    page = open(out, encoding='utf-8').read()
    assert out.endswith('stats.html')
    assert 'Gitdafa statistics: demo' in page
    assert '<dt>projdir</dt><dd>/project</dd>' in page
