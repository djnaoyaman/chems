# Interaction events

GA4 stream: G-GKZHN40P02. Existing page views remain unchanged.

- video_open: valid YouTube embed requested (not confirmed playback)
- video_seek_request: iframe loaded at requested position_seconds
- catalog_filter: catalog filter selected
- creator_site_visit: portfolio link activated; target_site

Events use gtag event commands, transport_type=beacon, and explicit send_to. Added payloads omit answers, correctness, scores, health/treatment selections, search strings, query parameters, fragments and personal identifiers. Parameters are allowlisted. Measurement failures never block the interaction. Only the public GitHub Pages hostname sends these events.

Verify event receipt with GA4 Realtime/DebugView. Browser tests check forwarding and payloads; they cannot prove GA ingestion. These changes do not mark key events or alter GA property settings.
