import re
import unittest
from translate import english, FIELDS

R = dict(id='x', name='臺北秋季程式設計節', organizer='Org', summary='隊伍 4-5 人', prize='NA', fit_reason='')

class TranslateTests(unittest.TestCase):
    def fake(self, calls):
        def tr(texts):
            calls.append(list(texts))
            return [re.sub('[\u4e00-\u9fff]+', 'zh', f'EN({t})'.replace('臺北秋季程式設計節', 'Taipei Codefest')) for t in texts]
        return tr

    def test_translates_only_non_english_and_keeps_source(self):
        calls, cache = [], {}
        out = english([R], cache, self.fake(calls))
        self.assertEqual(out[0]['name'], 'EN(Taipei Codefest)')
        self.assertEqual(out[0]['organizer'], 'Org')
        self.assertEqual(R['name'], '臺北秋季程式設計節')  # stored data untouched
        self.assertEqual(calls, [sorted(['臺北秋季程式設計節', '隊伍 4-5 人'])])

    def test_cache_reused_no_second_call(self):
        calls, cache = [], {}
        english([R], cache, self.fake(calls))
        english([R], cache, self.fake(calls))
        self.assertEqual(len(calls), 1)

    def test_changed_source_retranslated_old_kept(self):
        calls, cache = [], {}
        english([R], cache, self.fake(calls))
        out = english([dict(R, summary='隊伍 1-2 人')], cache, self.fake(calls))
        self.assertEqual(calls[-1], ['隊伍 1-2 人'])
        self.assertIn('隊伍 4-5 人', cache)
        self.assertNotRegex(out[0]['summary'], '[一-鿿]')

    def test_bad_translation_rejected(self):
        with self.assertRaises(ValueError):
            english([R], {}, lambda texts: list(texts))  # "translation" still Chinese
        with self.assertRaises(ValueError):
            english([R], {}, lambda texts: ['only one'])

    def test_no_translator_means_cache_only(self):
        with self.assertRaises(ValueError):
            english([R], {}, None)

    def test_fields(self):
        self.assertEqual(set(FIELDS), {'name', 'organizer', 'summary', 'prize', 'fit_reason'})

if __name__ == '__main__':
    unittest.main()
