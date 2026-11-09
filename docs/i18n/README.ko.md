# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

> **안정 버전:** [Taxo 10.14-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.14-r4) · 09.11.2026 · Windows 10/11, Windows 7, macOS Intel / Apple Silicon, START verified.
> **이전 안정 버전 / 롤백:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10).

## 다운로드 — 10.14-r4

**Windows 10/11 x64:** [설치 파일](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Setup_Windows_x64.exe) · [포터블](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [설치 파일](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Setup_Windows7_x64.exe) · [포터블](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_macOS_x86_64_Portable.zip)

**소스 / 체크섬:** [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/Taxo_v10_14_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.14-r4/SHA256SUMS_v10_14_r4.txt) · [Release notes (UK)](../releases/RELEASE_NOTES_v10.14-r4.md).

## 10.12-r10 이후 주요 변경 사항

운영 및 정비 화면 개선, 운전자·차량 복수 지정, 인사 및 업무 명령 번호 분리, 문서 미리보기, 편집 가능한 Word와 PDF/JPG, 일관된 표와 서식.

Taxo의 명령서는 업무 보조 문서입니다. 상태나 종이 서명 표시로 수정·삭제가 제한되지 않습니다. 공식 종이 원본은 사용자가 관리합니다.

업무 데이터베이스, 스캔, 개인 문서, 캐시는 배포 파일에 포함되지 않습니다. 업데이트 전에 백업하세요.

## 문서 및 개발

공식 운영 설명서는 우크라이나어로 제공됩니다. 빠른 시작과 운영·정비 안내서를 참조하세요. 다음 코드 개정은 10.14-r5입니다.

[Quick Start / Швидкий старт](../guides/QUICK_START.md) · [Operations & Maintenance / Експлуатація](../guides/OPERATIONS_STOIR_GUIDE.md) · [Release Index](../releases/RELEASE_INDEX.md) · [Current State](../../PROJECT_STATE.md).

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo is proprietary software.

## 시험 후보 10.15-r3 — 안전교육 및 운전자 실습 문서

안전교육은 여러 CSV 파일 대신 전체 교육 내용과 별도 자필 서명지가 포함된 편집 가능한 DOCX를 생성합니다. 운전자 실습 기록지와 작업 공간에 저장된 Word 문서를 검색하는 목록도 추가되었습니다(전체 백업에 포함). 문서 생성은 교육 실시, 서명 또는 운행 승인으로 간주하지 않습니다. 선택적 서명본 스캔과 계층형 문서 목록은 별도 작업(#289), Python 모듈 분리는 #290입니다. 안정 버전은 여전히 10.14-r4입니다.
