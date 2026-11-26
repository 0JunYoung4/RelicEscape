# Project Instructions

## Language

- Use English for project filenames and directory names by default. Preserve the user-selected Korean presentation folders and filenames described below.
- Write planning document contents in Korean. English filenames do not imply English document contents.
- Keep README explanations in Korean as well.
- Use English for source code identifiers. Follow the user's instructions and existing conventions for other file contents; do not infer that all contents must be English.
- Commit messages are exempt from the filename rule and may be written in Korean.
- Conversation with the user may remain in Korean.
- Preserve existing design decisions when translating or renaming files, and update references to renamed files.

## Git

- Commit repository changes at the end of each completed task. Include only changes made for that task.
- For map work, commit each completed work unit with a Korean commit message. Push only when the user explicitly requests it.

## Character asset source

- Use `assets/concepts/player-sd-idle-right-source-v3.png` as the working source for in-game character artwork and animation variants.
- Develop movement, jump, attack and other character poses by modifying this source design.
- The 64x64 PNGs in `assets/sprites/player/` are previous reference exports, not the required source or a fixed production resolution.
- Choose production frame dimensions during implementation. Keep the approved LD images as concept references.

## Image generation references

- Use Hollow Knight terrain and lighting as the default visual reference for cave and map art. Apply the silhouette, layering, and depth principles to RelicEscape's original designs.

- For project image generation, consult `docs/reference-production-guide.md` and filter the reference catalog at `docs/references/hollow-knight-silksong/index.html` or with `query_references.py` for the relevant room, material, lighting, or silhouette. Open selected images before writing the prompt.
- Use the selected references for composition, silhouette, materials, depth, and lighting. Build the artwork around RelicEscape's own designs and approved asset sources. Record the reference IDs and the visual decisions they informed in the asset's prompt file or metadata.

## Map art and rendering

- Lead level design and environment art from the user's room purpose, mood, core mechanics, and progression conditions. Plan the room shape, routes, platforms, passages, landmarks, layer placement, and asset specifications. Make routine placement and art decisions autonomously. When multiple directions fit, recommend one and build a reviewable draft. See [the map design workflow](.memoc/06-project-rules.md#맵-레벨-디자인과-환경-아트).
- Finish and review one room at a time. Verify depth, visual cohesion, and gameplay readability in the running game and iterate. If game views are inaccessible, request the specific camera views and gameplay states needed for review.
- Reuse suitable sprites from the [23-piece map decoration set](assets/terrain/moss-grotto-floor-decor/README.md) when building or revising map areas. Match new map art to its crisp dark contours, deep teal shadows, rounded shapes, and restrained moss-green highlights. Vary cluster size, spacing, and silhouette across each area.
- Follow the [layer production and rendering rules](docs/reference-production-guide.md#맵-미술-제작과-렌더링-기준). Create and preview the far background, floor, ceiling, walls when applicable, world decorations, and near foreground as independently adjustable assets. Render the far background behind the terrain and actors, and near foreground silhouettes in front of them at the edges.

맵 미술, 배경 합성, 조명, 전경이나 카메라를 변경할 때 프로젝트 루트의 `MAP_VISUAL_GUIDE.md`에서 해당 작업에 필요한 기준을 참고한다. 관련 없는 코드 수정에 맵 재설계를 추가하지 않는다.

- 맵 1의 바닥, 발판, 식생, 석조 유적과 조명은 첫 전투방을 공통 미술 기준으로 삼는다. 구간별 표현은 [맵 1 공통 미술과 하단 동선 시안](docs/map1-art-direction.md)을 참고한다.
- 목표는 거리감, 공기감, 일관된 소재와 플레이 가독성이다. 모든 맵의 색, 밝기, 안개와 전경을 동일하게 만들지 않는다.
- 거리 설계를 핵심으로 삼고 물체의 깊이를 먼저 정한다. 정지 화면의 대비, 색, 윤곽과 겹침이 움직일 때의 시차와 같은 거리를 표현하도록 맞춘다.
- 기존 렌더러와 에셋을 확인하고, 거리별 대비와 색 보정, 층 사이 공기감, 공통 환경광과 겹침부터 개선한다.
- 공기색 혼합 시 원래 알파를 유지한다. 안개와 빛은 작용할 레이어를 정해 합성한다.
- 시차는 카메라 이동량에 적용한다. 원경 0.25, 중경 0.60, 플레이 영역 1.00, 독립 전경 1.10을 시험용 출발값으로 삼고 상세 가이드의 축, 기준점과 줌 정의에 맞춰 조정한다. 고정 카메라 구간은 정지 화면의 깊이 표현을 우선한다.
- 붙어 있는 발판, 레일, 고정부와 지지대는 같은 변환을 사용한다.
- 미술 개선에서는 실제 충돌, 점프 거리, 유물 도착점과 공격 판정을 기준으로 그림을 맞춘다. 게임플레이 변경은 해당 요청 범위에서 수행한다.
- 사용자가 장식 하나하나를 지정하지 않아도 맵의 목적과 기존 테마에 맞춰 세부 배치를 구체화한다.
- 대표 화면과 관련 동작을 확인한 뒤 공통 처리와 맵별 설정으로 정리하고, 요청된 범위까지 적용한다.
- 결과에는 변경 이유와 실제 확인한 내용을 남긴다. 확인하지 않은 성능이나 플레이 결과를 통과했다고 보고하지 않는다.

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
