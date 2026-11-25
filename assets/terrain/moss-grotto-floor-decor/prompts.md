# 맵1 바닥과 전경 장식 생성 프롬프트

내장 imagegen으로 개별 원본 7장과 4종씩 담은 원본 스프라이트 시트 4장을 생성했다. 시트의 잘라낸 좌표는 [placement.json](placement.json)에 기록했다.

모든 생성의 첫 입력은 [실제 바닥 타일](../green-cavern-floor-v1.png)이다. 선명한 검은 윤곽, 깊은 청록과 작은 이끼빛 윗면을 기준으로 삼았다. 시트에는 앞서 완성한 바닥 장식 7종의 비교 이미지도 스타일 참고로 사용했다.

## low-hooked-grass

두 번째 입력 [HK-GP05](../../../docs/references/hollow-knight-greenpath/images/gp05.png)에서 바닥과 이어지는 짧은 잎 덩어리와 검은 윤곽을 참고했다.

```text
Use case: stylized-concept. Output one original game-ready isolated 2D decorative sprite for the PLAYABLE foreground of RelicEscape. Image 1 is the actual project's foreground moss-and-stone floor texture: match its surface vegetation and stone treatment up close, its near-black clear outside edges and compact jade/olive edge highlights. Do not recreate the floor strip. Image 2 is only a reference for the strong dark foreground silhouette, compact foliage groups and visual variety. Side-on orthographic profile. Crisp ink-dark outline, clean broad filled color shapes, a handful of small irregular moss-green light marks on top-facing surfaces, abrupt separation into deep cold charcoal under-leaf planes, controlled readable texture like hand-painted game terrain rendered at small size. No soft gouache fog, faint bluish background-style wash, sepia, bloom, feathery transparent shading, sharp spikes, excessive gradients, thick sticker border, casts on the canvas or ground below. The entire outside is TRUE TRANSPARENT ALPHA and there is margin around all parts. No text, no character, no icons, no repeating or mirror symmetry. One single connected cluster.
An asymmetric low tuft of about five dark grass ribbons with short rounded tips. One relatively long blade folds sharply halfway then arcs low to the right. Two shorter grass blades rise in a different direction, two nearly hug the moss-coated base. A few tiny green moss buttons cluster at one end. Fat curved leaves, no reedlike pointed tips. Compact, wider than tall, readable at 48 pixels wide.
```

## bead-moss-patch

두 번째 입력 [HK-GP05](../../../docs/references/hollow-knight-greenpath/images/gp05.png)에서 작고 굵은 잎이 보행면에 비대칭으로 모이는 방식을 참고했다.

```text
Use case: stylized-concept. Output one original game-ready isolated 2D decorative sprite for the PLAYABLE foreground of RelicEscape. Image 1 is the actual project's foreground moss-and-stone floor texture: match its surface vegetation and stone treatment up close, its near-black clear outside edges and compact jade/olive edge highlights. Do not recreate the floor strip. Image 2 is only a reference for the strong dark foreground silhouette, compact foliage groups and visual variety. Side-on orthographic profile. Crisp ink-dark outline, clean broad filled color shapes, a handful of small irregular moss-green light marks on top-facing surfaces, abrupt separation into deep cold charcoal under-leaf planes, controlled readable texture like hand-painted game terrain rendered at small size. No soft gouache fog, faint bluish background-style wash, sepia, bloom, feathery transparent shading, sharp spikes, excessive gradients, thick sticker border, casts on the canvas or ground below. The entire outside is TRUE TRANSPARENT ALPHA and there is margin around all parts. No text, no character, no icons, no repeating or mirror symmetry. One single connected cluster.
An uneven broken oval patch of small thick round two-toned moss leaves, like small waxy buttons and short oval leaves of different sizes. A dense left end, an exposed gap in the middle, three lower leaves stepping down toward the right. Minimal rounded dark moss base with no rock slab or flat ground line, silhouette only a few leaf heights tall. No flowers or bright tips floating separate from the cluster.
```

## overhanging-fern

두 번째 입력 [HK-GP10](../../../docs/references/hollow-knight-greenpath/images/gp10.png)에서 발판 아래로 자연스럽게 이어지는 불규칙한 작은 잎을 참고했다.

