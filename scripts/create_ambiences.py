#!/usr/bin/env python3
"""Crée cinq MP3 originaux, reproductibles, sans échantillon emprunté.

Dépendances de production : numpy, scipy, ffmpeg/libmp3lame. Si FFmpeg est
fourni par imageio-ffmpeg, son exécutable est détecté automatiquement.
Les boucles sont mixées sur un tampon circulaire et ne contiennent pas de voix.
"""
from pathlib import Path
from hashlib import sha256
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from scipy import fft

SR = 44100
ROOT = Path(__file__).resolve().parents[1]


def noise(n, rng, low, high, order=2):
    """Bruit périodique par filtrage fréquentiel pour garder une jointure lisse."""
    data = rng.standard_normal(n, dtype=np.float32)
    frequencies = fft.rfftfreq(n, 1 / SR).astype(np.float32)
    band = (1 / np.sqrt(1 + (low / np.maximum(frequencies, .01)) ** (2 * order))) / np.sqrt(1 + (frequencies / high) ** (2 * order))
    bank = fft.irfft(fft.rfft(data) * band, n=n)
    return bank / max(bank.std(), 1e-9)


def clocks(n, harmonics):
    t = np.arange(n, dtype=np.float32) / n
    return np.sin(2 * np.pi * harmonics * t)


def pad(n, bed, spread, side, rng):
    output = np.empty((n, 2), dtype=np.float32)
    for i in (0, 1):
        output[:, i] = bed + spread * noise(n, rng, *side) + np.roll(bed, (2 * i - 1) * 19) * .18
    return output


def texture_event(out, start_s, signal, pan):
    offset = int(start_s * SR)
    n = len(out)
    indexes = (np.arange(len(signal)) + offset) % n
    out[indexes, 0] += signal * np.sqrt((1 - pan) / 2)
    out[indexes, 1] += signal * np.sqrt((1 + pan) / 2)


def soft_pulse(t, attack, decay):
    return (-np.expm1(-t / attack)) * np.exp(-t / decay)


def rain(seconds, rng):
    n = seconds * SR
    intensity = .83 + .12 * clocks(n, 8) + .06 * clocks(n, 17)
    bed = intensity * (.37 * noise(n, rng, 230, 1550) + .28 * noise(n, rng, 1400, 7400)) + .18 * noise(n, rng, 55, 260)
    out = pad(n, bed, .253, (730, 6600), rng)
    for _ in range(285):
        width = rng.uniform(.031, .081)
        t = np.arange(int(SR * width)) / SR
        impact = (.74 * noise(len(t), rng, 900, 6800) + .28 * np.sin(2 * np.pi * rng.uniform(670, 1640) * t))
        signal = rng.uniform(.09, .55) * impact * soft_pulse(t, .0018, width / 5.5)
        texture_event(out, rng.uniform(0, seconds), signal, rng.uniform(-.92, .92))
    for start, pan in [(10.8, -.45), (38.6, .37), (57.4, -.23)]:
        t = np.arange(5 * SR) / SR
        thunder = (noise(len(t), rng, 22, 120) * .48 + noise(len(t), rng, 58, 280) * .12) * soft_pulse(t, .35, 1.4)
        texture_event(out, start, thunder * np.sin(np.pi * t / 5) ** .52, pan)
    for start, pan in [(22.3, .27), (46.0, -.35)]:
        t = np.arange(7 * SR) / SR
        phase = 2 * np.pi * (212 * t + 5 * np.sin(2 * np.pi * .23 * t))
        signal = (.045 * np.sin(phase) + .013 * np.sin(2 * phase)) * np.sin(np.pi * t / 7) ** 2
        texture_event(out, start, signal, pan)
    return out


def industrial(seconds, rng):
    n = seconds * SR
    bed = (.26 * noise(n, rng, 31, 150) + .26 * noise(n, rng, 160, 830)) * (.8 + .14 * clocks(n, 15))
    bed += .14 * clocks(n, seconds * 49) + .049 * clocks(n, seconds * 98) + .027 * clocks(n, seconds * 147)
    bed += .07 * noise(n, rng, 1150, 3200)
    out = pad(n, bed, .153, (112, 1150), rng)
    for _ in range(34):
        t = np.arange(int(SR * .67)) / SR
        f = rng.uniform(390, 820)
        click = (.15 * np.sin(2*np.pi*f*t) + .09 * np.sin(2*np.pi*f*1.95*t) + .077 * noise(len(t),rng,380,4200)) * soft_pulse(t, .005, .076)
        texture_event(out, rng.uniform(0, seconds), click, rng.uniform(-.7, .7))
    return out


