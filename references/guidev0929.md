# UserStory 콘텐츠 제작 가이드 (v0824)

제작사가 만드는 것은 **정적 HTML 한 벌**입니다. 헤더 · 참여 UI · 인증은 플랫폼이 붙입니다.

이 문서는 **지켜야 페이지가 정상 동작하는 규칙**만 담았습니다. 나머지 디자인과 구현은 자유입니다.

---

## 0. 5분 요약

**꼭 지켜야 하는 것 6가지**

| # | 규칙 | 어기면 |
|---|---|---|
| 1 | ZIP 최상위에 `index.html` 하나와 `assets` 폴더 하나 | 업로드 차단 |
| 2 | 콘텐츠 블록은 **표준 `id` + `class="page-section"`** · `<main>` 직속 | 업로드 차단 |
| 3 | 모든 화면에 **`data-screen-id` · `data-screen-name`** · 최상위 블록 이름은 **`{타이틀} {블록명}`** | 업로드 차단 |
| 4 | **브라우저 기본 세로 스크롤**로 끝까지 도달 | 뒷부분을 볼 수 없음 · 집계 불가 |
| 5 | **우측 하단 340 × 420px**에 핵심 정보 두지 않기 (배경은 채워도 됨) | 참여 패널이 콘텐츠를 가림 |
| 6 | 외부 스크립트 · 외부 호출 · 스토리지 사용 안 함 | 업로드 차단 |

**가장 권장하는 구성**

```
1920 × 1080으로 제작 · 1280까지 줄여도 깨지지 않게 · 각 블록 min-height: 100vh · 세로로만 쌓기
스크롤은 브라우저에 맡기고, 진입 효과는 IntersectionObserver로
```

---

## 1. 최소 템플릿 — 여기서 시작

제공 템플릿(`userstory_template.zip`)과 같은 구조입니다. 이 상태로 ZIP을 만들면 바로 통과합니다.
(템플릿 파일에는 맨 위에 비개발자용 사용법 주석이 더 붙어 있습니다.)

```text
userstory_template.zip
├── index.html
└── assets/
    ├── style.css
    ├── app.js
    ├── playbook/              플레이북 이미지 · 영상 · 글꼴
    ├── scenariocanvas/        시나리오 캔버스 이미지 · 영상 · 글꼴
    └── databook/              데이터북 이미지 · 영상 · 글꼴
```

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UserStory</title>
  <link rel="stylesheet" href="./assets/style.css">
</head>
<body>
  <main>
    <section id="playbook" class="page-section"
             data-screen-id="playbook_main"
             data-screen-name="가족을 위한 두 번째 차 플레이북">
      <div class="inner">
        <!-- ▼ 플레이북 코드 붙여넣기 시작 ▼ -->

        <!-- ▲ 플레이북 코드 붙여넣기 끝 ▲ -->
      </div>
    </section>

    <section id="scenario-canvas" class="page-section"
             data-screen-id="canvas_main"
             data-screen-name="가족을 위한 두 번째 차 시나리오 캔버스">
      <div class="inner">
        <!-- ▼ 시나리오캔버스 코드 붙여넣기 시작 ▼ -->

        <!-- ▲ 시나리오캔버스 코드 붙여넣기 끝 ▲ -->
      </div>
    </section>

    <!-- ✂ 데이터북이 없으면 여기부터 지우기 ✂ -->
    <section id="data-book" class="page-section"
             data-screen-id="databook_main"
             data-screen-name="가족을 위한 두 번째 차 데이터북">
      <div class="inner">
        <!-- ▼ 데이터북 코드 붙여넣기 시작 ▼ -->

        <!-- ▲ 데이터북 코드 붙여넣기 끝 ▲ -->
      </div>
    </section>
    <!-- ✂ 데이터북이 없으면 여기까지 지우기 ✂ -->
  </main>

  <script src="./assets/app.js"></script>
</body>
</html>
```

```css
/* assets/style.css */
* { box-sizing: border-box; }

html {
  overflow-x: hidden;
  overflow-y: auto;          /* hidden 금지 */
  scroll-behavior: smooth;
}

body { margin: 0; min-height: 100vh; }

.page-section {
  position: relative;        /* absolute · fixed 금지 */
  width: 100%;
  min-height: 100vh;         /* height 고정 금지 */
}

