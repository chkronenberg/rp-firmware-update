#!/usr/bin/env python3
"""Verify the checked-in manifest with the production public key."""

import base64
import json
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[1]
document = json.loads((root / "channels/stable/manifest.json").read_text(encoding="utf-8"))
if document.get("state") == "unconfigured":
    print("stable channel intentionally unconfigured")
    raise SystemExit(0)
payload = base64.b64decode(document["payload"], validate=True)
signature = base64.b64decode(document["signature"], validate=True)
with tempfile.NamedTemporaryFile() as payload_file, tempfile.NamedTemporaryFile() as signature_file:
    payload_file.write(payload)
    payload_file.flush()
    signature_file.write(signature)
    signature_file.flush()
    subprocess.run(["openssl", "dgst", "-sha256", "-verify", str(root / "ota_public_key.pem"),
                    "-signature", signature_file.name, payload_file.name], check=True)
