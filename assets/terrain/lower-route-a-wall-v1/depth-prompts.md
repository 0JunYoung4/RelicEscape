# A파트 아치 안쪽과 지지부 생성 기록

내장 ImageGen으로 기존 석벽 원화의 재질을 참고해 별도 회랑, 투명 아치 개구부를 갖는 석벽, 작은 레일 지지부를 제작했다. 입력은 같은 폴더의 `background.png`다. HK-CT-05의 서로 다른 거리의 큰 석조 실루엣, HK-GP07의 국소광과 어둠, SS-MG-02의 식생 덩어리와 전경 겹침을 참고했다. 문양과 석재는 RelicEscape 자산에서 이어갔다.

## wall-depth

Use case: precise-object-edit. Input is our original RelicEscape near-wall painting for a side-scrolling game. Preserve its entire 2172x724 framing, stone block arrangement, arch outlines and moss silhouettes. Deliver this close stone wall as a RGBA layer, with ONLY two openings into real transparency. The inner blocked stone fill of the CENTRAL LOWER arch roughly x1200..1480,y360..650 and the UPPER RIGHT arch roughly x1660..1850,y140..350 is removed, leaving the complete thick surrounding voussoir stones and the dark inner arch bevel edges. The holes are genuine transparent alpha, smoothly following the interior of each arch, not square cutouts. Behind them the game will draw a separate soft recessed corridor. Everything else in the full-bleed wall remains opaque and continuous through all four image edges. Lower fine crack contrast and vein highlights, reduce small leaf edge contrast, and shift wall shadow colors toward a calm slightly gray deep teal. Strong reduction of detailed microtexture contrast without a blur filter. Keep broad stones readable and darker than playable platforms, bottom wall extends fully to image edge. Arch rims carry quiet upper highlights and dark inset shadow around each opening so they read as recesses into a fairly close damp ancient wall. Keep the dark enclosed mossy ruin mood. No additional openings, free-standing monuments, characters, gameplay ground, devices, glowing lights, spritesheets, text, checkerboard or border.

Transparency requested: true

## recess

Use case: stylized-concept. Original RelicEscape background plane for looking a short distance into a damp ruined stone passage through two foreground arches. Independent full bleed opaque panoramic 3:1 painting. Muted low contrast desaturated blue teal air, a few large broad dim ancient stone buttresses and one or two repeating vault silhouettes receding behind each other into soft teal darkness. Large simple shapes, little internal line work. Aged broad stone floor slopes into dimness at bottom, top and sides continue the same deep teal stone air all the way to image edges. No bright cyan colors, no dramatic vista, no open sky, no very long vanishing-point perspective, no overlaid foreground portal frames or playable platforms, rails, characters, foliage clutter, glow specks, UI, text. Painterly flat orthographic side-view, faint reflected green-blue humid air. This plane will only be seen through small holes in a closer masonry wall. Contrast deliberately much lower than the input's near stone. Use the input as original palette and masonry identity reference only. All corners and the bottom are painted with spare broad forms, not vignette borders.

Transparency requested: false

## rail-bracket

Use case: stylized-concept. Original RelicEscape separate game sprite. A small wall mounted rail support assembly seen directly side-on, fixed to ancient slate-blue stone and blackened bronze. One compact oval-ish chipped blue-gray stone backplate, with a recessed original hexagonal groove, two aged muted bronze iron anchor rivets; dark metal fork clamps extend toward the viewer from either side of a narrow empty vertical slot in the center. The center empty slot must remain true transparent for a separately rendered vertical blue rail to show clearly. Chunky clean painted shapes, subtle damp teal shadows and moss tucked in a tiny upper crack, material/outline matches reference. Shape short and wider than tall, about 3:1; large transparent padding on all sides. Functional sturdy wall fixing with shallow depth and simple clear silhouette. One complete isolated asset with natural chipped boundary, true alpha. No rail or cyan center itself, no pedestal, floor, wall behind backplate, spotlight, atmospheric veil, text, checkerboard, grid or decorative frames. Grounded subdued tones, not a shiny gold jewel. Intended final screen width about 35 pixels.

Transparency requested: true
