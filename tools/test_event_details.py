import copy
import datetime as dt
import unittest
from event_details import validate_details, render_research


def fixture():
    url='https://example.org/event'
    req=dict(id='demo',label='Working demo',category='material',required=True,stage='application',details='A working prototype.',source_url=url,match_key='project.working_demo')
    return {'sample':dict(purpose='Fund civilian software research.',theme='Useful software.',activities='Build and explain a prototype.',cycle='Current intake',checked_at=dt.date.today().isoformat(),coverage='partial',company=dict(required=True,jurisdiction='Taiwan',entity_types='Company',min_age_months=None,max_age_months=36,age_reference='At application',formation_stage='application',notes='Less than three years old.',source_url=url),limitations=['Full form requires login.'],sources=[dict(url=url,title='Official rules')],requirements=[req],winners=[dict(year=dt.date.today().year-1,name='Example team',description='Built flood monitoring software.',source_url=url)])}


class EventDetailTests(unittest.TestCase):
    def setUp(self):
        self.rows=[dict(id='sample',fit='want'),dict(id='excluded',fit='skip')]
        self.details=fixture()
    def test_excluded_events_get_no_enrichment(self):
        self.details['excluded']=copy.deepcopy(self.details['sample'])
        self.assertEqual(set(validate_details(self.details,self.rows)),{'sample'})
    def test_private_fields_and_unsafe_links_rejected(self):
        for obj in [dict(self.details['sample'],personal_notes='private'),dict(self.details['sample'],requirements=[dict(self.details['sample']['requirements'][0],source_url='javascript:alert(1)')])]:
            with self.assertRaises(ValueError):validate_details({'sample':obj},self.rows)
    def test_conditional_required_and_constraints_are_typed(self):
        req=self.details['sample']['requirements'][0]
        for changes in [dict(required='yes'),dict(constraints={'max_seconds':'three'}),dict(constraints={'invented':True})]:
            with self.assertRaises(ValueError):validate_details({'sample':dict(self.details['sample'],requirements=[dict(req,**changes)])},self.rows)
    def test_research_html_escapes_and_keeps_optional_stages(self):
        self.details['sample']['theme']='<unsafe>'
        self.details['sample']['requirements'][0]['required']=False
        page=render_research(self.details['sample'])
        self.assertIn('&lt;unsafe&gt;',page);self.assertNotIn('<unsafe>',page)
        for text in ['Optional','Working demo','Full form requires login.','Example team','Previous winners','Application steps']:
            self.assertIn(text,page)
    def test_company_rules_are_required_and_visible(self):
        page=render_research(self.details['sample'])
        self.assertIn('Company formation and age',page)
        self.assertIn('Less than three years old.',page)
        broken=dict(self.details['sample']);del broken['company']
        with self.assertRaises(ValueError):validate_details({'sample':broken},self.rows)
    def test_empty_details_do_not_invent_requirements(self):
        self.assertEqual(render_research(None),'')

if __name__=='__main__':unittest.main()
