import hashlib,json,unittest
from pathlib import Path
from pipeline.build import parse
ROOT=Path(__file__).resolve().parents[1]
class OfficialDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads((ROOT/'public/data/specialties.json').read_text(encoding='utf-8'))
    def test_hashes(self):
        for s in self.data['sources']:self.assertEqual(hashlib.sha256((ROOT/s['file']).read_bytes()).hexdigest(),s['sha256'])
    def test_counts_and_names(self):
        self.assertEqual(len(self.data['specialties']),28)
        self.assertEqual(sum(len(s['records']) for s in self.data['specialties']),107)
        for year,count in [(2022,27),(2023,26),(2024,27),(2025,27)]:self.assertEqual(sum(r['year']==year for s in self.data['specialties'] for r in s['records']),count)
    def test_document_spot_checks(self):
        expected={'medicina-interna':{2022:(58.885,81.8815),2023:(59.2857,81.6071),2024:(59.4643,82.5),2025:(51.25,83.3929)},'medicina-de-la-actividad-fisica-y-deportiva':{2023:(68.0357,76.7857)},'otorrinolaringologia-y-cirugia-de-cabeza-y-cuello':{2023:(70.3571,80.7143)}}
        for s in self.data['specialties']:
            for r in s['records']:
                if r['year'] in expected.get(s['id'],{}):self.assertEqual((r['minimum'],r['maximum']),expected[s['id']][r['year']])
    def test_missing_not_zero(self):
        for s in self.data['specialties']:
            for r in s['records']:
                self.assertIsNone(r['applicants']);self.assertIsNone(r['places']);self.assertIsNone(r['comparable_group'])
    def test_all_projections_blocked(self):
        for s in self.data['specialties']:
            for k in ['trend','segmented','forecast','demand_forecast']:self.assertFalse(s['analytics'][k]['available'])
    def test_parser_reproduces_snapshot(self):
        for source in self.data['sources']:
            actual=parse(source)
            expected=[r for s in self.data['specialties'] for r in s['records'] if r['source_id']==source['id']]
            self.assertEqual(sorted(actual,key=lambda r:r['specialty_id']),sorted(expected,key=lambda r:r['specialty_id']))
