"""Rebuild from pinned official bytes in an independent directory and compare hashes."""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile
from civia_data.common import ROOT,sha256,write_json
from civia_data.download import download
from civia_data.build import build
from civia_data.train import train


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--from-cache',action='store_true');args=parser.parse_args()
    expected=json.loads((ROOT/'data/artifacts.sha256.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='civia-reproduce-') as tmp:
        fresh=Path(tmp);(fresh/'data').mkdir()
        shutil.copy2(ROOT/'data/sources.lock.json',fresh/'data/sources.lock.json')
        if args.from_cache:
            (fresh/'data/raw').mkdir()
            for source in (ROOT/'data/raw').glob('ine_*.zip'):
                try:os.link(source,fresh/'data/raw'/source.name)
                except OSError:shutil.copy2(source,fresh/'data/raw'/source.name)
        download(fresh)
        build(fresh)
        train(fresh)
        compared={}
        for name,value in expected.items():
            if name.startswith(('data/processed/','ml/artifacts/')):
                actual=sha256(fresh/name)
                if actual!=value:raise ValueError(f'No reproducible: {name}')
                compared[name]=actual
        write_json(ROOT/'docs/evidencias/etapa-1/reproducibility.json',{'status':'PASS','mode':'verified_raw_cache' if args.from_cache else 'fresh_official_downloads','isolated_directory':True,'matching_artifacts':compared})
        print(f'Reconstrucción independiente: {len(compared)} artefactos idénticos SHA256')


if __name__=='__main__':main()