def forest(seconds, rng):
    n = seconds * SR
    swells = .77 + .20 * clocks(n, 7) + .11 * clocks(n, 11)
    bed = swells * (.31 * noise(n, rng, 58, 285) + .18 * noise(n, rng, 310, 1400)) + .069 * noise(n, rng, 1800, 4200)
    out = pad(n, bed, .155, (650, 4100), rng)
    for _ in range(54):
        width = rng.uniform(.13,.77)
        t = np.arange(int(SR*width)) / SR
        sig = noise(len(t),rng,590,5200) * soft_pulse(t,.048,width/5) * rng.uniform(.14,.4)
        texture_event(out,rng.uniform(0,seconds),sig,rng.uniform(-.9,.9))
    for offset, pan in [(7.4, -.58), (34.2, .63), (45.7, .22)]:
        for index in range(3):
            t = np.arange(int(SR * .24)) / SR
            f = 1180 + 97 * index
            phase = 2 * np.pi * (f * t - 360 * t * t + 8.6*np.sin(2*np.pi*2.3*t))
            note = (.072 * np.sin(phase) + .018 * np.sin(2 * phase)) * np.sin(np.pi*t/.24) ** 2
            texture_event(out,offset+index*.37,note,pan)
    return out


def cue(seconds, rng, style):
    t = np.arange(int(seconds*SR)) / SR
    samples = np.zeros((len(t),2), dtype=np.float32)
    if style == 'click':
        body = noise(len(t),rng,430,3900) * soft_pulse(t,.002,.027) * .29
        ring = (.38*np.sin(2*np.pi*880*t) + .21*np.sin(2*np.pi*1370*t)) * soft_pulse(t,.003,.038)
        texture_event(samples,0,body+ring,.08)
        texture_event(samples,.065,np.roll(body,8)*.26,-.14)
    else:
        for offset, f, gain, pan in [(0,529,.31,0),(.17,706,.28,.05),(.34,890,.16,-.13)]:
            tn = t[:int(.28 * SR)]
            signal = (np.sin(2*np.pi*f*tn) + .20*np.sin(2*np.pi*2*f*tn)) * soft_pulse(tn,.009,.058)*gain
            texture_event(samples,offset,signal,pan)
        samples[int(.65 * SR):] *= np.linspace(1,0,len(samples)-int(.65*SR))[:,None]
    return samples


def ffmpeg_path():
    path = os.environ.get('TUG_FFMPEG') or shutil.which('ffmpeg')
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit('FFmpeg/libmp3lame est requis (ou installer imageio-ffmpeg).') from None


def render():
    cmd = ffmpeg_path()
    manifest = {'schemaVersion':1, 'methode':'Synthèse procédurale; aucun échantillon externe.', 'tracks': []}
    specs = [
        ('ambient/ambient_rain.mp3', 'Pluie sur les entrepôts', 60, rain, 585, True),
        ('ambient/ambient_industrial.mp3', 'Ventilation de la planque', 60, industrial, 377, True),
        ('ambient/ambient_forest.mp3', 'Forêt de nuit', 60, forest, 958, True),
        ('ui/ui_click.mp3', 'Clic radio', .27, lambda d, r: cue(d,r,'click'), 61, False),
        ('ui/ui_notification.mp3', 'Signal de notification', .82, lambda d, r: cue(d,r,'alert'), 43, False),
    ]
    for path,title,seconds,maker,seed,loop in specs:
        samples = maker(seconds,np.random.default_rng(seed))
        if loop:
            samples -= samples.mean(axis=0)
            samples *= .097 / np.sqrt(np.mean(samples**2))
        else:
            samples *= .41 / np.max(np.abs(samples))
        np.clip(samples,-.80,.80,out=samples)
        dest = ROOT / 'audio' / path
        dest.parent.mkdir(parents=True,exist_ok=True)
        raw = samples.astype('<f4',copy=False).tobytes()
        subprocess.run([cmd,'-hide_banner','-loglevel','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-map_metadata','-1','-c:a','libmp3lame', '-b:a','192k','-id3v2_version','3','-metadata',f'title={title}','-metadata','album=Tarkov Ultimate Guide · Ateliers sonores',str(dest)],input=raw,check=True)
        # Vérifier le décodage, la durée réelle et le pic RMS du média final, pas seulement du mix avant encodage.
        decoded = subprocess.check_output([cmd,'-v','error','-i',str(dest),'-f','f32le','-c:a','pcm_f32le','-'])
        level = np.frombuffer(decoded,dtype='<f4').reshape(-1,2)
        if abs(len(level)/SR - seconds) > .035 or np.max(np.abs(level)) >= .99:
            raise ValueError(f'MP3 invalide : {dest}')
        body = dest.read_bytes()
        entry={'file':f'audio/{path}','title':title,'seconds':round(len(level)/SR,3),'loop':loop,'sampleRate':SR,'channels':2,'bitRateKbps':192,'bytes':len(body),'peakDbFS':round(float(20*np.log10(np.max(np.abs(level)))),2),'sha256':sha256(body).hexdigest()}
        manifest['tracks'].append(entry)
        print(f"{entry['file']} · {entry['seconds']} s · {entry['peakDbFS']} dBFS max")
    (ROOT/'audio/manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    render()
