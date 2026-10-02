# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo는 하나의 운송 사업체를 위한 데스크톱 시스템입니다. 운전자와 직원, 근무표, 근로시간표, 운행기록지, 활동 확인서, 차량, 문서 관리, 보고서, 정비 관리 및 아날로그 타코그래프 디스크 확인을 다룹니다.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
> **`main`의 최신 통합 체크포인트:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **최신 전체 멀티플랫폼 체크포인트:** [Taxo 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1)  
> **이전 stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1)  
> `v10.9-r9`는 자동으로 stable이 되지 않습니다. stable 승격은 소유자의 별도 결정입니다.

## 다운로드

### 최신 통합 체크포인트 — 10.9-r9

[START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/SHA256SUMS_v10_9_r9.txt) · [Release 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)

10.9-r9는 최신 통합 코드 체크포인트이며 START 패키지가 제공됩니다. r9용 전체 실행 파일 세트는 별도로 다시 배포하지 않았습니다.

### 최신 전체 멀티플랫폼 체크포인트 — 10.9-r1

[Windows/macOS 패키지가 포함된 Release 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) · [Combined SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r1/SHA256SUMS_v10_9_r1_ALL.txt)

일반 사용에는 `v10.9-r1`의 준비된 Windows/macOS 패키지를 사용하십시오. `START.bat`은 주로 테스트와 기술 진단용입니다.

사용자 DB, SQLite 파일, 스캔, 캐시 및 개인 문서는 GitHub release에 포함되지 않습니다.

## 주요 기능

- 직원/운전자 등록부와 역할 이력;
- 개별 및 주기적 운전자 근무표;
- 계획과 실제를 구분하는 근로시간표와 분할 근무;
- 근로, 운전, 휴게 및 휴식 관리;
- 알 수 없는 시간을 임의로 휴식으로 만들지 않는 60일 활동 기록;
- 차량, 주행거리, 정비 및 차량 문서 관리;
- 정규/비정규 운행기록지;
- 개정 이력이 있는 활동 확인서;
- 아날로그 타코그래프 디스크 수동 검증;
- 승인/서명된 운영 명령과 운전자→차량 배정 이력 보호;
- PDF/Excel 보고서;
- 백업, 작업공간 이전 및 SQLite 스키마 호환성 관리.

## 10.9-r2 → 10.9-r9에 통합된 내용

발행된 운행기록지 번호 이력 보호, 전체 운행기간 차량 문서 유효성 검사, 근로/휴식 규칙 강화, 실제 데이터 소스 우선순위 안전화, 직원/P-5 이력 보정, 주행거리 및 정비 예측 강화, 승인/서명된 명령의 불변성, `PRAGMA user_version` 기반 SQLite 스키마 기준선이 포함됩니다.

자세한 내용: [10.9-r9 release notes](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [release index](docs/releases/RELEASE_INDEX.md)

## 개발 상태

운영 문서의 기준 언어는 우크라이나어입니다. 새 개발/복구 세션은 `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61 순서로 확인합니다. 발행된 revision은 변경하지 않습니다. `10.9-r9` 다음 코드 revision은 **10.9-r10**입니다.

## 저작권 및 라이선스

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo는 proprietary software입니다. 공개 저장소라는 사실만으로 오픈소스 라이선스나 재배포, 판매, 수정본/파생본 배포 권한이 부여되지 않습니다.

[LICENSE.md](LICENSE.md) · [COPYRIGHT.md](COPYRIGHT.md) · [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
