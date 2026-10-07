#!/usr/bin/env python3
import base64, hashlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT / "channels" / "stable" / "manifest.json"
MAX_MANIFEST = 12 * 1024
ALLOWED_ENVELOPE = {"schema", "algorithm", "key_id", "payload", "signature"}
REQUIRED_PAYLOAD = {"product","channel","generation","version","security_version","board","chip","partition_layout","size","sha256","url","min_updater","notes_de","notes_en"}
ALLOWED_BOARDS = {"esp32s3-n16r8","esp32s3wood-n16r8","esp32s3wood-n8r8","esp32s3echobase-n8r8", "esp32s3echobase-n16r8"}

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
layouts={"esp32s3-n16r8":"ota-v1-4m","esp32s3wood-n16r8":"ota-v1-4m","esp32s3wood-n8r8":"ota-v1-2m","esp32s3echobase-n8r8":"ota-v1-2m","esp32s3echobase-n16r8":"ota-v1-4m"}
if doc["key_id"]!="prod-2026-01" or type(payload["security_version"]) is not int or not 0<=payload["security_version"]<=65535:
    raise SystemExit("invalid key/security version")
if type(payload["generation"]) is not int or not 1<=payload["generation"]<=2147483647:
    raise SystemExit("generation exceeds device parser bounds")
if layouts[payload["board"]]!=payload["partition_layout"] or payload["size"]>(4 if payload["partition_layout"]=="ota-v1-4m" else 2)*1024*1024:
    raise SystemExit("invalid board/layout/size")
for field in ("version","min_updater"):
    if not isinstance(payload[field],str) or len(payload[field])>=32 or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?",payload[field]):
        raise SystemExit("invalid version")
for field in ("notes_de","notes_en"):
    if not isinstance(payload[field],str) or not 0<len(payload[field].encode())<256:
        raise SystemExit("invalid release notes")
if not payload["url"].startswith(prefix+"v"+payload["version"]+"/") or len(payload["url"])>=256:
    raise SystemExit("URL/version mismatch")
if MANIFEST.parent.name in ALLOWED_BOARDS:
    if payload["board"]!=MANIFEST.parent.name or payload["channel"]!=MANIFEST.parent.parent.name:
        raise SystemExit("manifest does not match its board/channel path")
print("manifest structure valid; cryptographic verification is performed separately")
