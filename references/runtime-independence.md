# Runtime independence

Final `CLEAN_REBUILD` and `CREATIVE_REBUILD` deliverables must make no runtime requests to the source origin. Run `scripts/check_runtime_independence.py` against captured network evidence. Declare legal third-party services with repeatable `--allow-origin` entries.

Teardown does not require this gate. Recovery work may temporarily use the original production backend; document the recovery stage and apply the gate incrementally rather than pretending independence already exists.
