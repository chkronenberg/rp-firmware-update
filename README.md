# RP Firmware Update

Public distribution repository for signed RP firmware releases and update manifests.

## Security boundary

- This repository contains release artefacts only, never proprietary source code.
- Devices accept an update only after HTTPS validation, manifest validation, compatibility checks and cryptographic verification.
- No SIP credentials, WLAN credentials, device identifiers, telemetry or signing private keys belong here.
- A GitHub release is transport, not trust. The firmware-embedded public key is the trust anchor.
- Development artefacts are not customer releases.

## Update channels

Firmware 0.4.3 reads `channels/{stable|pilot}/{board}/manifest.json`. Pilot is explicitly selected in the WebGUI. Firmware 0.4.2 reads the legacy `channels/stable/manifest.json`; its published image remains available as the transition baseline. Other board/channel combinations remain unconfigured until a compatible image is accepted and signed. A published manifest does not replace hardware acceptance.

See [docs/manifest-v1.md](docs/manifest-v1.md) for the format. The review-gated publishing procedure is documented in [docs/releasing.md](docs/releasing.md).
