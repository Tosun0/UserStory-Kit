# UserStory-Kit

유저스토리 키트는 제공된 가이드와 템플릿으로 콘텐츠를 제작·검수하는 Codex 플러그인입니다.

## Git으로 추가

Codex의 Git 마켓플레이스 추가 화면에서 `https://github.com/Tosun0/UserStory-Kit.git`을 입력한 뒤, 목록의 **유저스토리 키트**를 설치합니다.

저장소 루트의 [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json)이 Git 등록용 목록이며, 플러그인 본체는 [plugins/userstory-kit](plugins/userstory-kit/.codex-plugin/plugin.json)에 있습니다. 등록 파일의 `source.path`는 저장소 루트를 기준으로 해석합니다.

개인 마켓플레이스 등록이나 별도의 로컬 소스 설치는 필요하지 않습니다.

## 구성

- [에이전트 지침](plugins/userstory-kit/AGENTS.md): 제작 규칙과 원본 가이드 우선순위
- [원본 가이드](plugins/userstory-kit/references/guidev0929.md): v0929 전달본, 문서 내부 표제는 v0824 유지
- [기준 템플릿](plugins/userstory-kit/assets/template/index.html): index.html 및 assets 구조
- [제작 태스크](plugins/userstory-kit/tasks/build.md) / [검수 태스크](plugins/userstory-kit/tasks/audit.md): 조립·검수·ZIP 전달 절차

## 사용

Codex에 플러그인을 설치한 뒤 새 대화에서 다음 스킬을 사용합니다.

- `$userstory-build`: 제목, 영상/이미지 플레이북, 카드/세로형 시나리오 캔버스, 선택 데이터북과 출력 위치를 전달해 제작합니다.
- `$userstory-audit`: 제작된 폴더 또는 ZIP을 가이드 7장·9장과 대조하여 검수합니다. 검수만 요청하면 코드를 변경하지 않습니다.

원본 템플릿은 그대로 보관하고 별도 출력 사본에만 작성합니다. Git에서 사라지는 빈 리소스 폴더는 제작 태스크가 복원합니다. 생성한 콘텐츠·검수 캡처·ZIP은 이 플러그인 원본에 섞지 않습니다.

플러그인 소스를 갱신하면 설치본도 갱신하고 새 대화에서 확인합니다. 현재 키트는 스킬·태스크·양식 묶음이며, 별도의 제작 GUI나 자동 빌드 서버는 포함하지 않습니다.
