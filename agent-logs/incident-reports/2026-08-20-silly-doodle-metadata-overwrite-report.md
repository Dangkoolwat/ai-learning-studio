# 사고 보고서: Silly Doodle 프롬프트 메타데이터 덮어쓰기 및 누락

## 1. 사고 개요

- **사고 발생 일시**: 2026-08-20 16:30 (KST)
- **사고 대상 파일**: [silly-doodle.md](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/pages/sections/image-ai/silly-doodle.md)
- **사고 현상**: 프롬프트 가독성 정돈(마크다운 줄바꿈 및 리스트 마커 일원화) 작업을 수행하는 과정에서, 사용자가 직전 커밋(`7f80907`)에서 수동으로 수정/보완해 두었던 Frontmatter 내 다중 이미지 프리뷰(`preview`)와 원작자 출처(`source`) 정보가 에이전트의 speculative edit로 인해 누락되고 초기 생성본(`89d7e9b`) 데이터로 덮어씌워짐.

---

## 2. 원인 분석

1. **Read-Before-Write (사전 확인 규칙) 미비**
   - 수정을 propose 하기 전, 단순히 이전 에이전트로부터 전달받은 최초 생성 시점의 skeleton 데이터를 맹신하여 작업을 진행했습니다.
   - 대상 소스 파일의 최근 git 커밋 내역(`git log -p`)이나 로컬 변경 히스토리를 1 depth 더 들어가 대조하지 않아 사용자의 중간 수동 개입본을 감지하지 못했습니다.
2. **이전 세션 핸드오프(Handoff) 인계 기록 누락**
   - 이전 에이전트가 남겨둔 context/handoff 상에 사용자의 preview/source 추가 조치 기록이 기술되어 있지 않아, 에이전트가 단독으로 마크다운 파일을 정돈할 때 이를 발견하지 못하고 초기 상태를 기준으로 변경을 덮어썼습니다.
3. **메타데이터 정합성 자동 검증 누락**
   - 4각 설명문(description)의 일치 여부는 파이썬 진단기(`audit_prompts.py`)를 통해 기계적으로 검증했으나, `preview` 및 `source` 같은 부가 메타데이터의 변경 누락 여부는 별도의 검증 단계가 부재하여 배포 직전까지 오염 사실을 인지하지 못했습니다.

---

## 3. 조치 결과

1. **역추적 및 복원**
   - `git log -L` 및 `git show` 명령어를 구동해 사용자가 최종적으로 보완했던 `7f80907` 커밋 내의 Frontmatter 메타데이터 값을 안전하게 추출하여 [silly-doodle.md](file:///Users/sanghyoukjin/DongguramiProjects/AI%20Learning%20Studio/pages/sections/image-ai/silly-doodle.md)에 그대로 1:1 복원 적용했습니다.
     - **복원된 preview**: `/assets/images/image-ai/silly-doodle/preview.jpg, /assets/images/image-ai/silly-doodle/preview2.png, /assets/images/image-ai/silly-doodle/preview3.png`
     - **복원된 source**: `Threads (@ah_g_moo, @_0.beomi_)`
2. **정적 빌드 검증**
   - 복원 완료 후 `python3 scripts/build.py` 를 재구동하여 웹 정적 컴파일 및 배포판 정상 빌드를 완료했습니다. (Exit Code: 0)
3. **원격 저장소 배포**
   - 사용자의 명시적인 push 지시 승인을 득한 후, 복구된 소스 코드를 깃허브 원격 main 브랜치에 안전하게 최종 반영 완료했습니다. (`e6de460`)

---

## 4. 재발 방지 대책

1. **수정 전 Git 히스토리 대조 절차의 강제 의무화**
   - 향후 마크다운이나 설정 파일 등 사용자가 직접 관여하기 쉬운 리소스를 에디팅할 때는, Propose 전에 반드시 `git log -p -n 3 {파일명}` 또는 `git diff HEAD~1` 을 수행하여 사용자가 중간에 수동 수정한 이력이 존재하는지 교차 대조하는 검증 단계를 의무적으로 밟겠습니다.
2. **핸드오프 문서화 엄격화**
   - 세션 전환이나 중단 시점에 생성되는 `HANDOFF.md` 내에 단순 skeleton 생성 사항 외에도 사용자가 수동 개입해 변경한 부가 리소스(이미지 파일, 부가 속성 등)에 대한 이력을 구체적인 리스트로 명문화하겠습니다.
3. **진단기 검증 로직 확장**
   - `audit_prompts.py`에 프롬프트 description 외에도 `preview` 이미지의 경로 존재 여부 및 `source` 데이터의 유무도 함께 스캔하여 누락 시 에러를 뿜는 검증 장치를 보강하겠습니다.
