import copy,json,unittest
from pipeline.ingest import ROOT
from pipeline.university_identity import university_profiles

class UniversityIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads((ROOT/'data/normalized/platform.json').read_text(encoding='utf8'))
    def test_panamericana_history_and_original_fields(self):
        original=copy.deepcopy(self.data['academic_records'])
        profiles=university_profiles(original,self.data['sources'])
        u=next(u for u in profiles if u['id']=='ciudad-de-mexico-univ-panamericana')
        self.assertEqual([r['year'] for r in u['records']],list(range(2002,2026)))
        row=next(r for r in u['records'] if r['year']==2004)
        self.assertEqual((row['examined'],row['selected']),(32,18))
        self.assertEqual(row['id'],'distrito-federal-universidad-panamericana')
        self.assertEqual(row['state_original'],'DISTRITO FEDERAL')
        self.assertIsNone(next(r for r in u['records'] if r['year']==2009)['state'])
        self.assertEqual(original,self.data['academic_records'])
        self.assertEqual(sum(len(u['records']) for u in profiles),2528)
        self.assertEqual(len([u for u in profiles if 'PANAMERICANA' in u['name'].upper()]),1)
    def test_changed_sources_and_duplicate_year_fail_closed(self):
        sources=copy.deepcopy(self.data['sources'])
        next(s for s in sources if s['year']==2004 and s['kind']=='academic')['sha256']='changed'
        with self.assertRaises(ValueError):university_profiles(self.data['academic_records'],sources)
        duplicate=next(r for r in self.data['academic_records'] if r['id']=='distrito-federal-universidad-panamericana' and r['year']==2004)
        with self.assertRaises(ValueError):university_profiles(self.data['academic_records']+[duplicate],self.data['sources'])
