"""Photos des dossiers et palette des éléments non textuels."""
from datetime import datetime, timezone
from functools import lru_cache
import json
import math
from pathlib import Path
import re
import sys

from PIL import Image
from phase1_colors import ROOT, luma
from phase2_colors import ratio

fast_luma = lru_cache(maxsize=65536)(luma)


def palette():
    def rgb(s):
        return tuple(int(s[i:i+2],16) for i in (0,2,4))
    pairs = [
      ('FAQ, bord de contrôle et fond', '787568', '151713', 3),
      ('Spoilers, bord de contrôle et fond', '9e7d5e', '201913', 3),
      ('HUD, bord de repère sur le panneau', '879184', '151a17', 3),
      ('Focalisation, anneau doré sur onglet', 'f2d59c', '252017', 3),
      ('Onglet actif, texte', 'e1c48d','252017',4.5),
      ('Légende du HUD, texte secondaire', 'c2c0b5','151713',4.5),
      ('Chiffre du HUD', 'eac994','151a17',4.5),
      ('Étiquette de lore, texte', 'b6cfcb','1a2120',4.5),
      ('Bouton de spoiler, étiquette', 'f7c79b','332417',4.5),
    ]
    checks = []
    for label, fg, bg, minimum in pairs:
        value = ratio(luma(rgb(fg)), luma(rgb(bg)))
        assert value >= minimum, (label, value)
        checks.append(dict(label=label,color='#'+fg,background='#'+bg,ratio=round(value,2),minimum=minimum))
    return checks


def main(folder):
    output, failed = [], []
    for name in sorted(folder.glob('*.json')):
        data = json.loads(name.read_text(encoding='utf-8'))
        measured=[]
        with Image.open(name.with_suffix('.jpg')) as f:
            raster=f.convert('RGB')
        for sample in data.pop('samples'):
            text = luma(tuple(int(n) for n in re.findall(r'\d+',sample['color'])[:3]))
            values=[]
            for l,t,r,b in sample['rects']:
                box=(max(0,int(l)),max(0,int(t)),min(raster.width,math.ceil(r)),min(raster.height,math.ceil(b)))
                assert box[2]>box[0] and box[3]>box[1], (name.stem, sample)
                photo=raster.crop(box)
                pixels=photo.get_flattened_data() if hasattr(photo,'get_flattened_data') else photo.getdata()
                values.append(min(ratio(text,fast_luma(p)) for p in pixels))
            measured.append((min(values),sample['selector'],sample['label']))
        value, selector, label=min(measured)
        if value<4.5: failed.append((name.stem,value,selector,label))
        output.append({**data,'testedSamples':len(measured),'lowestRatio':round(value,2),'at':selector,'text':label})
        print(f'{name.stem}: {len(measured)} mesures, minimum {value:.2f}:1 ({selector})')
    assert len(output)==20
    assert not failed, failed
    report={'schemaVersion':1,'checkedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'profiles':output,
            'palette':palette(),'method':'Chromium DPR 1 ; texte et décorations masqués, capture JPEG qualité 100 ; pixels les moins favorables dans les boîtes de texte des deux visuels principaux. Palette des contrôles calculée séparément.'}
    (ROOT/'data/snapshots/contraste-phase-3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    main(Path(sys.argv[1]))
