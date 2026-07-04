#!/usr/bin/env python3
"""Release smoke tests for GCW's public command-line workflows."""

from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
NODE = "node"


def run(*args: str, expect: int = 0, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=ROOT,
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path == "/redirect-external":
            self.send_response(302)
            self.send_header("Location", "http://127.0.0.1:65530/outside")
            self.end_headers()
            return
        if self.path == "/asset.bin":
            body = b"gcw-asset"
            content_type = "application/octet-stream"
        elif self.path.startswith("/asset.js"):
            body = b"window.fixtureLoaded = true;"
            content_type = "text/javascript"
        elif self.path == "/child":
            body = b"<!doctype html><title>Child</title><h1>Child route</h1>"
            content_type = "text/html"
        elif self.path == "/missing":
            self.send_error(404)
            return
        else:
            body = b"""<!doctype html>
<html><head><title>GCW fixture</title><script src='/asset.js?x-amz-signature=topsecret'></script></head>
<body style='margin:0;background:#ff0000;min-height:100vh'><a href='/child'>Child</a>
<canvas id='unused'></canvas><canvas id='used'></canvas>
<script>document.querySelector('#used').getContext('2d'); setTimeout(() => { document.body.style.background = '#00ff00'; }, 1000);</script>
</body></html>"""
            content_type = "text/html"
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def fixture_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def complete_teardown_artifacts(workspace: Path, gpu_required: bool = False) -> None:
    root = workspace / ".gcw"
    spec = root / "SITE_SPEC.md"
    spec_text = re.sub(r"<!-- REQUIRED.*?-->", "Completed from persisted evidence.", spec.read_text(encoding="utf-8"))
    spec_text = spec_text.replace(
        "| Completed from persisted evidence. | Exact / Approximate / Unknown / Excluded | SOURCE / PARTIAL / GUESS |  | yes / no |  |",
        "| Layout | Exact | SOURCE | evidence/site-inventory.json | no | Matches measured grid and breakpoints |",
    )
    spec.write_text(spec_text, encoding="utf-8")
    design = {
        "meta": {"name": "fixture"},
        "design_system": {"color": {"primary": "#000000"}},
        "design_style": {"aesthetic": {"mood": ["neutral"]}},
        "visual_effects": {"overview": {"effect_intensity": "none"}},
    }
    design_path = root / "evidence" / "design-dna" / "design-dna.json"
    design_path.write_text(json.dumps(design), encoding="utf-8")
    (root / "evidence" / "site-inventory.json").write_text(json.dumps({"fixture": True}), encoding="utf-8")
    (root / "evidence" / "route-map.json").write_text(json.dumps({"routes": [{"route": "/"}]}), encoding="utf-8")
    interaction_states = {
        "schemaVersion": 1,
        "states": [{
            "id": "home-stable",
            "route": "/",
            "trigger": "initial load",
            "expected": "stable home view",
            "evidence": ["screenshots/desktop/home.png"],
        }],
    }
    (root / "evidence" / "interaction-states.json").write_text(json.dumps(interaction_states), encoding="utf-8")
    Image.new("RGB", (8, 8), "#ffffff").save(root / "evidence" / "screenshots" / "desktop" / "home.png")
    Image.new("RGB", (8, 8), "#ffffff").save(root / "evidence" / "screenshots" / "mobile" / "home.png")
    (root / "evidence" / "network" / "requests.json").write_text(json.dumps({"requests": []}), encoding="utf-8")
    shader = root / "evidence" / "web-shader-extractor"
    if gpu_required:
        decision = {"schemaVersion": 1, "decision": "required", "checkedSurfaces": ["canvas#hero"], "detectionEvidence": ["evidence/site-inventory.json"]}
        scout = {"schemaVersion": 3, "lockStatus": "locked", "gateDecision": {"targetLocked": True}}
        replay = {"schemaVersion": 3, "unknowns": {"blocking": []}, "gateDecision": {"replayReady": True, "blockers": []}}
        (shader / "scout-card.json").write_text(json.dumps(scout), encoding="utf-8")
        (shader / "replay-manifest.json").write_text(json.dumps(replay), encoding="utf-8")
    else:
        decision = {"schemaVersion": 1, "decision": "not-applicable", "checkedSurfaces": ["main document and iframes"], "detectionEvidence": ["evidence/site-inventory.json"]}
    (shader / "gpu-decision.json").write_text(json.dumps(decision), encoding="utf-8")


class ReleaseSmokeTests(unittest.TestCase):
    def test_skill_and_package_contract(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\nname: gcw\n"))
        for reference in re.findall(r"`references/([^`]+\.md)`", skill):
            self.assertTrue((ROOT / "references" / reference).is_file(), reference)

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('$gcw', metadata)
        short = re.search(r'^  short_description: "([^"]+)"$', metadata, re.M)
        self.assertIsNotNone(short)
        self.assertGreaterEqual(len(short.group(1)), 25)
        self.assertLessEqual(len(short.group(1)), 64)

        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        harness = json.loads((ROOT / "assets" / "gcw-package.json").read_text(encoding="utf-8"))
        harness_lock = json.loads((ROOT / "assets" / "gcw-package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(package["version"], lock["version"])
        self.assertEqual(package["dependencies"]["playwright"], harness["dependencies"]["playwright"])
        self.assertEqual(harness["dependencies"]["playwright"], harness_lock["packages"]["node_modules/playwright"]["version"])
        self.assertEqual(package["version"], "1.2.0")

        flow = "TEARDOWN_PHASE -> FAITHFUL_CLONE -> REVIEW_GATE -> CREATIVE_REBUILD"
        self.assertIn(flow, (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn(flow, (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("## Evidence orchestration: the GCW difference", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("## 证据编排：GCW 的核心差异", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("A screenshot is one frame. A live website is a million.", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("截图只有一帧。活的网站有千万帧。", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("GCW stands for Gao Copy Website. Yes, the name is that literal.", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("GCW 就是 Gao Copy Website。对，名字就这么直白。", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("SITE_SPEC.md", skill)
        self.assertIn("Stop at REVIEW_GATE", skill)
        self.assertIn("During every standard or deep `TEARDOWN_PHASE`, invoke `design-dna`", skill)
        self.assertIn("also invoke `web-shader-extractor`", skill)
        self.assertIn("Only after these decisions and calls are complete", skill)
        self.assertIn("If required `design-dna` is unavailable, stop", skill)
        for asset in (
            "site-spec-template.md", "site-spec-minimal-template.md", "creative-brief-template.md", "asset-manifest.example.json",
            "teardown-manifest.template.json", "evidence-index.template.json", "gpu-decision.template.json",
        ):
            self.assertTrue((ROOT / "assets" / asset).is_file(), asset)

        workflows = [ROOT / ".github" / "workflows" / "ci.yml", ROOT / "assets" / "github-workflows" / "gcw-visual-regression.yml"]
        for workflow in workflows:
            content = workflow.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"uses:\s+[^\s#]+@v\d+", content), workflow)

        environment = json.loads(run(NODE, "scripts/check_environment.mjs").stdout)
        self.assertIn("teardownReady", environment)
        self.assertIn("teardownRequirements", environment)
        self.assertNotIn("companionSkills", environment["optional"])

    def test_init_is_non_destructive_and_rejects_secret_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            state_path = Path(temp) / ".gcw" / "run-state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["schemaVersion"], 4)
            self.assertIn("cloneMode", state)
            self.assertEqual(state["permissionBoundary"], "unconfirmed")
            self.assertEqual(state["currentPhase"], "TEARDOWN_PHASE")
            self.assertEqual(state["outcome"], "teardown")
            self.assertEqual(state["teardownDepth"], "standard")
            self.assertEqual(state["reviewDecisions"], [])
            self.assertEqual(state["conditionalGates"]["assetProvenance"], "enable-when-asset-heavy-offline-or-maintained")
            self.assertTrue(state["conditionalGates"]["designDna"])
            self.assertEqual(state["conditionalGates"]["gpuForensics"], "required-when-canvas-webgl-webgpu-or-shaders-detected")
            gcw = Path(temp) / ".gcw"
            self.assertTrue((gcw / "SITE_SPEC.md").is_file())
            self.assertTrue((gcw / "teardown-manifest.json").is_file())
            self.assertTrue((gcw / "evidence" / "evidence-index.json").is_file())
            self.assertTrue((gcw / "evidence" / "screenshots" / "desktop").is_dir())
            self.assertTrue((gcw / "evidence" / "design-dna").is_dir())
            self.assertTrue((gcw / "evidence" / "web-shader-extractor" / "gpu-decision.json").is_file())
            for name in ("site-inventory.json", "route-map.json", "interaction-states.json"):
                self.assertTrue((gcw / "evidence" / name).is_file())
            state_path.write_text('{"preserved": true}\n', encoding="utf-8")
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), {"preserved": True})
            rejected = run(
                PYTHON,
                "scripts/init_reconstruction.py",
                temp,
                "--url",
                "https://example.com/?token=secret",
                expect=2,
            )
            self.assertIn("credential-like", rejected.stderr)
            recovery = run(
                PYTHON, "scripts/init_reconstruction.py", temp,
                "--url", "https://example.com/", "--implementation-path", "PRODUCTION_RECOVERY",
                expect=2,
            )
            self.assertIn("requires confirmed authorization", recovery.stderr)

    def test_ci_installer_is_reproducible_and_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            run(PYTHON, "scripts/install_ci.py", temp, "--source-url", "https://example.com/")
            package = json.loads((project / ".gcw" / "package.json").read_text(encoding="utf-8"))
            lock = json.loads((project / ".gcw" / "package-lock.json").read_text(encoding="utf-8"))
            self.assertEqual(package["dependencies"]["playwright"], "1.61.1")
            self.assertEqual(lock["packages"]["node_modules/playwright"]["version"], "1.61.1")
            self.assertTrue((project / ".gcw" / "tools" / "url_safety.mjs").exists())
            self.assertTrue((project / ".gcw" / "tools" / "url_safety.py").exists())
            self.assertTrue((project / ".gcw" / "tools" / "check_runtime_independence.py").exists())
            self.assertEqual((project / ".gcw" / "requirements.txt").read_text(encoding="utf-8").strip(), "Pillow==12.2.0")
            run(PYTHON, str(project / ".gcw" / "tools" / "route_smoke.py"), "--help")
            copied_capture = run(NODE, str(project / ".gcw" / "tools" / "capture_compare.mjs"), expect=1)
            self.assertIn("Usage: capture_compare.mjs", copied_capture.stderr)
            scenario = project / ".gcw" / "capture-scenarios.json"
            scenario.write_text('{"preserved": true}\n', encoding="utf-8")
            run(PYTHON, "scripts/install_ci.py", temp, "--source-url", "https://example.com/")
            self.assertEqual(json.loads(scenario.read_text(encoding="utf-8")), {"preserved": True})

    def test_route_smoke_stays_on_base_origin(self) -> None:
        with fixture_server() as base:
            run(PYTHON, "scripts/route_smoke.py", "--base-url", base, "--route", "/", "--route", "/child")
            rejected = run(
                PYTHON,
                "scripts/route_smoke.py",
                "--base-url",
                base,
                "--route",
                "https://example.com/",
                expect=2,
            )
            self.assertIn("stay on the configured origin", rejected.stderr)
            redirected = run(
                PYTHON,
                "scripts/route_smoke.py",
                "--base-url",
                base,
                "--route",
                "/redirect-external",
                expect=1,
            )
            self.assertIn("redirect left the base origin", redirected.stdout)

    def test_inventory_crawls_routes_and_redacts_resource_secrets(self) -> None:
        with fixture_server() as base, tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "inventory.json"
            run(NODE, "scripts/site_inventory.mjs", "--url", base, "--out", str(out), "--settle-ms", "0")
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual({item["route"] for item in report["routes"]}, {"/", "/child"})
            serialized = json.dumps(report)
            self.assertNotIn("topsecret", serialized)
            self.assertIn("REDACTED", serialized)
            canvases = report["routes"][0]["surface"]["canvases"]
            self.assertEqual([canvas["context"] for canvas in canvases], ["unknown", "2d"])
            route_map = json.loads((Path(temp) / "route-map.json").read_text(encoding="utf-8"))
            self.assertEqual({item["route"] for item in route_map["routes"]}, {"/", "/child"})
            network = json.loads((Path(temp) / "network" / "requests.json").read_text(encoding="utf-8"))
            self.assertTrue(any(item["url"].endswith("/asset.js?x-amz-signature=REDACTED") for item in network["requests"]))

            redirected = Path(temp) / "redirected.json"
            run(NODE, "scripts/site_inventory.mjs", "--url", f"{base}/redirect-external", "--out", str(redirected), "--settle-ms", "0")
            redirect_report = json.loads(redirected.read_text(encoding="utf-8"))
            self.assertIn("redirect left the allowed origin", redirect_report["routes"][0]["error"])

    def test_capture_applies_phase_and_rejects_filename_collisions(self) -> None:
        with fixture_server() as base, tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = {
                "sourceUrl": base,
                "candidateUrl": base,
                "seed": 7,
                "scenarios": [
                    {
                        "id": "phase",
                        "route": "/",
                        "viewport": {"width": 64, "height": 64},
                        "clockMode": "controlled",
                        "readyFunction": "document.readyState === 'complete'",
                        "readyDelayMs": 0,
                        "phaseMs": 1200,
                        "afterInputDelayMs": 0,
                    }
                ],
            }
            config_path = root / "capture.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            output = root / "results"
            run(NODE, "scripts/capture_compare.mjs", "--config", str(config_path), "--output", str(output))
            manifest = json.loads((output / "capture-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["captures"][0]["timing"]["phaseMs"], 1200)
            pixel = Image.open(output / "phase.source.png").convert("RGB").getpixel((32, 32))
            self.assertGreater(pixel[1], 200)
            self.assertLess(pixel[0], 30)

            config["scenarios"] = [
                {"id": "same id", "route": "/", "readyFunction": "true"},
                {"id": "same-id", "route": "/", "readyFunction": "true"},
            ]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            rejected = run(
                NODE,
                "scripts/capture_compare.mjs",
                "--config",
                str(config_path),
                "--output",
                str(root / "collision"),
                expect=1,
            )
            self.assertIn("id collision", rejected.stderr)

    def test_image_diff_threshold_validation_and_batch_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sample.source.png"
            candidate = root / "sample.candidate.png"
            Image.new("RGB", (8, 8), "#000000").save(source)
            Image.new("RGB", (8, 8), "#000000").save(candidate)
            run(PYTHON, "scripts/batch_image_diff.py", temp)
            report = json.loads((root / "visual-diff-report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["passed"])
            invalid = run(PYTHON, "scripts/image_diff.py", str(source), str(candidate), "--threshold", "256", expect=2)
            self.assertIn("between 0 and 255", invalid.stderr)

    def test_workflow_requires_review_gate_before_creative(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            invalid = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "CREATIVE_REBUILD", expect=2)
            self.assertIn("invalid transition", invalid.stderr)
            incomplete_study = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "COMPLETE", expect=2)
            self.assertIn("finalize_teardown.py to pass", incomplete_study.stderr)
            missing_analysis = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "FAITHFUL_CLONE", expect=2)
            self.assertIn("finalize_teardown.py to pass", missing_analysis.stderr)
            complete_teardown_artifacts(Path(temp))
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "FAITHFUL_CLONE")
            missing_report = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE", expect=2)
            self.assertIn("CLONE_REPORT.md", missing_report.stderr)
            (Path(temp) / ".gcw" / "CLONE_REPORT.md").write_text("# Clone report\n\nBaseline verified.\n", encoding="utf-8")
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "REVIEW_GATE")
            mismatched_decision = run(
                PYTHON, "scripts/advance_workflow.py", temp,
                "--to", "CREATIVE_REBUILD", "--decision", "A", expect=2,
            )
            self.assertIn("requires --to FAITHFUL_CLONE", mismatched_decision.stderr)
            missing_decision = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "CREATIVE_REBUILD", expect=2)
            self.assertIn("--decision", missing_decision.stderr)
            missing_brief = run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "CREATIVE_REBUILD", "--decision", "C", expect=2)
            self.assertIn("CREATIVE_BRIEF.md", missing_brief.stderr)
            brief = """# Creative brief

## Keep
Layout.
## Remove
Original branding.
## Change
Content.
## New brand, content, and features
New identity.
## Innovation direction
Editorial motion.
## Final acceptance target
Approved screenshots.
"""
            (Path(temp) / ".gcw" / "CREATIVE_BRIEF.md").write_text(brief, encoding="utf-8")
            run(PYTHON, "scripts/advance_workflow.py", temp, "--to", "CREATIVE_REBUILD", "--decision", "C")
            state = json.loads((Path(temp) / ".gcw" / "run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["reviewDecisions"][-1]["decision"], "C")
            self.assertEqual(state["analysisGates"], {"designDna": "complete", "gpuForensics": "not-applicable", "teardown": "passed"})
            manifest = json.loads((Path(temp) / ".gcw" / "teardown-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "passed")
            evidence_index = json.loads((Path(temp) / ".gcw" / "evidence" / "evidence-index.json").read_text(encoding="utf-8"))
            self.assertTrue({"design-dna", "gpu-decision", "site-spec", "site-inventory", "route-map", "interaction-states"}.issubset({entry["kind"] for entry in evidence_index["entries"]}))
            design_entry = next(entry for entry in evidence_index["entries"] if entry["kind"] == "design-dna")
            self.assertEqual(design_entry["schemaContract"], "three-dimension-v1")

    def test_gpu_teardown_requires_target_lock_and_replay_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace, gpu_required=True)
            scout_path = workspace / ".gcw" / "evidence" / "web-shader-extractor" / "scout-card.json"
            scout = json.loads(scout_path.read_text(encoding="utf-8"))
            scout["lockStatus"] = "provisional"
            scout_path.write_text(json.dumps(scout), encoding="utf-8")
            blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("TARGET_LOCKED", blocked.stderr)
            scout["lockStatus"] = "locked"
            scout["schemaVersion"] = 4
            scout_path.write_text(json.dumps(scout), encoding="utf-8")
            drifted = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("schema drift", drifted.stderr)
            scout["schemaVersion"] = 3
            scout_path.write_text(json.dumps(scout), encoding="utf-8")
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            manifest = json.loads((workspace / ".gcw" / "teardown-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["gpuAnalysis"]["status"], "replay-ready")
            index = json.loads((workspace / ".gcw" / "evidence" / "evidence-index.json").read_text(encoding="utf-8"))
            shader_entries = [entry for entry in index["entries"] if entry["sourceSkill"] == "web-shader-extractor"]
            self.assertTrue(shader_entries)
            self.assertTrue(all(entry["schemaVersion"] == 3 for entry in shader_entries))

    def test_teardown_rejects_invalid_truth_fidelity_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            spec_path = workspace / ".gcw" / "SITE_SPEC.md"
            valid_spec = spec_path.read_text(encoding="utf-8")
            cases = (
                ("| Exact | SOURCE |", "| Similar | SOURCE |", "invalid Fidelity"),
                ("| Exact | SOURCE |", "| Exact | CERTAIN |", "invalid Truth"),
                ("| no | Matches measured", "| maybe | Matches measured", "invalid Blocking"),
                ("| evidence/site-inventory.json |", "|  |", "requires Evidence and Acceptance"),
                ("| Matches measured grid and breakpoints |", "|  |", "requires Evidence and Acceptance"),
            )
            for old, new, message in cases:
                spec_path.write_text(valid_spec.replace(old, new), encoding="utf-8")
                blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
                self.assertIn(message, blocked.stderr)
            spec_path.write_text(valid_spec, encoding="utf-8")
            run(PYTHON, "scripts/finalize_teardown.py", temp)

    def test_teardown_validation_failure_does_not_finalize_site_spec(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            index_path = workspace / ".gcw" / "evidence" / "evidence-index.json"
            index_path.write_text("not json", encoding="utf-8")
            blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("invalid JSON artifact", blocked.stderr)
            spec = (workspace / ".gcw" / "SITE_SPEC.md").read_text(encoding="utf-8")
            self.assertIn("Status: DRAFT", spec)
            self.assertNotIn("Status: FINAL", spec)

    def test_teardown_rejects_invalid_screenshot_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(PYTHON, "scripts/init_reconstruction.py", temp, "--url", "https://example.com/")
            complete_teardown_artifacts(workspace)
            (workspace / ".gcw" / "evidence" / "screenshots" / "desktop" / "home.png").write_bytes(b"not-an-image")
            blocked = run(PYTHON, "scripts/finalize_teardown.py", temp, expect=1)
            self.assertIn("invalid screenshot image", blocked.stderr)

    def test_minimal_teardown_uses_reduced_spec_and_optional_design_dna(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            run(
                PYTHON, "scripts/init_reconstruction.py", temp,
                "--url", "https://example.com/", "--teardown-depth", "minimal",
            )
            complete_teardown_artifacts(workspace)
            root = workspace / ".gcw"
            spec = root / "SITE_SPEC.md"
            text = re.sub(r"<!-- REQUIRED.*?-->", "Completed from persisted evidence.", spec.read_text(encoding="utf-8"))
            text = text.replace(
                "| Completed from persisted evidence. | Exact / Approximate / Unknown / Excluded | SOURCE / PARTIAL / GUESS |  | yes / no |  |",
                "| Layout | Exact | SOURCE | evidence/site-inventory.json | no | Matches the authorized page |",
            )
            spec.write_text(text, encoding="utf-8")
            (root / "evidence" / "design-dna" / "design-dna.json").unlink()
            run(PYTHON, "scripts/finalize_teardown.py", temp)
            manifest = json.loads((root / "teardown-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["designDna"]["status"], "recommended-not-provided")

    def test_runtime_independence_blocks_source_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / "network.json"
            evidence.write_text(json.dumps({"requests": ["https://source.example/app.js", "https://cdn.example/a.js"]}), encoding="utf-8")
            build = Path(temp) / "dist"
            build.mkdir()
            (build / "index.js").write_text("const api = 'https://cdn.example/a.js';", encoding="utf-8")
            blocked = run(
                PYTHON, "scripts/check_runtime_independence.py", str(evidence),
                "--source-url", "https://source.example:443", "--build-dir", str(build), expect=1,
            )
            self.assertIn("source.example/app.js", blocked.stdout)
            evidence.write_text(json.dumps({"requests": ["https://cdn.example/a.js"]}), encoding="utf-8")
            (build / "index.js").write_text("const api = 'https://source.example/runtime';", encoding="utf-8")
            build_blocked = run(
                PYTHON, "scripts/check_runtime_independence.py", str(evidence),
                "--source-url", "https://source.example", "--build-dir", str(build), expect=1,
            )
            self.assertIn("index.js", build_blocked.stdout)
            (build / "index.js").write_text("const api = 'https://cdn.example/a.js';", encoding="utf-8")
            run(
                PYTHON, "scripts/check_runtime_independence.py", str(evidence),
                "--source-url", "https://source.example", "--build-dir", str(build),
            )

    def test_asset_downloader_checks_type_checksum_and_is_idempotent(self) -> None:
        with fixture_server() as base, tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            digest = hashlib.sha256(b"gcw-asset").hexdigest()
            manifest = root / "assets.json"
            manifest.write_text(json.dumps({"assets": [{
                "sourceUrl": f"{base}/asset.bin",
                "localPath": "public/asset.bin",
                "contentType": "application/octet-stream",
                "checksumSha256": digest,
            }]}), encoding="utf-8")
            first = run(PYTHON, "scripts/download_assets.py", str(manifest), "--output", str(root / "out"))
            self.assertIn('"status": "downloaded"', first.stdout)
            second = run(PYTHON, "scripts/download_assets.py", str(manifest), "--output", str(root / "out"))
            self.assertIn('"status": "skipped"', second.stdout)
            manifest.write_text(json.dumps({"assets": [{
                "sourceUrl": f"{base}/asset.bin",
                "localPath": "../escape.bin",
                "contentType": "application/octet-stream",
            }]}), encoding="utf-8")
            escaped = run(PYTHON, "scripts/download_assets.py", str(manifest), "--output", str(root / "out"), expect=1)
            self.assertIn("localPath must stay inside output", escaped.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
