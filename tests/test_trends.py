import json,unittest
from pipeline.ingest import ROOT
from pipeline.trends import model_checks,observation,series

class TrendCoverageTests(unittest.TestCase):
    def read(self,name):return json.loads((ROOT/'public/data'/f'{name}.json').read_text(encoding='utf8'))
    def test_coverage_matches_current_datasets(self):
        index=self.read('trends-index');actual=self.read('platform')
        self.assertEqual(index['datasets']['national']['years'],actual['academic_years'])
        self.assertEqual(index['datasets']['universities']['records'],len(actual['academic_records']))
        self.assertEqual(index['datasets']['national']['last_year'],2025)
        self.assertEqual(index['datasets']['specialties']['years'],[2022,2023,2024,2025])
        self.assertEqual(index['datasets']['receiving']['years'],[2023,2024,2025])
    def test_national_new_editions_and_missing_selected(self):
        entity=self.read('trends-national')['entities'][0]
        volume=entity['series']['examined'];self.assertEqual(volume['coverage']['editions'],25)
        self.assertEqual(next(r['value'] for r in volume['records'] if r['year']==2025),44911)
        selected=entity['series']['selected'];r=next(r for r in selected['records'] if r['year']==2024)
        self.assertIsNone(r['value']);self.assertIn('18180',r['note'])
        checks={c['id']:c for c in volume['models']['forecast']['checks']}
        self.assertTrue(checks['length']['passed']);self.assertFalse(checks['comparability']['passed'])
        self.assertFalse(volume['models']['forecast']['available'])
    def test_every_new_source_has_traceability(self):
        data=self.read('trends-national');sources={s['id']:s for s in data['sources']}
        for year in [2024,2025]:
            r=next(r for r in data['entities'][0]['series']['examined']['records'] if r['year']==year)
            self.assertEqual(len(r['source_ids']),1)
            s=sources[r['source_ids'][0]];self.assertEqual(s['year'],year);self.assertEqual(len(s['sha256']),64)
    def test_extra_editions_do_not_enable_unreviewed_models(self):
        rows=[observation(y,50.,[]) for y in range(2001,2026)]
        result=series(rows,'%',True)
        for model in result['models'].values():self.assertFalse(model['available'])
    def test_approved_trend_and_all_blockers(self):
        rows=[observation(2000+i,50+i*.5,[],group='fixture-reviewed') for i in range(8)]
        result=series(rows,'%',True);self.assertTrue(result['models']['trend']['available']);self.assertAlmostEqual(result['models']['trend']['slope'],.5)
        rows[1]['value']=None;rows[2]['comparable_group']=None
        checks={c['id']:c for c in model_checks(rows,14)}
        self.assertFalse(checks['length']['passed']);self.assertFalse(checks['complete']['passed']);self.assertFalse(checks['comparability']['passed']);self.assertTrue(checks['consecutive']['passed'])
