# Security Policy

## Sensitive local files

The PeMS browser state contains authenticated cookies. Keep `.pems/storage-state.json` private, do not attach it to issues, and revoke the PeMS session if it is exposed.

Credentials are accepted only through the interactive login page or temporary `PEMS_USERNAME` and `PEMS_PASSWORD` environment variables. They must not be placed in source code or committed configuration.

## Reporting a vulnerability

Report vulnerabilities through the repository's
[private vulnerability reporting form](https://github.com/wcc961129/pems-data-downloader/security/advisories/new).
Do not open a public issue for credential disclosure, cookie leakage,
authentication bypass, or arbitrary file-write findings.

Supported security fixes target the latest released version.
