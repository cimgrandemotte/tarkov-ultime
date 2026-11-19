#!/usr/bin/env python3
"""Vérifie hors ligne le livrable d’initialisation, sans modifier le projet."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {'items', 'weapons', 'ammo', 'armor'}
MODES = {'regular', 'pve', 'pvp-season'}


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def require(condition, description):
    if not condition:
        raise SystemExit(f'Échec : {description}')


def main():
    workflow, machine = load('workflow.json'), load('state_machine.json')
    phases = [p['id'] for p in workflow['phases']]
    require(phases == machine['ordre_phases'], 'ordre des phases incohérent')
    require(machine['instantane']['etat'] == workflow['etat_global'], 'état global désynchronisé')
    require(machine['instantane']['phase_active'] == workflow['phase_active'], 'phase active désynchronisée')
    require('PHASE_0' in workflow['phases_terminees'], 'phase 0 non terminée')
    for task in workflow['suivi_phase_0']:
        require(task['statut'] == 'TERMINE', f'tâche non clôturée : {task["id"]}')
        for ref in task['preuves']:
            require((ROOT / ref).exists(), f'preuve introuvable : {ref}')
    if workflow['etat_global'] == 'ATTENTE_CONTINUE':
        require(machine['instantane']['attend_confirmation'], 'confirmation manquante')
        require(machine['instantane']['prochaine_phase'] == workflow['prochaine_phase'], 'prochaine phase désynchronisée')
        last = machine['instantane']['derniere_phase_terminee']
        require(workflow['prochaine_phase'] == phases[phases.index(last) + 1], 'ordre de transition invalide')

    plan = load('docs/plan-editorial.json')
    sources = load('docs/sources.json')['sources']
    routes = [p['fichier'] for p in plan['pages']]
    require(len(set(routes)) == len(routes) == plan['total'], 'routes non uniques ou total de manifest invalide')
    require(plan['total'] == workflow['production']['pages_planifiees'], 'nombre de pages planifiées désynchronisé')
    require(len(routes) >= workflow['contraintes']['pages_html_minimum'], 'couverture des routes insuffisante')
    require('index.html' in routes and 'pages/maps/terminal.html' in routes, 'accueil ou Terminal hors plan')
    for entry in plan['pages']:
        target = Path(entry['fichier'])
        require(not target.is_absolute() and '..' not in target.parts and target.suffix == '.html', str(target))
        require((ROOT / target.parent).is_dir(), f'dossier de route absent : {target.parent}')
        require(entry['phase'] in phases and len(entry['sections']) >= 3, f'plan incomplet : {target}')
        require(len(entry['illustrations_jpg']) >= 2, f'illustrations non spécifiées : {target}')
        require(set(entry['sources_a_consulter']) <= sources.keys() and bool(entry['revalidation']), f'source ou contrôle absent : {target}')
    for phase, count in Counter(p['phase'] for p in plan['pages']).items():
        require(next(p for p in workflow['phases'] if p['id'] == phase)['pages_planifiees'] == count, phase)

    versions = load('data/snapshots/versions-2026-11-18.json')
    for fact in versions['faits']:
        require(fact['sources'] and set(fact['sources']) <= sources.keys(), f'fait non traçable : {fact["id"]}')
    manifest = load('js/data/catalog-manifest.json')
    require(set(manifest['modes']) == MODES and manifest['gameBuild'] is None, 'modes ou métadonnée build inattendus')
    require(all(v['httpStatus'] == 200 for v in manifest['upstream'].values()), 'réponse amont invalide dans le manifest')
    for mode, info in manifest['modes'].items():
        require(set(info['files']) == DATASETS, f'jeux manquants dans {mode}')
        ids_by_kind = {}
        for kind, file in info['files'].items():
            raw = (ROOT / file['path']).read_bytes()
            require(len(raw) == file['bytes'] and sha256(raw).hexdigest() == file['sha256'], f'empreinte divergente : {mode}/{kind}')
            doc = json.loads(raw)
            require(doc['kind'] == kind and doc['mode'] == mode, f'mode de données incohérent : {mode}/{kind}')
            records = doc['records']
            ids = {r['id'] for r in records}
            require(bool(ids) and len(ids) == file['count'] == len(records), f'identifiants non uniques : {mode}/{kind}')
            require(sum(bool(r.get('nameFr')) for r in records) == file['frNameCount'], f'langue incohérente : {mode}/{kind}')
            ids_by_kind[kind] = ids
        for kind in DATASETS - {'items'}:
            require(ids_by_kind[kind] <= ids_by_kind['items'], f'objet référencé introuvable : {mode}/{kind}')
        print(f'{mode}: ' + ', '.join(f"{vals['count']} {key}" for key, vals in info['files'].items()))

    files = [p for p in ROOT.rglob('*') if p.is_file()]
    require(not any(p.suffix.lower() in {'.zip', '.pdf'} for p in files), 'format interdit trouvé')
    out = workflow['production']
    require(sum((ROOT / r).is_file() for r in routes) == out['pages_generees'], 'compteur des pages livrées incohérent')
    if machine['instantane']['prochaine_phase'] == 'PHASE_1':
        require(out['pages_generees'] == 0 and not out['images_creees'] and not out['audios_crees'], 'le cadrage seul ne livre pas de pages ni de média')
    print(f"OK · {len(routes)} routes · {len(sources)} sources et pistes · 12 catalogues vérifiés · workflow synchronisé")


if __name__ == '__main__':
    main()
