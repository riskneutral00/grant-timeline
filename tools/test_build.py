import copy
import unittest
from build import validate, normalized, sort_key, render

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
    def test_skip_section(self):
        page=render([self.r, dict(self.r, id='s', name='Skipped one', fit='skip', fit_reason='Needs HKID')],'{{TABLE}}')
        want, skip = page.split('<details')
        self.assertIn('data-id="x"', want); self.assertNotIn('Skipped one', want)
        self.assertIn('Skipped one', skip); self.assertIn('Needs HKID', skip)
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
    def test_team_and_prize_columns(self):
        page = render([dict(self.r, team_min=1, team_max=2, prize='NT$700,000 total'), dict(self.r, id='y', team_min=1, team_max=1), dict(self.r, id='z')], '{{TABLE}}')
        self.assertIn('<th>Team size</th><th>Prize / money</th>', page)
        self.assertIn('<td>1–2</td><td>NT$700,000 total</td>', page)
        self.assertIn('<td>Solo OK</td>', page)
        self.assertIn('<td>NA</td><td>NA</td>', page)
    def test_template_invalid(self):
        with self.assertRaises(ValueError): render([self.r],'No marker')

if __name__=='__main__': unittest.main()
