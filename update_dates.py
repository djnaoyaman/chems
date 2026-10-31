"""Stable site-source modification time, never build or deployment time.

All pages share the navigation, archive data and templates. This clock
therefore covers their shared content dependencies as well as rendered prose.
Research verification dates and original publication dates remain independent.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import subprocess

SOURCE_PATHS = ('build.py', 'update_dates.py', 'config.json', 'data', 'texts', 'art', 'src')
# Reviewed source-export baseline for non-Git local previews. Not datetime.now().
# Production checkout has full history and always derives the value from Git.
SOURCE_EXPORT_UPDATED = '2026-10-31T09:58:00+00:00'

def source_modified(root):
    root = Path(root)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True, stderr=subprocess.DEVNULL).strip()
    try:
        top = git('rev-parse', '--show-toplevel')
    except (subprocess.CalledProcessError, FileNotFoundError):
        return SOURCE_EXPORT_UPDATED
    if Path(top).resolve() != root.resolve():
        return SOURCE_EXPORT_UPDATED
    if git('rev-parse', '--is-shallow-repository') == 'true':
        raise RuntimeError('Update dates require full source history (checkout fetch-depth: 0)')
    value = git('log', '-1', '--format=%cI', '--', *SOURCE_PATHS)
    if not value:
        raise RuntimeError('No source revision date found')
    return datetime.fromisoformat(value).astimezone(timezone.utc).isoformat(timespec='seconds')

def japanese_timestamp(value):
    dt = datetime.fromisoformat(value).astimezone(timezone(timedelta(hours=9)))
    return dt.strftime('%Y年%m月%d日 %H:%M JST')
