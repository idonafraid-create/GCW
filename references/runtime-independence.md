# Runtime independence

Final `CLEAN_REBUILD` and `CREATIVE_REBUILD` deliverables must make no runtime requests to the source origin. Check both captured network evidence and the final build output:

```text
python scripts/check_runtime_independence.py <network-evidence.json> --source-url <canonical-url> --build-dir <dist>
```

Third-party origins are not blocked by this gate. The source origin cannot be allowlisted; if the deliverable intentionally depends on it, the runtime-independence gate has not passed. Default HTTP and HTTPS ports are normalized before origins are compared.

Teardown does not require this gate. Recovery work may temporarily use the original production backend; document the recovery stage and apply the gate incrementally rather than pretending independence already exists.
