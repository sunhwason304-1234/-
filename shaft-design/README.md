# 파크나라 CHAMPION 파크골프채 샤프트 디자인

크기: **40 × 380 mm** (하단 로고 존 40 mm). 레퍼런스 샤프트 도안의 레이아웃을 따르고, 트라이벌 문양을 벡터로 새로 그려 적용했습니다.

![preview](parknara-champion-preview.png)

## 구성 (위 → 아래)
| 위치 | 내용 |
|---|---|
| 0–30 mm | 파크나라 P 모노그램 엠블럼 (골드 링) |
| 30–35 mm | 골드 트러스(지그재그) 밴드 |
| 41–111 mm | 트라이벌 플레임 (두 번째 이미지를 재해석한 벡터, 메탈 골드 + 오렌지 외곽선 + 글로우) |
| 120–330 mm | **CHAMPION** 세로 로고 (Cinzel Black, 메탈 골드), 별 3개, 오렌지 스피드 프레임, 시리즈 문구, 모델 넘버 01 |
| 334–339 mm | 골드 트러스 밴드 |
| 340–380 mm | 파크나라 정식 로고 (V2 가로형, `logo/v2` 원본 사용) |

배경은 카본 직조 텍스처입니다. 폭 40 mm가 샤프트를 감싸는 방향이므로, 핵심 그래픽은 정면에서 보이는 가운데 20 mm 안에 배치했습니다.

## 파일
| 파일 | 용도 |
|---|---|
| `parknara-champion-shaft-40x380.svg` | 원본 벡터 (mm 단위, 글자는 모두 아웃라인 처리) |
| `parknara-champion-shaft-40x380.pdf` / `.ai` | 인쇄용 실제 크기 (PDF 호환 AI, Illustrator에서 열림) |
| `parknara-champion-shaft-40x380-300dpi.png` | 300 dpi 비트맵 |
| `parknara-champion-preview.png` | 치수가 적힌 도안 + 샤프트 장착 목업 |

인쇄 참고: 색상은 RGB로 되어 있으니 발주 전에 CMYK로 바꿔 주세요. 도련은 사방 2 mm를 권장합니다(배경은 끝까지 채우기).

## 재생성
`FONT_DIR=<fontsource 폴더> python3 shaft-design/build_champion.py` (`pip install fonttools`, `@fontsource/cinzel`, `@fontsource/montserrat`)
