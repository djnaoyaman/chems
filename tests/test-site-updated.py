"""Regression: published content/art advances the footer, rebuilds/docs do not."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.site_updated import site_updated


class SiteUpdated(unittest.TestCase):
    def test_archive_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(site_updated(d, '2026-11-01T23:26:00+00:00'),
                             '2026-11-01T23:26:00+00:00')

    def test_published_inputs_and_rebuild(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def git(*args, **kwargs):
                return subprocess.check_output(['git', '-C', d, *args], stderr=subprocess.DEVNULL, **kwargs)
            git('init'); git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.invalid')
            def commit(path, date):
                target = root / path; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(date)
                git('add', path)
                git('commit', '-m', path, env={**os.environ, 'GIT_AUTHOR_DATE': date, 'GIT_COMMITTER_DATE': date})
            fallback = '2026-10-01T00:00:00+00:00'
            for path, stamp in [('data/works.json', '2026-11-01T14:00:00+00:00'),
                                ('art/sw.jpg', '2026-11-01T16:54:49+00:00'),
                                ('texts/ja/sw.md', '2026-11-02T00:00:00+00:00')]:
                commit(path, stamp)
                self.assertEqual(site_updated(root, fallback), stamp)
                self.assertEqual(site_updated(root, fallback), stamp)
            for path in ['README.md', 'notes/review.md', 'texts/en/sw.md', 'tests/check.py']:
                commit(path, '2026-11-03T00:00:00+00:00')
                self.assertEqual(site_updated(root, fallback), stamp)
            # Integration time, not an older feature-branch authoring timestamp.
            git('checkout', '-b', 'art-fix')
            commit('art/wo.jpg', '2026-11-03T01:00:00+00:00')
            git('checkout', '-')
            merged = '2026-11-03T02:00:00+00:00'
            git('merge', '--no-ff', 'art-fix', '-m', 'Publish artwork',
                env={**os.environ, 'GIT_AUTHOR_DATE': merged, 'GIT_COMMITTER_DATE': merged})
            self.assertEqual(site_updated(root, fallback), merged)
            # A future source baseline must not be rolled back by old history.
            self.assertEqual(site_updated(root, '2026-11-04T00:00:00+00:00'), '2026-11-04T00:00:00+00:00')

    def test_jst_rollover(self):
        stamp = datetime.fromisoformat('2026-11-01T16:54:49+00:00')
        self.assertEqual(stamp.astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M JST'),
                         '2026-11-02 01:54 JST')


if __name__ == '__main__':
    unittest.main()
