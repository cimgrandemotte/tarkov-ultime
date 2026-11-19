#!/usr/bin/env python3
"""Boucle originale Norvinsk (60 s). Complète le manifeste sans réencoder la phase 1."""
import json
import subprocess
from hashlib import sha256

import numpy as np
from create_ambiences import SR, ROOT, noise, clocks, pad, soft_pulse, texture_event, ffmpeg_path


def make():
    seconds = 60
    n = seconds * SR
    rng = np.random.default_rng(21610)
    gusts = .66 + .16 * clocks(n, 5) + .14 * clocks(n, 13) + .11 * clocks(n, 21)
    bed = gusts * (.24 * noise(n, rng, 43, 230) + .34 * noise(n, rng, 160, 850))
    bed += .11 * noise(n, rng, 650, 4600)
    bed += .055 * clocks(n, seconds * 56) * (.7 + .22 * clocks(n, 19))
    samples = pad(n, bed, .15, (520, 4850), rng)
    # Les retours proviennent de la résonance d'un décor, sans échantillon sonore emprunté.
    for k in range(60):
        width = rng.uniform(.08, .22)
        t = np.arange(int(SR * width)) / SR
        f = rng.uniform(560, 1300)
        drop = (.29 * np.sin(2*np.pi*f*t) + .65 * noise(len(t),rng,1100,6900)) * soft_pulse(t,.0015,width*.17)
        at = float(rng.uniform(0, seconds)); pan = float(rng.uniform(-.85, .85))
        texture_event(samples,at,drop*rng.uniform(.2,.57),pan)
        texture_event(samples,at+.102,drop*.076,-pan*.53)
    for at, pan, f in [(9.2,-.35,282), (27.7,.67,310),(42.5,-.13,269),(58.4,.23,299)]:
        t = np.arange(int(SR*2.5)) / SR
        phase = 2*np.pi*(t*f - 5.4*t*t + 1.9*np.sin(2*np.pi*.79*t))
        creak = (.23*np.sin(phase)+.08*np.sin(2.1*phase)+.078*noise(len(t),rng,250,850))
        ring = creak * np.sin(np.pi*t/2.5)**2 * np.exp(-t/1.9)
        texture_event(samples,at,ring,pan)
        texture_event(samples,at+.215,ring*.31,-pan*.65)
    samples -= np.mean(samples,axis=0)
    samples *= .087 / np.sqrt(np.mean(samples ** 2))
    np.clip(samples,-.81,.81,out=samples)
    dest = ROOT / 'audio/ambient/ambient_city.mp3'
    ff = ffmpeg_path()
    subprocess.run([ff,'-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-map_metadata','-1','-c:a','libmp3lame','-b:a','192k',
                    '-id3v2_version','3','-metadata','title=Ville abandonnée','-metadata','album=Tarkov Ultimate Guide · Ateliers sonores',str(dest)],
                    input=samples.astype('<f4',copy=False).tobytes(),check=True)
    decoded = subprocess.check_output([ff,'-v','error','-i',str(dest),'-f','f32le','-c:a','pcm_f32le','-'])
    wave=np.frombuffer(decoded,dtype='<f4').reshape(-1,2)
    peak=float(np.max(np.abs(wave)))
    assert len(wave)==SR*seconds and 0 < peak < .98
    manifest_path=ROOT/'audio/manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    source=dest.read_bytes(); file=dest.relative_to(ROOT).as_posix()
    manifest['tracks']=[t for t in manifest['tracks'] if t['file'] != file]
    manifest['tracks'].append(dict(file=file,title='Ville abandonnée',seconds=60.0,loop=True,sampleRate=SR,channels=2,bitRateKbps=192,
                                   bytes=len(source),peakDbFS=round(20*np.log10(peak),2),sha256=sha256(source).hexdigest()))
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(file, manifest['tracks'][-1])


if __name__ == '__main__':
    make()
