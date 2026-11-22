# 미사용 이미지·검수 자료 보관

정리일: 2026-11-23 (Asia/Seoul)

- 총 215개 파일, 이미지/애니메이션 146개, 131.02 MiB를 이동했습니다. 파일을 삭제하거나 압축하지 않아 전체 디스크 사용량은 줄지 않습니다.
- `assets/`: 현재 코드·테스트의 직접 참조, 동적 플레이어 파일명, JSON의 이미지/원본 참조를 확인한 뒤 미사용 시안·구버전·GIF/APNG 미리보기를 분리했습니다.
- `docs/`: 과거 구현 검수용 캡처를 분리했습니다. README가 보여주는 현재 화면, 최신 v6 검수 화면, 맵·설정·기획 참고 그림은 원래 위치에 남겼습니다.
- `assets/concepts/` 전체, 캐릭터 설정/승인 참고 내보내기, 원본 소스, 미구현 몬스터 디자인, 현재 자산의 프롬프트와 메타데이터, 발표·기획 자료는 보존했습니다. 구버전 지형 원본은 해당 버전과 함께 이 폴더에 보존했습니다.
- 코드·게임 동작·테스트 파일은 변경하지 않았습니다. 옮긴 파일은 원본 바이트 그대로이며 문서의 기존 경로는 새 보관 경로로 갱신했습니다.
- 정리 전부터 수정 중이던 작업 파일은 그대로 유지했습니다.

오래된 PowerPoint 임시 잠금 파일 `~$RelicEscape_1차_발표자료.pptx`(165B)는 PowerPoint가 실행 중이 아니고 파일이 잠겨 있지 않음을 확인한 후 삭제했습니다. 실제 발표 파일은 보존했습니다.

## 찾기와 복원

하위 `assets/`와 `docs/`는 원래 프로젝트 상대 경로 구조입니다. `manifest.json`의 `original_path`는 정리 전 위치, `archived_path`는 보관 위치이며 크기·SHA-256·분류 이유도 기록했습니다. 보관된 JSON은 원래 경로 기준의 상대 참조를 유지하므로 재사용할 때 관련 PNG·JSON·프롬프트를 원래 폴더로 함께 복원합니다. 같은 이름의 새 작업 파일이 있으면 덮어쓰지 말고 비교합니다. 이동한 구버전을 새 기본 자산으로 자동 선택하지 않습니다.

## 파일 목록

