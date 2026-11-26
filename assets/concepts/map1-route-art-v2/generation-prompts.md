# 맵 1 하단 동선 시안 생성 기록

내장 ImageGen으로 네 장을 만들었다. 각 장면의 첫 입력은 해당 구간의 배치 기준이고 두 번째 입력은 최신 전투방 화면 `docs/combat-room-lighting-gameplay.png`다. [공통 미술 기준](../../../docs/map1-art-direction.md)

| 참고 ID | 반영한 판단 |
| --- | --- |
| [HK-GP07](../../../docs/references/hollow-knight-greenpath/images/gp07.png) | 가까운 비석과 먼 석재의 대비 차이, 틈빛이 잎과 석재 윗면에 닿는 배치 |
| [HK-CT-05](../../../docs/references/hollow-knight-silksong/images/hk-ct-05.png) | 하강과 협곡에서 서로 다른 높이의 착지면을 구별하는 명암 |
| [SS-MG-02](../../../docs/references/hollow-knight-silksong/images/ss-mg-02.png) | 모서리에 모이는 둥근 이끼와 중앙 여백 |
| [SS-CK-06](../../../docs/references/hollow-knight-silksong/images/ss-ck-06.png) | 가까운 장치와 멀리 겹쳐 보이는 구조물의 대비 차이 |
| [SS-MF-04](../../../docs/references/hollow-knight-silksong/images/ss-mf-04.png) | 어두운 휴식 공간에서 작은 국소광으로 시선을 모으는 배치 |

아래 공통 프롬프트에 장면별 프롬프트를 이어서 입력했다.

## 공통 프롬프트

```text
Use case: environment concept compositing for RelicEscape, an original 2D side-view adventure game. Input 1 is the layout to preserve; input 2 is the current approved RelicEscape combat room and the ONLY art palette/material/lighting identity source. Never borrow stage composition from input 2. Match the game's modest asset scale and flat orthographic cameras, crisp near-black rock cores, irregular rounded blue gray rock, flat readable safe top lips with small jade bead moss and hooked plants, atmospheric desaturated navy-teal recesses. Shape the moss into uneven islands with clean gaps rather than a continuous bright luminous stripe. Show the same old civilization through RelicEscape's shallow hexagonal recessed stone carvings and weathered collapsed masonry. Use sparse related far silhouettes in low-contrast air color, an optional middle-depth ruin or its rubble occluded by aligned terrain, plus dark leaves framing only the edges. One legible reason for each ambient light. Soft daylight touches exposed tops and leaves at the contact, shadow stays in the stone mass. No bright light blobs in empty foreground, neon decoration, magical beams with imaginary emitters, text, labels, map symbols, UI, borders, character additions or new gameplay geometry. This is a gameplay art study, not a texture atlas.
```

## 하강과 A파트

[descent-lift.png](descent-lift.png) · 배치 기준 `docs/map1-lower-route-a-v3-open.png` · 생성 원본 `exec-74bb0808-197b-4ae3-b71f-43d4de7b4164.png`

```text
Asset: wide 3:1 A-room full visual proposal with the combat shaft landing, lower lane and upper exit. Keep exact layout ratio and entire crop of input 1. The ONLY actual descent aperture is the opening in the upper-right at x≈90%, and the high right entry bank sits under it. Leave its safe emerald stone crown and the two staggered right steps at the same coordinates. Preserve left upper continuous shelf and existing lower horizontal route. Lock the distinctive ㄷ-shaped cyan rail sections, single curve rising on its right, and starting lower carriage, left-upper finish, plain floor button, right return mechanism and existing carved support; use the same exact rail locations and no added tracks. Cyan function signals stay crisp and only at rail and devices. This art revision replaces the broad saturated cyan wash with deeper blue-green air and a new softly visible vertical oblique mint light coming from that real upper-right aperture, lighting the right edge of the tall beveled entry stele and the nearest upper stone and leaf tips. A much dimmer diffuse trace in the far depth across the lift, no second dramatic beam. Under the upper-left shelf retain dark roots and a quiet air gap for seeing the two floors clearly. Repeat compact far steles and ruin arches as soft intermittent background shapes behind the support, distinctly lower contrast than the carved middle-depth actual support. Preserve right-to-left traversal. Layer studies HK-CT-05 (readable landing and vertical depth), SS-MG-02 (nonuniform moss framing), HK-GP07 (selective stone/leaf edge light).
```

## A–B 연결 절벽