```text
Use case: stylized-concept. Output one original game-ready isolated 2D decorative sprite for the PLAYABLE foreground of RelicEscape. Image 1 is the actual project's foreground moss-and-stone floor texture: match its surface vegetation and stone treatment up close, its near-black clear outside edges and compact jade/olive edge highlights. Do not recreate the floor strip. Image 2 is only a reference for the strong dark foreground silhouette, compact foliage groups and visual variety. Side-on orthographic profile. Crisp ink-dark outline, clean broad filled color shapes, a handful of small irregular moss-green light marks on top-facing surfaces, abrupt separation into deep cold charcoal under-leaf planes, controlled readable texture like hand-painted game terrain rendered at small size. No soft gouache fog, faint bluish background-style wash, sepia, bloom, feathery transparent shading, sharp spikes, excessive gradients, thick sticker border, casts on the canvas or ground below. The entire outside is TRUE TRANSPARENT ALPHA and there is margin around all parts. No text, no character, no icons, no repeating or mirror symmetry. One single connected cluster.
A short sloping ledge decoration. Small tight moss crown at its upper left that attaches at one edge, two irregularly spaced curl-and-drop stems bearing a handful of rounded oval leaflets. One drop is longer and bends to the right, one only hugs the upper base. The silhouette should cling to the side of a rock with a few lobes above the attachment and most leaf mass curving below it. No platform, brick, soil or dangling roots of uniform length.
```

## squat-cave-fungi

두 번째 입력 [HK-GP05](../../../docs/references/hollow-knight-greenpath/images/gp05.png)에서 장식이 붙은 부분과 비어 있는 바닥의 높이 차이을 참고했다.

```text
Use case: stylized-concept. Output one original game-ready isolated 2D decorative sprite for the PLAYABLE foreground of RelicEscape. Image 1 is the actual project's foreground moss-and-stone floor texture: match its surface vegetation and stone treatment up close, its near-black clear outside edges and compact jade/olive edge highlights. Do not recreate the floor strip. Image 2 is only a reference for the strong dark foreground silhouette, compact foliage groups and visual variety. Side-on orthographic profile. Crisp ink-dark outline, clean broad filled color shapes, a handful of small irregular moss-green light marks on top-facing surfaces, abrupt separation into deep cold charcoal under-leaf planes, controlled readable texture like hand-painted game terrain rendered at small size. No soft gouache fog, faint bluish background-style wash, sepia, bloom, feathery transparent shading, sharp spikes, excessive gradients, thick sticker border, casts on the canvas or ground below. The entire outside is TRUE TRANSPARENT ALPHA and there is margin around all parts. No text, no character, no icons, no repeating or mirror symmetry. One single connected cluster.
Two small low cave mushrooms emerging from sparse moss. One large low asymmetric rounded cap curves lower to the right, one much smaller cap leans to the left, and two round moss leaves tuck beside the roots. Caps are dark slate-teal with a soft ink edge, sparse jade edge chips and charcoal gills. Short stems, grouped in a shallow low triangle. No spots, luminosity, flowers, red or pale cream caps.
```

## moss-rock-chips

두 번째 입력 [HK-GP05](../../../docs/references/hollow-knight-greenpath/images/gp05.png)에서 청록 회색 바위의 둥근 외곽과 잎 가장자리을 참고했다.

```text
Use case: stylized-concept. Output one original game-ready isolated 2D decorative sprite for the PLAYABLE foreground of RelicEscape. Image 1 is the actual project's foreground moss-and-stone floor texture: match its surface vegetation and stone treatment up close, its near-black clear outside edges and compact jade/olive edge highlights. Do not recreate the floor strip. Image 2 is only a reference for the strong dark foreground silhouette, compact foliage groups and visual variety. Side-on orthographic profile. Crisp ink-dark outline, clean broad filled color shapes, a handful of small irregular moss-green light marks on top-facing surfaces, abrupt separation into deep cold charcoal under-leaf planes, controlled readable texture like hand-painted game terrain rendered at small size. No soft gouache fog, faint bluish background-style wash, sepia, bloom, feathery transparent shading, sharp spikes, excessive gradients, thick sticker border, casts on the canvas or ground below. The entire outside is TRUE TRANSPARENT ALPHA and there is margin around all parts. No text, no character, no icons, no repeating or mirror symmetry. One single connected cluster.
Three very low irregular rounded dark blue slate pebbles touching at their base, with the largest offset toward one side. One has a slanted oval cross section, another is squat and partly tucked behind. Short localized moss and a few shiny rounded leaves on the crown. Use near-black undersides, cool mineral green-blue flat stone planes, a few moss highlights. A decorative small floor gravel group only, not a rectangular collision tile, not a boulder or step.
```

