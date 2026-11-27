# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo는 운송업체용 데스크톱 프로그램으로 직원과 차량, 일정과 근무시간, 운행일지, 명령서, 문서, 정비, 보고서와 백업을 관리합니다.

## 이전 Stable 10.24-r3

**10.24-r3는 2026년 11월 23일 소유자의 명시적 결정으로 Stable/Latest로 승격되었습니다.** 10.23-r4의 승인된 기능에 더해 r1–r3 서신 기능이 포함됩니다. 수신/발신 저널, 안전한 번호 부여, 제어 첨부, 검색, 날짜/달력, 정렬 가능한 표, 서신 카드, 새 서신·답변·첨부·문서 열기 기능을 제공합니다. 발송일이 비어 있으면 실제 발송으로 간주하지 않습니다.

37개의 엄격한 live UI 경로가 표시 여부, 화면 내 위치, 사용 가능 상태와 실제 활성화를 검사합니다. START, Windows, Windows 7, macOS Intel/Apple Silicon 검사가 성공했으며 Windows/Win7은 Defender와 무결성 검사도 통과했습니다. 전체 기능 완전 커버리지(#556)와 더 넓은 명령서 end-to-end 감사(#553)는 계속 진행 중입니다.

## 다운로드

**Stable / Latest: [Taxo 10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9).** 이전 Stable: [10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r9/Taxo_v10_24_candidate_r9_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r9/SHA256SUMS_v10_24_r9.txt)

**Stable / Latest:** [Taxo 10.24-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r9), 8개 파일, exact source `e3770aa72b0744eee192979a2e569651bac4f257`. 차량 문서 보존 및 backup/restore 보호 기능이 이제 Stable에 포함됩니다.


**Current Test:** [Taxo 10.25-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.25-r3), 8개 파일, exact source `0c76b38b3aa3970245f430bee2bde7b5c062c5dd`. 변경 불가 프로그램 revision, 공용 레지스트리의 누적 직원 선택, 결정적 planned session, document ID·filename·SHA-256으로 PaperDocuments DOCX에 정확히 연결하는 기능을 추가합니다. DOCX 준비는 `prepared` 상태만 의미하며 실시 또는 서명을 뜻하지 않습니다. Stable은 10.24-r9로 유지됩니다.

데이터베이스와 문서는 별도 작업 폴더에 보관하고 업데이트 전에 백업하세요. [사용 설명서(우크라이나어)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

개발: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). 모든 권리 보유. [LICENSE](../../LICENSE.md).