.inner {
  padding: 80px 40px 96px;   /* 상단 헤더 · 하단 FAB 회피 */
}

/* ▼ 내 디자인 붙여넣기 ▼ */

/* ▲ 여기까지 ▲ */
```

```js
// assets/app.js
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => e.target.classList.toggle('is-visible', e.isIntersecting));
}, { threshold: 0.25 });

document.querySelectorAll('.page-section').forEach(el => io.observe(el));

// ▼ 내 스크립트 붙여넣기 ▼  (io 라는 이름은 이미 쓰고 있으니 겹치지 않게)

// ▲ 여기까지 ▲
```

**넣는 방법**

| 블록 | 넣는 것 | 넣는 곳 |
|---|---|---|
| 플레이북 (필수) | 내 파일의 `<body>` 안 내용 | 플레이북 붙여넣기 표시 줄 사이 |
| 시나리오 캔버스 (필수) | 내 파일의 `<body>` 안 내용, 또는 이미지 한 장 | 시나리오캔버스 붙여넣기 표시 줄 사이. 이미지 한 장이면 `<img src="./assets/scenariocanvas/canvas.webp" alt="…">` 한 줄 |
| 데이터북 (선택) | 내 파일의 `<body>` 안 내용 | 데이터북 붙여넣기 표시 줄 사이 |
| 디자인 · 동작 | `<style>` · `<script>` 안 내용, 또는 따로 연결된 css · js 파일 내용 | `style.css` · `app.js`의 붙여넣기 표시 줄 아래 |

- 데이터북이 없으면 ✂ 표시 줄 사이를 통째로 지웁니다. 빈 데이터북 블록을 남기지 않습니다.
- 한 블록씩 끝까지 옮긴 뒤(본문 → 디자인 → 이미지 → 경로 수정) 다음 블록으로 넘어갑니다. 섞어서 하면 '모두 바꾸기'로 경로를 고칠 때 서로 꼬입니다.
- 썸네일(목록 이미지)은 플랫폼에 따로 올립니다. ZIP에는 넣지 않습니다.

---

## 2. 페이지 구조

### 콘텐츠 블록 3종 — 순서 고정

| 순서 | `id` | 블록명 | | `data-screen-id` | `data-screen-name` |
|---|---|---|---|---|---|
| 1 | `playbook` | 플레이북 | **필수** | `playbook_main` | `{타이틀} 플레이북` |
| 2 | `scenario-canvas` | 시나리오 캔버스 | **필수** | `canvas_main` | `{타이틀} 시나리오 캔버스` |
| 3 | `data-book` | 데이터북 | 선택 | `databook_main` | `{타이틀} 데이터북` |

우측 두 열은 **고정값**입니다. `{타이틀}`만 각 유저스토리의 타이틀로 바꿔 넣습니다.

- `<main>`의 **직접 자식**으로 작성합니다.
- 최상위 블록에는 **반드시 `class="page-section"`**을 붙입니다. 플랫폼이 경계를 인식하는 기준입니다.
- 순서를 바꾸지 않습니다. 데이터북(선택)이 없으면 **빈 채로 두지 말고 블록을 통째로 지웁니다**.
- 내부에서 `<section>`을 써도 되지만 표준 `id`와 `page-section`은 붙이지 않습니다.
- 블록 내부의 HTML 구조와 디자인은 **완전히 자유**입니다.

### 화면 식별자 — 모든 화면에 2개

```html
<section id="scenario-canvas" class="page-section"
         data-screen-id="canvas_main"
         data-screen-name="가족을 위한 두 번째 차 시나리오 캔버스">
