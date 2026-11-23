# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo는 운송업체용 데스크톱 프로그램으로 직원과 차량, 일정과 근무시간, 운행일지, 명령서, 문서, 정비, 보고서와 백업을 관리합니다.

## Stable 10.24-r3

**10.24-r3는 2026년 11월 23일 소유자의 명시적 결정으로 Stable/Latest로 승격되었습니다.** 10.23-r4의 승인된 기능에 더해 r1–r3 서신 기능이 포함됩니다. 수신/발신 저널, 안전한 번호 부여, 제어 첨부, 검색, 날짜/달력, 정렬 가능한 표, 서신 카드, 새 서신·답변·첨부·문서 열기 기능을 제공합니다. 발송일이 비어 있으면 실제 발송으로 간주하지 않습니다.

37개의 엄격한 live UI 경로가 표시 여부, 화면 내 위치, 사용 가능 상태와 실제 활성화를 검사합니다. START, Windows, Windows 7, macOS Intel/Apple Silicon 검사가 성공했으며 Windows/Win7은 Defender와 무결성 검사도 통과했습니다. 전체 기능 완전 커버리지(#556)와 더 넓은 명령서 end-to-end 감사(#553)는 계속 진행 중입니다.

## 다운로드

**Stable / Latest: [Taxo 10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).** 이전 안정 버전: [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r3/Taxo_v10_24_candidate_r3_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r3/SHA256SUMS_v10_24_r3.txt)

**Current Test:** [Taxo 10.24-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r7), 8개 파일 prerelease, exact source `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d`. 업무 규칙을 바꾸지 않고 명령서의 **참여자 / 차량** 블록을 end-to-end로 강화했습니다. 검색/선택, 역할·메모 편집, 차량 추가, 선택 제거, live preview 동기화를 보호하며 DOCX/PDF는 동일한 frozen participant snapshot과 대조됩니다. full backup/restore는 identity, role, note, snapshot, sequence를 보존합니다. Taxo는 총 58개의 strict live route를 가지며 서신 contract는 exact 17 routes 그대로입니다. Stable/Latest는 10.24-r3 그대로입니다.

데이터베이스와 문서는 별도 작업 폴더에 보관하고 업데이트 전에 백업하세요. [사용 설명서(우크라이나어)](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

개발: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). 모든 권리 보유. [LICENSE](../../LICENSE.md).
