import argparse
import json
from pathlib import Path
from civia_data.common import ROOT, sha256, write_json


def manifest(root=ROOT):
    root=Path(root)
    paths=list((root/'data/processed').glob('*'))+list((root/'ml/artifacts').glob('*'))
    paths += [root/'data/sources.lock.json',root/'data/dictionary.csv',root/'contracts/openapi.yaml',root/'requirements.lock']
    paths += list((root/'contracts/examples').glob('*.json'))
    hashes={p.relative_to(root).as_posix():sha256(p) for p in sorted(paths) if p.is_file()}
    write_json(root/'data/artifacts.sha256.json',hashes)
    return hashes


def verify(root=ROOT):
    root=Path(root)
    hashes=json.loads((root/'data/artifacts.sha256.json').read_text(encoding='utf-8'))
    for name,expected in hashes.items():
        if sha256(root/name)!=expected:
            raise ValueError('Hash de artefacto incorrecto: '+name)
    print(f'{len(hashes)} artefactos verificados')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--write',action='store_true');a=p.parse_args()
    manifest(a.root) if a.write else verify(a.root)
