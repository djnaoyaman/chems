"""Stable site-wide revision time, independent of build/deployment wall clocks."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess

# This source correction was authored on 2026-11-02 JST. Also supports source ZIPs.
SOURCE_UPDATED = '2026-11-01T23:26:00+00:00'
# Published inputs only: archived English drafts, notes and test runs are not updates.
PUBLISHED_PATHS = ('build.py', 'config.json', 'data', 'texts/ja', 'src', 'art',
                   'tools/listening_catalog.py', 'tools/site_updated.py')


def site_updated(root, fallback=SOURCE_UPDATED):
    """Use the latest published-input commit, with an explicit source ZIP fallback.

    CI checks out full history so an unrelated docs commit cannot become the date.
    A rebuild of the same source returns the same value; release dates are separate.
    """
    root = Path(root).resolve()
    baseline = datetime.fromisoformat(fallback)
    if baseline.tzinfo is None:
        raise ValueError('Source update timestamp must include a timezone')
    try:
        top = subprocess.check_output(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                                      text=True, stderr=subprocess.DEVNULL).strip()
        if Path(top).resolve() != root:
            return baseline.astimezone(timezone.utc).isoformat()
        value = subprocess.check_output(
            ['git', '-C', str(root), 'log', '--first-parent', '-1', '--format=%cI', '--', *PUBLISHED_PATHS],
            text=True, stderr=subprocess.DEVNULL).strip()
        if value:
            baseline = max(baseline, datetime.fromisoformat(value))
    except (OSError, subprocess.CalledProcessError):
        pass  # Source archives do not contain Git metadata.
    return baseline.astimezone(timezone.utc).isoformat()
