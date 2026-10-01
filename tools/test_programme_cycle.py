import copy
import datetime as dt
import unittest
from programme_cycle import roll_programmes, effective_date, catalogue_name

class ProgrammeCycleTests(unittest.TestCase):
    def setUp(self):
        self.today=dt.date.today();self.past=(self.today-dt.timedelta(days=30)).isoformat()
        self.row={'id':'sample','name':f'Software programme {self.today.year}','fit':'want','status':'closed','deadline':self.past,'summary':'The previous round ended.'}
        self.details={'sample':{'cycle':'Previous intake','requirements':[]}}
    def test_expired_round_becomes_next_year_planning_without_confirmed_deadline(self):
        rows,details=roll_programmes([self.row],self.details,self.today)
        self.assertEqual(rows[0]['status'],'planning');self.assertIsNone(rows[0]['deadline'])
        p=details['sample']['planning'];self.assertEqual(p['year'],self.today.year+1)
        self.assertEqual(p['last_round_deadline'],self.past)
        self.assertIn(str(self.today.year+1),rows[0]['name'])
        self.assertIn('planning',rows[0]['name'].lower())
        self.assertGreaterEqual(effective_date(rows[0],details['sample']),self.today.isoformat())
        self.assertEqual(self.row['status'],'closed');self.assertNotIn('planning',self.details['sample'])
    def test_verified_far_future_date_is_retained_and_excluded_not_rolled(self):
        future=self.today.replace(year=self.today.year+5,day=min(self.today.day,28)).isoformat()
        active=dict(self.row,id='future',status='open',deadline=future)
        excluded=dict(self.row,id='excluded',fit='skip')
        rows,details=roll_programmes([active,excluded],self.details,self.today)
        self.assertEqual(rows[0]['deadline'],future);self.assertEqual(rows[1],excluded)
        self.assertNotIn('excluded',details)
    def test_unknown_old_deadline_does_not_invent_an_estimate(self):
        rows,details=roll_programmes([dict(self.row,deadline=None)],self.details,self.today)
        self.assertIsNone(details['sample']['planning']['estimated_deadline'])
        self.assertEqual(rows[0]['status'],'planning')
    def test_future_year_rollover_keeps_programme_tracked(self):
        previous=dt.date(self.today.year-1,12,31)
        row=dict(self.row,name=f'Software programme {previous.year}',deadline=previous.isoformat())
        rows,details=roll_programmes([row],self.details,self.today)
        future=dt.date(self.today.year+2,1,1)
        updated,new=roll_programmes(rows,details,future)
        self.assertEqual(new['sample']['planning']['year'],future.year)
        self.assertEqual(updated[0]['status'],'planning')
        self.assertGreaterEqual(new['sample']['planning']['estimated_deadline'],future.isoformat())

    def test_passed_planning_window_advances_without_hiding_programme(self):
        previous=dt.date(self.today.year-1,1,15)
        row=dict(self.row,name=f'Software programme {previous.year}',deadline=previous.isoformat())
        before=dt.date(self.today.year,1,1)
        rows,details=roll_programmes([row],self.details,before)
        after=dt.date(self.today.year,2,1)
        advanced,next_details=roll_programmes(rows,details,after)
        self.assertEqual(next_details['sample']['planning']['year'],after.year+1)
        self.assertEqual(advanced[0]['status'],'planning');self.assertIsNone(advanced[0]['deadline'])

    def test_verified_next_call_replaces_planning(self):
        rows,details=roll_programmes([self.row],self.details,self.today)
        actual=dict(rows[0],status='open',deadline=(self.today+dt.timedelta(days=60)).isoformat(),name='Announced new intake')
        updated,new=roll_programmes([actual],details,self.today)
        self.assertEqual(updated[0],actual);self.assertNotIn('planning',new['sample'])

if __name__=='__main__':unittest.main()
