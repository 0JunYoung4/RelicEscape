"""Build the offline research gallery and analytical image plates from saved sources."""
import csv
import html
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
CATALOG='''GP01|폭포 아래 벤치와 등불|휴식,조명,레이어|낮은 바닥과 비어 있는 중앙 위로 폭포가 높게 열린다.|큰 둥근 돌 사이에 작은 잎 덩어리를 밀집시킨다.|천장 덩굴은 어둡고 가까우며 폭포와 기둥은 흐리고 멀다.|흰 등불의 작은 광원과 넓은 청록색 수직 빛이 겹친다.|유물 획득 직후 쉬어 가는 구간에 작은 등불 하나와 넓은 빈 배경을 배치한다.
GP02|웅덩이 위 철문과 수직 샛길|맵,위험,레이어|왼쪽 낮은 문과 오른쪽 높은 발판이 수평·수직 경로를 함께 제시한다.|철문의 얇은 선과 두꺼운 이끼 지형이 대비된다.|화면 위 검은 덩어리는 지형 내부이고 뒤의 낙수는 원경이다.|산성 액체의 밝은 수평면이 낙하 위험을 분명하게 만든다.|경로를 바꿀 때 벽 표면보다 다음 발판과 위험 경계를 먼저 읽히게 한다.
GP03|산성 호수 위 유적 회랑|유적,텍스처,조명|아치 두 층과 긴 수평 보행면이 반복된다.|매끈한 곡선 석재 위에 잎이 부분적으로 침식한다.|뒤 회랑의 기둥은 낮은 대비로 반복되고 앞 가장자리가 선명하다.|차가운 등불과 밝은 녹색 액체가 서로 다른 높이에 놓인다.|유적 장치 주변만 구조적 대칭을 쓰고 자연 지형과 구분한다.
GP04|가시로 둘러싸인 좁은 통로|위험,맵,텍스처|위·아래 가시 사이에 열린 이동 통로가 있다.|주황·분홍 끝이 있는 뾰족한 가시가 둥근 이끼와 확실히 구별된다.|바깥 검은 덩어리와 안쪽 가시 테두리가 통로를 액자처럼 감싼다.|중앙 배경은 청록색으로 밝고 위험한 가시는 따뜻한 가장자리를 갖는다.|위험물은 색뿐 아니라 뾰족한 외곽선으로도 식별하게 한다.
GP05|이끼 기사의 평평한 전투 공간|전투,몬스터,조명|중앙 보행면을 길게 비우고 가장자리의 장식만 높인다.|돌기둥과 잎 덩어리는 촘촘하지만 전투 공간은 단순하다.|위 덩굴은 검은 프레임이며 뒤 기둥은 흐리다.|두 줄기 이상의 세로 빛이 전투 공간 뒤를 나눈다.|현재 전투방 중앙과 적 공격 궤적 뒤에는 조밀한 잎이나 밝은 점을 줄인다.
GP06|유적 기둥과 매달린 검은 발판|유적,레이어,그림자|중앙 위쪽의 검은 발판 아래로 큰 기둥들이 이어진다.|밝은 석재는 윤곽과 홈을 읽히게 하고 발판 속은 검게 묻힌다.|발판 검정은 충돌 지형의 내부이며 원경의 아치와 다르다.|기둥 뒤의 수직 광막과 앞쪽 작은 등불이 깊이를 만든다.|검은 지형 코어를 유지하면서 장치 받침의 표면선만 드러낸다.
GP07|호넷 공간의 문양 비석|전투,랜드마크,조명|평평한 바닥 위 큰 문양 돌 하나가 시각적 중심이 된다.|굵은 소용돌이 문양과 덩굴이 돌의 큰 형태를 보조한다.|뒤의 식물과 수직 줄기는 비석보다 흐리고 덜 선명하다.|비스듬한 밝은 기둥이 비석과 빈 전투 공간을 비춘다.|보스 도착점에 프로젝트 고유 문양석 하나를 두고 공격 공간을 남긴다.
GP08|대각선 가시와 낮은 유적 통로|위험,맵,유적|위에서 오른쪽 아래로 내려오는 가시가 이동 여유를 압축한다.|유적 아치의 매끈한 곡선과 가시의 뾰족한 선이 대비된다.|상부 검은 지형 밑으로 뿌리가 매달리고 뒤 회랑이 비친다.|배경은 푸르게 눌러 가시 끝과 이동면이 먼저 읽힌다.|천장이 낮은 구간의 장식과 실제 위험 경계를 섞지 않는다.
GP09|역 입구와 벤치|휴식,랜드마크,유적|왼쪽 큰 원형 문과 오른쪽 벤치가 방향과 기능을 나눈다.|부챗살 장식·문틀·얇은 기둥은 식생보다 규칙적이다.|아래 전경 난간과 뒤 기둥 사이에 보행면이 놓인다.|문과 벤치 근처의 작은 등불이 기능 지점을 표시한다.|유물 장착기나 재시작 지점에 반복되는 고유 표식을 붙인다.
GP10|낮은 천장 아래 고립된 벤치|휴식,그림자,레이어|대부분을 가린 검은 천장 아래 작은 밝은 공간이 열린다.|천장의 돌 표면보다 아래로 뻗은 가는 뿌리 실루엣이 강하다.|검은 상부 코어와 가까운 뿌리, 푸른 배경을 구별한다.|벤치 주변만 낮은 대비의 푸른 빛으로 드러낸다.|작은 휴식 포켓은 주변을 어둡게 하고 중앙 여백으로 위치를 기억시키자.
GP11|안개 협곡으로 바뀌는 경계|전이,레이어,맵|왼쪽 넓은 땅이 오른쪽 수직 낙하 틈으로 끝난다.|오른쪽 구형 식물이 잎 위주의 왼쪽과 다른 재질을 알린다.|검은 바닥 내부와 뒤의 식물층이 명확히 분리된다.|푸른 공간에 흰 둥근 발광체가 점진적으로 늘어난다.|다음 구역의 색과 소품을 출구 이전부터 조금씩 섞는다.
GP12|사냥꾼의 식생 위장 은신처|몬스터,랜드마크,조명|낮은 잎 무더기에 큰 입과 눈이 묻혀 있다.|겹친 작은 잎과 큰 흰 이빨의 스케일 차이가 인상을 만든다.|멀리 가는 큰 줄기와 가까운 둥근 잎 덩어리가 겹친다.|위에서 내려오는 사선 광선은 눈과 잎 표면을 읽히게 한다.|위장형 오브젝트는 재질을 공유하되 눈·균열·움직임으로 식별 신호를 둔다.
GP13|쉐오의 집과 가시 경계|랜드마크,위험,유적|중앙 둥근 집과 양옆 가시가 안전한 목적지를 감싼다.|집의 큰 판형 곡면 위로 덩굴이 감기고 외곽에는 날카로운 가시가 있다.|어두운 전경 아래로 집 입구가 밝게 열린다.|하얀 출입구 빛과 차가운 외부 청록빛이 대비된다.|유물 장치 방 입구는 고유 큰 형태 하나와 명확한 문틈으로 표시한다.
GP14|산성 호수 위 넓은 다리|맵,위험,조명|긴 평평한 다리가 웅덩이와 넓은 배경을 가른다.|난간·아치의 가는 선과 잎의 작은 덩어리가 공존한다.|다리 아래 검은 코어와 뒤의 큰 줄기는 서로 다른 깊이다.|등불은 국소광이고 산성 수면은 넓은 가로 발광면이다.|넓은 방에서는 점광원과 수평 위험 경계를 다른 크기로 읽히게 한다.
GP15|우운 사당 안의 어두운 휴식 공간|휴식,그림자,조명|거의 검은 입구 테두리 안에 벤치가 작게 놓인다.|안쪽 큰 조각과 긴 곡선 구조는 돌보다 나무 같은 유기 형태를 보인다.|입구를 두르는 검은 프레임과 뒤 벽의 푸른 층이 구분된다.|천장 틈의 좁은 빛이 벤치로 내려오고 주변은 깊게 어둡다.|하강 착지 이후 회복 공간에 전체 밝기 상승 대신 좁은 빛의 통로를 쓴다.
GP16|이층 유적의 벤치 포켓|휴식,맵,유적|위·아래 통로 사이 오른쪽에 벤치가 놓인 작은 공간이 있다.|정교한 다리 하단 장식과 거친 잎 테두리가 겹친다.|전경 아래 실루엣과 여러 층의 유적 기둥이 깊이를 만든다.|벤치 뒤의 푸른 빛이 복잡한 건축에서 쉬는 지점을 분리한다.|샛길의 휴식 지점은 주 경로와 연결되는 시야를 남기고 조명으로 구분한다.
GP17|오블 구역의 수직 발판|수직,맵,레이어|작은 발판이 좌우 다른 높이로 흩어지고 긴 기둥이 시선을 세로로 끈다.|발판 가장자리의 이끼 띠와 아래 뿌리는 크기가 짧고 불규칙하다.|큰 뒤 줄기는 흐리고 전면의 발판·벽 가장자리는 선명하다.|점 형태 포자와 부드러운 청록 광막이 빈 공중을 채운다.|낙하 통로에서는 다음 착지면과 유물 목표가 장식 기둥보다 먼저 보이게 한다.
GP18|여왕의 정원으로 통하는 경계|전이,맵,그림자|좌우 높은 벽 아래 중앙 문양석이 목적지를 표시한다.|둥근 잎 테두리와 규칙적 돌 문양이 섞인다.|중앙 위의 검은 코어와 먼 배경의 아치를 구분한다.|양옆 푸른 광막이 중앙 어두운 문양석을 감싼다.|장치 도착점은 복잡한 광효과보다 고유 실루엣과 좌우 여백으로 표시한다.
GP19|초기 개발판의 낮은 물가|개발판,텍스처,조명|낮은 보행 띠와 큰 빈 배경을 공유한다.|현재 출시판보다 알갱이·기포 같은 점묘가 두드러진다.|앞의 검은 덩어리와 뒤의 푸른 돌층이 겹친다.|사선으로 내려오는 넓은 빛과 밝은 수면이 보인다.|참고용 초기안으로만 사용하고 최종 녹색 거리의 자산 규칙과 혼합하지 않는다.
GP20|초기 개발판의 거대 유해|개발판,랜드마크,레이어|작은 주인공 옆에 거대한 껍질 또는 유해가 배치된다.|큰 곡면의 몇 개 구멍만으로 낡은 생물의 규모를 만든다.|앞쪽 어둠과 뒤의 푸른 큰 형태 사이에 작은 캐릭터가 있다.|차가운 대기광이 유해의 윤곽만 드러낸다.|프로젝트 유적에 거대한 장치 파편 한 점을 두어 공간 규모를 암시한다.
GP21|초기 개발판의 호숫가 난간|개발판,맵,조명|가느다란 다리와 넓은 물가가 수평으로 이어진다.|구멍 난 큰 유기체와 문양 수면이 초기판 특징이다.|앞 난간·중앙 보행면·뒤 큰 유기체가 분리된다.|청록빛 수면과 사선 빛이 화면 아래와 위를 연결한다.|물이나 낭떠러지 주변에 열린 시야를 만들되 고유한 구조물로 재해석한다.
GP22|비행 적과 수직 발판|몬스터,수직,맵|작은 발판 사이 공중에 돌진형 적이 놓인다.|작은 발판은 잎 테두리와 아래 뿌리로 한 덩어리가 된다.|오른쪽 검은 벽과 뒤 큰 식물의 대비가 뚜렷하다.|청록색 밝은 공간 안에 캐릭터와 비행 적이 보인다.|벽점프 첫 학습 공간은 비운 뒤 숙련 구간에서 비행 적을 조합한다.
GP23|잎 단서가 있는 높은 길|탐색,텍스처,그림자|상부 통로와 아래 발판이 겹쳐 샛길의 높이 차를 보여준다.|흩어진 잎과 빽빽한 가장자리 이끼가 방향의 단서가 된다.|중앙 검은 지형 속과 그 아래 선명한 뿌리가 보인다.|화면 우측 위의 작은 밝은 영역이 열린 길을 읽히게 한다.|샛길 앞에는 동일한 잎·문양 파편을 반복해 탐색 단서를 준다.
GP24|덩굴을 타격하는 장면|상호작용,조명,맵|공격이 닿는 덩굴 근처에 발판과 길이 모인다.|얇은 덩굴과 잎 조각이 무거운 지형에서 분리된다.|검은 상부 코어 뒤로 큰 푸른 줄기가 있다.|짧은 흰 공격선과 주황색 타격 광점이 배경보다 강하다.|상호작용 대상은 사전 표식과 타격 후 파편으로 확인시킨다. 정지 화면만으로 정확한 지속시간은 판단하지 않는다.
GP25|높은 곳의 구출 보상|탐색,맵,조명|오른쪽 높은 지점의 병과 아래 발판이 목적·접근로를 나눈다.|벽의 잎 띠와 둥근 문양 돌이 반복된다.|앞의 검은 위쪽 천장과 아래 푸른 원경이 열린다.|목표 부근이 주변 잎보다 밝게 보여 보상을 찾게 한다.|수집물은 미리 보여 주고 유물로 도달할 경로를 이후에 찾게 한다.
GP26|잘린 덩굴 아래 이동 발판|상호작용,맵,텍스처|중앙 큰 발판과 옆의 작은 발판이 단계적인 이동을 만든다.|부서지는 덩굴 잎과 발판 아래 뿌리가 다른 밀도로 표현된다.|위 검은 천장과 뒤 청록색 여백이 충돌면을 둘러싼다.|착지할 발판을 둘러싼 배경이 밝아 외곽이 잘 읽힌다.|이동 장치는 경로와 정지점을 먼저 설계하고 장식으로 가리지 않는다.
GP27|가시 위에 남는 안전 공간|위험,맵,텍스처|작은 안전면과 가시 바닥이 가까워 이동 판단을 요구한다.|밝고 날카로운 가시와 둥근 이끼가 재질로 분리된다.|오른쪽과 아래 검은 지형 내부가 통로의 끝을 만든다.|위험물 끝은 흐리지 않고 중앙만 청록색으로 연다.|안전면의 실제 너비를 장식 잎으로 넓어 보이게 만들지 않는다.
GP28|가시 구덩이를 건너는 발판|위험,수직,맵|양옆 안전면 사이 가시와 발판이 놓여 이동 순서를 만든다.|매달린 뿌리와 뾰족한 가시의 방향성이 서로 다르다.|상하 검은 덩어리가 가운데 밝은 통로를 감싼다.|경로 중앙의 부드러운 푸른 빛이 이동 공간을 드러낸다.|순간이동 퍼즐은 출발·중간 정지점·도착을 한 장면에서 읽히게 한다.
GP29|산성 웅덩이의 작은 섬|위험,맵,조명|물 위 두 작은 발판과 우측 보상 높이가 단계적으로 이어진다.|떠 있는 발판의 불규칙한 잎 덩어리가 배경과 분리된다.|아래 수면은 넓고 상부 천장은 검은 실루엣이다.|밝은 액체 면과 어두운 발판의 명암 대비가 위험을 알린다.|하강 뒤에는 위험 경계와 첫 안전 발판을 카메라가 함께 보여 주게 한다.
GP30|구출 직후의 작은 보상방|탐색,휴식,맵|오른쪽 끝의 안전한 바닥에 캐릭터와 보상이 모인다.|둥근 돌과 잎이 좁은 방을 감싼다.|바닥 속은 검고 배경은 푸른 대기층으로 물러난다.|보상 주변의 밝기를 유지하고 위 천장은 어둡게 닫는다.|보상 획득 직후 공격보다 공간 인지와 귀환 경로를 먼저 확인하게 한다.
GP31|이끼 돌진충의 큰 잎 덩어리|몬스터,전투,텍스처|긴 평평한 보행면에 가로로 긴 적이 놓인다.|잎 위장 덩어리에 얼굴이 드러나 배경 식생과 몸체를 구별한다.|위 유적 발판의 검은 코어와 하단 적의 밝은 외곽이 대비된다.|차가운 빛 속에서 적 얼굴의 밝은 점이 시선을 끈다.|공벌레의 등갑은 배경과 재질을 공유하되 얼굴·실루엣은 독립시킨다.
GP32|작은 이끼족 무리|몬스터,전투,레이어|낮은 통로에 비슷한 체형 둘이 배치된다.|털·잎처럼 일어난 외곽과 밝은 몸통이 특징이다.|검은 중간 지형 때문에 적은 아래 통로에 또렷하게 보인다.|큰 원형 효과 없이 몸통 명암만으로 적을 분리한다.|약한 적 무리는 수보다 간격과 밝은 식별 부분을 먼저 조절한다.
GP33|폭발하는 이끼족의 주황 신호|몬스터,조명,위험|좁은 발판의 둥근 적과 주황 구름이 결합한다.|둥근 몸에 점 같은 돌기가 있고 큰 주황 덩어리가 녹색을 깨뜨린다.|검은 천장과 푸른 배경이 폭발 신호의 대비를 높인다.|따뜻한 주황색은 차가운 지역 팔레트에서 위험 신호가 된다.|골렘의 공격 경고는 색과 자세 변화로 구별하고 유물의 푸른빛과 혼동시키지 않는다.
GP34|방패와 긴 무기의 이끼 기사|몬스터,전투,텍스처|낮고 긴 무기 실루엣이 이동·공격 방향을 가리킨다.|둥근 방패와 잘게 갈라진 잎 갑옷이 다른 크기로 읽힌다.|뒤 큰 나무줄기는 어두워 무기 윤곽을 과도하게 방해하지 않는다.|낮은 채도의 배경 위 밝은 갑옷과 흰 무기가 보인다.|골렘 공격은 팔과 투사체의 큰 방향성이 멀리서도 읽히게 한다.
GP35|통로 옆 고정형 식물 적|몬스터,맵,그림자|좌상단 작은 식물과 아래 이동 공간이 분리된다.|배경 잎과 비슷한 형상에 얼굴·입 부분이 작게 보인다.|큰 검은 중앙 코어가 통로를 위아래로 나눈다.|푸른 주변광 위로 적의 작은 밝은 얼굴이 대비된다.|벽부착 적 제안은 첫 등장 위치를 넓은 시야 안에 두고 사전 신호를 준다.
GP36|상하 지형 사이 바보잡이풀|몬스터,위험,레이어|위아래 통로 틈의 큰 벌어진 입이 이동 경계와 겹친다.|식물 잎과 이빨의 날카로운 외곽을 함께 쓴다.|검은 지형 내부와 입의 밝은 면이 대비되어 위치가 드러난다.|밝은 입 내부가 푸른 배경에서 눈에 띈다.|숨은 위험은 반복 학습용 단서를 두고 최초 착지면·유물 도착점을 바로 덮지 않는다.
GP37|오블의 공중 탄막|몬스터,전투,조명|작은 발판 주변의 둥근 비행 적과 여러 발사체가 공중을 나눈다.|둥근 적 몸과 둥근 탄환이 같은 계열 형태를 쓴다.|뒤 수직 빛줄기는 흐리고 탄환 가장자리는 선명하다.|따뜻한 발사체가 차가운 청록 배경에서 강하게 보인다.|현재 골렘 탄환 뒤에는 낮은 대비의 배경을 두고 포자를 줄인다.
GP38|모기의 가늘고 뾰족한 몸|몬스터,맵,전투|왼쪽 공중의 길쭉한 적이 작은 발판 사이 경로를 가로지른다.|침 모양 주둥이와 얇은 날개가 둥근 이끼와 다른 외곽을 만든다.|오른쪽 검은 지형 코어가 비행 경로의 끝을 또렷하게 한다.|별도 강한 광원보다 가는 밝은 몸체 윤곽이 중요하다.|비행 적을 추가한다면 돌진 방향이 자세로 먼저 드러나게 한다.
GP39|가시 틈의 단단한 비행체|몬스터,위험,텍스처|위·아래 가시 사이의 비행체가 좁은 이동 공간을 차지한다.|단단한 껍질의 가시와 둥근 중앙 몸체가 위험 형태를 반복한다.|배경의 흐린 유적과 선명한 적 껍질이 분리된다.|밝은 주황색 눈과 차가운 껍질이 구별된다.|위험을 겹치는 조합은 숙련 구간 제안으로 남기고 현재 방에 즉시 추가하지 않는다.
EX01|여왕의 정원의 큰 전경 잎|레이어,그림자,비교|큰 식물과 유적 기둥이 화면 양끝을 채운다.|넓은 잎 면·작은 꽃·가느다란 건축 선이 크기로 구분된다.|하단의 거의 검은 큰 잎은 카메라 가까운 가림물로 읽힌다.|중앙 청록 빛과 점 발광 식물이 겹친다.|전경은 가장자리에 큰 덩어리로 두고 작은 잎을 화면 전체에 균일하게 채우지 않는다.
EX02|여왕의 정원의 매달린 발판|맵,레이어,조명|얇은 줄과 발판이 수직 이동의 규칙을 만든다.|규칙적인 금속·돌 테두리에 자연 식물이 끼어든다.|앞쪽 검은 식물, 중앙 매달린 구조, 흐린 초록 배경을 구분한다.|여러 작은 발광체가 층마다 다른 크기로 배치된다.|레일 장치는 규칙적인 형태로 자연 지형과 구분하되 배경 장식 줄과 혼동시키지 않는다.
EX03|안개 협곡의 발광 생물과 흐린 전경|레이어,조명,비교|구불거리는 지형 사이 열린 공간에 발광 생물이 뜬다.|둥근 기포와 부드러운 생물 표면이 돌과 다른 감촉을 만든다.|크고 흐린 원은 가까운 입자처럼 읽히며 지형 속의 검정과 다르다.|흰 중심·분홍 후광·보랏빛 안개가 겹친다.|근접 입자와 유물의 후광은 소수만 사용하고 실제 충돌체와 구별한다.
EX04|버섯 황무지의 하단 실루엣|레이어,그림자,비교|천장과 바닥이 가운데 큰 푸른 빈 공간을 감싼다.|둥근 버섯 갓과 가는 줄기라는 단순 형태를 반복한다.|앞 하단 버섯은 검고 뒤 버섯은 청록색으로 물러난다.|중앙 황록색 작은 빛무리가 깊이를 만든다.|화면 아래 전경을 추가할 때 하단 외곽에 한정하고 플레이어의 발과 착지면을 비운다.
EX05|눈물의 도시의 층진 건축|유적,레이어,조명|긴 수평 발판과 큰 수직 기둥이 도시 깊이를 만든다.|금속 장식의 얇은 선과 돌 받침의 큰 면이 대비된다.|앞 난간·중앙 가로등·먼 건물의 명암 차가 뚜렷하다.|흰 작은 가로등 주변으로 푸른 안개가 번진다.|인공 장치 방의 먼 구조물은 얇고 낮은 대비로 반복해 깊이를 만든다.
EX06|수정 봉우리의 보랏빛 광막|유적,조명,비교|중앙 발판과 긴 사슬이 밝은 배경 앞에 놓인다.|각진 수정과 격자 구조가 유기적 이끼와 반대되는 형태다.|검은 사슬·중앙 발판·보라 원경이 층으로 겹친다.|넓은 보라 빛과 작은 흰 등불은 서로 다른 범위를 갖는다.|지역 변화는 장식 교체와 팔레트로 표현하되 현재 이끼 구간에 보라빛을 무작정 섞지 않는다.'''

