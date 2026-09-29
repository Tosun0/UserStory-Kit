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
- [부품 양식](plugins/userstory-kit/assets/components): 영상형 플레이북, 카드형 시캔, 이미지형 플레이북·세로형 시캔 공통 img
- [조립·정적 검사기](plugins/userstory-kit/scripts/userstory.py): 폴더 제작 `build`, 읽기 전용 검사 `audit`, 별도 ZIP 포장 `package` (Python 표준 라이브러리)
- [제작 태스크](plugins/userstory-kit/tasks/build.md) / [검수 태스크](plugins/userstory-kit/tasks/audit.md) / [ZIP 포장 태스크](plugins/userstory-kit/tasks/package.md): 제작·직접 화면 검수 후 요청 시 포장

## 사용

Codex에 플러그인을 설치한 뒤 새 대화에서 다음 스킬을 사용합니다.

| 표시명 | 호출명 | 역할 |
|---|---|---|
| [00. 총괄](plugins/userstory-kit/skills/00-userstory/SKILL.md) | `$00-userstory` | 입력 확인·전체 조립·직접 화면 검수. ZIP은 요청 시 별도 포장, 검수만 요청하면 읽기 전용 |
| [01. 플레이북](plugins/userstory-kit/skills/01-playbook/SKILL.md) | `$01-playbook` | 사용자 HTML 이관 또는 영상/이미지 조립. 원본 인터랙션·게임·분기·재생 조작 유지 |
| [02. 시나리오 캔버스](plugins/userstory-kit/skills/02-scenariocanvas/SKILL.md) | `$02-scenariocanvas` | 카드/세로형 시캔의 배치·전환·인디케이터 |
| [03. 데이터북](plugins/userstory-kit/skills/03-databook/SKILL.md) | `$03-databook` | 선택 데이터북 조립 또는 전체 블록 삭제 |

전체 제작은 총괄로 시작하고, 특정 블록만 바꿀 때는 해당 스킬을 사용합니다. 블록 스킬은 다른 블록을 재생성하지 않습니다. 검수는 총괄의 후속 태스크로 유지하며 별도 중복 스킬은 두지 않습니다.

기본 제작은 콘텐츠 폴더를 만든 뒤 에이전트가 로컬 HTTP로 직접 열어 화면·동작을 검수하고 결과를 보고하는 데까지입니다. ZIP은 자동 생성하지 않습니다. ZIP 포장을 요청하면 검수된 폴더를 별도 포장 태스크에서 묶고 다시 검사합니다. 검수 캡처·상세 보고서는 임시 경로에 보관합니다.

원본 템플릿은 그대로 보관하고 별도 출력 사본에만 작성합니다. Git에서 사라지는 빈 리소스 폴더는 제작 태스크가 복원합니다. 생성한 콘텐츠·검수 캡처·ZIP은 이 플러그인 원본에 섞지 않습니다.

플러그인 소스를 갱신한 뒤 Git 설치본 갱신은 사용자가 진행합니다. 개인 설정이나 캐시를 별도로 덮어쓰지 않습니다. 제작 GUI나 자동 빌드 서버는 포함하지 않습니다.

## 양식 출처와 정리

| 부품 | 가져온 기준 | 정리한 부분 |
|---|---|---|
| 카드 시캔 | `Hyundai_UserStory_Card`와 현재 Tech의 SC 코드 | 크기·전환·숫자 캡슐 유지. 플레이북·헤더·History·스크롤 자동 스냅·모바일 규칙 제거. 시캔 자체 코드만 포함 |
| 세로형 / 이미지 | `Hyundai_UserStory_Journal`과 현재 Tech의 이미지 배치 | 원본 비율·중앙·자연 스크롤을 공통 img로 구현. 정적 이미지에 SVG 로더·Lottie를 붙이지 않음 |
| 영상 플레이북 | 현재 `Hyundai_UserStory_14px_Photo`의 재생 UI | 시작 캡슐·중앙 조작·볼륨 UI 재사용. 고정 조작을 블록 내부 배치로 변경하고 종료 후 중앙 다시보기 유지. 자동 페이지 이동·전역 음소거 해제·별도 시캔 상태 제거 |

형식별 본문은 제공된 새 전달 템플릿의 붙여넣기 슬롯에 넣습니다. 원본 가이드·기준 템플릿은 보존합니다. 영상은 잘리지 않도록 contain을 사용하므로 원본 비율에 따라 여백이 생깁니다. 볼륨은 좌측 56px·하단 112px로 플랫폼 UI를 피합니다. 카드 크기는 기존 `min(가로−80px, 세로−208px, 1080px)`를 공유합니다.

순수 미디어의 입력 JSON과 실행 명령은 [제작 태스크](plugins/userstory-kit/tasks/build.md)에 있습니다. 완성 영상 한 파일, 이미지/카드/세로형 한 장 이상, 선택 이미지 데이터북을 자동 조립합니다. 사용자 HTML은 [HTML 이관 태스크](plugins/userstory-kit/tasks/playbookhtml.md)로 본문·CSS·JS·로컬 의존 리소스를 옮깁니다. 플레이북은 고정 양식이 아니므로 게임·인터랙션·영상 분기를 영상/이미지 부품으로 대체하지 않습니다. CLI는 순수 미디어 전용이고, 작성된 HTML·PDF 등은 해당 블록 스킬이 원본 기능을 보존해 조립합니다.

플러그인 루트에서 `python scripts/test_userstory.py`를 실행하면 8가지 조합과 누락·대소문자·외부 참조·중복 식별자·스토리지·스크롤 가로채기·ZIP 탈출·덮어쓰기 거부를 확인합니다. 자동 정적 검사는 실호스팅, 미디어 재생, 실제 플랫폼 검수와 구분됩니다.
