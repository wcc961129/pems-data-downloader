# Community governance implementation report

## Objective

The repository uses a maintainer-reviewed contribution model:

1. anyone may open a structured Issue;
2. external contributors fork the public repository and open a Pull Request;
3. automated tests validate the proposed change;
4. the repository owner reviews and decides whether to merge;
5. direct repository access is reserved for trusted maintainers.

Contributors do not need collaborator access to propose code.

## Repository controls

The intended default-branch rules are:

- require a Pull Request before updating `main`;
- require the CI workflow to pass;
- require review conversations to be resolved;
- block force pushes and branch deletion;
- retain the repository owner as the final merger.

With a single maintainer, the rule does not require a numeric approval that
would prevent the owner from merging their own maintenance Pull Requests.
Before granting another person write access, enable one required approval and
require Code Owner review.

## Governance files

- `.github/CODEOWNERS` requests review from `@wcc961129`.
- `.github/PULL_REQUEST_TEMPLATE.md` collects scope, validation, data safety,
  documentation, and compatibility evidence.
- `.github/ISSUE_TEMPLATE/` separates reproducible bugs from feature requests.
- `CONTRIBUTING.md` defines the fork, branch, test, and review workflow.
- `CODE_OF_CONDUCT.md` defines participation standards.
- `SUPPORT.md` routes PeMS account, project, model, and security questions.
- `SECURITY.md` directs vulnerabilities to private reporting.

## Automation and supply-chain posture

CI runs for pushes and Pull Requests across supported Python and operating
system combinations. Fork workflows from first-time contributors require
maintainer approval, and the default workflow token remains read-only.

Dependabot monitors the `uv` and GitHub Actions ecosystems weekly. Dependency
alerts, security updates, private vulnerability reporting, secret protection,
and push protection should remain enabled.

## Growth path

Keep external contributors on the fork-and-Pull-Request path. Grant direct
access only after repeated, trusted contributions.

If several maintainers need differentiated triage, write, release, and
administrative roles, transfer the project to a GitHub organization and manage
access through teams. At that point:

- require at least one approval;
- require Code Owner review;
- dismiss stale approvals after new commits;
- document release authority and maintainer succession.

## Documentation boundary

Version-controlled files under `docs/` remain the canonical documentation.
Keep the GitHub Wiki disabled unless the project adopts a specific,
maintained use for it. Use Discussions for open-ended support and research
questions only when Issue traffic shows a clear need.
