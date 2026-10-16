#!/usr/bin/env python3
"""Restore an install's changed files. Review manifest first; later edits are replaced."""
import argparse
import json
from pathlib import Path
import shutil
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('manifest', type=Path)
p.add_argument('--apply', action='store_true', help='apply the displayed restoration')
a = p.parse_args()
for item in reversed(json.loads(a.manifest.read_text())):
    dest = Path(item['path'])
    print(('Restore ' if item['backup'] else 'Remove ') + str(dest))
    if a.apply:
        if dest.is_symlink() or (dest.exists() and not dest.is_file()):
            raise SystemExit(f'Refusing unexpected file type: {dest}')
        if item['backup']:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item['backup'], dest)
        else:
            dest.unlink(missing_ok=True)
