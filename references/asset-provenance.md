# Asset provenance

Use an asset manifest for asset-heavy, offline, or maintained work. Each entry records source URL, deterministic local path, purpose, license/attribution, content type, and SHA-256 checksum. Only download in-scope assets whose reuse is permitted.

Run `scripts/download_assets.py` with a concurrency limit. Existing checksum-matching files are skipped; `--refresh` is explicit. The downloader rejects traversal paths, credential-bearing URLs, content-type mismatches, and checksum mismatches. Never package target-site assets inside the GCW skill.
