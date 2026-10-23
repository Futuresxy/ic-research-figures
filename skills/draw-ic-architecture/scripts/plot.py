#!/usr/bin/env python3
"""CSV -> reproducible DSE or component breakdown; Matplotlib preferred, stdlib SVG optional."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

PALETTE=['#0072B2','#E69F00','#009E73','#CC79A7','#56B4E9','#D55E00']

def pareto_mask(points):
    """Minimize all objectives. Keep equal nondominated coordinates."""
    return [not any(all(a<=b for a,b in zip(q,p)) and any(a<b for a,b in zip(q,p))
                    for q in points) for p in points]

def number(value):
    x=float(value)
    if not math.isfinite(x) or x<0: raise ValueError('Values must be finite and nonnegative')
    return x

def read_data(path, kind):
    with open(path, newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
    if not rows: raise ValueError('Empty CSV')
    if kind=='dse':
        required={'design','family','area_mm2','latency_ms','feasible'}
        for r in rows:
            if not required <= r.keys(): raise ValueError('DSE columns: '+','.join(sorted(required)))
            r['area_mm2']=number(r['area_mm2']); r['latency_ms']=number(r['latency_ms'])
            if r['feasible'].lower() not in ('true','false','1','0'): raise ValueError('Invalid feasible flag')
            r['feasible']=r['feasible'].lower() in ('true','1')
        valid=[r for r in rows if r['feasible']]
        if not valid: raise ValueError('No feasible design')
        mask=pareto_mask([(r['area_mm2'],r['latency_ms']) for r in valid])
        for r,m in zip(valid,mask): r['pareto']=m
        designs=[r['design'] for r in rows]
        if len(set(designs))!=len(designs): raise ValueError('Duplicate design ID')
    else:
        required={'design','component','value','unit'}
        keys=[]
        for r in rows:
            if not required <= r.keys(): raise ValueError('Breakdown columns: design,component,value,unit')
            r['value']=number(r['value']); keys.append((r['design'],r['component']))
        if len(set(keys))!=len(keys): raise ValueError('Duplicate design/component')
        if len({r['unit'] for r in rows})!=1: raise ValueError('Do not stack different units')
        components={r['component'] for r in rows}
        for design in {r['design'] for r in rows}:
            if {r['component'] for r in rows if r['design']==design}!=components:
                raise ValueError('Missing component: explicit zero required if truly absent')
    return rows

def mpl_plot(rows,kind,out,style):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit('Install matplotlib>=3.6,<4 or explicitly select --backend svg') from exc
    plt.rcParams.update({'font.family':style.get('font','DejaVu Sans'), 'font.size':9,
                         'pdf.fonttype':42, 'ps.fonttype':42,'svg.fonttype':'none',
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=style.get('figsize',[3.6,2.8]),layout='constrained')
    colors=style.get('colors',PALETTE)
    if kind=='dse':
        families=list(dict.fromkeys(r['family'] for r in rows))
        for i,family in enumerate(families):
            group=[r for r in rows if r['family']==family and r['feasible']]
            if group: ax.scatter([r['area_mm2'] for r in group],[r['latency_ms'] for r in group],
                                  label=family,color=colors[i%len(colors)],marker=['o','s','^','D'][i%4],s=30)
        bad=[r for r in rows if not r['feasible']]
        if bad: ax.scatter([r['area_mm2'] for r in bad],[r['latency_ms'] for r in bad],
                           color='#999999',marker='x',label='Infeasible')
        front=sorted({(r['area_mm2'],r['latency_ms']) for r in rows if r.get('pareto')})
        ax.plot(*zip(*front),'--',color='#333333',linewidth=1,label='Sampled Pareto')
        ax.set(xlabel='Area (mm²)',ylabel='Latency (ms)')
    else:
        designs=list(dict.fromkeys(r['design'] for r in rows))
        components=list(dict.fromkeys(r['component'] for r in rows)); bottom=[0.]*len(designs)
        lookup={(r['design'],r['component']):r['value'] for r in rows}
        for i,c in enumerate(components):
            values=[lookup[(d,c)] for d in designs]
            ax.bar(designs,values,bottom=bottom,label=c,color=colors[i%len(colors)],
                   edgecolor='white',linewidth=.4)
            bottom=[a+b for a,b in zip(bottom,values)]
        ax.set(ylabel=style.get('ylabel','Value')+' ('+rows[0]['unit']+')',ylim=(0,max(bottom)*1.12 or 1))
    ax.legend(frameon=False,fontsize=7,loc='upper left',bbox_to_anchor=(0,1.23),ncol=2)
    ax.tick_params(direction='out'); ax.grid(axis='y',alpha=.2); ax.set_axisbelow(True)
    if 'xlim' in style: ax.set_xlim(style['xlim'])
    if 'ylim' in style: ax.set_ylim(style['ylim'])
    for ext in ('svg','pdf','png'): fig.savefig(out.with_suffix('.'+ext),dpi=300)
    plt.close(fig)

def svg_plot(rows,kind,out,style):
    """Portable, editable SVG fallback; no Matplotlib/PDF/PNG claim."""
    svg=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width='720',height='480',viewBox='0 0 720 480')
    def elem(tag,**attrs): return ET.SubElement(svg,tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})
    def text(x,y,s,anchor='middle',size=14):
        t=elem('text',x=x,y=y,text_anchor=anchor,font_family='Arial,sans-serif',font_size=size,fill='#222222');t.text=s;return t
    elem('rect',width=720,height=480,fill='white')
    colors=style.get('colors',PALETTE); left,right,top,bottom=90,670,95,395
    if kind=='dse':
        xmax=max(r['area_mm2'] for r in rows)*1.1 or 1
        ymax=max(r['latency_ms'] for r in rows)*1.1 or 1
        xlabel,ylabel='Area (mm²)','Latency (ms)'
        groups=list(dict.fromkeys(r['family'] for r in rows))
    else:
        designs=list(dict.fromkeys(r['design'] for r in rows))
        groups=list(dict.fromkeys(r['component'] for r in rows))
        xmax=len(designs)
        ymax=max(sum(r['value'] for r in rows if r['design']==d) for d in designs)*1.12 or 1
        xlabel,ylabel='',style.get('ylabel','Value')+' ('+rows[0]['unit']+')'
    px=lambda v:left+(right-left)*v/xmax
    py=lambda v:bottom-(bottom-top)*v/ymax
    for k in range(6):
        v=ymax*k/5; y=py(v)
        elem('line',x1=left,y1=y,x2=right,y2=y,stroke='#E5E7EB'); text(left-12,y+4,f'{v:.3g}','end',12)
        if kind=='dse':
            x=px(xmax*k/5);text(x,bottom+22,f'{xmax*k/5:.3g}',size=12)
    elem('path',d=f'M {left} {top} V {bottom} H {right}',fill='none',stroke='#333333')
    text((left+right)/2,452,xlabel)
    t=text(25,(top+bottom)/2,ylabel);t.set('transform',f'rotate(-90 25 {(top+bottom)/2})')
    for i,g in enumerate(groups):
        lx=left+(i%3)*190;ly=25+(i//3)*23
        elem('rect',x=lx,y=ly-10,width=12,height=12,fill=colors[i%len(colors)])
        text(lx+20,ly,g,'start',12)
    if kind=='dse':
        front=sorted({(r['area_mm2'],r['latency_ms']) for r in rows if r.get('pareto')})
        elem('polyline',points=' '.join(f'{px(x)},{py(y)}' for x,y in front),fill='none',stroke='#333333',stroke_dasharray='6 4')
        for r in rows:
            x,y=px(r['area_mm2']),py(r['latency_ms'])
            if r['feasible']:
                i=groups.index(r['family']);color=colors[i%len(colors)]
                if i%2: elem('rect',x=x-5,y=y-5,width=10,height=10,fill=color)
                else: elem('circle',cx=x,cy=y,r=5,fill=color)
            else: elem('path',d=f'M {x-5} {y-5} L {x+5} {y+5} M {x-5} {y+5} L {x+5} {y-5}',stroke='#999999')
        elem('line',x1=left,y1=72,x2=left+30,y2=72,stroke='#333333',stroke_dasharray='6 4')
        text(left+38,76,'Sampled Pareto','start',12)
        text(left+240,76,'× Infeasible','start',12)
    else:
        lookup={(r['design'],r['component']):r['value'] for r in rows}
        for i,d in enumerate(designs):
            base=0;barw=(right-left)/len(designs)*.55
            for j,g in enumerate(groups):
                v=lookup[d,g]
                elem('rect',x=px(i+.5)-barw/2,y=py(base+v),width=barw,height=py(base)-py(base+v),
                     fill=colors[j%len(colors)],stroke='white',stroke_width='.5');base+=v
            text(px(i+.5),bottom+24,d,size=12)
    ET.indent(svg);ET.ElementTree(svg).write(out.with_suffix('.svg'),encoding='utf-8',xml_declaration=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv',type=Path);p.add_argument('--kind',choices=['dse','breakdown'],required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--style',type=Path)
    p.add_argument('--backend',choices=['matplotlib','svg'],default='matplotlib')
    p.add_argument('--force',action='store_true');args=p.parse_args()
    suffixes=['.svg','.pdf','.png','.metadata.json','.caption.md']
    outputs=[args.out.with_suffix(s) for s in suffixes]
    if args.csv.resolve() in [f.resolve() for f in outputs]: raise ValueError('Output cannot replace source')
    if not args.force and any(f.exists() for f in outputs): raise FileExistsError('Use new output name or explicit --force')
    rows=read_data(args.csv,args.kind);style=json.loads(args.style.read_text()) if args.style else {}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    (mpl_plot if args.backend=='matplotlib' else svg_plot)(rows,args.kind,args.out,style)
    demo='demo' in args.csv.stem.lower()
    metadata={'input_file':args.csv.name,'sha256':hashlib.sha256(args.csv.read_bytes()).hexdigest(),
              'kind':args.kind,'backend':args.backend,'synthetic_demo':demo,
              'style':style,'objectives':{'area_mm2':'min','latency_ms':'min'} if args.kind=='dse' else {},
              'pareto_designs':[r['design'] for r in rows if r.get('pareto')],
              'notes':'Demo values are not measured hardware results.' if demo else 'Add source and experimental conditions before publication.'}
    args.out.with_suffix('.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    caption=('Synthetic demonstration only; not experimental evidence. ' if demo else 'Complete source and conditions before publication. ')
    caption+=('Area–latency design-space sample, minimizing both objectives; dashed line connects sampled nondominated feasible points and does not imply realizable intermediate designs.'
              if args.kind=='dse' else 'Absolute component breakdown; segments use a single common unit and are summed within each design.')
    args.out.with_suffix('.caption.md').write_text(caption+'\n')
    print(json.dumps(metadata,indent=2))

if __name__=='__main__': main()
