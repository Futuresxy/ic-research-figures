#!/usr/bin/env python3
"""Generate editable mxGraph objects and a deterministic SVG preview (stdlib)."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

COLORS = {'group': '#FFFFFF', 'memory': '#E6F2E8', 'compute': '#DDEBF7',
          'control': '#FCE8D5', 'io': '#ECEFF1'}

def validate(spec):
    nodes = spec['nodes']
    ids = [n['id'] for n in nodes] + [e['id'] for e in spec.get('edges', [])]
    if len(set(ids)) != len(ids) or any(i in ('0', '1') for i in ids):
        raise ValueError('IDs must be unique and not 0/1')
    byid = {n['id']: n for n in nodes}
    for n in nodes:
        if n['w'] <= 0 or n['h'] <= 0:
            raise ValueError('Node dimensions must be positive')
        if n.get('role', 'compute') not in COLORS:
            raise ValueError('Unknown node role')
        seen = {n['id']}
        parent = n.get('parent')
        while parent:
            if parent not in byid or parent in seen:
                raise ValueError('Missing parent or containment cycle')
            if byid[parent].get('role') != 'group':
                raise ValueError('Parents must be groups')
            seen.add(parent)
            parent = byid[parent].get('parent')
    for e in spec.get('edges', []):
        if e['source'] not in byid or e['target'] not in byid:
            raise ValueError('Unknown edge endpoint')
        for key in ('exit', 'entry'):
            xy = e.get(key, [1, .5] if key == 'exit' else [0, .5])
            if len(xy) != 2 or not all(0 <= v <= 1 for v in xy):
                raise ValueError('Ports must be normalized x,y pairs')
    return byid

def absolute(n, byid):
    x, y = n['x'], n['y']
    while n.get('parent'):
        n = byid[n['parent']]
        x, y = x+n['x'], y+n['y']
    return x, y

def write_diagram(spec, out, force=False):
    byid = validate(spec)
    out = Path(out)
    paths = [out.with_suffix('.drawio'), out.with_suffix('.svg')]
    if not force and any(p.exists() for p in paths):
        raise FileExistsError('Refusing overwrite: preserve manual edits; use a new output name')
    out.parent.mkdir(parents=True, exist_ok=True)
    mxfile = ET.Element('mxfile', host='app.diagrams.net')
    diagram = ET.SubElement(mxfile, 'diagram', id='page-1', name=spec['name'])
    model = ET.SubElement(diagram, 'mxGraphModel', grid='1', gridSize='10', page='1',
                          pageWidth=str(spec['width']), pageHeight=str(spec['height']))
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')
    # Containers first, then leaves; parent references remain stable across edits.
    def depth(n):
        return 1 + depth(byid[n['parent']]) if n.get('parent') else 0
    nodes = sorted(spec['nodes'], key=depth)
    for n in nodes:
        role = n.get('role', 'compute')
        style = ('rounded=0;whiteSpace=wrap;html=0;fontFamily=Arial;fontSize=14;'
                 'strokeColor=#334155;strokeWidth=1.2;fillColor='+COLORS[role]+';')
        if role == 'group':
            style += 'container=1;collapsible=0;recursiveResize=0;verticalAlign=top;spacingTop=8;'
        cell = ET.SubElement(root, 'mxCell', id=n['id'], value=n['label'],
                             style=style, vertex='1', parent=n.get('parent', '1'))
        ET.SubElement(cell, 'mxGeometry', x=str(n['x']), y=str(n['y']),
                      width=str(n['w']), height=str(n['h']), attrib={'as': 'geometry'})
    for e in spec.get('edges', []):
        ex, ey = e.get('exit', [1, .5]); ix, iy = e.get('entry', [0, .5])
        style = ('edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;'
                 'fontFamily=Arial;fontSize=12;labelBackgroundColor=#FFFFFF;'
                 f'exitX={ex};exitY={ey};entryX={ix};entryY={iy};'
                 'strokeColor=#334155;'+('dashed=1;' if e.get('kind') == 'control' else ''))
        cell = ET.SubElement(root, 'mxCell', id=e['id'], value=e.get('label', ''),
                             style=style, edge='1', parent='1',
                             source=e['source'], target=e['target'])
        geo = ET.SubElement(cell, 'mxGeometry', relative='1', attrib={'as':'geometry'})
        if e.get('waypoints'):
            arr = ET.SubElement(geo, 'Array', attrib={'as': 'points'})
            for x, y in e['waypoints']:
                ET.SubElement(arr, 'mxPoint', x=str(x), y=str(y))
    ET.indent(mxfile)
    ET.ElementTree(mxfile).write(paths[0], encoding='utf-8', xml_declaration=True)
    svg = ET.Element('svg', xmlns='http://www.w3.org/2000/svg',
                     viewBox=f"0 0 {spec['width']} {spec['height']}",
                     width=str(spec['width']), height=str(spec['height']))
    ET.SubElement(svg, 'rect', width='100%', height='100%', fill='white')
    defs = ET.SubElement(svg, 'defs')
    marker = ET.SubElement(defs, 'marker', id='arrow', viewBox='0 0 10 10',
                           refX='9', refY='5', markerWidth='6', markerHeight='6', orient='auto')
    ET.SubElement(marker, 'path', d='M 0 0 L 10 5 L 0 10 z', fill='#334155')
    for n in nodes:
        x, y = absolute(n, byid); role = n.get('role', 'compute')
        g = ET.SubElement(svg, 'g', id=n['id'])
        ET.SubElement(g, 'rect', x=str(x), y=str(y), width=str(n['w']), height=str(n['h']),
                      fill=COLORS[role], stroke='#334155', attrib={'stroke-width':'1.2'})
        lines = n['label'].split('\n')
        start = y+20 if role == 'group' else y+n['h']/2-8*(len(lines)-1)+5
        for j, line in enumerate(lines):
            t = ET.SubElement(g, 'text', x=str(x+n['w']/2), y=str(start+16*j),
                              fill='#17212B', attrib={'font-family':'Arial,sans-serif',
                              'font-size':'14','text-anchor':'middle'})
            t.text = line
    for e in spec.get('edges', []):
        a, b = byid[e['source']], byid[e['target']]
        ax, ay = absolute(a, byid); bx, by = absolute(b, byid)
        ex, ey = e.get('exit', [1,.5]); ix, iy = e.get('entry', [0,.5])
        start = (ax+ex*a['w'], ay+ey*a['h']); end = (bx+ix*b['w'], by+iy*b['h'])
        middle = e.get('waypoints')
        if middle is None:
            mx = (start[0]+end[0])/2
            middle = [(mx, start[1]), (mx, end[1])]
        pts = [start]+list(middle)+[end]
        attrs = {'id':e['id'], 'points':' '.join(f'{x},{y}' for x,y in pts),
                 'fill':'none','stroke':'#334155','stroke-width':'1.3','marker-end':'url(#arrow)'}
        if e.get('kind') == 'control': attrs['stroke-dasharray'] = '5 4'
        ET.SubElement(svg, 'polyline', attrs)
        if e.get('label'):
            # Put label above the longest horizontal segment.
            segments = list(zip(pts, pts[1:]))
            p, q = max(segments, key=lambda pq: abs(pq[1][0]-pq[0][0]))
            t = ET.SubElement(svg, 'text', x=str((p[0]+q[0])/2), y=str((p[1]+q[1])/2-7),
                              attrib={'font-family':'Arial,sans-serif','font-size':'11',
                                      'text-anchor':'middle','fill':'#17212B'})
            t.text=e['label']
    ET.indent(svg)
    ET.ElementTree(svg).write(paths[1], encoding='utf-8', xml_declaration=True)
    return paths

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('spec', type=Path); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--force', action='store_true', help='Explicitly replace outputs; loses manual edits')
    args=p.parse_args()
    for path in write_diagram(json.loads(args.spec.read_text()), args.out, args.force): print(path)

if __name__ == '__main__': main()
