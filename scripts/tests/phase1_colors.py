"""Analyse les fonds réellement composés sous les textes du hero.

Input : JPG du fond avec le texte masqué et boîtes de Chromium (voir phase1-colors.cjs).
La luminance max par zone donne un seuil conservateur pour le texte clair, même en titre.
"""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def srgb(channel):
    value = channel / 255
    return value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4


LUT = [srgb(i) for i in range(256)]


def luma(rgb):
    r, g, b = rgb
    return .2126 * LUT[r] + .7152 * LUT[g] + .0722 * LUT[b]


def theme_swatches():
    def rgb(s):
        return [int(s[i:i+2],16) for i in (0,2,4)]
    palette = (ROOT / 'css/main.css').read_text(encoding='utf-8')
    base, contrast = palette.split(":root[data-theme='contrast']", 1)
    get = lambda css, key: re.search(fr'--{key}: #([\da-f]{{6}});', css).group(1)
    tests = [
        ('Texte atténué sur surface sombre', get(base,'muted'), '272820', 4.5),
        ('Texte secondaire sur surface sombre', get(base,'text-soft'), '272820', 4.5),
        ('Texte blanc sur surface sombre', get(base,'text'), '272820', 4.5),
        ('Texte or sur surface sombre', get(base,'gold-high'), '272820', 4.5),
        ('Texte sur bouton principal', get(base,'gold-ink'), get(base,'gold'), 4.5),
        ('Étiquette de version', get(base,'olive-text'), '182017', 4.5),
        ('Contours de commande', get(base,'control-edge'), '272820', 3),
        ('Anneau de focus', get(base,'focus'), '272820', 3),
        ('Texte atténué en contraste renforcé', get(contrast,'muted'), '272820', 4.5),
    ]
    out = []
    for label, fore, back, target in tests:
        dark, bright = sorted([luma(rgb(fore)), luma(rgb(back))])
        ratio = (bright + .05) / (dark + .05)
        if ratio < target:
            raise ValueError(f'Contraste insuffisant : {label} ({ratio:.2f})')
        out.append({'label': label, 'color': '#'+fore, 'background': '#'+back, 'ratio': round(ratio, 2), 'minimum':target})
    return out


def main(folder):
    out = []
    for item in sorted(folder.glob('*.json'), key=lambda p: (int(p.stem.split('-')[0]), p.stem)):
        width, mode = item.stem.split('-')
        with Image.open(item.with_suffix('.jpg')) as file:
            image = file.convert('RGB')
        measured = []
        for sample in json.loads(item.read_text(encoding='utf-8')):
            text = luma(tuple(int(n) for n in re.findall(r'\d+',sample['color'])[:3]))
            points = []
            for x, y, r, b in sample['rects']:
                box = (max(0,int(x)), max(0,int(y)), min(image.width,math.ceil(r)), min(image.height,math.ceil(b)))
                if box[2] > box[0] and box[3] > box[1]:
                    tile = image.crop(box)
                    pixels = tile.get_flattened_data() if hasattr(tile,'get_flattened_data') else tile.getdata()
                    points.append(max(map(luma, pixels)))
            if points:
                measured.append(((text + .05) / (max(points) + .05), sample['label']))
        minimum, least = min(measured)
        if minimum < 4.5:
            raise ValueError(f'Contraste hero insuffisant : {item.stem} {minimum:.2f} ({least})')
        out.append({'widthCssPx':int(width),'theme':mode,'testedSamples':len(measured),'lowestRatio':round(minimum,2),'at':least})
        print(f'{item.stem} : minimum {minimum:.2f}:1 ({least})')
    if len(out) != 10:
        raise SystemExit('Dix profils de contraste sont nécessaires.')
    doc = {'schemaVersion':1,'checkedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),
           'method':'Chromium : luminance maximale de chaque zone de texte, fond photographique et filtres déjà composés ; état immobile. Palette CSS : fond #272820 volontairement plus clair que les panneaux.',
           'hero':out, 'palette':theme_swatches()}
    (ROOT / 'data/snapshots/contraste-phase-1.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
