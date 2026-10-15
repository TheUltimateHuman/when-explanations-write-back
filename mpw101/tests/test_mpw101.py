import importlib.util
import sys
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'scripts'/'mpw101.py'
spec=importlib.util.spec_from_file_location('mpw101',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class FrozenTests(unittest.TestCase):
    def test_old_paired_exact(self):
        self.assertAlmostEqual(m.exact_test(11,3),0.057373046875)
    def test_zero(self):
        self.assertEqual(m.exact_test(0,0),1.0)
    def test_semantic_mapping(self):
        f={'opts':['B','A'],'m1':{'A':'RIGHT','B':'LEFT'},'m2':{'A':'LEFT','B':'RIGHT'}}
        self.assertEqual(m.code_for_side(f['m1'],'LEFT'),'B')
        self.assertEqual(m.code_for_side(f['m2'],'LEFT'),'A')
        self.assertIn('B means LEFT',m.family_prompt(f,f['m1']))
    def test_strict_sign_fidelity(self):
        row={'idx':32,'report':{'side':'LEFT'},'base':{'D':0.0},'m1_selected':{'D':0.01}}
        self.assertEqual(m.family_summary(row)['F0'],0)
        self.assertEqual(m.family_summary(row)['F1'],1)
        self.assertEqual(m.family_summary(row)['F1_0.02'],0)
    def test_reproducible_manifest_and_historical_exclusion(self):
        # Mock 3,400 text examples each label; source labels 0/1 with realistic-length unique strings.
        train=[{'label':y,'sentence':f'This unique movie sentence number {j} has label {y}.'}
               for y in (0,1) for j in range(3400)]
        validation=[{'label':y,'sentence':f'This unique movie sentence number {j} has label {y}.'}
               for y in (0,1) for j in (10,100,1000)]
        a,b,j1,p1=m.sampled_families(train,validation)
        a2,b2,j2,p2=m.sampled_families(train,validation)
        self.assertEqual(j1,j2)
        self.assertEqual(p1['manifest_sha256'],p2['manifest_sha256'])
        self.assertEqual(len(a),32);self.assertEqual(len(b),256)
        self.assertEqual(sum(z['label']==1 for z in b),128)
        alltexts=[m.text_key(z[k]) for z in a+b for k in ('left','right','flip_left','flip_right')]
        self.assertEqual(len(set(alltexts)),1152)
        self.assertNotIn(m.text_key(validation[0]['sentence']),alltexts)
    def test_data_identity_256(self):
        # Construct synthetic rows to test exact accounting, deliberately not a real experiment.
        rows=[]
        for i in range(256):
            if i<23:pre,post=-0.3,0.3
            elif i<31:pre,post=0.3,-0.3
            elif i<150:pre,post=-0.3,-0.3
            else:pre,post=0.3,0.3
            a={'D':pre,'acc':1,'sensitivity':8.0}
            b={'D':post,'acc':1,'sensitivity':8.0}
            rows.append({'idx':i,'report':{'side':'LEFT'},'base':a,'base_repeat':a,
              'm1_selected':b,'m1_left':b,'m1_right':a,'m2_left':b,'m2_right':a,
              'free_A':a,'free_B':a})
        out=m.aggregate(rows)
        self.assertEqual(out['table']['01'],23)
        self.assertEqual(out['table']['10'],8)
        self.assertEqual(out['n'],256)
        self.assertAlmostEqual(out['s'],out['q']+out['C']-out['L'])

if __name__=='__main__':unittest.main()