## near-shadow-ribbon-grass

두 번째 입력 [HK-GP10](../../../docs/references/hollow-knight-greenpath/images/gp10.png)에서 시야 바깥을 감싸는 가깝고 어두운 큰 풀을 참고했다.

```text
Use case: stylized-concept. Output one original game-ready isolated 2D decorative sprite for the PLAYABLE foreground of RelicEscape. Image 1 is the actual project's foreground moss-and-stone floor texture: match its surface vegetation and stone treatment up close, its near-black clear outside edges and compact jade/olive edge highlights. Do not recreate the floor strip. Image 2 is only a reference for the strong dark foreground silhouette, compact foliage groups and visual variety. Side-on orthographic profile. Crisp ink-dark outline, clean broad filled color shapes, a handful of small irregular moss-green light marks on top-facing surfaces, abrupt separation into deep cold charcoal under-leaf planes, controlled readable texture like hand-painted game terrain rendered at small size. No soft gouache fog, faint bluish background-style wash, sepia, bloom, feathery transparent shading, sharp spikes, excessive gradients, thick sticker border, casts on the canvas or ground below. The entire outside is TRUE TRANSPARENT ALPHA and there is margin around all parts. No text, no character, no icons, no repeating or mirror symmetry. One single connected cluster.
A clean asymmetric near-black foreground silhouette of three rounded broad grass ribbons bending low close to the floor and one short upward curled leaf. One blade extends low to the left, the other two overlap with a negative-space notch toward the right. Side profile, compact base, large silhouette shapes. Nearly opaque charcoal ink #040b0d, with only a very dark teal separator on the upper overlapping edges. No bright moss, no detailed veins, no glow. Should read clearly and stay visually quiet at 96 pixels wide in the bottom corner.
```

## near-shadow-rounded-leaves

두 번째 입력 [HK-GP05](../../../docs/references/hollow-knight-greenpath/images/gp05.png)에서 밝은 전투면 앞에 낮게 겹치는 검은 잎 실루엣을 참고했다.

```text
Use case: stylized-concept. Output one original game-ready isolated 2D decorative sprite for the PLAYABLE foreground of RelicEscape. Image 1 is the actual project's foreground moss-and-stone floor texture: match its surface vegetation and stone treatment up close, its near-black clear outside edges and compact jade/olive edge highlights. Do not recreate the floor strip. Image 2 is only a reference for the strong dark foreground silhouette, compact foliage groups and visual variety. Side-on orthographic profile. Crisp ink-dark outline, clean broad filled color shapes, a handful of small irregular moss-green light marks on top-facing surfaces, abrupt separation into deep cold charcoal under-leaf planes, controlled readable texture like hand-painted game terrain rendered at small size. No soft gouache fog, faint bluish background-style wash, sepia, bloom, feathery transparent shading, sharp spikes, excessive gradients, thick sticker border, casts on the canvas or ground below. The entire outside is TRUE TRANSPARENT ALPHA and there is margin around all parts. No text, no character, no icons, no repeating or mirror symmetry. One single connected cluster.
An original compact foreground ornament of four blunt bent oval leaves, with one low broad oval projecting toward the right and one slightly higher broad leaf leaning left. Include two low irregular folded forms at the foot. A distinctive silhouette like overlapping rounded stones made from leaves, with large dark gaps between outlines. Almost-black charcoal-petrol #040b0d flat mass and one dark petrol shape inside no brighter than #172728. No visible leaf veins or noisy matte.
```

## ground-sprouts

세 번째 입력 [HK-GP05](../../../docs/references/hollow-knight-greenpath/images/gp05.png)에서 표면에 붙은 작은 잎과 드문드문 보이는 빈 구간을 참고했다. [원본 스프라이트 시트](source/ground-sprouts.png)

