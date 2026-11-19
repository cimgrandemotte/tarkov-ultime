"""Contrôle du texte sur les visuels principaux de PHASE_4 et de sa palette de lecture."""
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


def rgb(hex_value):
    return tuple(int(hex_value[index:index + 2], 16) for index in (0, 2, 4))


def palette():
    pairs = [
        ('Texte principal sur surface Cartes', 'e8e6e3', '151713', 4.5),
        ('Texte secondaire sur surface Cartes', 'c2c0b5', '151713', 4.5),
        ('Teinte éditoriale sur surface Cartes', 'c7b47f', '151713', 4.5),
        ('Lien doré sur surface Cartes', 'e1c48d', '151713', 4.5),
        ('Texte actif du bouton de mode', 'f7e4ad', '292316', 4.5),
        ('Texte du réseau sur surface relevée', 'e8e6e3', '1b1d17', 4.5),
        ('Lien de citation sur fond de fiche', 'e1c48d', '151713', 4.5),
        ('Texte de statut filtré sur surface', 'c7b47f', '151713', 4.5),
    ]
    results = []
    for label, foreground, background, minimum in pairs:
        value = ratio(luma(rgb(foreground)), luma(rgb(background)))
        assert value >= minimum, (label, value)
        results.append({
            'label': label, 'color': '#' + foreground, 'background': '#' + background,
            'ratio': round(value, 2), 'minimum': minimum,
        })
    return results


def main(folder: Path):
    profiles, failures = [], []
    for name in sorted(folder.glob('*.json')):
        data = json.loads(name.read_text(encoding='utf-8'))
        with Image.open(name.with_suffix('.jpg')) as image:
            raster = image.convert('RGB')
        measured = []
        for sample in data['samples']:
            numbers = [int(value) for value in re.findall(r'\d+', sample['color'])[:3]]
            assert len(numbers) == 3, (name.name, sample['color'])
            foreground = luma(tuple(numbers))
            values = []
            for left, top, right, bottom in sample['rects']:
                box = (
                    max(0, int(left)), max(0, int(top)),
                    min(raster.width, math.ceil(right)), min(raster.height, math.ceil(bottom)),
                )
                if box[2] <= box[0] or box[3] <= box[1]:
                    continue
                photo = raster.crop(box)
                pixels = photo.get_flattened_data() if hasattr(photo, 'get_flattened_data') else photo.getdata()
                values.append(min(ratio(foreground, fast_luma(pixel)) for pixel in pixels))
            if values:
                measured.append((min(values), sample['selector'], sample['label']))
        assert measured, f'aucun texte mesuré : {name.name}'
        value, selector, label = min(measured)
        if value < 4.5:
            failures.append((name.stem, value, selector, label))
        profiles.append({
            'route': data['route'], 'width': data['width'], 'theme': data['theme'],
            'testedSamples': len(measured), 'lowestRatio': round(value, 2),
            'at': selector, 'text': label,
        })
        print(f"{name.stem}: {len(measured)} échantillons · minimum {value:.2f}:1 ({selector})")
    assert len(profiles) == 20, f'20 profils attendus, obtenus : {len(profiles)}'
    assert not failures, failures
    report = {
        'schemaVersion': 1,
        'checkedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'profiles': profiles,
        'palette': palette(),
        'method': 'Chromium DPR 1 ; prélèvement des pixels sous les boîtes de glyphes dans une capture JPEG qualité 100 du hero composé, texte masqué mais image et dégradés conservés ; 2 routes × 5 largeurs × 2 thèmes. Palette de texte et boutons calculée séparément selon le contraste relatif WCAG.',
    }
    output = ROOT / 'data/snapshots/contraste-phase-4.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
