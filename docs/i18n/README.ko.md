# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo는 운송업체용 데스크톱 프로그램으로 직원과 차량, 일정과 근무시간, 운행일지, 명령서, 문서, 정비, 보고서와 백업을 관리합니다.

## Stable 10.23-r4

**10.23-r4는 2026년 11월 20일 소유자가 직접 확인했으며 Stable/Latest입니다.** 문서 검색·필터·정렬, 유형/날짜 트리, 중첩 사용자 폴더, 관리되는 Word 개정판, PDF/인쇄, DocumentVault, 선택적 종이 원본 스캔과 별도의 종이 서명 상태를 포함합니다. 명령서는 명시적 운전자–차량 쌍, 기존 쌍 편집, 참여자의 역할/메모 편집, 검색 중에도 유지되는 다중 선택을 지원합니다. 문서 작업 영역과 카탈로그 트리 너비를 조절할 수 있습니다. 명령서 미리보기의 DOCX/PDF/JPG 작업은 760×560의 좁은 창에서도 접근 가능합니다.

37개의 엄격한 live UI 경로가 표시 여부, 화면 내 위치, 사용 가능 상태와 실제 활성화를 검사합니다. START, Windows, Windows 7, macOS Intel/Apple Silicon 검사가 성공했으며 Windows/Win7은 Defender와 무결성 검사도 통과했습니다. 전체 기능 완전 커버리지(#556)와 더 넓은 명령서 end-to-end 감사(#553)는 계속 진행 중입니다.

## 다운로드

**Stable / Latest: [Taxo 10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).** 이전 안정 버전: [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/SHA256SUMS_v10_23_r4.txt)

**Current Test:** [Taxo 10.23-r8](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r8), 8개 파일 prerelease, exact source `d3d34f7a0fc3de88280324eaeb2d97a72c172359`. 관리되는 import batch를 검증하고 날짜, 번호, category/kind, source fallback 기준의 결정적 read-only sorting preview를 생성합니다. 빈 값은 뒤로 보내고 번호는 natural sort를 사용하며 stable identity가 최종 tie-breaker입니다. OCR, AI APPLY, 물리 파일 정렬은 하지 않으며 Stable/Latest는 10.23-r4 그대로입니다.

데이터베이스와 문서는 별도 작업 폴더에 보관하고 업데이트 전에 백업하세요. [사용 설명서(우크라이나어)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

개발: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). 모든 권리 보유. [LICENSE](../../LICENSE.md).
