import copy
import unittest
from build import validate, normalized, sort_key, render

class BuildTests(unittest.TestCase):
    def setUp(self):
        self.r = dict(id='x', name='<unsafe>', type='grant', country='TW', organizer='Org', url='https://example.org/', deadline=None, status='rolling', summary='A & B', first_seen='2026-09-18', last_checked='2026-09-18', source_url='https://example.org/', fit='want', fit_reason='')
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
    def test_template_invalid(self):
        with self.assertRaises(ValueError): render([self.r],'No marker')

if __name__=='__main__': unittest.main()
