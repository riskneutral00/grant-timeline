import unittest
from upsert import upsert
E = dict(id='x', name='X', type='grant', country='TW', organizer='O', url='https://a.b', deadline=None,
         status='rolling', summary='s', first_seen='2026-01-01', last_checked='2026-01-01', source_url='https://a.b', fit='want', fit_reason='', team_min=None, team_max=None, prize='NA')
class T(unittest.TestCase):
    def test_add_and_update_keeps_first_seen(self):
        rows, a, u = upsert([dict(E)], [dict(E, id='y', name='Y')], '2026-10-01')
        self.assertEqual((a, u, rows[1]['first_seen']), (['y'], [], '2026-10-01'))
        rows, a, u = upsert(rows, [dict(E, summary='new')], '2026-11-01')
        self.assertEqual((u, rows[0]['first_seen'], rows[0]['last_checked'], rows[0]['summary']), (['x'], '2026-01-01', '2026-11-01', 'new'))
    def test_bad_entry_rejected(self):
        with self.assertRaises(ValueError): upsert([dict(E)], [dict(E, id='z', country='US')], '2026-10-01')
    def test_want_needs_no_reason(self):
        new = {k: v for k, v in E.items() if k != 'fit_reason'}
        rows, a, _ = upsert([dict(E)], [dict(new, id='w')], '2026-10-01')
        self.assertEqual(rows[1]['fit_reason'], '')
    def test_team_prize_default_to_na(self):
        new = {k: v for k, v in E.items() if k not in ('team_min', 'team_max', 'prize')}
        rows, _, _ = upsert([dict(E)], [dict(new, id='n')], '2026-10-01')
        self.assertEqual((rows[1]['team_min'], rows[1]['team_max'], rows[1]['prize']), (None, None, 'NA'))
if __name__ == '__main__': unittest.main()
