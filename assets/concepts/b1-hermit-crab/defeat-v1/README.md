# 바위 소라게 격파 · 점멸 전후 자세

B1의 기존 직립 원본에서 내장 ImageGen으로 두 자세를 따로 만들었다. 기존 소라게의 나선 암판, 청회색 석재, 황록 이끼와 큰 집게를 기준으로 삼았다. [정체성 원본](../assembled-upright-v6.png)

- [점멸 직전](before-flash.png)은 한쪽 집게로 낮아진 몸을 버틴다. 옅은 호박색 안광이 두 점으로 남아 있다.
- [점멸 직후](after-flash.png)는 다리와 집게가 풀려 바닥에 내려앉는다. 등딱지 한쪽이 조금 깨지고 눈과 나선 문양은 어둡다.
- 두 원본은 1536 × 1024 투명 RGBA다. 알파 8 초과 범위는 직전 (31, 145, 1490, 969), 직후 (10, 195, 1527, 955)다. 미리보기에서 같은 배율을 사용하고 두 자세의 발밑을 같은 바닥에 맞춘다.

## 4초 애니메이션 미리보기

실제 B1의 배경·지형·전경을 캡처해 자세, 떨림, 몸에서 뻗는 빛줄기와 섬광을 겹친 [점멸 전후 WebP](defeat-preview.webp)다. 막타 멈춤 0.15초와 폭발 전 정적 0.15초를 포함한다. 화면이 가장 밝을 때 자세를 바꾸고 빛이 걷히면 쓰러진 자세를 잠시 유지한다.

