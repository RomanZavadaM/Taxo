# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo는 단일 운송 회사를 위한 데스크톱 시스템입니다: 직원 및 운전자, 근무표, 근무 시간 관리, 운행일지, 활동 확인서, 차량, 문서 관리, 정비, 보고서 및 아날로그 타코그래프 점검.

> **안정 버전:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 2026-10-05
> **이전 안정 버전 / 롤백:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **다음 코드 리비전:** `10.10-r4`

## 다운로드 — Taxo 10.10 (안정 버전)

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/SHA256SUMS_v10_10.txt) · [10.10 릴리스 노트 (우크라이나어)](../releases/RELEASE_NOTES_v10_10.md) · [릴리스 색인](../releases/RELEASE_INDEX.md)

업무 데이터베이스, SQLite 파일, 스캔, 캐시 및 개인 문서는 GitHub 릴리스에 포함되지 않습니다. 업데이트 시 업무 데이터를 다시 입력할 필요가 없습니다.

## 10.10의 새로운 기능

- **PyMuPDF 제거.** 활동 확인서(PDF/JPG), 340호 보고서 날짜 스탬프, PDF 보기/인쇄가 허용적 라이선스 라이브러리(pypdfium2, reportlab, pypdf)로 동작하며, 결과는 이전 버전과 픽셀 단위로 동일합니다.
- **올바른 버전 표시** — 창 제목, 정보 창, PDF 머리글, 백업 매니페스트.
- **백업**이 데이터베이스만 포함할 때 명확히 경고합니다.
- **인프라:** 오래된 배포 워크플로 비활성화, 테스트를 업무 저장소와 격리, 모든 빌드에 라이선스 검사.
- 10.4 … 10.9 전체 라인 포함: 운행 전체 기간의 차량 문서 유효성, 발행된 운행일지와 번호 보호, 강화된 근무/휴식 통제, 60일 등록부, 인력 균형, 정비, 서명된 명령의 불변성, SQLite 스키마 호환성.

## 주요 기능

직원 및 운전자 이력; 개인별·주기적 근무표; 계획/실적 근무 시간과 분할 근무; 근무·운전·휴게·휴식 통제; 60일 활동 등록부; 차량, 주행거리, 정비 및 문서; 정기·비정기 운행일지; 활동 확인서; 아날로그 타코그래프 점검; 보호된 명령과 운전자→차량 배정; PDF/Excel 보고서; 백업 및 SQLite 호환성 관리.

## 개발

공식 운영 문서는 우크라이나어로 관리됩니다. [`START_HERE.md`](../../START_HERE.md)에서 시작하세요. 안정 버전 10.10 이후 새 코드는 현재 `main`에서 `10.10-r4`로 시작합니다. 발행된 리비전은 변경되지 않습니다.

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo는 독점 소프트웨어입니다.