| 원래 경로 | 구분 |
| --- | --- |
| `assets/sprites/enemies/stone-crystal-golem-attack-left-v1-preview.gif` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-crystal-golem-death-v1-preview.apng` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-crystal-golem-death-v1-preview.gif` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-crystal-golem-emerge-left-v1-preview.apng` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-crystal-golem-emerge-left-v1-preview.gif` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-crystal-golem-walk-left-v1-preview.apng` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-crystal-golem-walk-left-v1-preview.gif` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-crystal-golem-walk-left-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/enemies/stone-crystal-golem-walk-left-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/enemies/stone-crystal-golem-walk-left-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/enemies/stone-crystal-golem-walk-left-v2-preview.apng` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-crystal-golem-walk-left-v2-preview.gif` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-pillbug-death-blue-v1-preview.apng` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-pillbug-death-blue-v1-preview.gif` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-pillbug-death-v1-preview.apng` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-pillbug-death-v1-preview.gif` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-pillbug-emerge-left-v1-preview.apng` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/enemies/stone-pillbug-emerge-left-v1-preview.gif` | 게임에서 읽지 않는 애니메이션 미리보기 |
| `assets/sprites/player/air-attack-right-draft-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-attack-right-draft-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-attack-right-draft-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-attack-right-draft-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-down-attack-right-draft-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-down-attack-right-draft-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-down-attack-right-draft-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-down-attack-right-draft-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-down-attack-right-draft-v3.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/air-down-attack-right-draft-v3.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-forward-right-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-forward-right-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-right-draft-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-right-draft-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-right-draft-v2.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-right-draft-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-right-draft-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-semicircle-right-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-semicircle-right-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-semicircle-right-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v3.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v3.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v3.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v4.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v4.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-sweep-right-v4.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-windup-right-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/attack-windup-right-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/crawl-right-draft-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/crawl-right-draft-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/hard-landing-right-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/hard-landing-right-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/idle-sword-dust-right-draft-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/idle-sword-dust-right-draft-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/idle-sword-dust-right-draft-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/idle-sword-dust-right-draft-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-investigate-unarmed-right-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-investigate-unarmed-right-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-investigate-unarmed-right-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-investigate-unarmed-right-v2.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-investigate-unarmed-right-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-investigate-unarmed-right-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-shaft-fall.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-shaft-fall.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/opening-shaft-fall.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/wall-slide-right-draft-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/wall-slide-right-draft-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/wall-slide-right-draft-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/wall-slide-right-draft-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/wall-slide-right-draft-v3.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/player/wall-slide-right-draft-v3.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/projectiles/back-crystal-shard-source-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/projectiles/back-crystal-shard-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/projectiles/back-crystal-shard-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/projectiles/back-crystal-shard-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-carriage-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-track-bend-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-track-bend-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-track-blue-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-track-blue-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-track-blue-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-track-blue-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-track-blue-v3.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/rail/relic-track-blue-v3.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/relic/relic-departure-sigil-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/relic/relic-departure-sigil-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/relic/relic-departure-sigil-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/sprites/relic/relic-departure-sigil-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v1-source.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v2-source.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v2.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v3-source.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v3.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v3.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-floor-cover-v3.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-room-shell-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-room-shell-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-room-shell-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-room-shell-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-room-shell-v3.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-room-shell-v3.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-room-shell-v4.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-room-shell-v4.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-shaft-rim-v1-source.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-shaft-rim-v1.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-shaft-rim-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-shaft-rim-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-shaft-rim-v2-source.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-shaft-rim-v2.json` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-shaft-rim-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/moss-combat-shaft-rim-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v3.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v3.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v4.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v4.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v5.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v5.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v6.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-rune-v6.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-backdrop-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-background-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-background-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-escape-wall-cracks-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-rune-fine-cracks-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-rune-interior-detail-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-rune-wall-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-cave-rune-wall-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-fall-shaft-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-fall-shaft-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-fall-shaft-v3.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-sigil-emission-v2.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/opening-sigil-emission-v2.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/ruins-background-wall-tile-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/ruins-background-wall-tile-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/ruins-background-wall-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/ruins-background-wall-v1.prompt.txt` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `assets/terrain/ruins-floor-spike-recess-v1.png` | 현재 코드/테스트 및 간접 JSON 참조에서 사용하지 않는 구버전/시안 |
| `docs/combat-clear-passage-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-clear-passage-opening.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-gate-cleared.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-gate-comparison.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-gate-locked.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-room-after-trigger.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-room-before-trigger.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-room-descent.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-room-exit-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-room-four-enemies.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v2-closed.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v2-half-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v2-landing.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v2-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v2-opening.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v2-states.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-approach.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-approaching.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-closed.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-half-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-landing.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-open-dark.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-open-near.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-opening.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v3-states.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-approach.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-approaching.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-closed.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-half-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-landing.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-open-dark.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-open-near.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v4-states.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v5-approach.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v5-closed.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v5-half-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v5-landing.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v5-open-dark.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v5-open-near.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v5-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-shaft-v5-states.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-stone-wall-aligned.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-stone-wall-dust.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-stone-wall-motion-check.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-stone-wall-motion.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/combat-stone-wall-open.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/crystal-golem-attack-contact-sheet.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/crystal-golem-attack-in-game-v2.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/crystal-golem-attack-in-game.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/crystal-golem-attack-in-game.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/crystal-golem-attack-preview-check.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/crystal-golem-attack-preview-v2-check.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/golem-death-contact-sheet.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/golem-death-in-game.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/golem-emergence-contact-sheet.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/golem-emergence-in-game.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/pillbug-death-blue-in-game.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/pillbug-death-blue-preview.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/pillbug-death-contact-sheet.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/pillbug-death-in-game.gif` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/pillbug-death-in-game.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/pillbug-emergence-contact-sheet.png` | 이전 구현 검수용 캡처/애니메이션 |
| `docs/pillbug-emergence-in-game.png` | 이전 구현 검수용 캡처/애니메이션 |

## 검증 결과

- 정리 전/후 전체 단위 테스트 각각 165개 통과(`python -m unittest discover -s tests -q`).
- 이동 파일215개 및 보존 자산212개 SHA-256 일치. 실행 참조 파일111개 존재 확인.
- README와 docs의 이미지/JSON 링크 대상 존재 확인, `git diff --check` 통과.