```text
Use case: stylized-concept. A square 2×2 production sprite atlas for the PLAYABLE foreground of the first map of RelicEscape, true transparent alpha. Image 1 is the project's actual playable moss-stone floor. Image 2 shows the seven newly generated floor decorations: match their charcoal-black crisp outlines, small range of dark mineral blue-green planes, broken tiny jade/olive highlights, smooth round silhouettes and small-scale clarity. Image 3 is general inspiration for vegetation mass and foreground negative space only. Do not recreate any existing scenery, characters or exact tiles. Four DIFFERENT ORIGINAL sprites according to the quadrant descriptions. All side-on 2D where appropriate. Each sprite is completely contained in its own quadrant; the alpha is fully zero in a generous invisible cross gutter centered at x=50% and y=50%, at least 10% of the canvas thick. Outer margin at least 7%. Nothing crosses a quadrant. There are no drawn labels, grid lines, visual guides, drop shadows, backgrounds or checkerboard, no thin sharp spikes, no haze or bloom. Preserve strongly inked contours and plain dark color groups. Use original amber-free, blue-green forest accents.
TOP LEFT: An uneven tight group of three tiny straight-to-curved stalks in a floor crack, each bearing a pair of rounded jade paddle tips at very different heights. One minimal spot of moss at the foot. Tall compared with the other cell sprites, but miniature and delicate when scaled.
TOP RIGHT: A very shallow two-lobed creeping moss cushion connected by a thin dark runner, with a few cushion moss swirls rising from one lobe and a clearly visible notch between them. Mostly low carpet moss with no visible stalks and no rocks.
BOTTOM LEFT: One uneven pair of rounded-lobed ferns, low fan of three wide round lobes to the left and one larger folded spoon frond leaning outward right. Lower dark base, leaf lobes very broad and curved, never needle-like.
BOTTOM RIGHT: A little cluster of unequal short springy crooked moss-green stems with blunt soft dark oval club ends about the same tone as the moss. Taller isolated club leans left, others too short to look like a mushroom. Subtle rim of moss at the foot, no caps, glow, flowers or white dots.
```

## ceiling-wall-roots

세 번째 입력 [HK-GP10](../../../docs/references/hollow-knight-greenpath/images/gp10.png)에서 길이가 다른 천장 잎과 암벽 쪽의 크고 작은 식생을 참고했다. [원본 스프라이트 시트](source/ceiling-wall-roots.png)

```text
Use case: stylized-concept. A square 2×2 production sprite atlas for the PLAYABLE foreground of the first map of RelicEscape, true transparent alpha. Image 1 is the project's actual playable moss-stone floor. Image 2 shows the seven newly generated floor decorations: match their charcoal-black crisp outlines, small range of dark mineral blue-green planes, broken tiny jade/olive highlights, smooth round silhouettes and small-scale clarity. Image 3 is general inspiration for vegetation mass and foreground negative space only. Do not recreate any existing scenery, characters or exact tiles. Four DIFFERENT ORIGINAL sprites according to the quadrant descriptions. All side-on 2D where appropriate. Each sprite is completely contained in its own quadrant; the alpha is fully zero in a generous invisible cross gutter centered at x=50% and y=50%, at least 10% of the canvas thick. Outer margin at least 7%. Nothing crosses a quadrant. There are no drawn labels, grid lines, visual guides, drop shadows, backgrounds or checkerboard, no thin sharp spikes, no haze or bloom. Preserve strongly inked contours and plain dark color groups. Use original amber-free, blue-green forest accents.
TOP LEFT: A shallow asymmetrical inverted moss bank with two rounded dripping lumps on its underside, dense slightly opaque shale-moss shapes at the top and less leaf mass below. One end tapers into empty space. Works as a small roof border, with no flat rectangular tile.
TOP RIGHT: One long crooked descending dark woody root that bends sideways in a slow curve halfway down, with two shorter rounded branches that end at different heights. Very few moss leaves on upper third, clear silhouette, no needle tips.
BOTTOM LEFT: Compact upright wall-hugging ivy patch of five broad matte round-heart-shaped leaves. Large leaf slightly off center, other leaves much smaller and wind tight to a single short stem emerging on the right. No slab behind it.
BOTTOM RIGHT: A horizontal low vine running right from an irregular mossy crown, soft oval tiny foliage clustered at one end and one asymmetric curling stem which curves down from the far end. One connected plant. Long thin profile, no stones, no long leaflets or fern.
```

## ruin-fragments

세 번째 입력 [HK-GP05](../../../docs/references/hollow-knight-greenpath/images/gp05.png)에서 짙은 석재와 단순한 전경 유적 실루엣을 참고했다. [원본 스프라이트 시트](source/ruin-fragments.png)