```

| 속성 | 용도 | 값 |
|---|---|---|
| `data-screen-id` | 도달률 집계 키 | 소문자 · 숫자 · `-` · `_`, **40자 이내**, 문서 내 유일 |
| `data-screen-name` | 관리자 화면과 리포트에 뜨는 이름 | 최상위 블록은 규칙 고정 · 내부 화면은 자유 (한글 가능) |

- HTML의 `id`와 **다른 것**입니다. `id`는 자유롭게 쓰되 플랫폼은 `data-screen-id`만 봅니다.
- **선언 순서**가 화면 순서가 됩니다.

### 최상위 블록의 이름 — 규칙 고정

최상위 블록 3종의 `data-screen-name`은 **`{유저스토리 타이틀} {블록명}`** 형식으로 씁니다.

```
가족을 위한 두 번째 차 플레이북
└────── 타이틀 ──────┘└ 블록명 ┘
```

- 블록명은 **`플레이북` · `시나리오 캔버스` · `데이터북`** 셋 중 하나입니다. 다른 표현이나 줄임말을 쓰지 않습니다.
- 타이틀과 블록명 사이는 **공백 한 칸**. 괄호 · 하이픈 · 구분 기호를 넣지 않습니다.
- 타이틀은 해당 유저스토리의 타이틀을 **그대로** 씁니다.
- **블록 내부 화면의 이름은 자유입니다.** 타이틀을 반복해 붙이지 않습니다.

여러 유저스토리를 한 화면에서 비교할 때 이름만으로 어느 스토리의 어느 블록인지 구분하기 위한 규칙입니다.

**리포트에 이렇게 나옵니다.** `data-screen-name`을 잘 적으면 그대로 읽히는 리포트가 됩니다.

```
가족을 위한 두 번째 차 플레이북           100%
  └ 불안의 시작                           88%
  └ 첫 번째 신호                           74%
  └ 선택의 순간                            66%
가족을 위한 두 번째 차 시나리오 캔버스      61%
가족을 위한 두 번째 차 데이터북            57%   ← 완독률
```

### 블록을 여러 화면으로 나누기 — 선택

한 블록 안의 페이지별 도달률이 필요하면 **최상위 블록은 그대로 두고, 그 안에 자식 요소를 만들어 식별자만 붙입니다.** 2단 구조입니다.

```
main
└── section#playbook.page-section          ← 최상위 블록 (블록당 1개)
    ├── div.pb-page                         ← 자식 화면 1
    ├── div.pb-page                         ← 자식 화면 2
    └── div.pb-page                         ← 자식 화면 3
```

```html
<section id="playbook" class="page-section"
         data-screen-id="playbook_main"
         data-screen-name="가족을 위한 두 번째 차 플레이북">

  <div class="pb-page" data-screen-id="playbook_01"
       data-screen-name="불안의 시작">…</div>

  <div class="pb-page" data-screen-id="playbook_02"
       data-screen-name="첫 번째 신호">…</div>

  <div class="pb-page" data-screen-id="playbook_03"
       data-screen-name="선택의 순간">…</div>
</section>
```

| | 최상위 `section` | 자식 요소 |
|---|---|---|
| 정체 | 콘텐츠 블록 | 도달률 집계 단위 |
| 표준 `id` | **필수** | 붙이지 않음 |
| `class="page-section"` | **필수** | 붙이지 않음 |
| `data-screen-id` | 있음 | 각각 있음 |
| `data-screen-name` | `{타이틀} {블록명}` | 자유 |
| `<main>` 직속 | 예 | 아니오 |

- 자식 태그는 `div` · `article` 무엇이든 됩니다. 플랫폼은 `data-screen-id` 속성만 봅니다.
- `data-screen-id`는 **문서 전체에서 유일**해야 합니다. `playbook_main`과 `playbook_01`처럼 접두어로 나눠두면 관리가 쉽습니다.
- 자식도 **실제로 스크롤 위치를 차지**해야 도달로 집계됩니다. `min-height: 100vh`를 주고 `position`은 `relative`로 둡니다. 같은 자리에서 내용만 교체되면 잡히지 않습니다.
- 부모에 `height` 고정이나 `overflow: hidden`을 걸면 뒤쪽 자식이 잘려 도달률이 0으로 찍힙니다.

```css
.pb-page {
  position: relative;   /* absolute · fixed 금지 */
  min-height: 100vh;    /* height 고정 금지 */
}
```

나누지 않으면 블록 하나가 화면 하나로 처리됩니다. 세분화해도 **완독률 수치는 달라지지 않습니다**.

### 버전을 올릴 때

- 같은 의미의 화면은 **같은 ID를 유지**합니다. 바뀌면 그 화면의 누적 도달 데이터가 끊깁니다.
- 의미가 달라진 화면에 **기존 ID를 재사용하지 않습니다**. 다른 내용이 한 화면으로 합산됩니다.
- 업로드 시 플랫폼이 이전 버전과 자동 대조해 **유지 / 신규 / 사라짐**을 검수 화면에 표시합니다.

---

## 3. 스크롤 — 브라우저에 맡깁니다

사용자는 **기본 세로 스크롤만으로** 마지막 블록까지 갈 수 있어야 합니다.

플랫폼은 스크롤에 따른 화면 진입을 감지해 **도달률을 집계하고, 현재 화면에 연결된 참여 패널을 띄웁니다.** 자체 로직으로 화면을 전환하면 **DOM은 그대로인 채 보이는 것만 바뀌므로** 플랫폼이 이동을 알지 못합니다.

### 금지

- `html` · `body` · `main`에 `overflow: hidden`
- 최상위 블록을 `position: absolute` / `fixed`로 겹치기
- `window` · `document`에 **wheel · touch · keydown 핸들러**를 걸어 페이지 이동을 제어
- 페이지 이동 목적의 `event.preventDefault()`
- `currentStep` 같은 값으로 블록을 보이고 숨기기

### 허용 — 블록 내부는 자유

클릭 전환 · 가로 슬라이드 · 스와이프 · 영상 재생 · 차트 탐색 · 컴포넌트 내부 스크롤 모두 됩니다.

**구분 기준은 하나입니다 — 페이지 전체의 세로 이동을 가로채는가.** 이벤트는 해당 컴포넌트에만 겁니다. 전역에 걸면 사용자가 **참여 패널 안에서 댓글을 스크롤하거나 입력할 때 페이지가 함께 움직입니다.**

### 권장

```js
// 진입 효과는 자체 상태 머신 대신 IntersectionObserver로
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => e.target.classList.toggle('is-visible', e.isIntersecting));
}, { threshold: 0.25 });

