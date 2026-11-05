# Project Instructions

## Language

- Use English for project filenames and directory names by default. Preserve the user-selected Korean presentation folders and filenames described below.
- Write planning document contents in Korean. English filenames do not imply English document contents.
- Keep README explanations in Korean as well.
- Use English for source code identifiers. Follow the user's instructions and existing conventions for other file contents; do not infer that all contents must be English.
- Commit messages are exempt from the filename rule and may be written in Korean.
- Conversation with the user may remain in Korean.
- Preserve existing design decisions when translating or renaming files, and update references to renamed files.

## Character asset source

- Use `assets/concepts/player-sd-idle-right-source-v3.png` as the working source for in-game character artwork and animation variants.
- Develop movement, jump, attack and other character poses by modifying this source design.
- The 64x64 PNGs in `assets/sprites/player/` are previous reference exports, not the required source or a fixed production resolution.
- Choose production frame dimensions during implementation. Keep the approved LD images as concept references.

## Presentation and planning deliverables

- The user designated `발표&기획서/` as the location for future presentation and planning PPT files. Create and edit PPT deliverables there, using an appropriate presentation subfolder.
- Current first-presentation files are in `발표&기획서/1차 발표 및 기획/`:
  - `RelicEscape_1차_발표자료.pptx`: presentation deck.
  - `RelicEscape_1차_기획안.pptx`: detailed planning deck.
  - `Presentation_Script_4Week.md`: current narration script.
- Preserve these user-selected folder and file names, including Korean characters. They are an explicit exception to the default English naming convention.
- Update the existing relevant PPT in this location unless the user asks for a separate version. Do not recreate the former `deliverables/2026-11-03/` output location.
- Update documentation links if the user moves or renames deliverables.

<!-- memoc:managed:start -->
## Session Start
- [ ] Read `.memoc/session-summary.md`
- [ ] `.pending` exists? Review changed files, update memory if needed, then delete it.
- [ ] If `memoc` is not found, use the project-local wrapper for the rest of the session: Windows `.\.memoc\bin\memoc.cmd <command>`; sh `.memoc/bin/memoc <command>`

## Before Opening More Files
- [ ] Search memory first: `memoc search "<query>" --limit 5`, or wrapper fallback above if PATH fails
- [ ] Open on demand: `02` status, `04` resume, `06` rules, `llms.txt` map
- [ ] If memory search is not enough, search project files with `memoc grep "<query>" --limit 5` (or wrapper fallback)
- [ ] If asked to refresh/update memoc project memory, run `memoc update` first; this refreshes managed sections, wiki links, and Obsidian tags.
- [ ] For durable source material use `memoc ingest <path-or-url>`; for durable analysis/query results use `memoc note "<title>"`; after wiki edits run `memoc lint-wiki`.
- [ ] In shared repos, record meaningful work with `memoc work "<title>"`; actor defaults to `MEMOC_ACTOR`, local actor, git user, git email, or OS user.
- [ ] Keep output small: `summary`, `search --limit`, `grep --limit`, `--snippets`

## Before Finishing _(update only applicable files; skip Q&A / throwaway exploration)_
- [ ] Code/config/deps changed? Update `02` + `session-summary.md`
- [ ] Decision made? Update `03-decisions.md` + `02`
- [ ] Work incomplete or risky? Update `04-handoff.md`
- [ ] Rule/preference set? Update `06-project-rules.md`
- [ ] Wiki/project-memory work? Read `skills/project-memory-maintainer/SKILL.md`
- [ ] User asked to update memoc/project memory? Run `memoc update`, then update the smallest relevant agent-owned memory files.
- [ ] Shared repo work? Prefer `memoc work "<title>" --from-git` over appending shared files; run `memoc activity --write` only when regenerating indexes.
- [ ] Keep `session-summary.md` as a replace-only snapshot under 800B; move completed work to actor worklogs and resume risks to `04-handoff.md`. If it grew, run `memoc trim-summary`.
<!-- memoc:managed:end -->
