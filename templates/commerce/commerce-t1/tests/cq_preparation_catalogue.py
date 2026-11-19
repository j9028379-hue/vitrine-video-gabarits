"""Mission 1 : contrôler le canon distribué, hors ligne, sans construire de client OTA."""
import json
from pathlib import Path
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]


def unique(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError(f'Clé JSON en double : {k}')
        obj[k] = v
    return obj


def read(path):
    return path.read_text(encoding='utf-8')


def verifier():
    repo = ROOT.parents[2]
    load = lambda p: json.loads(read(p), object_pairs_hook=unique)
    entry, = (e for e in load(repo/'catalogue/catalogue.json')['entries'] if e['template_id'] == 'COMMERCE-T1')
    path = repo/entry['contrat']
    assert path.resolve() == ROOT/'montage/contrat-candidat.json'
    raw = read(path)
    canon = load(path)
    validate(canon, load(ROOT/'schemas/template.json'))
    music = load(ROOT/'audio/catalogue.json')
    assert canon['id'] == canon['template_id'] == entry['template_id']
    assert canon['version'] == entry['version'] == '2.0.0' and music['pack_version'] == '1.0.0'
    assert canon['audio_profile'] == music['audio_profile'] == entry['audio_profile'] == 'afrobeat_amapiano_commerce'
    approved = load(ROOT/'approvals/musiques-validees.json')['pistes_pixabay']
    ids = [t['id'] for t in music['pistes']]
    assert ids == [t[0] for t in approved] and len(set(ids)) == 4 and 573944 not in ids
    assert not any(str(t[0]) in raw or t[1].casefold() in raw.casefold().replace(canon['audio_profile'], '') for t in approved if t[1] != 'Afrobeat')
    assert all(str(i) not in raw for i in ids + [573944])
    # Une URL éditoriale préexistante dans reference.url n'est pas un transport du moteur.
    def walk(obj, at=()):
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert k.lower() not in {'ota','endpoint','cloudflare','bucket','pack_version','pistes','tracks','download_url'}
                walk(v, at+(k,))
        elif isinstance(obj, list):
            for v in obj: walk(v, at)
        elif isinstance(obj, str):
            assert obj.casefold() not in {t[1].casefold() for t in approved}
            assert '.mp3' not in obj.lower()
            if '://' in obj: assert at == ('reference','url')
    walk(canon)
    assert entry['ota_implemented'] is False
    return {'canon':entry['contrat'], 'version_gabarit':canon['version'], 'version_pack':music['pack_version'], 'profil':music['audio_profile'], 'pistes_approuvees':len(ids), 'ota_implemente':False}


if __name__ == '__main__':
    print(json.dumps(verifier(), ensure_ascii=False, indent=2))