document.querySelectorAll('.page-section').forEach(el => io.observe(el));
```

플랫폼도 같은 방식으로 도달을 감지하므로 동작이 어긋나지 않습니다.

Scroll Snap을 쓴다면 `y proximity`까지만 권장합니다. `mandatory`는 긴 콘텐츠 탐색을 방해합니다.

---

## 4. 플랫폼이 덮는 영역 — 핵심 정보는 피하세요

콘텐츠 위에 플랫폼 UI가 겹칩니다. 해당 위치에 **핵심 정보나 조작 요소를 두지 않습니다**.
배경 · 사진 · 영상은 화면 끝까지 채워도 됩니다. 글 · 버튼처럼 가려지면 안 되는 것만 피합니다.

| 영역 | 위치 | 확보 |
|---|---|---|
| 타이틀 헤더 | 상단 | **80px** |
| 뒤로가기 | 좌측 상단 | 좌측 80px |
| 진행 레일 | 좌측 | 좌측 40px |
| 반응 바 | 하단 중앙 | 하단 **96px** |
| 공유 FAB | 우측 상단 | 96px |
| **참여 패널** | **우측 하단** | **약 340 × 420px** |

참여 패널이 가장 넓습니다. 접혀 있을 땐 작은 버튼이지만 펼치면 우측 하단이 덮입니다.

```css
.inner {
  padding: 80px 40px 96px;
  padding-left: 56px;                    /* 진행 레일 */
}

/* 우측 하단에 중요한 요소를 둬야 한다면 */
.key-visual { margin-right: 360px; }
```

### 해상도

| | 기준 |
|---|---|
| **제작 기준** | **1920 × 1080** (16:9) |
| **최소 지원** | **가로 1280px** (1280 × 768, 노트북 화면) |
| 모바일 · 태블릿 세로 | 대응 대상 아님 — 플랫폼이 안내 문구를 띄웁니다 |

1920 × 1080으로 만들고, **창을 가로 1280px까지 줄였을 때 잘리거나 겹치지 않는지** 확인하면 됩니다. 1280용 화면을 따로 만들 필요는 없고, **가로 폭만 유동**이면 충분합니다.

---

## 5. 패키지

```text
userstory.zip
├── index.html          필수 · 유일한 HTML 진입점
└── assets/             나머지 파일은 전부 이 안에
    ├── style.css       디자인
    ├── app.js          동작
    ├── playbook/       플레이북 이미지 · 영상 · 글꼴 (있을 때만)
    ├── scenariocanvas/ 시나리오 캔버스 이미지 · 영상 · 글꼴 (있을 때만)
    └── databook/       데이터북 이미지 · 영상 · 글꼴 (있을 때만)