def read_rows():
    notes={}
    for line in CATALOG.splitlines():
        key,title,tags,composition,texture,layers,lighting,application=line.split('|')
        notes[key]=dict(label=title,tags=tags.split(','),composition=composition,texture=texture,layers=layers,lighting=lighting,application=application)
    rows=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    for row in rows:
        row.update(notes[row['id']])
    assert len(rows)==len(notes)==45
    return rows

def annotated_plates(rows):
    # Normalized boxes are visual interpretation, not an extracted engine layer stack.
    specs={
      'GP01': [('전경 덩굴',(.68,0,.75,.42)),('플레이 지형',(.05,.77,.75,.99)),('먼 폭포와 숲',(.61,.28,.93,.75)),('등불 중심과 후광',(.37,.32,.48,.67)),('수직 빛줄기',(.45,.02,.64,.66))],
      'GP05': [('천장과 뿌리 가림',(.16,0,.85,.19)),('전투면과 적',(.12,.57,.62,.96)),('뒤 식생과 유적',(.56,.40,.91,.70)),('넓은 수직 광막',(.64,.16,.78,.91))],
      'GP06': [('검은 지형 코어',(.35,.03,.73,.25)),('코어 끝의 뿌리',(.39,.24,.67,.54)),('배경 유적 기둥',(.75,.18,.94,.85)),('기둥 뒤 대기광',(.15,.05,.32,.88))],
      'GP15': [('입구의 검은 프레임',(.02,.03,.25,.93)),('휴식 면',(.26,.80,.76,.96)),('뒤 구조물',(.38,.22,.69,.79)),('천장 틈의 빛',(.43,.14,.59,.82))],
      'GP17': [('충돌 지형과 발판',(.01,.48,.22,.84)),('뒤로 물러난 큰 줄기',(.41,.11,.55,.58)),('선명한 벽 테두리',(.91,.02,.99,.98)),('깊은 푸른 빈 공간',(.64,.29,.87,.48))],
      'GP37': [('전경성 천장 뿌리',(.07,.01,.88,.19)),('발판과 적',(.43,.16,.87,.81)),('주황 발사체',(.43,.11,.62,.38)),('뒤 수직 빛',(.28,.20,.44,.89))],
      'EX01': [('큰 하단 전경 잎',(.58,.50,.99,.99)),('중앙 지형과 식생',(.38,.29,.80,.64)),('상단의 유적 구조',(.05,.04,.36,.22)),('작은 발광 식물',(.49,.09,.68,.42))],
      'EX03': [('가까운 흐린 원',(.69,.51,.93,.87)),('검은 지형 코어',(.36,.58,.60,.96)),('발광 생물',(.33,.08,.47,.39)),('멀고 흐린 보라 배경',(.50,.05,.78,.45))]
    }
    colors=['#ffd479','#7cddca','#92baff','#f4a4e8','#c6ec8a']
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
    small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
    (ROOT/'analysis').mkdir(exist_ok=True)
    lookup={r['id']:r for r in rows}
    for key,marks in specs.items():
        row=lookup[key];im=Image.open(ROOT/row['local_file']).convert('RGB').resize((1440,810))
        out=Image.new('RGB',(1520,1120),'#101d24');out.paste(im,(40,88));d=ImageDraw.Draw(out)
        d.text((40,22),key+'  '+row['label'],font=font,fill='white')
        for i,(label,box) in enumerate(marks):
            x1,y1,x2,y2=box;x1=40+x1*1440;y1=88+y1*810;x2=40+x2*1440;y2=88+y2*810
            d.rectangle((x1,y1,x2,y2),outline=colors[i],width=4)
            d.rectangle((x1,y1,x1+33,y1+34),fill=colors[i]);d.text((x1+8,y1),str(i+1),font=font,fill='#08151c')
            d.text((40+(i%2)*740,922+(i//2)*43),f'{i+1}. {label}',font=font,fill=colors[i])
        d.text((40,1060),'스크린샷의 시각적 해석 · 실제 엔진 레이어/그림자 계산 방식은 미확인 · 출처는 갤러리의 동일 ID',font=small,fill='#abc0c9')
        out.save(ROOT/'analysis'/f'{key.lower()}-layers-lighting.jpg',quality=94)

def texture_atlas(rows):
    cells=[('GP01','둥근 돌과 이끼 테두리',(.02,.36,.22,.76)),('GP05','검은 천장과 긴 뿌리',(.25,.01,.65,.27)),('GP07','문양석과 잎의 겹침',(.17,.30,.41,.85)),('GP03','유적 아치의 반복',(.02,.07,.51,.52)),('GP04','따뜻한 끝을 가진 가시',(.54,.12,.98,.63)),('GP13','집의 큰 곡면과 덩굴',(.18,.10,.77,.85)),('GP31','몬스터의 잎 위장',(.30,.42,.54,.68)),('GP33','폭발 위험의 주황색',(.22,.38,.50,.67)),('EX01','큰 전경 잎의 검은 면',(.66,.48,.99,.99)),('EX03','흐린 원과 생물의 후광',(.68,.49,.97,.90)),('EX05','작은 가로등과 푸른 안개',(.45,.38,.69,.73)),('EX06','각진 수정과 보라 광막',(.65,.02,.98,.76))]
    lookup={r['id']:r for r in rows};out=Image.new('RGB',(1600,1120),'#101d24');d=ImageDraw.Draw(out)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20)
    for i,(key,label,box) in enumerate(cells):
        x=(i%4)*400;y=(i//4)*370
        im=Image.open(ROOT/lookup[key]['local_file']).convert('RGB');w,h=im.size
        crop=im.crop(tuple(round(v*(w if j%2==0 else h)) for j,v in enumerate(box)))
        crop.thumbnail((380,290));out.paste(crop,(x+(400-crop.width)//2,y+12))
        d.text((x+12,y+310),key+' '+label,font=font,fill='#d0e1e7')
    out.save(ROOT/'analysis'/'texture-lighting-atlas.jpg',quality=94)

def write_catalog(rows):
    intro='''# 할로우 나이트 녹색 거리 이미지 자료집

2026년 11월 23일 조사. **녹색 거리 39장과 비교 지역 6장, 총 45장**을 실제 파일로 보관했다. 녹색 거리 39장에는 개발 중 공식 이미지 3장이 포함된다. 주석 이미지·확대 크롭·연락표는 이 수량에 포함하지 않는다. 원본 파일의 SHA-256 중복은 없다.

- [오프라인 이미지 갤러리](index.html): 키워드·지역·태그 검색, 이미지별 분석, 크게 보기.
- [종합 분석과 프로젝트 적용안](../../hollow-knight-greenpath-study.md)
- [전경과 배경 구분 및 조명 분석](../../hollow-knight-layer-lighting-study.md)
- [출처와 파일 메타데이터](sources.json) · [이미지별 구조화 분석](analysis.json) · [CSV 목록](catalog.csv)
- [연락표 1](contact-sheet-01.jpg) · [연락표 2](contact-sheet-02.jpg) · [연락표 3](contact-sheet-03.jpg) · [연락표 4](contact-sheet-04.jpg)
- [텍스처와 빛 확대 자료](analysis/texture-lighting-atlas.jpg)

이미지 저작권은 Team Cherry 및 해당 권리자에게 있다. 이 폴더는 분석용 참고 자료이며 게임에 직접 넣을 제작 자산 폴더가 아니다. Wiki 자료는 다운로드 가능한 800px 미리보기를 보관했고, 제작사·공략 자료는 제공된 해상도로 보관했다. 원본 링크는 `sources.json`에 별도 기록하되 원본 다운로드 완료를 뜻하지 않는다.

각 카드의 **관찰**은 이미지에서 읽히는 형태, **적용안**은 RelicEscape에 대한 제안이다. 깊이·전경·조명 구분은 화면의 겹침·선명도·명암을 이용한 시각적 해석이다. 정지 화면만으로 실제 시차 속도, 충돌, 빛 합성 방식이나 애니메이션 시간을 확정하지 않는다. GP22~GP30은 같은 공략 연속 장면으로, 서로 다른 9개 방을 뜻하지 않는다.

'''
    parts=[intro]
    for row in rows:
        parts.append(f'''## {row['id']} {row['label']}

![{row['id']} {row['label']}]({row['local_file']})

- 구분: {row['region']} · {row['edition']} · {row['width']}×{row['height']} · {', '.join(row['tags'])}
- 맵과 배치: {row['composition']}
- 스타일과 텍스처: {row['texture']}
- 전경과 배경: {row['layers']}
- 조명: {row['lighting']}
- 프로젝트 적용안: {row['application']}
- [출처 페이지]({row['source_page']}) · [제공 이미지]({row['image_url']}) · {row['credit']}

''')
    (ROOT/'README.md').write_text(''.join(parts),encoding='utf-8')
    (ROOT/'analysis.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    with (ROOT/'catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['id','label','region','edition','tags','local_file','width','height','composition','texture','layers','lighting','application','source_page','image_url','sha256']
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        for row in rows:writer.writerow(dict(row,tags=', '.join(row['tags'])))

def write_html(rows):
    esc=html.escape
    cards=[]
    for row in rows:
        fields=''.join(f'<dt>{title}</dt><dd>{esc(row[key])}</dd>' for title,key in [('맵과 배치','composition'),('스타일과 텍스처','texture'),('전경과 배경','layers'),('조명','lighting'),('프로젝트 적용안','application')])
        searchable=' '.join([row['id'],row['label'],row['region'],*row['tags'],row['composition'],row['texture'],row['layers'],row['lighting'],row['application']])
        cards.append(f'''<article class="card" data-region="{esc(row['region'])}" data-tags="{esc(' '.join(row['tags']))}" data-search="{esc(searchable)}"><a class="picture" href="{esc(row['local_file'])}" data-large><img loading="lazy" src="{esc(row['local_file'])}" alt="{esc(row['id']+' '+row['label'])}" width="{row['width']}" height="{row['height']}"></a><div class="body"><div class="eyebrow">{row['id']} · {esc(row['region'])} · {row['width']}×{row['height']}</div><h3>{esc(row['label'])}</h3><p class="tags">{esc(' · '.join(row['tags']))}</p><p class="edition">{esc(row['edition'])}</p><dl>{fields}</dl><footer><a href="{esc(row['source_page'])}" target="_blank" rel="noopener">출처 페이지 ↗</a><a href="{esc(row['image_url'])}" target="_blank" rel="noopener">제공 이미지 ↗</a></footer><small>{esc(row['credit'])}</small></div></article>''')
    plates=''.join(f'<a href="analysis/{key}-layers-lighting.jpg" data-large><img loading="lazy" src="analysis/{key}-layers-lighting.jpg" alt="{key.upper()} 전경 배경 조명 주석"></a>' for key in ['gp01','gp05','gp06','gp15','gp17','gp37','ex01','ex03'])
    doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>녹색 거리 이미지 조사와 미술 분석</title><style>
:root{color-scheme:dark;--bg:#0c181e;--panel:#14252d;--line:#34515a;--text:#e2edea;--sub:#a5bec5;--accent:#a7e6b7}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.75 'Malgun Gothic',sans-serif}a{color:var(--accent);text-underline-offset:4px}header,main{max-width:1500px;margin:auto;padding:36px}h1{font-size:clamp(28px,4vw,50px);line-height:1.3;margin:10px 0 24px}h2{font-size:27px;margin:38px 0 18px}p{max-width:1000px}.eyebrow{color:var(--accent);font-size:13px;letter-spacing:.05em}.lead{font-size:19px;color:#c2d8dc}.stat{display:inline-block;padding:8px 16px;border:1px solid var(--line);border-radius:24px;margin:4px}.nav{display:flex;flex-wrap:wrap;gap:20px;margin:22px 0}.note{padding:18px 22px;border-left:3px solid var(--accent);background:#173039;color:#c7dce0}.filters{position:sticky;top:0;z-index:3;background:#0c181ef5;border-block:1px solid var(--line);padding:16px 0;display:flex;gap:12px;flex-wrap:wrap;align-items:center}input,select,button{font:inherit;color:var(--text);background:#1b313a;border:1px solid #4b6c76;padding:9px 12px;border-radius:7px}input{width:clamp(220px,35vw,440px)}label{font-size:13px;color:var(--sub);display:flex;flex-direction:column}button{cursor:pointer}#count{margin-left:auto;font-size:14px;color:var(--sub)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin-top:24px}.card{border:1px solid var(--line);background:var(--panel);border-radius:13px;overflow:hidden}.card[hidden]{display:none}.picture{display:block;background:#02080c}.picture img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:contain}.body{padding:22px}.body h3{font-size:21px;line-height:1.4;margin:8px 0 6px}.tags{color:#b4d3bd;font-size:13px;margin:0}.edition{font-size:12px;color:var(--sub);margin:4px 0 20px}dt{font-size:13px;color:var(--accent);font-weight:bold;margin-top:13px}dd{margin:3px 0;font-size:15px;line-height:1.75}footer{display:flex;gap:18px;font-size:13px;border-top:1px solid var(--line);padding-top:16px;margin-top:20px}small{display:block;color:var(--sub);font-size:11px;margin-top:10px}.plates{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.plates img{width:100%;height:auto;border:1px solid var(--line);border-radius:9px}table{border-collapse:collapse;width:100%;font-size:15px}th,td{border-bottom:1px solid var(--line);padding:14px;text-align:left;vertical-align:top}th{color:var(--accent)}.table-scroll{overflow-x:auto}dialog{border:1px solid #5e8893;background:#08131a;color:white;max-width:96vw;max-height:96vh;padding:15px}dialog::backdrop{background:#000d}dialog img{display:block;max-width:90vw;max-height:80vh;object-fit:contain}dialog button{float:right;margin-bottom:10px}#empty{display:none;color:var(--sub)}@media(max-width:1080px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:680px){header,main{padding:22px}.grid,.plates{grid-template-columns:1fr}.filters{position:static}#count{margin-left:0}.body{padding:18px}}
</style><header><div class="eyebrow">RELICESCAPE · 환경 미술 참고 조사 · 2026년 11월 23일</div><h1>녹색 거리의 공간과 재질<br>전경 그림자와 빛의 구조</h1><p class="lead">검은 지형 내부와 식생 테두리, 푸른 원경, 비워 둔 이동 공간을 함께 읽는다. 화면 앞쪽의 가림물과 실제 지형을 구별하고, 조명은 방향·범위·역할로 나눈다.</p><div><span class="stat">녹색 거리 39장</span><span class="stat">비교 지역 6장</span><span class="stat">주석 분석 8장</span><span class="stat">총 45개 개별 분석</span></div><nav class="nav"><a href="#catalog">이미지 자료집</a><a href="#depth">레이어 구분</a><a href="#light">조명 구분</a><a href="#plates">주석 이미지</a><a href="../../hollow-knight-greenpath-study.md">종합 분석서</a><a href="../../hollow-knight-layer-lighting-study.md">레이어와 조명 상세</a><a href="README.md">전체 목록</a><a href="catalog.csv">CSV 목록</a></nav><p class="note">모든 이미지는 이 폴더에 저장되어 오프라인으로 볼 수 있다. 이미지를 누르면 크게 열린다. 개발 중 공식 자료 3장은 별도로 표시했다. 주석과 크롭은 총 이미지 수에 포함하지 않는다. 이미지의 저작권은 Team Cherry 및 해당 권리자에게 있으며, 게임 제작 자산과 분리해 참고용으로 보관한다.</p></header><main>
<section id="depth"><h2>전경 그림자와 배경 구분</h2><p>아래 구분은 겹침·선명도·명암을 바탕으로 한 시각적 해석이다. 검은 부분을 모두 그림자로 취급하면 충돌 지형과 장식이 섞인다. 스크린샷만으로 실제 엔진 레이어와 시차 속도를 확정할 수는 없다.</p><div class="table-scroll"><table><tr><th>구분</th><th>보이는 특징과 역할</th><th>프로젝트 적용안</th><th>참고</th></tr><tr><td>원경</td><td>푸르고 흐린 큰 줄기·기둥·폭포. 세부 묘사가 적고 대비가 낮다.</td><td>큰 공간감을 담당하며 플레이 경계로 읽히지 않게 한다.</td><td>GP01, GP17, EX05</td></tr><tr><td>중경</td><td>배경보다 또렷한 기둥·식물. 지형 뒤에서 구역의 성격을 만든다.</td><td>유물 목표 뒤는 비우고 옆쪽에 큰 형태를 배치한다.</td><td>GP06, GP07, EX02</td></tr><tr><td>플레이 지형</td><td>검은 내부와 선명한 돌·이끼 테두리. 밟는 면을 보여 준다.</td><td>충돌 상면과 스킨 기준을 맞추고 발판 폭을 정확하게 읽힌다.</td><td>GP02, GP06, GP28</td></tr><tr><td>근접 전경</td><td>큰 검은 잎·뿌리·난간이 화면 가장자리를 가린다.</td><td>상단·좌우 가장자리에 집중하고 착지면·탄환·유물 도착점을 비운다.</td><td>GP10, EX01, EX04</td></tr><tr><td>지형 속 암전</td><td>돌 내부를 통째로 검게 가린 면. 별도 그림자 투사 증거는 아니다.</td><td>현재 shadow_floor와 검은 코어를 유지한다.</td><td>GP06, GP18, GP23</td></tr><tr><td>안개와 입자</td><td>작은 밝은 포자, 크고 흐린 가까운 원, 뒤쪽의 광막.</td><td>깊이별 크기·선명도를 달리하고 공격 효과와 구별한다.</td><td>GP01, EX03</td></tr></table></div></section>
<section id="light"><h2>조명을 만드는 요소</h2><div class="table-scroll"><table><tr><th>종류</th><th>화면에서의 역할</th><th>제작 방향</th><th>참고</th></tr><tr><td>청록·청색 주변광</td><td>방 전체의 큰 색조와 원경 깊이를 만든다.</td><td>앞 지형까지 똑같이 밝히지 않고 뒤의 빈 공간 위주로 둔다.</td><td>GP05, GP17</td></tr><tr><td>천장 틈 빛줄기</td><td>위에서 아래로 공간을 연결하고 시선을 끈다.</td><td>끝이 부드러운 긴 쐐기 모양을 쓰고 중앙 전투 시야와 겹침을 줄인다.</td><td>GP01, GP07, GP15</td></tr><tr><td>등불과 후광</td><td>작은 흰 중심과 넓고 약한 청록 번짐이 기능 지점을 표시한다.</td><td>유물이나 장치는 중심·중간 후광·바깥 번짐을 분리한다.</td><td>GP01, GP09, EX05</td></tr><tr><td>대기 산란과 안개</td><td>빛 뒤 큰 구조물의 대비를 낮춰 깊이를 만든다.</td><td>전경에는 선명함을 남기고 배경 쪽에 낮은 알파의 색층을 둔다.</td><td>GP06, GP15, EX03</td></tr><tr><td>넓은 발광면</td><td>산성 수면처럼 긴 밝은 면이 위험 경계를 만든다.</td><td>위험 재질의 경계는 선명하게 두고 주변 번짐은 제한한다.</td><td>GP03, GP14, GP29</td></tr><tr><td>위험과 타격의 빛</td><td>주황색 신호와 흰 공격선이 차가운 지역색에서 튄다.</td><td>유물의 푸른 신호, 적 경고, 피격 섬광을 형태·색·지속으로 나눈다.</td><td>GP24, GP33, GP37</td></tr><tr><td>가장자리 암전</td><td>중앙을 남기고 큰 검은 덩어리와 어두운 모서리가 시야를 모은다.</td><td>장식 가림과 화면 암전을 따로 제어한다. UI는 마지막에 그린다.</td><td>GP10, GP15</td></tr></table></div></section>
<section id="plates"><h2>전경 배경과 조명 영역을 표시한 8장</h2><p>박스는 특징을 읽는 위치를 표시한다. 실제 레이어 마스크를 추출한 이미지가 아니다.</p><div class="plates">PLATES</div><p><a href="analysis/texture-lighting-atlas.jpg" data-large>돌·이끼·가시·전경 잎·후광 확대 자료 보기</a></p></section>
<section id="catalog"><h2>이미지별 관찰과 프로젝트 적용안</h2><div class="filters"><label>키워드<input id="search" type="search" placeholder="예: 전경, 그림자, 등불, 몬스터, GP01"></label><label>지역<select id="region"><option value="">모든 지역</option>REGIONS</select></label><label>분석 주제<select id="topic"><option value="">모든 주제</option>TOPICS</select></label><button id="reset">초기화</button><span id="count" aria-live="polite"></span></div><p id="empty">조건에 맞는 이미지가 없습니다.</p><div class="grid">CARDS</div></section><p class="note">출처와 저장 해상도, 접근일, SHA-256은 <a href="sources.json">sources.json</a>에 기록했다. GP22–GP30은 공략의 연속 장면이며 서로 다른 방 9개라는 뜻은 아니다. 시차 속도·블렌드 방식·효과 시간은 정지 이미지에서 측정한 값으로 제시하지 않았다.</p></main><dialog id="viewer"><button id="close" autofocus>닫기 ×</button><img id="large" alt=""></dialog><script>
const cards=[...document.querySelectorAll('.card')],q=document.querySelector('#search'),r=document.querySelector('#region'),t=document.querySelector('#topic');function filter(){let n=0;const query=q.value.trim().toLocaleLowerCase();cards.forEach(c=>{let ok=(!query||c.dataset.search.toLocaleLowerCase().includes(query))&&(!r.value||c.dataset.region===r.value)&&(!t.value||c.dataset.tags.split(' ').includes(t.value));c.hidden=!ok;if(ok)n++});document.querySelector('#count').textContent=n+' / '+cards.length+'장';document.querySelector('#empty').style.display=n?'none':'block'}[q,r,t].forEach(x=>x.addEventListener('input',filter));document.querySelector('#reset').onclick=()=>{q.value=r.value=t.value='';filter()};filter();const d=document.querySelector('#viewer'),large=document.querySelector('#large');document.querySelectorAll('[data-large]').forEach(a=>a.addEventListener('click',e=>{if(typeof d.showModal!=='function')return;e.preventDefault();large.src=a.getAttribute('href');large.alt=a.querySelector('img')?.alt||'확대 자료';d.showModal()}));document.querySelector('#close').onclick=()=>d.close();d.onclick=e=>{if(e.target===d)d.close()};
</script></html>'''
    regions=''.join('<option>'+esc(s)+'</option>' for s in sorted({r['region'] for r in rows}))
    topics=''.join('<option>'+esc(s)+'</option>' for s in sorted({t for r in rows for t in r['tags']}))
    doc=doc.replace('PLATES',plates).replace('REGIONS',regions).replace('TOPICS',topics).replace('CARDS',''.join(cards))
    (ROOT/'index.html').write_text(doc,encoding='utf-8')

if __name__=='__main__':
    rows=read_rows();write_catalog(rows);annotated_plates(rows);texture_atlas(rows);write_html(rows)
    print('Built 45 analysis entries, 8 annotated plates, 1 atlas and offline HTML gallery.')
