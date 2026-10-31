import json,hashlib,unittest,math
from collections import defaultdict
from pipeline.ingest import ROOT
from pipeline.platform import concentration,binomial_interval,national_aggregate,state_name,clean,academic_pdf
from pipeline.institutional_analytics import cross_section,partial_pooling
from pipeline.receiving_analytics import analyse

class PlatformDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d=json.loads((ROOT/'data/normalized/platform.json').read_text(encoding='utf8'))
    def test_all_raw_hashes(self):
        for s in self.d['sources']:self.assertEqual(hashlib.sha256((ROOT/s['file']).read_bytes()).hexdigest(),s['sha256'])
    def test_real_coverage(self):
        self.assertEqual(self.d['academic_years'],list(range(2001,2026)));self.assertEqual(len(self.d['academic_records']),2528);self.assertEqual(len(self.d['sites']),2544)
        self.assertEqual(self.d['issues'],[])
    def test_academic_uniqueness_and_domains(self):
        seen=set()
        for r in self.d['academic_records']:
            key=(r['id'],r['year']);self.assertNotIn(key,seen);seen.add(key)
            self.assertGreater(r['examined'],0)
            if r['selected'] is not None:self.assertLessEqual(r['selected'],r['examined']);self.assertAlmostEqual(r['rate'],100*r['selected']/r['examined'])
            self.assertIsNone(r['score_comparable_group']);self.assertIsNone(r['rate_comparable_group'])
    def test_official_academic_spot_checks(self):
        for year,exam,selected,score in [(2021,264,163,61.82),(2022,239,122,59.28),(2023,237,143,60.1317),(2024,287,168,59.7014),(2025,242,122,61.6336)]:
            row=next(r for r in self.d['academic_records'] if r['year']==year and r['name']=='UNIV. AUT. DE AGUASCALIENTES');self.assertEqual((row['examined'],row['selected'],row['score']),(exam,selected,score))
    def test_2024_blank_selected_and_2025_observed_zero(self):
        rows=[r for r in self.d['academic_records'] if r['name']=='ESC. MÉDICO - NAVAL SEMAR']
        a=next(r for r in rows if r['year']==2024);b=next(r for r in rows if r['year']==2025)
        self.assertEqual(a['examined'],3);self.assertIsNone(a['selected']);self.assertIsNone(a['rate'])
        self.assertEqual(b['examined'],5);self.assertEqual(b['selected'],0);self.assertEqual(b['rate'],0)
        national=next(r for r in self.d['national'] if r['year']==2024)
        self.assertEqual(national['selected_missing_rows'],1);self.assertEqual(national['selected_observed_subtotal'],18180)
        self.assertIsNone(national['selected']);self.assertIsNone(national['rate'])
    def test_recent_reports_counts_and_totals(self):
        for year,count,examined in [(2024,153,49226),(2025,159,44911)]:
            rows=[r for r in self.d['academic_records'] if r['year']==year]
            self.assertEqual(len(rows),count);self.assertEqual(sum(r['examined'] for r in rows),examined)
        self.assertEqual(next(r for r in self.d['national'] if r['year']==2025)['selected'],15779)
    def test_recent_parser_reproduces_snapshot(self):
        fields=['id','name','state','examined','selected','score','page','original_values']
        for source in self.d['sources']:
            if source['kind']=='academic' and source['year'] in [2024,2025]:
                actual=academic_pdf(source);expected=[r for r in self.d['academic_records'] if r['source_id']==source['id']]
                self.assertEqual([{k:r[k] for k in fields} for r in actual],[{k:r[k] for k in fields} for r in expected])
    def test_medians_not_averaged(self):
        for year in [2005,2006]:
            rows=[r for r in self.d['academic_records'] if r['year']==year];self.assertTrue(all(r['score_statistic']=='median' for r in rows));self.assertIsNone(national_aggregate(rows)['score'])
    def test_missing_selected_not_imputed(self):
        rows=[r for r in self.d['academic_records'] if r['year']==2001];self.assertTrue(any(r['selected'] is None for r in rows));self.assertIsNone(national_aggregate(rows)['selected']);self.assertEqual(national_aggregate(rows)['examined'],18083)
    def test_receiver_totals_by_document(self):
        expected={2023:18167,2024:18207,2025:18515}
        for year,total in expected.items():self.assertEqual(sum(r['places'] for r in self.d['receiving'] if r['year']==year),total)
        self.assertEqual(sum(r['places'] for r in self.d['sites']),18515)
    def test_sedes_reconcile_by_specialty(self):
        matrix=defaultdict(int);sites=defaultdict(int)
        for r in self.d['receiving']:
            if r['year']==2025:matrix[r['specialty_id']]+=r['places']
        for r in self.d['sites']:sites[r['specialty_id']]+=r['places']
        self.assertEqual(dict(matrix),dict(sites))
    def test_no_double_counting_or_geocoding(self):
        self.assertEqual(len({r['code'] for r in self.d['sites']}),len(self.d['sites']))
        for r in self.d['sites']:self.assertIsNone(r['clues']);self.assertIsNone(r['latitude']);self.assertIsNone(r['longitude']);self.assertIsNotNone(state_name(r['state']))
        for rec in self.d['reconciliation']:self.assertEqual(rec['difference'],0)
    def test_public_partitions_valid(self):
        for name in ['national','academic','receiving','atlas','platform-sources','research','receiving-analysis','catalogue']:
            self.assertIsInstance(json.loads((ROOT/'public/data'/f'{name}.json').read_text(encoding='utf8')),dict)
    def test_geographic_metadata(self):
        metadata=json.loads((ROOT/'data/geography_source.json').read_text(encoding='utf8'));geo=ROOT/'public/data/mexico-states.geojson'
        self.assertEqual(hashlib.sha256(geo.read_bytes()).hexdigest(),metadata['public_sha256']);self.assertEqual(len(json.loads(geo.read_text())['features']),32)

