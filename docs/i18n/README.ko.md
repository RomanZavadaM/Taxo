# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo는 단일 운송 회사를 위한 데스크톱 시스템입니다: 직원 및 운전자, 근무표, 근무 시간 관리, 운행일지, 활동 확인서, 차량, 문서 관리, 정비, 보고서 및 아날로그 타코그래프 점검.

> **안정 버전:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10) — 실제 데이터로 검증됨
> **이전 안정 버전 / 롤백:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **테스트 라인:** [10.10-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) (사전 릴리스, 실제 데이터로 검증 중)

## 다운로드 — Taxo 10.9-r10 (안정 버전)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [10.9-r10 릴리스 노트 (우크라이나어)](../releases/RELEASE_NOTES_v10.9-r10.md) · [릴리스 색인](../releases/RELEASE_INDEX.md)

업무 데이터베이스, SQLite 파일, 스캔, 캐시 및 개인 문서는 GitHub 릴리스에 포함되지 않습니다. 업데이트 시 업무 데이터를 다시 입력할 필요가 없습니다.

## 안정 버전 10.9-r10 내용

- 발행된 운행일지와 번호의 영구 이력; 보존 기간 정리가 연결된 사실을 삭제하지 않음
- 계획된 운행 전체 기간의 차량 문서 유효성
- 강화된 근무/휴식 통제: 중복, 3+9, 주간 및 2주 휴식
- 가공된 휴식 없는 60일 등록부; 실제 출처 우선
- 인력 균형 / P-5, 2/2 및 3/3 근무 체계
- 정비: 주행거리 기록 순서와 정비 예측
- 승인/서명된 명령과 운전자→차량 배정의 불변성
- SQLite 스키마 호환성 관리
- 업무 로직 변경 없는 코드 구조화

## 테스트 버전 (안정 버전 아님)

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) 은 실제 데이터 검증용 사전 릴리스입니다: PyMuPDF 제거, 창에 올바른 버전 표시, DB 전용 백업 경고, CI 강화. 소유자의 검증 후에만 안정 버전이 됩니다.

## 개발

공식 운영 문서는 우크라이나어로 관리됩니다. [`START_HERE.md`](../../START_HERE.md)에서 시작하세요. `main`의 코드는 10.10 테스트 라인이며 다음 코드 리비전은 `10.10-r4`입니다.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo는 독점 소프트웨어입니다.