`.\.venv\Scripts\python.exe -m tools.render_b1_defeat_preview`로 다시 렌더링한다. [격파 연출 전체 계획](../../../../docs/b1-hermit-crab-combat-design.md#격파-연출과-다리-장벽-해제-계획)

## 섬광 독립 레이어

- [투명 빛줄기 WebP](defeat-flash.webp)는 960 × 540 RGBA이며 합성본과 같은 화면 좌표를 쓴다. 격파 타임라인의 0.55초부터 등딱지와 몸의 틈에서 0.12초 간격으로 한 줄기씩 나온다. 여덟 줄기가 화면의 상하좌우 끝에 닿는다. 전체 재생 시간은 1.34초다.
- 1.60–1.66초에는 여덟 줄기가 한꺼번에 굵어진다. 보스방 미리보기에서 그 뒤로 백색 정점이 한 번 오고, 가장 밝을 때 쓰러진 자세로 전환한다. [보스방 합성 미리보기](defeat-preview.webp)

## 빛줄기 원본과 조명

- [빛줄기 원본 PNG](defeat-beam-source.png)는 내장 ImageGen으로 제작한 2172 × 724 RGBA 이미지다. HK-AY-05에서 광원 입구는 좁고 멀어질수록 광선이 넓어지는 관계를 참고했다. [참고 화면](../../../../docs/references/hollow-knight-silksong/images/hk-ay-05.png)
- 점멸 전 소라게 이미지의 암석 접합부 여덟 곳을 기준점으로 잡았다. 각 프레임에서 보스의 떨림을 같이 따라가며, 원본 빛줄기를 방향에 맞춰 회전하고 화면 끝 바깥까지 늘린다. 섬광 직전에는 폭이 동시에 커진다.
- 빛줄기와 발광 시작점에서 별도 조명 마스크를 만든다. 보스 석재, 배경과 전경의 반사 강도를 달리하고, 바닥을 만나는 줄기의 접점에는 가로로 번지는 반사광을 더한다. 원래 레이어의 투명도와 석재 디테일을 유지한 채 조명이 올라왔다 가라앉는다.

### 빛줄기 생성 프롬프트

Create exactly one isolated transparent 2D game VFX sprite: a long, straight horizontal shaft of blue-white light leaking out of a narrow stone crack, but depict ONLY the light itself. The light points from left to right and its axis remains perfectly level at the vertical center. A small tight white-hot entry at the left widens gradually into a broad soft-edged ribbon with a pearly white center, cool icy cyan intermediate band, and feathered muted cobalt-blue outer spill. A few subtle longitudinal filaments within the beam convey luminous motion and avoid a flat solid triangle. Keep the beam bright along almost its entire length, with only a brief fade at the far-right end. The actual luminous shape should be about six times as long as its widest point. Maintain a clean alpha edge. This is an original directionless VFX texture to rotate and stretch in a hand-painted dark fantasy 2D game, so its shape should read at small game resolution and the background must be genuinely transparent. Wide landscape canvas, a little clean margin on every side. No rocks, no surface, no cast shadow, no text, no stars, no sparks, no dots detached from the light, no circle, no lens flare, no glow blob, no characters, no second beam, no panel, no sample composition, no visible black or colored backdrop.

## 점멸 직전 생성 프롬프트

Pose edit of the attached original RelicEscape stone hermit crab. Make one transparent 2D game sprite of this EXACT creature a fraction of a second before its defeat flash, during its final faltering effort. Match the reference's fixed almost straight-on platformer camera, relative size, compact faceted dark slate-blue rock shell, original spiral stone plate near the top left, sparse yellow-olive moss across the same rock seams, same two chunky crescent rock pincers, stone face and segmented legs, and restrained hand-painted pixel-raster game-art edge style. Change ONLY its pose and expression: lower the body substantially, shift the heavy shell down and a little toward the viewer's left. The big pincer at the viewer's left plants firmly on the common floor line and supports its weight, claw half-open and visibly tense. The other pincer sits slightly higher but droops heavily toward the floor. Bent, trembling-looking legs still barely support its lowered body. Under the familiar shadowed brow the SAME two square amber eyes are very dim and small, still faintly alive. The face droops low, with a small gap below the belly. One recognizable heavy crab just before collapse, not a standing or fighting pose. Preserve the shell and claw mass and identity, keep the face readable. No energy trails, lighting burst, particles, loose debris, animation streaks, flames, shadows on background, props, lines, words or duplicate poses. One complete transparent png game sprite, centered with comfortable 8% clear margins, full silhouette including claws, feet and crown always in view. Wide landscape 3:2. Keep alpha truly transparent.

## 점멸 직후 생성 프롬프트

Make the AFTER-FLASH defeat pose by editing this immediately-before-flash RelicEscape stone hermit crab sprite. It must be recognizably the same individual in two successive shots. Match the reference's exact nearly frontal side-scroller angle, pixel-raster paint treatment, blue-gray faceted stone, charcoal outlines, original carved spiral stone plate, sparse yellow-olive moss, size and layout of every major shell plate, claws and face. Same centered landscape 3:2 framing, same apparent shoulder and shell width, use the same ground baseline as input. Main change: the crab has completely collapsed. The heavy rock shell settles lower and tilts a little toward the viewer's left, the stone jaw and belly slump nearly to the floor and all short legs buckle outward or fold flat beneath the weight. Both huge crescent pincers are slack, rolled down and resting low on that same ground line, with the claw on the viewer's left loosely open and stretched away, rather than propping the body up. The face is still just visible under the brow. BOTH EYES ARE ENTIRELY EXTINGUISHED: only two barely discernible matte charcoal sockets in deep shade, with ZERO luminous pixels, zero iris dots, no amber or colored highlights, and no eye reflections or tears. Keep the spiral engraved into the rock with absolutely no light. Add one modest chipped-out corner to an upper-right shell plate with a couple of short cracks, preserving the bulk of the shell and its familiar profile. Muted, inert, lifeless, weight pressed into the ground. It is a whole unanimated stone creature that has gone cold, no gore. NO lighting aura, particles, smoke, dust, detached debris, pooled shadow, wisps, motion lines, props, text, floor or background. Exactly one complete isolated transparent PNG sprite on a genuinely clear alpha channel, all limbs visible.
