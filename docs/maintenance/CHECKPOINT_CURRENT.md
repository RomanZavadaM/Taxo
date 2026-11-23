# Поточна контрольна точка Taxo

**23.11.2026 — Stable/Latest 10.24-r3; Current Test 10.24-r4.**

## Stable

- Release: [v10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3)
- Exact source: `c9cb6b7787d991c5ce612ceec1efb32ecc90891d`
- 8 canonical assets; GitHub Latest; prerelease=false; draft=false.
- Owner explicit promotion decision: 23.11.2026.
- Stable не змінювати без окремого рішення власника.

## Current Test

- Release: [v10.24-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r4)
- Exact source: `e1616ea0063575b2c989d684934364f38f995966`
- 8 canonical assets; prerelease=true; draft=false.
- Prep after UI fix: START #45157632285, Windows #45157632313, Win7 #45157632280, macOS Intel/ARM #45157632297 — SUCCESS.
- Candidate: START #45159393780, Windows #45159393870, Win7 #45159393814, macOS #45159393725 — SUCCESS.
- Exact source: START #45160194606, Windows #45160194713, Win7 #45160194576, macOS Intel/ARM #45160194864 — SUCCESS.
- Windows/Win7 Defender + post-scan integrity — SUCCESS.
- Guarded release-trigger merged as `ee4958f3cf1470f120e3b28f853640fea272c803`; publisher #45162074730 — SUCCESS.

## Що перевірено у r4

- explicit actual received/sent з обов'язковою фактичною датою;
- registration/attachment не означають actual delivery;
- safe forward-only transitions + append-only history;
- tampered history fail-closed;
- legacy registry migration без втрати numbering;
- due/overdue — read-only control для відкритих записів;
- actions/history physically reachable at 760×520 після винесення action rows з resizable card pane.

## Далі

Після recovery визначити наступний bounded correspondence slice окремо. Automatic e-mail, cases/threads, OCR/AI APPLY і physical attachment purge не змішувати автоматично.

#553/#556/#562 remain open; draft #543/#395 stay open.
