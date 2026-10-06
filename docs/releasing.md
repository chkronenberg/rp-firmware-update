# Signierte Firmware veröffentlichen

## Einmalig

- P-256-Schlüssel ausschliesslich als Environment-Secret `OTA_SIGNING_KEY_PEM` in `stable-release`.
- Environment: erforderlicher Reviewer, kein Admin-Bypass, nur `main`.
- Branchschutz: Pull Request und erfolgreicher `validate`-Check, Force-Push und Löschen sperren.
- GitHub Actions darf optional Pull Requests erstellen. Ohne diese Berechtigung liefert der Workflow einen manuellen PR-Link; der signierte Branch bleibt erhalten.

## Pro Release

1. Private Firmwareversion in CMakeLists.txt erhöhen; vollständige CI und WebGUI-Prüfung auf dem freigegebenen Commit ausführen.
2. Exaktes Boardartefakt sichern. Nur die Anwendung `.bin` veröffentlichen, niemals Provisionierungsdaten, Quellcode, private Schlüssel oder vollständige Factory-Pakete.
3. Commit, CI-Run, Toolchain, sdkconfig, Lockdatei, Prüfsumme und Testprotokoll dauerhaft im privaten Nachweispaket sichern. Eine vollständige SBOM/CVE-Bewertung ist vor Kundenfreigabe erforderlich.
4. GitHub Release `vVERSION` erstellen und Anwendungsimage anhängen. Pilot als Pre-release kennzeichnen.
5. Workflow `Prepare signed firmware release` auf `main` starten. Kanal `pilot`, exaktes Board/Layout und Asset auswählen. Mindest-Updater und DE/EN-Notizen angeben.
6. Generation höher als alle auf diesem Board bereits veröffentlichten Pilot-/Stable-Generationen wählen. Security-Version nicht routinemässig erhöhen und nie reduzieren. Für das erste Paket: Generation 1, Security-Version 0.
7. Environment freigeben. Workflow prüft Imageversion, Chip, enthaltene Boardkennung, Slotgrösse und Layout; dann signiert und verifiziert er das Manifest.
8. Manifest-PR prüfen: Imageherkunft, Version, SHA-256, Grösse, Board, Layout, Kanal, Generation und Security-Version. CI muss grün sein.
9. Pilot-PR mergen. Auf einem Pilotgerät ausdrücklich Pilotkanal wählen und über die WebGUI installieren. Authentifizierte NTS-Zeit und aufgelegter Hörer sind Voraussetzung.
10. Hardwaretestprotokoll abschliessen. Dasselbe unveränderte Image für Stable mit einer höheren Generation signieren und nach Review mergen.

## Migration und Kompatibilität

Firmware bis 0.4.2 liest `channels/stable/manifest.json`. Firmware ab 0.4.3 liest `channels/{stable|pilot}/{board}/manifest.json`.
Der alte Pfad bleibt unverändert als Vertrauens-/Kompatibilitätsbrücke bestehen. Um alte Geräte auf 0.4.3 zu bringen, muss ein zusätzliches signiertes Stable-Manifest für deren Board am alten Pfad veröffentlicht werden. Ein alter Pfad kann nur ein Board bedienen. Kein automatischer unsignierter Fallback.

## Hardwareabnahme

Erfolgreiches Update und Erhalt von WLAN/SIP/Admin/Identität/Sprache/Anrufliste; Downloadabbruch; Stromverlust während Schreiben und Testboot; absichtlich fehlgeschlagener Boot; Hörerwechsel; Anruf während Update; Wiederherstellung über Fertigungszugang. Offline PBX und fehlendes Internet nach Boot dürfen allein keinen Rollback auslösen.

## Stop und Schlüsselvorfall

Releaseangebote stoppen, ohne laufende Geräte remote zurückzusetzen. Bereits installierte Images benötigen einen signierten Korrekturrelease mit höherer Generation. Schlüsselrotation zuerst mit überlappenden Vertrauensankern implementieren und testen. Bei kompromittiertem Schlüssel ohne unabhängigen Anker kann physischer Service erforderlich sein.

Status: Softwareprozess implementiert. Branchschutz, echte Hardwareabnahme, geschützter Zeitbootstrap, Secure Boot/Flash Encryption, Schlüsselrotation und vollständige SBOM/CVE-Abnahme sind separat nachzuweisen.

### Übergangsmanifest für bestehende Geräte

Bei der Stable-Freigabe von 0.4.3 für `esp32s3wood-n16r8` im Workflow `legacy_bridge=true` wählen. Der Workflow schreibt denselben signierten Inhalt zusätzlich nach `channels/stable/manifest.json` und nimmt beide Pfade in den Freigabe-PR auf. Pilot erlaubt diesen Schalter nicht. `min_updater=0.4.1` beibehalten, sofern der Hardwaretest den Übergang von 0.4.2 bestätigt. Andere Boards benötigen einen Serviceflash für den ersten Wechsel auf die boardgebundenen Pfade. Bis zur geprüften Freigabe bleiben die bestehenden 0.4.2-Manifeste unverändert.
