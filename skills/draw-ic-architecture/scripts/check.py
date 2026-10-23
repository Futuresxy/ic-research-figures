#!/usr/bin/env python3
"""Check uncompressed native draw.io structure, not circuit correctness or rendering."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

def check(path):
    tree=ET.parse(path)
    pages=tree.findall('./diagram')
    if not pages: raise ValueError('No diagram pages')
    count=0
    for page in pages:
        cells=page.findall('./mxGraphModel/root/mxCell')
        if not cells: raise ValueError('Expected uncompressed native mxGraphModel')
        ids=[c.get('id') for c in cells]
        if None in ids or len(set(ids))!=len(ids): raise ValueError('Missing/duplicate ID')
        byid={c.get('id'):c for c in cells}
        for c in cells:
            if 'image=' in c.get('style','') or 'shape=image' in c.get('style',''):
                raise ValueError('Image cell found: use editable native shapes')
            for key in ('parent','source','target'):
                if c.get(key) and c.get(key) not in byid: raise ValueError('Dangling '+key)
            seen={c.get('id')}; parent=c.get('parent')
            while parent:
                if parent in seen: raise ValueError('Parent cycle')
                seen.add(parent); parent=byid[parent].get('parent')
            if c.get('vertex')=='1':
                geo=c.find('mxGeometry')
                if geo is None or any(float(geo.get(k,'0'))<=0 for k in ('width','height')):
                    raise ValueError('Invalid vertex geometry')
                count+=1
            if c.get('edge')=='1' and not (c.get('source') and c.get('target')):
                raise ValueError('Edge must stay attached to source and target')
    if not count: raise ValueError('No editable vertices')
    return count

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('files',nargs='+',type=Path)
    for f in p.parse_args().files: print(f'{f}: {check(f)} native vertices; structural checks passed')
