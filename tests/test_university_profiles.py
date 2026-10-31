import json,unittest
from pipeline.ingest import ROOT
from pipeline.institutional_analytics import profile_analysis

class UniversityProfileTests(unittest.TestCase):
    def test_panamericana_actual_diagnostics(self):
        data=json.loads((ROOT/'public/data/academic.json').read_text(encoding='utf8'))
        u=next(u for u in data['universities'] if u['id']=='ciudad-de-mexico-univ-panamericana')
        result=profile_analysis(u['records'])
        self.assertEqual(result['years'],list(range(2016,2026)))
        self.assertEqual(result['missing_years'],[])
        last=result['changes'][-1]
        self.assertEqual(last['examined_change'],-9)
        self.assertAlmostEqual(last['rate_change_pp'],65-100*38/49)
        self.assertEqual(len(result['unreviewed_years']),10)
        for model in result['models'].values():self.assertFalse(model['available'])
        self.assertTrue(result['models']['segmented']['checks'][0]['passed'])
        self.assertFalse(result['models']['forecast']['checks'][0]['passed'])
        self.assertTrue(result['exploratory_models']['trend']['available'])
        self.assertTrue(result['exploratory_models']['segmented']['available'])
        self.assertFalse(result['exploratory_models']['forecast']['available'])
        self.assertFalse(result['exploratory_models']['trend']['comparability_approved'])
        self.assertTrue(all(r['rate_comparable_group'] is None for r in u['records']))

    def test_changes_do_not_bridge_gaps_or_missing_values(self):
        def row(year,rate):return {'year':year,'rate':rate,'examined':20,'source_id':'fixture','rate_comparable_group':None}
        result=profile_analysis([row(2025,50),row(2022,40),row(2024,None)])
        self.assertEqual(result['missing_years'],[2023])
        self.assertEqual(result['missing_rate_years'],[2024])
        self.assertIsNone(result['changes'][1]['examined_change'])
        self.assertIsNone(result['changes'][2]['rate_change_pp'])
        self.assertEqual(result['changes'][2]['examined_change'],0)
        self.assertFalse(result['exploratory_models']['trend']['available'])
        self.assertFalse(result['exploratory_models']['segmented']['available'])

    def test_public_diagnostics_cover_every_identity(self):
        profiles=json.loads((ROOT/'public/data/academic-profiles.json').read_text(encoding='utf8'))
        data=json.loads((ROOT/'public/data/academic.json').read_text(encoding='utf8'))
        self.assertEqual(set(profiles['institutions']),{u['id'] for u in data['universities']})
