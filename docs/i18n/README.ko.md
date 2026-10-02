# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md)

Taxo는 하나의 운송 사업체를 위한 데스크톱 시스템입니다. 운전자와 직원, 근무표, 근로시간, 운행기록지, 활동 확인서, 차량, 문서, 정비, 보고서, 아날로그 타코그래프를 다룹니다.

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
> **`main`에 통합된 최신 checkpoint:** **Taxo 10.9-r10**  
> **최근 공개된 전체 멀티플랫폼 release:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **다음 코드 revision:** `10.10-r1`

`10.9-r10`은 이미 `main`에 통합되었지만 별도의 전체 공개 멀티플랫폼 release로 게시되지는 않았습니다. 바로 사용할 수 있는 Windows/macOS 패키지는 `v10.9-r9`를 사용하십시오.

## 다운로드 — 10.9-r9

**Windows 10/11:** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip)

**Windows 7 SP1:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**테스트/소스:** [START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [10.9-r10 release notes](../releases/RELEASE_NOTES_v10.9-r10.md) · [Release index](../releases/RELEASE_INDEX.md)

사용자 DB, SQLite 파일, 스캔, 캐시 및 개인 문서는 GitHub release에 포함되지 않습니다.

## 10.9-r10 변경 사항

비즈니스 로직을 변경하지 않고 저장소 구조를 정리했습니다. runtime 모듈은 `src/taxo/`, 템플릿은 `assets/`, 활성 packaging 정의는 `packaging/`으로 이동했습니다. 사용자 데이터 마이그레이션은 도입되지 않았습니다.

## 주요 기능

직원/운전자 이력, 개별/주기적 근무표, 계획/실제 및 분할 근무, 근로·운전·휴게·휴식 관리, 60일 활동 기록, 차량·주행거리·정비·문서, 운행기록지, 활동 확인서, 아날로그 타코그래프, 보호된 명령 및 운전자→차량 배정, PDF/Excel 보고서, 백업 및 SQLite 호환성 관리.

## 개발

기준 운영 문서는 우크라이나어로 유지됩니다. 시작점: [`START_HERE.md`](../../START_HERE.md). `10.9-r10` 이후 새 코드 작업은 현재 `main`에서 `10.10-r1`로 시작합니다. 발행된 revision은 변경하지 않습니다.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo는 proprietary software입니다.