```

- ZIP 최상위에는 **`index.html`과 `assets` 폴더만** 둡니다. 두 개를 함께 선택해서 압축합니다. 폴더째 압축해 ZIP 안에 폴더가 한 겹 더 생기면 업로드가 막힙니다.
- `assets` 안의 하위 폴더 이름과 나누는 방식은 자유입니다. 위 구조는 제공 템플릿 기준입니다.
- 파일 · 폴더 이름은 **영어 소문자 · 숫자 · `-` · `_`**로 짓습니다. 공백 · 한글은 운영체제에 따라 깨질 수 있습니다. 서버는 대소문자를 구분합니다.
- CSS · JS · 이미지는 **파일로 분리해도 됩니다.** "단일 HTML"은 진입점이 하나라는 뜻입니다.
- 경로는 **상대 경로**. `../`로 ZIP 바깥을 가리키지 않습니다.
  - `index.html` · `app.js` 안의 경로는 `index.html` 기준: `assets/playbook/p1.jpg`
  - `style.css` 안의 `url()`은 `style.css` 기준: `playbook/p1.jpg`
- 빌드 없이 **정적 서버에서 그대로 실행**되어야 합니다.
- ZIP 파일명은 ID나 버전과 무관합니다. 자유롭게 지으세요.

| 용량 | 한도 |
|---|---|
| ZIP 총 용량 | **50MB** (영상 포함) |
| 이미지 단건 | 400KB 권장 — 확정 한도는 별도 공지 |

폰트 · 아이콘 · 라이브러리는 **모두 ZIP에 포함**합니다. 외부 CDN에 의존하면 사내망에서 깨집니다.

---

## 6. 넣지 않는 것

플랫폼이 담당하므로 콘텐츠에 넣지 않습니다.

| 항목 | 담당 |
|---|---|
| 참여 UI 마크업 · SDK | 플랫폼이 패널로 렌더 |
| 타이틀 헤더 · 뒤로가기 · 진행 레일 | 플랫폼이 그림 |
| 반응 · 공유 FAB | 플랫폼이 그림 |
| 인증 · API 호출 · Firebase | 플랫폼 담당 |

**업로드가 차단되는 것**

- 외부 스크립트 · 외부 네트워크 호출 (CDN · API · iframe)
- `localStorage` · `sessionStorage`
- Service Worker
- 플랫폼 예약 class · 경로 (`.userstory-*`, `/userstory-sdk/*`)

브라우저 뒤로가기와 History도 임의로 바꾸지 않습니다.

---

## 7. 업로드 시 검사

### 자동 검증 5종 — 하나라도 실패하면 검수 요청 불가

| # | 규칙 |
|---|---|
| 1 | ZIP 최상위 `index.html` · 구조 준수 |
| 2 | 총 용량 50MB 이하 |
| 3 | 표준 `id`(`playbook` · `scenario-canvas` 필수) · `page-section` class · `main` 직속 · 중복 없음 |
| 4 | 금지 요소 없음 |
| 5 | 화면 식별자 존재 · 형식 준수 · 중복 없음 · 최상위 블록 이름이 `{타이틀} {블록명}` 형식 |

### 자가 체크 3종 — 사람이 확인

| # | 항목 |
|---|---|
| 1 | 금칙어 · 대외비 표기 없음 |
| 2 | 1920 × 1080에서 제작, 가로 1280px까지 줄여도 레이아웃 깨짐 없음 |
| 3 | **우측 하단 340 × 420px에 핵심 정보 없음** |

3번을 건너뛰면 게시 후 참여 패널이 중요한 내용을 가려 **콘텐츠를 다시 만들어야 합니다.**

---

## 8. 제출 전 확인

브라우저 콘솔에서 바로 확인할 수 있습니다.

```js
// 1. 최상위 블록 구성과 이름 — name이 「타이틀 + 블록명」인지 확인
const secs = [...document.querySelectorAll('main > .page-section')];
console.table(secs.map(s => ({ id: s.id, screen: s.dataset.screenId, name: s.dataset.screenName })));

// 2. 블록을 나눴다면 자식 화면 — top이 서로 다르고 h가 0이 아니어야 함
console.table([...document.querySelectorAll('.page-section [data-screen-id]')]
  .map(s => ({ screen: s.dataset.screenId, name: s.dataset.screenName,
               h: s.offsetHeight, top: s.offsetTop })));

// 3. 식별자 중복
const ids = [...document.querySelectorAll('[data-screen-id]')].map(el => el.dataset.screenId);
console.log('중복:', ids.filter((v, i) => ids.indexOf(v) !== i));

// 4. 전역 핸들러 (wheel · touchmove · keydown 이 있으면 점검)
getEventListeners(window);
getEventListeners(document);
```

**눈으로 확인**

- 휠 · 트랙패드 · Page Down · 터치로 처음부터 끝까지 이동된다
- 화면이 바뀔 때 **`window.scrollY`가 실제로 변한다** — 같은 자리에서 내용만 교체되면 도달로 집계되지 않습니다
- 마지막 블록 이후, 첫 블록 이전에 갇히지 않는다
- 내부 인터랙션을 쓴 뒤에도 다음 블록으로 넘어간다
- 가로 1280px까지 줄여도 잘리거나 겹치지 않는다
- 우측 하단이 가려져도 내용을 이해할 수 있다
- 콘솔 오류와 asset 404가 없다

---

## 9. 최종 체크리스트

**패키지**

- [ ] ZIP 최상위에 `index.html`과 `assets` 폴더만 있다 (폴더가 한 겹 더 있지 않다)
- [ ] 파일 · 폴더 이름이 영어 소문자 · 숫자다 (공백 · 한글 없음)
- [ ] 모든 경로가 상대 경로이고 외부 CDN에 의존하지 않는다
- [ ] 빌드 없이 정적 서버에서 실행된다
- [ ] ZIP 총 용량 50MB 이하
- [ ] `meta.json` · 참여 UI · SDK · 자체 헤더가 없다

**구조**

- [ ] `playbook`과 `scenario-canvas`가 있다
- [ ] 콘텐츠 블록이 표준 순서(플레이북 → 시나리오 캔버스 → 데이터북)로 `main` 직속에 있다
- [ ] 데이터북이 없다면 데이터북 블록을 통째로 지웠다
- [ ] 모든 최상위 블록에 `class="page-section"`이 있다
- [ ] 표준 `id`가 한 번씩만 쓰였다
- [ ] 모든 화면에 `data-screen-id`와 `data-screen-name`이 있다
- [ ] 최상위 블록의 `data-screen-id`가 고정값(`playbook_main` · `canvas_main` · `databook_main`) 그대로다
- [ ] `data-screen-id`가 중복되지 않고 40자 이내다
- [ ] 최상위 블록 3종의 `data-screen-name`이 `{타이틀} {블록명}` 형식이다
- [ ] 블록을 나눴다면 자식에 `page-section`과 표준 `id`를 붙이지 않았다
- [ ] 버전 업데이트라면 같은 화면의 ID를 유지했다

**스크롤**

- [ ] 기본 세로 스크롤로 모든 블록에 접근된다
- [ ] `overflow: hidden`으로 막지 않았다
- [ ] 최상위 블록을 absolute/fixed로 겹치지 않았다
- [ ] `window` · `document`에 전역 핸들러가 없다
- [ ] 화면이 바뀔 때 `window.scrollY`가 변한다

**레이아웃**

- [ ] 1920 × 1080으로 만들었고, 가로 1280px까지 줄여도 깨지지 않는다
- [ ] 상단 80px · 좌측 40px · 하단 96px에 핵심 정보 · 조작 요소가 없다
- [ ] 우측 하단 340 × 420px에 핵심 정보가 없다

**내용**

- [ ] 금칙어 · 대외비 표기를 확인했다
- [ ] 최상위 블록의 타이틀 표기가 실제 유저스토리 타이틀과 일치한다
- [ ] 블록 내부 화면의 `data-screen-name`이 리포트에서 읽히는 이름이다

---

## 10. AI에게 한 번에 맡기기 — 요청문

파일을 만들어 내려받게 해 주는 AI(Claude · ChatGPT 등)에 **세 가지를 한꺼번에 첨부**하고, 아래 글을 복사해 보냅니다. `[ ]` 안만 채우면 됩니다.

| 첨부 | 내용 |
|---|---|
| ① 가이드 | 이 문서 (`04_TEMPLATES_GUIDE_v0824.md`) |
| ② 템플릿 | `userstory_template.zip` |
| ③ 내 작업물 | 플레이북 · 시나리오캔버스 · 데이터북(있다면). HTML · CSS · JS · 이미지 · 글꼴 — 폴더째 압축해서 올려도 됨 |

```
첨부한 파일로 UserStory에 올릴 ZIP 파일을 완성해서, 내려받을 수 있게 줘. 유저스토리 제목은 [유저스토리 제목]이야.

- 첨부한 가이드(.md)가 규칙이야. 끝까지 읽고 그대로 따라줘. 이 요청과 가이드가 다르면 가이드를 따라줘.
- 첨부한 템플릿(.zip)의 index.html · assets 구조를 그대로 쓰고, ‘붙여넣기’ 표시 자리만 채워줘. 나머지 첨부는 내가 만든 플레이북 · 시나리오캔버스 · 데이터북(있다면)이야. 어느 게 뭔지 헷갈리면 시작 전에 물어봐.
- 플레이북 → 시나리오캔버스 → 데이터북 순서로 넣어줘. 이미지 한 장짜리는 <img>로 넣고, 데이터북이 없으면 ✂ 표시 사이를 통째로 지워줘.
- CSS는 assets/style.css, JS는 assets/app.js로 합치되 이름이 서로 겹치지 않게 해줘. 이미지 · 영상 · 글꼴은 assets/playbook · scenariocanvas · databook에 나눠 담고 경로를 고쳐줘. 새 파일 · 폴더 이름은 영어 소문자 · 숫자로 해줘.
- data-screen-id는 템플릿 값 그대로 두고, data-screen-name은 ‘가족을 위한 두 번째 차’ 부분만 위 제목으로 바꿔줘.
- 가이드가 금지한 것(인터넷 주소로 불러오기, 유튜브 같은 끼워넣기, 고정 헤더 · 메뉴, localStorage, 한 장씩 넘기는 스크롤 등)은 빼거나 고치고, 연출이 달라진 곳은 알려줘.
- 화면은 1920 × 1080 기준으로, 가로 1280까지 줄여도 안 깨지게 해줘. 글 · 버튼은 위 80px, 아래 가운데 96px, 오른쪽 아래 340 × 420px에 걸리지 않게 해줘.
- 다 만들면 스스로 검사해줘. 가이드의 ‘7. 업로드 시 검사’와 ‘9. 최종 체크리스트’를 하나씩 보고, index.html이 부르는 파일이 ZIP 안에 다 있는지, 인터넷 주소가 남지 않았는지 확인해줘. 틀린 건 고친 뒤에 줘.
- ZIP은 열자마자 index.html과 assets가 보이게(폴더 한 겹 없이), 50MB 이하로 묶어줘.
- 마지막에 ① ZIP 파일 ② 바꾼 내용 ③ 첨부에 없어서 못 넣은 파일 ④ 내가 브라우저로 직접 확인할 것을 알려줘. 파일을 만들어 줄 수 없는 환경이면 시작 전에 먼저 말해줘.
```

받은 ZIP은 풀어서 `index.html`을 브라우저로 열어 보고, 8장 ‘제출 전 확인’대로 점검합니다. AI가 ‘못 넣은 파일’을 알려주면 그 파일을 첨부해 다시 요청합니다.

---

## 부록 · v0824 원본 대비 바뀐 점

| 항목 | 내용 |
|---|---|
| 표지 | 표지 블록(`cover`)을 뺌. 썸네일은 플랫폼에 따로 올림. 콘텐츠 블록은 플레이북 · 시나리오 캔버스 · 데이터북 3종 |
| 최소 템플릿 | 제공 템플릿(`userstory_template.zip`)과 같게 맞춤 — 붙여넣기 표시 줄, 데이터북 자리(없으면 삭제), `app.js` 추가 |
| 패키지 | ZIP 최상위는 `index.html` + `assets`만 (README 제외). 파일 · 폴더 이름 규칙, 경로 기준 추가 |
| 플랫폼이 덮는 영역 | 배경은 채워도 되고 핵심 정보 · 조작 요소만 피한다는 기준으로 표현 정리 |
| 해상도 | 제작 기준 1280 × 768 → **1920 × 1080**, 최소 지원 1024px → **가로 1280px** |
| AI 요청문 | 10장 추가 — 가이드 · 템플릿 · 작업물을 한꺼번에 첨부하면 AI가 업로드용 ZIP까지 만들고 스스로 검사 |
