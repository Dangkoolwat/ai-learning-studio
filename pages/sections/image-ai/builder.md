---
registry_id: image-ai-builder
title: AI 이미지 프롬프트 빌더
description: 피사체, 스타일, 조명, 구도를 선택하면 친절한 설명과 함께 실시간으로 완벽한 프롬프트가 조립됩니다.
---

# AI 이미지 프롬프트 빌더 (친절한 학습형)

원하는 조건과 분위기를 선택하세요. 각 항목 라벨 옆의 `?` 버튼을 클릭하면 세부 의미와 추천 활용 가이드를 팝업으로 확인할 수 있습니다.

```prompt-field
id: ai-target
label: 사용할 AI 선택
placeholder: ChatGPT / Gemini / Imagen / Midjourney / Flux
description: 적용할 AI 모델을 선택하세요. AI 종류에 따라 최적의 마무리 지침이 자동으로 연결됩니다.
```

```prompt-field
id: subject
label: 중심 피사체 및 주인공
placeholder: 예: 노란 원피스를 입은 여성 여행자
description: 이미지에서 가장 먼저 시선이 가야 하는 중심 대상을 구체적으로 작성해 보세요.
```

```prompt-field
id: action
label: 행동 또는 장면 연출
placeholder: 예: 오래된 골목길을 천천히 걸으며 주변을 바라본다
description: 대상의 동작이나 행동을 적어주면 장면이 더욱 자연스러워집니다.
```

```prompt-field
id: background
label: 장소 및 배경
placeholder: 예: 해 질 무렵의 이탈리아 소도시
description: 배경 장소나 계절, 시간대를 지정해 인물과의 공간적 조화를 만듭니다.
```

```prompt-field
id: style
label: 사진 및 디자인 스타일
placeholder: Editorial (잡지 화보) / Travel (여행 감성) / Commercial (광고 사진) / Minimal (미니멀 디자인) / Cinematic (영화 분위기) / Kodak Portra (따뜻한 필름)
description: 잡지 화보처럼 정돈된 구도, 영화 같은 분위기, 필름 감성 등 시각적 톤앤매너를 결정합니다.
```

```prompt-field
id: lighting
label: 조명 및 시간대
placeholder: Golden Hour (노을 빛) / Soft Daylight (자연광) / Neon (네온 조명)
description: 빛의 분위기를 정합니다. Golden Hour 선택 시 해 질 무렵의 따뜻한 감성과 긴 그림자를 연출합니다.
```

```prompt-field
id: composition
label: 화면 구도 및 렌즈
placeholder: Rule of Thirds (삼분할 구도) / Centered (중앙 배치) / Negative Space (여백 강조) / 35mm (광각) / 85mm (인물 중심)
description: 시선의 위치를 결정합니다. 85mm 렌즈 선택 시 인물에 시선이 몰리고 배경은 아련하게 흐려집니다.
```

```prompt-field
id: ratio
label: 이미지 화면 비율
placeholder: 1:1 (정사각형) / 4:5 (세로 포스터) / 16:9 (가로 썸네일) / 9:16 (모바일 릴스)
description: SNS, 포스터, 썸네일 등 사용 목적에 맞는 가로/세로 비율을 선택합니다.
```
