# Device icons

All device icons use the owner-approved ivory myChems wordmark from `src/brand/mychems-wordmark-ivory-1024.png` on opaque black. The full outline and aspect ratio are preserved; no emoji, substitute typeface, album artwork or official artist mark is used.

Regenerate with `python3 tools/generate_icons.py` (Pillow required). Exports: Apple 180, PNG 16/32/48/192/512, ICO 16/32/48, and maskable 192/512. Maskable exports keep the wordmark inside the central 80% safe circle.

The shared page template, 404 page and web manifest point to the `mychems-` exports. Compatibility copies at the previous `icons/` filenames and conventional root favicon/Apple Touch URLs also contain the current wordmark. The standalone preview embeds the same logo and icons. The build validates PNG SHA-256 values while retaining artwork/source and audio-file checks. Update that allowlist if deliberately regenerating assets.