[ridge-connection.png](ridge-connection.png) · 배치 기준 `docs/map1-lower-route-ab-connection.png` · 생성 원본 `exec-2a793346-054b-487c-bdf2-dc92613cebda.png`

```text
Asset: 16:9 single camera image of A–B connecting ledge. Preserve camera, character identity, sprite scale, absolutely continuous horizontal walk line at ~63% frame height, dark grounded cliff silhouette beneath, and B rail dock ending partly at the far left exactly as in input 1. Preserve the large tilted RelicEscape stele and adjacent hexagonal break at mid-background, with the original small upright marker on the far right, but give their faces colder muted slate and their top moss irregular calm jade. Place only two distant corresponding narrow partly buried monuments behind the main pair and a broken aqueduct silhouette running through blue-green mist at the farthest depth. Delicate atmospheric light coming from one opening up and to the right strokes the tall stone crown and falls across a short stretch on the middle of the ledge, allowing texture and low plants to connect to the full scene. Moss on deck only in short groups; plant fern beds behind the playable line with clear frontal black rock edge and no break or step in the continuous floor; use edge roots nearest, muted. The left dock is the sole high-chroma cyan. Show a feeling of depth under the continuous stone and keep same stone form at left and right so the ledge looks continuous; the actual exit left remains entirely readable. Internal depth references HK-CT-05 for low-contrast distant arches and HK-GP07 for silhouette echoes, no shapes sourced from those images.
```

## B파트 레일 협곡

[rail-gorge.png](rail-gorge.png) · 배치 기준 `tools/preview_lower_route_b.py`의 현행 SDL 전체 구도 (`.cache/map1-route-concept/b-runtime-overview.png`) · 생성 원본 `exec-18d4dd0d-bdf8-4c3e-96b1-51db3d21f33f.png`

```text
ing over the current combat-room's cool blue-gray slabs and near-black rock cores, broken round toe stones and sparse jade bead moss at intersections; make the wall-jump surfaces readable and visually distinct from dry spine silhouettes. Suggest small mechanical brackets on existing rail joints at supported points only and never across open flight gaps. Retain cyan wire light as the strongest hue, incoming ambient mint considerably fainter. Use one clearly sourced pale slit of light at the upper right and a softer diagonal reflected light toward the left landing, not a flat bright cyan wash. Use gray-teal shadow and quiet air through the open center, far background remains a continuation of the ancient site's original narrow hex steles and fractured aqueduct motifs, largely swallowed by haze behind near obstacles. Foreground is thin upper roots and sparse lower edges away from bottom rail. Functional path and terrain are photographed in a very legible game-engine orthographic frame. Research SS-CK-06 for high-contrast usable mechanism against low-contrast large rear structures, HK-CT-05 for depth and separating landing planes, HK-GP07 for selective overhead light only; do not copy any non-RelicEscape asset shapes.
```

## C 전실과 B1 봉인문

[boss-antechamber.png](boss-antechamber.png) · 배치 기준 `assets/concepts/lower-route-combat-style-v1/c-antechamber-v2.png` · 생성 원본 `exec-d53f018d-3f7b-4fb4-a12d-7815dbe19ae8.png`

```text
Asset: 16:9 C-room full visual concept at the approach to the sealed B1 gate from the right. Preserve input 1 exactly: floor line at y≈62.6% across all width, unbroken rock mass sinking to dark at bottom, same ceiling and overhanging left rock, open right entrance from B, sealed circular-topped original stone door centered x≈15% and grounded y≈62.6%; same compact original hexagonal cyan retry lantern centered x≈37.3% grounded below eye level, separated from the large door. Right half keeps the two original small pillbug silhouettes, no new enemy and no boss revealed. Background shifts from current even saturated blue toward layered dark blue teal; two softened abandoned slate hex steles or broken piers behind the broad arch vestiges, low atmospheric contrast, not an alternative passage. One diffuse reflected pale mint ray from a narrow ceiling fissure on the RIGHT hits the ash-blue floor edge and the closest moss at the B opening; it softens towards the left through an unbroken walk plane. The retry lantern is the one clear saturated signal in the sheltered left half, reflecting only onto a small stone patch and adjacent leaf tips. Gate remains dark and sculptural, thin light on a few exposed slate edges, no glowing center and same carved shape. Sparse moist ferns and bead moss at bases and roof, thinner vegetation immediately around the threshold. Give quiet sheltered anticipation with open negative space and no new platform. SS-MF-04 informs localized small light in dark alcove, HK-GP07 informs foreground shadow and moss texture principles only.
```
