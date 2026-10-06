# Signed manifest v1

The device requests `https://raw.githubusercontent.com/chkronenberg/rp-firmware-update/main/channels/stable/manifest.json`. It does not call the GitHub API and stores no GitHub credential.

## Envelope

A publishable manifest contains `schema`, `algorithm`, `key_id`, `payload` and `signature`. The payload is the exact UTF-8 release JSON encoded as standard Base64. The signature is an ASN.1 DER ECDSA P-256 signature over SHA-256 of the decoded payload, also encoded as standard Base64.

Required payload fields are `product`, `channel`, `generation`, `version`, `security_version`, `board`, `chip`, `partition_layout`, `size`, `sha256`, `url`, `min_updater`, `notes_de` and `notes_en`. Unknown fields are rejected in version 1.

The checked-in `state: unconfigured` document intentionally cannot install firmware. A GitHub release is transport only. The device verifies TLS, the envelope signature, compatibility, monotonic generation, image size and image SHA-256.

See [releasing.md](releasing.md) for the controlled release procedure. Private signing keys must never be committed, uploaded as release assets or embedded in firmware.
