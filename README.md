# RP Firmware Update

Public distribution repository for signed RP firmware releases and update manifests.

## Security boundary

- This repository contains release artefacts only, never proprietary source code.
- Devices accept an update only after HTTPS validation, manifest validation, compatibility checks and cryptographic verification.
- No SIP credentials, WLAN credentials, device identifiers, telemetry or signing private keys belong here.
- A GitHub release is transport, not trust. The firmware-embedded public key is the trust anchor.
- Development artefacts are not customer releases.

## Stable channel

The device reads `channels/stable/manifest.json`. Until the production signing ceremony and hardware acceptance are complete, the manifest deliberately publishes no installable image.

See [docs/manifest-v1.md](docs/manifest-v1.md) for the format. The review-gated publishing procedure is documented in [docs/releasing.md](docs/releasing.md).
