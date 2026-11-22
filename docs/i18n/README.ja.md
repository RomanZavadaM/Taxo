# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo は運送事業者向けのデスクトップアプリです。従業員・車両、勤務予定・労働時間、運行記録、命令書、文書、整備、帳票、バックアップを管理します。

## Stable 10.23-r4

**10.23-r4 は 2026年11月20日に所有者が手動確認し、Stable/Latest になりました。** 文書検索・絞り込み・並べ替え、種類/日付ツリー、入れ子の独自フォルダー、管理された Word 改訂版、PDF/印刷、DocumentVault、任意の紙原本スキャン、紙の署名状態を含みます。命令書では明示的な運転者–車両ペア、既存ペアの編集、参加者の役割/注記編集、検索中も保持される複数選択を利用できます。文書作業領域とカタログツリー幅は調整可能です。命令書プレビューの DOCX/PDF/JPG 操作は 760×560 の狭いウィンドウでも到達できます。

37 の厳格な live UI 経路で表示・画面内配置・利用可能性・操作実行を検証します。START、Windows、Windows 7、macOS Intel/Apple Silicon は成功し、Windows/Win7 は Defender と整合性検査も通過しました。全機能の完全な網羅 (#556) と命令書のより広い end-to-end 監査 (#553) は引き続き未完了です。

## ダウンロード

**Stable / Latest: [Taxo 10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).** 前の安定版: [10.23-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/Taxo_v10_23_candidate_r4_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r4/SHA256SUMS_v10_23_r4.txt)

**Current Test:** [Taxo 10.23-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r10)。8ファイルの prerelease、exact source は `f87991c624a971fe3ffd4112e5dfde9fd9e4b6cd` です。import proposal 用に独立した REVIEW 状態を追加し、confirm/reject/needs_review、proposal の正確な fingerprint、再起動後の復元、古い/改ざんされた判断に対する fail-closed を提供します。REVIEW は DocumentVault/DB、source、immutable import batch に変更を適用しません。OCR、外部AI、APPLY、物理ファイル整理は行わず、Stable/Latest は 10.23-r4 のままです。

データベースと文書は別の作業フォルダーに保存し、更新前にバックアップしてください。[利用者ガイド（ウクライナ語）](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

開発: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved. [LICENSE](../../LICENSE.md).
