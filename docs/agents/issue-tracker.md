# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues on **`ericdahl-dev/friture`**. Use the `gh` CLI for all operations.

This clone also has `upstream` (`tlecomte/friture`). When working on upstream bugs or contributing back, read upstream issues with `--repo tlecomte/friture`; create and triage work for this fork with `--repo ericdahl-dev/friture` unless the user says otherwise.

## Conventions

- **Create an issue**: `gh issue create --repo ericdahl-dev/friture --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --repo ericdahl-dev/friture --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --repo ericdahl-dev/friture --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --repo ericdahl-dev/friture --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --repo ericdahl-dev/friture --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --repo ericdahl-dev/friture --comment "..."`

## When a skill says "publish to the issue tracker"

Create a GitHub issue on `ericdahl-dev/friture`.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --repo ericdahl-dev/friture --comments`.