```text
Use case: stylized-concept. A square 2×2 production sprite atlas for the PLAYABLE foreground of the first map of RelicEscape, true transparent alpha. Image 1 is the project's actual playable moss-stone floor. Image 2 shows the seven newly generated floor decorations: match their charcoal-black crisp outlines, small range of dark mineral blue-green planes, broken tiny jade/olive highlights, smooth round silhouettes and small-scale clarity. Image 3 is general inspiration for vegetation mass and foreground negative space only. Do not recreate any existing scenery, characters or exact tiles. Four DIFFERENT ORIGINAL sprites according to the quadrant descriptions. All side-on 2D where appropriate. Each sprite is completely contained in its own quadrant; the alpha is fully zero in a generous invisible cross gutter centered at x=50% and y=50%, at least 10% of the canvas thick. Outer margin at least 7%. Nothing crosses a quadrant. There are no drawn labels, grid lines, visual guides, drop shadows, backgrounds or checkerboard, no thin sharp spikes, no haze or bloom. Preserve strongly inked contours and plain dark color groups. Use original amber-free, blue-green forest accents.
TOP LEFT: A low broken upright piece of carved dark bluish slab with a softly rounded chipped top leaning to one side. Two tiny rubbed shallow grooves only, no signs or writing. It is partly buried in moss and should read as a modest bit of floor rubble.
TOP RIGHT: A small thick curved C-shaped fragment of an ancient dark slate stone rim, lying tilted low so it has an obvious solid base. Broad chipped blunt ends, short band of dull moss. One broken segment only, not a ring, icon, glowing effect, or freestanding doorway.
BOTTOM LEFT: Three small flat sliding slate chunks crossing each other at unequal diagonals as if broken off a stair. Chipped softened corners, cool near-black faces with simple planes, sparse low moss only under one end. Clearly different height and structure from rounded pebbles. Low decorative pile.
BOTTOM RIGHT: One very low sideways ancient root stump with a dark old rounded broken section at one end and two low curves sprawling to the right. The main mass is blue-petrol shaded old wood, with one small olive moss patch and an opaque near-black root base. No sharp branch spikes, drab brown or visible ring pattern that looks like a glyph.
```

## foreground-silhouettes

세 번째 입력 [HK-GP10](../../../docs/references/hollow-knight-greenpath/images/gp10.png)에서 화면 가장자리의 검은 덩어리와 중앙 여백을 참고했다. [원본 스프라이트 시트](source/foreground-silhouettes.png)

```text
Use case: stylized-concept. A square 2×2 production sprite atlas for the PLAYABLE foreground of the first map of RelicEscape, true transparent alpha. Image 1 is the project's actual playable moss-stone floor. Image 2 shows the seven newly generated floor decorations: match their charcoal-black crisp outlines, small range of dark mineral blue-green planes, broken tiny jade/olive highlights, smooth round silhouettes and small-scale clarity. Image 3 is general inspiration for vegetation mass and foreground negative space only. Do not recreate any existing scenery, characters or exact tiles. Four DIFFERENT ORIGINAL sprites according to the quadrant descriptions. All side-on 2D where appropriate. Each sprite is completely contained in its own quadrant; the alpha is fully zero in a generous invisible cross gutter centered at x=50% and y=50%, at least 10% of the canvas thick. Outer margin at least 7%. Nothing crosses a quadrant. There are no drawn labels, grid lines, visual guides, drop shadows, backgrounds or checkerboard, no thin sharp spikes, no haze or bloom. Preserve strongly inked contours and plain dark color groups. Use original amber-free, blue-green forest accents. For all four sprites use near-black #040b0d and very limited darkest teal internal shapes, keep them visibly darker than the reference floor decorations.
TOP LEFT: A small near-black foreground silhouette with one soft curled fiddlehead on a thick low stem and one much smaller curved leaf. Unequal positions, subtle negative space. Sparse, slightly vertical, compact base.
TOP RIGHT: A very low mass of two long sparse overlapping broad blunt leaves nearly laid along the ground, stretching horizontally to one side, with one small rounded side leaf behind. Strong horizontal silhouette, fill mostly near black. Very different from an upright plant crown.
BOTTOM LEFT: A compact near-black side-corner silhouette of a bent hook-shaped woody root, emerging from an implied left wall, curves out right and turns down, with one small low blunt branching knob. Avoid lengthy pointed tips. No foliage required, keep the dark interior shape readable.
BOTTOM RIGHT: A very low irregular dark silhouette of four flattened overlapping moss lobes with a tiny nick between lobe pairs and softly scalloped rounded contours. Use only colored shape separation in the deepest petrol blue, no sharp leaves, stones or protruding lines.
```
