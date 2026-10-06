# Publishing a stable firmware update

The stable channel changes only through a reviewed pull request. The workflow never builds proprietary firmware and cannot read the private source repository.

## One-time setup

1. Store the P-256 private key as the Actions secret `OTA_SIGNING_KEY_PEM`.
2. Protect the `stable-release` environment with required reviewers.
3. Keep Actions permissions restricted to the workflow-declared scope.
4. Provision the matching public key and key ID `prod-2026-01` in customer firmware.

## Per release

1. Build and test the firmware at an immutable commit in the private repository.
2. Perform hardware acceptance for the exact board and partition layout.
3. Create release `vVERSION` here and upload the application `.bin` file.
4. Run **Prepare stable firmware release** manually with the approved metadata.
5. Review the generated pull request: version, generation, security version, board, layout, asset URL, size and SHA-256.
6. Test installation and rollback on pilot devices, then merge the manifest pull request.

The workflow downloads the existing release asset, computes its digest and size, signs the canonical payload, verifies the signature with the checked-in public key and opens a pull request. It does not publish directly to `main`.

If key compromise is suspected, publish nothing further. Stop the release process and rotate the trust anchor through the existing trusted key where possible.
