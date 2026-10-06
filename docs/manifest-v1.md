# Signed manifest v1

Firmware 0.4.3 requests the static, board-specific channel URL:

`https://raw.githubusercontent.com/chkronenberg/rp-firmware-update/main/channels/{stable|pilot}/{board}/manifest.json`

Firmware 0.4.2 uses the legacy `channels/stable/manifest.json`. The transition procedure is documented in releasing.md.

It does not call the GitHub API and stores no GitHub credential.

## Envelope

A publishable manifest is a JSON object containing `schema`, `algorithm`, `key_id`, `payload` and `signature`. The payload is the exact UTF-8 release JSON encoded as standard Base64. The signature is an ASN.1 DER ECDSA P-256 signature over SHA-256 of the decoded payload, also encoded as standard Base64.

Required payload fields:

- `product`: `rp-phone`
- `channel`: `stable` or `pilot`
- `generation`: monotonically increasing positive integer
- `version`: semantic firmware version
- `security_version`: separately governed anti-downgrade value
- `board`: exact hardware profile
- `chip`: `esp32s3`
- `partition_layout`: compatible partition identifier
- `size`: exact application-image byte count
- `sha256`: lowercase SHA-256 of the application image
- `url`: immutable HTTPS GitHub release URL in this repository
- `min_updater`: oldest updater version able to process the release
- `notes_de` and `notes_en`: short display text

Unknown fields are rejected in version 1. A release URL is transport only. The device verifies TLS, the envelope signature, compatibility, monotonic generation, image size and image SHA-256 before selecting the inactive OTA partition.

## Unconfigured state

The checked-in `state: unconfigured` document intentionally cannot install firmware. It is used for board/channel combinations that do not yet have an approved signed image.

## Release procedure

1. Build and test the private source repository at an immutable commit.
2. Record the approved hardware profile and partition layout.
3. Perform hardware acceptance for the exact image.
4. Upload the immutable image to a GitHub Release in this repository.
5. Run the manually dispatched, environment-protected publish workflow.
6. Independently review the generated manifest pull request and download URL.
7. Merge the reviewed pilot-channel manifest and test installation and rollback on pilot devices.
8. Publish and merge a separate stable-channel manifest with a higher generation only after hardware acceptance.

See [releasing.md](releasing.md) for the operational procedure. Private signing keys must never be committed, uploaded as release assets or embedded in firmware.
