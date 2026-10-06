#!/usr/bin/env python3
import base64, hashlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT / "channels" / "stable" / "manifest.json"
MAX_MANIFEST = 12 * 1024
ALLOWED_ENVELOPE = {"schema", "algorithm", "key_id", "payload", "signature"}
REQUIRED_PAYLOAD = {"product","channel","generation","version","security_version","board","chip","partition_layout","size","sha256","url","min_updater","notes_de","notes_en"}
ALLOWED_BOARDS = {"esp32s3-n16r8","esp32s3wood-n16r8","esp32s3wood-n8r8","esp32s3echobase-n8r8"}

raw = MANIFEST.read_bytes()
if len(raw) > MAX_MANIFEST:
    raise SystemExit("manifest too large")
doc = json.loads(raw)
if doc.get("state") == "unconfigured":
    if set(doc) != {"schema","state","channel","message"} or doc["schema"] != 1 or doc["channel"] not in ("stable","pilot"):
        raise SystemExit("invalid unconfigured manifest")
    print("stable channel intentionally unconfigured")
    raise SystemExit(0)
if set(doc) != ALLOWED_ENVELOPE or doc["schema"] != 1 or doc["algorithm"] != "ECDSA-P256-SHA256":
    raise SystemExit("invalid envelope")
if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,31}", doc["key_id"]):
    raise SystemExit("invalid key id")
try:
    payload_raw = base64.b64decode(doc["payload"], validate=True)
    base64.b64decode(doc["signature"], validate=True)
except Exception as exc:
    raise SystemExit(f"invalid base64: {exc}")
payload = json.loads(payload_raw)
if set(payload) != REQUIRED_PAYLOAD:
    raise SystemExit(f"payload fields differ: {set(payload) ^ REQUIRED_PAYLOAD}")
if payload["product"] != "rp-phone" or payload["channel"] not in ("stable","pilot") or payload["chip"] != "esp32s3":
    raise SystemExit("wrong product, channel or chip")
if payload["board"] not in ALLOWED_BOARDS:
    raise SystemExit("unsupported board")
if not isinstance(payload["generation"], int) or payload["generation"] < 1:
    raise SystemExit("invalid generation")
if not isinstance(payload["size"], int) or payload["size"] < 65536 or payload["size"] > 4 * 1024 * 1024:
    raise SystemExit("invalid image size")
if not re.fullmatch(r"[0-9a-f]{64}", payload["sha256"]):
    raise SystemExit("invalid image digest")
prefix = "https://github.com/chkronenberg/rp-firmware-update/releases/download/"
if not payload["url"].startswith(prefix) or "?" in payload["url"] or "#" in payload["url"]:
    raise SystemExit("release URL is not immutable or is outside this repository")
print("manifest structure valid; cryptographic verification is performed separately")
