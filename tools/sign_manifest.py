#!/usr/bin/env python3
"""Create a signed RP stable-channel manifest for one immutable release asset."""

import argparse
import base64
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile
import struct

REPOSITORY = "chkronenberg/rp-firmware-update"
KEY_ID = "prod-2026-01"
ALLOWED_BOARDS = {"esp32s3-n16r8", "esp32s3wood-n16r8", "esp32s3wood-n8r8", "esp32s3echobase-n8r8"}
SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?")
SAFE_ASSET = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.bin")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", choices=("stable","pilot"), default="stable")
    parser.add_argument("--image", required=True, type=pathlib.Path)
    parser.add_argument("--private-key", required=True, type=pathlib.Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--generation", required=True, type=int)
    parser.add_argument("--security-version", required=True, type=int)
    parser.add_argument("--board", required=True, choices=sorted(ALLOWED_BOARDS))
    parser.add_argument("--partition-layout", required=True, choices=("ota-v1-2m", "ota-v1-4m"))
    parser.add_argument("--asset-name", required=True)
    parser.add_argument("--min-updater", required=True)
    parser.add_argument("--notes-de", required=True)
    parser.add_argument("--notes-en", required=True)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    return parser.parse_args()


def require_semver(name, value):
    if not SEMVER.fullmatch(value):
        raise SystemExit(f"{name} must be a semantic version")


def main():
    args = parse_args()
    require_semver("version", args.version)
    require_semver("min-updater", args.min_updater)
    if args.generation < 1 or args.security_version < 0:
        raise SystemExit("generation must be positive and security-version non-negative")
    if not SAFE_ASSET.fullmatch(args.asset_name) or args.image.name != args.asset_name:
        raise SystemExit("asset-name must be a plain .bin filename matching the downloaded image")
    if not args.image.is_file() or not args.private_key.is_file():
        raise SystemExit("image or private key is missing")
    size = args.image.stat().st_size
    if not 65536 <= size <= 4 * 1024 * 1024:
        raise SystemExit("image size is outside the supported OTA range")

    image = args.image.read_bytes()
    layouts={"esp32s3-n16r8":"ota-v1-4m","esp32s3wood-n16r8":"ota-v1-4m","esp32s3wood-n8r8":"ota-v1-2m","esp32s3echobase-n8r8":"ota-v1-2m"}
    if layouts[args.board] != args.partition_layout:
        raise SystemExit("board/layout combination is invalid")
    if len(image) > (4 if args.partition_layout=="ota-v1-4m" else 2)*1024*1024:
        raise SystemExit("image exceeds its target OTA slot")
    if len(image)<256 or image[0]!=0xE9 or struct.unpack_from("<H",image,12)[0]!=9:
        raise SystemExit("not an ESP32-S3 application image")
    if struct.unpack_from("<I",image,32)[0]!=0xABCD5432:
        raise SystemExit("missing ESP-IDF application descriptor")
    image_version=image[48:80].split(b"\0",1)[0].decode("ascii")
    if image_version!=args.version:
        raise SystemExit("manifest version differs from application version")
    if args.board.encode()+b"\0" not in image:
        raise SystemExit("selected board identifier is absent from image")
    if not 0<=args.security_version<=65535 or not 1<=args.generation<=2147483647:
        raise SystemExit("generation/security-version exceeds device parser bounds")
    if any(len(v.encode())>=256 for v in (args.notes_de,args.notes_en)):
        raise SystemExit("release notes exceed device limits")
    key_details = subprocess.run(
        ["openssl", "pkey", "-in", str(args.private_key), "-text", "-noout"],
        check=True, capture_output=True, text=True,
    ).stdout
    if "ASN1 OID: prime256v1" not in key_details and "NIST CURVE: P-256" not in key_details:
        raise SystemExit("signing key must use ECDSA P-256")

    payload = {
        "product": "rp-phone", "channel": args.channel, "generation": args.generation,
        "version": args.version, "security_version": args.security_version,
        "board": args.board, "chip": "esp32s3", "partition_layout": args.partition_layout,
        "size": size, "sha256": hashlib.sha256(args.image.read_bytes()).hexdigest(),
        "url": f"https://github.com/{REPOSITORY}/releases/download/v{args.version}/{args.asset_name}",
        "min_updater": args.min_updater, "notes_de": args.notes_de, "notes_en": args.notes_en,
    }
    payload_raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    with tempfile.NamedTemporaryFile() as payload_file, tempfile.NamedTemporaryFile() as signature_file:
        payload_file.write(payload_raw)
        payload_file.flush()
        subprocess.run(["openssl", "dgst", "-sha256", "-sign", str(args.private_key),
                        "-out", signature_file.name, payload_file.name], check=True)
        signature = pathlib.Path(signature_file.name).read_bytes()
    envelope = {
        "schema": 1, "algorithm": "ECDSA-P256-SHA256", "key_id": KEY_ID,
        "payload": base64.b64encode(payload_raw).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
