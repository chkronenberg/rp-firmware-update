# Signed manifest v1

The device requests the static stable-channel URL:

`https://raw.githubusercontent.com/chkronenberg/rp-firmware-update/main/channels/stable/manifest.json`

It does not call the GitHub API and stores no GitHub credential.

## Envelope

A publishable manifest is a JSON object containing `schema`, `algorithm`, `key_id`, `payload` and `signature`. The payload is the exact UTF-8 release JSON encoded as standard Base64. The signature is an ASN.1 DER ECDSA P-256 signature over SHA-256 of the decoded payload, also encoded as standard Base64.

Required payload fields:

- `product`: `rp-phone`
- `channel`: `stable` or `beta`
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

The checked-in `state: unconfigured` document intentionally cannot install firmware. It exists so development devices receive a clear “release channel not configured” result until an offline production key and the first approved release exist.

## Release procedure

1. Build and test the private source repository at an immutable commit.
2. Record the approved hardware profile and partition layout.
3. Hash the application image.
4. Prepare and independently review the payload.
5. Sign the payload outside normal CI with the production private key.
6. Upload the immutable image to a GitHub Release in this repository.
7. Validate the signature and download URL from a clean environment.
8. Replace the channel manifest only after approval.
9. Roll out to pilot devices before broader release.

Private signing keys must never be committed, uploaded as release assets or embedded in firmware.
