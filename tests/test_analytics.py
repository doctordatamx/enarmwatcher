"""Synthetic values here are test fixtures, never shipped as official data."""
import unittest, math
from pipeline.analytics import eligible, pressure, robust_trend, segmented, forecast, convergence, longitudinal_clusters, volatility, rank_stability

def rows(n=16,offset=0):
    return [{'year':2000+i,'minimum':50+i*.2+offset,'maximum':80,'population':'mexicana','stage':'published','comparable_group':'test-reviewed','specialty_id':'test'} for i in range(n)]

class AnalyticsTests(unittest.TestCase):
    def test_pending_comparability_blocks(self):
        r=rows();r[0]['comparable_group']=None
        self.assertFalse(eligible(r)[0]);self.assertFalse(forecast(r)['available'])
    def test_mixed_scales_blocks(self):
        r=rows();r[-1]['comparable_group']='other'
        self.assertFalse(eligible(r)[0])
    def test_population_mismatch_blocks(self):
        r=rows();r[-1]['population']='extranjera'
        self.assertFalse(eligible(r)[0])
    def test_stage_mismatch_blocks(self):
        r=rows();r[-1]['stage']='preliminary'
        self.assertFalse(eligible(r)[0])
    def test_missing_value_blocks(self):
        r=rows();r[3]['minimum']=None
        self.assertFalse(eligible(r)[0])
    def test_gap_blocks(self):
        r=rows();del r[3]
        self.assertFalse(eligible(r)[0])
    def test_duplicate_year_blocks(self):
        r=rows();r[1]['year']=r[0]['year']
        self.assertFalse(eligible(r)[0])
    def test_short_forecast_blocks(self):self.assertFalse(forecast(rows(13))['available'])
    def test_demand_requires_joint_compatible_counts(self):
        self.assertIsNone(pressure({'applicants':100,'places':20}))
        self.assertIsNone(pressure({'applicants':100,'places':0,'demand_comparable':True}))
        self.assertIsNone(pressure({'applicants':None,'places':20,'demand_comparable':True}))
        self.assertEqual(pressure({'applicants':100,'places':20,'demand_comparable':True}),5)
    def test_robust_slope_resists_outlier(self):
        r=rows();r[4]['minimum']=99
        self.assertAlmostEqual(robust_trend(r)['slope'],.2)
        self.assertAlmostEqual(robust_trend(list(reversed(r)))['slope'],.2)
    def test_segmented_detects_hinge(self):
        r=rows(20)
        for i,row in enumerate(r): row['minimum']=45+.1*i+max(i-10,0)*1.5
        fit=segmented(r)
        self.assertTrue(fit['supported']);self.assertEqual(fit['candidate_year'],2010)
    def test_forecast_rolling_origins(self):
        fit=forecast(rows())
        self.assertEqual(fit['backtests'][0]['year'],2006)
        self.assertEqual(fit['backtests'][0]['naive'],51)
        self.assertIn('mae',fit['metrics']['naive'])
        if fit['available']:
            self.assertLessEqual(fit['interval90'][0],fit['point']);self.assertGreaterEqual(fit['interval90'][1],fit['point'])
    def test_no_future_leakage(self):
        r=rows();a=forecast(r);r[-1]['minimum']=10;b=forecast(r)
        self.assertEqual(a['backtests'][0],b['backtests'][0])
    def test_convergence_controls_composition(self):
        panel={str(i):rows(10,i) for i in range(5)}
        panel['0']=panel['0'][1:]
        fit=convergence(panel)
        self.assertTrue(fit['available']);self.assertEqual(fit['years'][0],2001)
        self.assertAlmostEqual(fit['sigma'][0],fit['sigma'][-1])
    def test_cross_specialty_scales_block(self):
        panel={str(i):rows(10,i) for i in range(5)}
        for r in panel['0']:r['comparable_group']='different'
        self.assertFalse(convergence(panel)['available'])
    def test_cluster_reproducible(self):
        panel={str(i):rows(10,i*2) for i in range(6)}
        self.assertEqual(longitudinal_clusters(panel),longitudinal_clusters(panel))
    def test_nonfinite_blocks(self):
        r=rows();r[0]['minimum']=float('nan');self.assertFalse(eligible(r)[0])
    def test_volatility(self):
        result=volatility(rows(8));self.assertTrue(result['available'])
        self.assertAlmostEqual(result['yearly_changes'][0]['absolute'],.2)
        self.assertAlmostEqual(result['range'],1.4)
    def test_rank_stability_with_ties(self):
        panel={str(i):rows(10,i) for i in [0,1,2,3,4]};panel['1']=rows(10)
        result=rank_stability(panel)
        self.assertTrue(result['available']);self.assertEqual(result['ranks']['0'][0],4.5)
        self.assertEqual(result['rank_sd']['0'],0)
    def test_demand_forecast_requires_review(self):
        r=rows()
        for row in r:row['pressure']=5
        self.assertFalse(eligible(r,field='pressure')[0])
    def test_unbalanced_panel_explains_missing_common_years(self):
        panel={str(i):rows(10,i) for i in range(5)};panel['0']=rows(1)
        self.assertFalse(convergence(panel)['available']);self.assertIn('ediciones comunes',convergence(panel)['reason'])
