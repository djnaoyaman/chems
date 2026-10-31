"""Build listening data separately from existing editorial embeds; no external calls."""
import re

def catalog(works, sources):
    result = {'releases': [], 'editions': {}, 'recordings': {}, 'videos': {}, 'checkedAt': sources['checkedAt']}
    bindings = {(b['workId'], b['position']): b for b in sources['bindings']}
    assert len(bindings) == len(sources['bindings']), 'Duplicate listening binding'
    seen = set()
    for order, w in enumerate(works):
        declared = sources['editions'].get(w['id'])
        edition_id = declared['id'] if declared else w['id'] + '-unresolved-edition'
        date = w.get('records', {}).get('date', {}).get('v')
        precise = bool(date and re.fullmatch(r'\d{4}-\d{2}-\d{2}', date))
        release = {'id': w['id'], 'title': w['title'], 'type': w['type'], 'slug': w['slug'],
                   'date': {'year': int(w['year']), 'precision': 'day' if precise else 'year'},
                   'editorialOrder': order, 'editionIds': [edition_id]}
        if precise:
            release['date']['value'] = date
        else:
            note = w.get('records', {}).get('date_note', {}).get('v')
            if note:
                release['date']['label'] = note
                release['date']['precision'] = 'early' if note.get('en', '').startswith('early ') else ('late' if note.get('en', '').startswith('late ') else 'partial')
        result['releases'].append(release)
        edition = {'id': edition_id, 'releaseId': w['id'], 'label': declared['label'] if declared else {'ja': '掲載曲目・録音版の照合待ち', 'en': 'Listed tracklist; recording edition not yet matched'}, 'entries': []}
        if declared:
            edition['source'] = declared['source']
        for index, track in enumerate(w.get('tracklist', []), 1):
            recording_id = f"{w['id']}-recording-{index}"
            entry = {'id': f"{w['id']}-entry-{index}", 'position': index, 'positionLabel': str(track.get('no', index)), 'recordingId': recording_id, 'videoKey': None}
            recording = {'id': recording_id, 'title': track['title'], 'version': 'unresolved'}
            binding = bindings.get((w['id'], index))
            if binding:
                assert declared, 'Edition source required'
                assert binding['title'] == track['title'], 'Binding title mismatch'
                assert binding['videoId'] not in sources.get('excluded', []), 'Excluded unofficial source'
                recording['version'] = binding['version']
                key = binding['videoId']; entry['videoKey'] = key
                result['videos'][key] = {'id': key, 'testOnly': False, 'officialEvidence': binding['officialEvidence'],
                    'availability': binding['availability'], 'match': {'recordingId': recording_id, 'entryId': entry['id'], 'editionId': edition_id,
                    'title': track['title'], 'version': binding['version'], 'sourceUrl': edition['source'], 'checkedAt': sources['checkedAt'], 'reviewed': True}}
                seen.add((w['id'], index))
            edition['entries'].append(entry); result['recordings'][recording_id] = recording
        result['editions'][edition_id] = edition
    assert seen == set(bindings), 'Unmatched listening binding'
    return result
