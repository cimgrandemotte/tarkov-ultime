"""Rapport de contraste aux endroits où l'audit automatique ne connaît pas le fond."""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sys

from PIL import Image
from phase1_colors import ROOT, luma


def ratio(a, b):
    low, high = sorted((a,b))
    return (high + .05) / (low + .05)


def palette():
    def rgb(s):
        return tuple(int(s[i:i+2],16) for i in (0,2,4))
    pairs = [
        ('Bouton filtres · contour', '817d6e', '1a1c17', 3),
        ('Filtre courant · contour', 'ba9d64', '2d2619', 3),
        ('Bouton secondaire sur le hero · contour', '8d8976', '101412', 3),
        ('Focus doré sur surface claire du panneau patch', 'f2d59c', '30281b', 3),
        ('Panneaux éditoriaux · texte secondaire', 'c2c0b5', '282619', 4.5),
        ('Actualités · libellé date', 'babbb0', '1d211a', 4.5),
        ('Onglet courant · texte', 'e1c48d', '252017', 4.5),
    ]
    checks=[]
    for label, fg, bg, minimum in pairs:
        value=ratio(luma(rgb(fg)),luma(rgb(bg)))
        assert value >= minimum, (label, value)
        checks.append(dict(label=label, color='#'+fg, background='#'+bg, ratio=round(value,2), minimum=minimum))
    return checks


def main(folder):
    output=[]
    failures=[]
    for name in sorted(folder.glob('*.json'), key=lambda p: (int(p.stem.split('-')[0]),p.stem)):
        width, theme = name.stem.split('-')
        measured=[]
        with Image.open(name.with_suffix('.jpg')) as f:
            raster=f.convert('RGB')
        for sample in json.loads(name.read_text(encoding='utf-8')):
            text = luma(tuple(int(n) for n in re.findall(r'\d+',sample['color'])[:3]))
            boxes=[]
            for x,y,right,bottom in sample['rects']:
                box=(max(0,int(x)),max(0,int(y)),min(raster.width,math.ceil(right)),min(raster.height,math.ceil(bottom)))
                if box[2]<=box[0] or box[3]<=box[1]: continue
                photo=raster.crop(box)
                pixels=photo.get_flattened_data() if hasattr(photo,'get_flattened_data') else photo.getdata()
                boxes.append(min(ratio(text,luma(p)) for p in pixels))
            if boxes:
                measured.append((min(boxes),sample['selector'],sample['label']))
        value, selector, label=min(measured)
        if value<4.5: failures.append((name.stem,value,selector,label))
        output.append({'widthCssPx':int(width),'theme':theme,'testedSamples':len(measured),'lowestRatio':round(value,2),'at':selector,'text':label})
        print(f'{name.stem} · {len(measured)} échantillons · minimum {value:.2f}:1 ({selector} : {label[:62]})')
    assert len(output)==10, 'Les dix profilages de contraste sont requis.'
    assert not failures, failures
    doc={'schemaVersion':1,'checkedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'), 'profiles':output, 'palette':palette(),
         'method':'Chromium à DPR 1 : texte masqué sur JPG qualité 100 de l’arrière-plan composé, contraste WCAG relatif calculé pour la luminance la plus défavorable dans la boîte des glyphes.'}
    (ROOT/'data/snapshots/contraste-phase-2.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main(Path(sys.argv[1]))
