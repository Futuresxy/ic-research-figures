import copy
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS=Path(__file__).resolve().parents[1]/'skills/draw-ic-architecture/scripts'
sys.path.insert(0,str(SCRIPTS))
from diagram import write_diagram
from check import check
from plot import pareto_mask, read_data, svg_plot

class Figures(unittest.TestCase):
    def test_dominance_ties(self):
        self.assertEqual(pareto_mask([(1,3),(2,2),(3,1),(3,3),(2,2)]),
                         [True,True,True,False,True])

    def test_native_and_overwrite_protection(self):
        spec={'name':'Test','width':500,'height':300,
              'nodes':[{'id':'a','label':'A & B','x':10,'y':10,'w':100,'h':60},
                       {'id':'b','label':'C','x':200,'y':10,'w':100,'h':60}],
              'edges':[{'id':'e','source':'a','target':'b'}]}
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'test';write_diagram(spec,out)
            self.assertEqual(check(out.with_suffix('.drawio')),2)
            with self.assertRaises(FileExistsError):write_diagram(spec,out)
            bad=copy.deepcopy(spec);bad['edges'][0]['target']='missing'
            with self.assertRaises(ValueError):write_diagram(bad,Path(d)/'bad')

    def test_cycle_rejected(self):
        spec={'nodes':[{'id':'a','parent':'b','w':10,'h':10,'role':'group'},
                       {'id':'b','parent':'a','w':10,'h':10,'role':'group'}]}
        with self.assertRaises(ValueError):write_diagram(spec,Path('/tmp/not-written'))

    def test_infeasible_and_data_edit(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'demo.csv'
            p.write_text('design,family,area_mm2,latency_ms,feasible\nA,F,10,5,true\nB,F,1,1,false\n')
            rows=read_data(p,'dse')
            self.assertEqual([r['design'] for r in rows if r.get('pareto')],['A'])
            svg_plot(rows,'dse',d/'before',{})
            p.write_text(p.read_text().replace('10,5','10,7'))
            svg_plot(read_data(p,'dse'),'dse',d/'after',{})
            self.assertNotEqual((d/'before.svg').read_bytes(),(d/'after.svg').read_bytes())

    def test_mixed_units_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'data.csv'
            p.write_text('design,component,value,unit\nA,compute,1,W\nA,memory,2,mm2\n')
            with self.assertRaises(ValueError):read_data(p,'breakdown')

if __name__=='__main__':unittest.main()

