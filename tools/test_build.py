import copy
import datetime as dt
from html.parser import HTMLParser
import unittest
from build import validate, normalized, sort_key, render, render_detail, program_path

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.r = dict(id='x', name='<unsafe>', type='grant', country='TW', organizer='Org', url='https://example.org/', deadline=None, status='rolling', summary='A & B', first_seen='2026-09-18', last_checked='2026-09-18', source_url='https://example.org/', fit='want', fit_reason='', team_min=None, team_max=None, prize='NA')
    def test_valid(self):
        self.assertEqual(len(validate([self.r])), 1)
    def test_duplicate(self):
        with self.assertRaises(ValueError): validate([self.r, self.r])
    def test_invalid(self):
        for k,v in [('country','US'),('type','loan'),('status','unknown'),('url','javascript:alert(1)'),('deadline','2026-02-30')]:
            r=dict(self.r, **{k:v})
            with self.assertRaises(ValueError): validate([r])
    def test_expiry_retains(self):
        rows=normalized([dict(self.r,deadline='2026-09-17',status='open')],'2026-09-18')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['status'],'closed')
    def test_sort(self):
        rows=[dict(self.r,status=s,deadline=d,id=i) for i,s,d in [('closed','closed','2020-01-01'),('rolling','rolling',None),('late','open','2026-12-01'),('early','upcoming','2026-10-01'),('unknown','upcoming',None)]]
        self.assertEqual([r['id'] for r in sorted(rows,key=sort_key)],['early','late','unknown','rolling','closed'])
    def test_escape_template(self):
        page=render([self.r],'<h1>Keep this</h1>{{TABLE}}<p>Plan</p>')
        self.assertIn('&lt;unsafe&gt;',page)
        self.assertIn('A &amp; B',page)
        self.assertTrue(page.startswith('<h1>Keep this</h1>'))
        self.assertTrue(page.endswith('<p>Plan</p>'))
    def test_fit(self):
        for r in [dict(self.r, fit='maybe'), dict(self.r, fit='skip', fit_reason='')]:
            with self.assertRaises(ValueError): validate([r])
        self.assertEqual(len(validate([dict(self.r, fit='skip', fit_reason='HK university teams only')])), 1)
    def test_all_records_remain_accessible(self):
        page=render([self.r, dict(self.r, id='s', name='Skipped one', fit='skip', fit_reason='Needs HKID')], '{{TABLE}}')
        self.assertIn('data-id="x"', page)
        self.assertIn('data-id="s"', page)
        self.assertIn('data-fit="skip"', page)
        self.assertIn('Needs HKID', page)
    def test_program_links_open_separate_detail_pages(self):
        class Links(HTMLParser):
            def __init__(self):
                super().__init__(); self.links = []
            def handle_starttag(self, tag, attrs):
                if tag == 'a': self.links.append(dict(attrs))
        parser = Links(); parser.feed(render([self.r], '{{TABLE}}'))
        link = next(a for a in parser.links if a.get('href') == program_path(self.r))
        self.assertEqual(link['target'], '_blank')
        self.assertIn('noopener', link['rel'])
    def test_detail_has_full_facts_and_safe_sources(self):
        row = dict(self.r, summary='Long explanation. Full requirements & conditions.', fit='skip', fit_reason='Needs HKID', prize='Up to $123,456')
        page = render_detail(row)
        for value in ['&lt;unsafe&gt;', 'Full requirements &amp; conditions.', 'Needs HKID', 'Up to $123,456', 'https://example.org/', 'Not announced']:
            self.assertIn(value, page)
        self.assertNotIn('<unsafe>', page)
    def test_safe_stable_program_paths(self):
        path = program_path(dict(self.r, id='../escape'))
        self.assertTrue(path.startswith('programs/'))
        self.assertNotIn('..', path)
        self.assertEqual(path, program_path(dict(self.r, id='../escape')))
    def test_deadlines_increase_inside_directory(self):
        today = dt.date.today()
        early = (today + dt.timedelta(days=4)).isoformat()
        late = (today + dt.timedelta(days=12)).isoformat()
        page = render([dict(self.r,id='late',deadline=late,status='open'),dict(self.r,id='early',deadline=early,status='upcoming')], '{{TABLE}}')
        self.assertLess(page.index('data-id="early"'), page.index('data-id="late"'))
    def test_render_refuses_chinese(self):
        with self.assertRaises(ValueError): render([dict(self.r, name='臺北')], '{{TABLE}}')
    def test_validate_allows_source_language(self):
        self.assertEqual(len(validate([dict(self.r, summary='隊伍 4-5 人')])), 1)
    def test_team_rule(self):
        with self.assertRaises(ValueError): validate([dict(self.r, team_min=3, team_max=10)])
        with self.assertRaises(ValueError): validate([dict(self.r, team_min=2, team_max=1)])
        with self.assertRaises(ValueError): validate([dict(self.r, team_min='2')])
        self.assertEqual(len(validate([dict(self.r, team_min=4, team_max=5, fit='skip', fit_reason='Teams of 4-5 required.')])), 1)
        self.assertEqual(len(validate([dict(self.r, team_min=1, team_max=6)])), 1)
    def test_key_facts_and_unknown_values(self):
        page = render([dict(self.r, team_min=1, team_max=2, prize='NT$700,000 total'), dict(self.r, id='y', team_min=1, team_max=1), dict(self.r, id='z')], '{{TABLE}}')
        self.assertIn('1–2', page)
        self.assertIn('NT$700,000 total', page)
        self.assertIn('Solo OK', page)
        self.assertIn('Not specified', page)
        self.assertIn('Not announced', page)
    def test_company_columns_have_separate_formation_and_age_values(self):
        from test_event_details import fixture
        details=fixture();details['x']=details.pop('sample')
        page=render([self.r],'{{TABLE}}',details)
        self.assertIn('class="company-formation"',page)
        self.assertIn('class="company-age"',page)
        self.assertIn('Less than three years old.',page)
        excluded=render([dict(self.r,fit='skip',fit_reason='Not eligible')],'{{TABLE}}',details)
        self.assertNotIn('Less than three years old.',excluded)

    def test_template_invalid(self):
        with self.assertRaises(ValueError): render([self.r],'No marker')

if __name__=='__main__': unittest.main()