class InstitutionalMethodsTests(unittest.TestCase):
    def test_confirmed_redundant_glyph_only(self):
        self.assertEqual(clean('SECRETARÍ(cid:141)A'),'SECRETARÍA')
        self.assertEqual(clean('UNKNOWN(cid:999)'),'UNKNOWN(cid:999)')
    def test_hhi_and_gini(self):
        result=concentration([10,10,10,10]);self.assertEqual(result['hhi'],2500);self.assertAlmostEqual(result['gini'],0);self.assertEqual(result['top3'],75)
        self.assertIsNone(concentration([0,0])['hhi'])
    def test_wilson_bounds(self):
        for k,n in [(0,10),(10,10),(5,10),(1,1000)]:
            lo,hi=binomial_interval(k,n);self.assertGreaterEqual(lo,-1e-12);self.assertLessEqual(hi,100+1e-12);self.assertLess(lo,hi)
        self.assertIsNone(binomial_interval(None,10));self.assertIsNone(binomial_interval(0,0))
    def test_variance_decomposition_identity(self):
        rows=[{'id':str(i),'examined':100+i*10,'selected':i*4,'rate':100*i*4/(100+i*10),'state':'A' if i<6 else 'B'} for i in range(12)]
        r=cross_section(rows);v=r['variance_decomposition'];self.assertAlmostEqual(v['total'],v['between']+v['within'],places=10);self.assertLessEqual(abs(r['spearman']),1)
    def test_pooling_intervals_and_small_samples(self):
        self.assertFalse(partial_pooling([])['available'])
        rows=[{'id':str(i),'examined':100+i*10,'selected':i*4} for i in range(12)];r=partial_pooling(rows)
        self.assertTrue(r['available'])
        for row in r['institutions']:self.assertTrue(0<=row['pooled']<=100);self.assertTrue(0<=row['interval95'][0]<=row['interval95'][1]<=100)
    def test_correspondence_and_diversity_reproducible(self):
        rows=[{'institution_id':str(i),'institution_name':str(i),'specialty_id':str(j),'places':(i+j+1)*2} for i in range(6) for j in range(8)]
        a=analyse(rows);b=analyse(rows);self.assertEqual(a,b);self.assertLessEqual(sum(a['correspondence']['inertia_explained']),1+1e-10)
        for r in a['institutions']:self.assertTrue(1<=r['effective_specialties']<=8)
