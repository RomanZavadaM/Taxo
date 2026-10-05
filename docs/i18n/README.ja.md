# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo は単一の運送会社向けデスクトップシステムです：従業員とドライバー、勤務表、労働時間管理、運行日誌、活動確認書、車両、書類管理、整備、レポート、アナログタコグラフの点検。

> **安定版:** [Taxo 10.10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10) — 2026-10-05
> **以前の安定版 / ロールバック:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)
> **次のコードリビジョン:** `10.10-r4`

## ダウンロード — Taxo 10.10（安定版）

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/Taxo_v10_10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.10/SHA256SUMS_v10_10.txt) · [10.10 リリースノート（ウクライナ語）](../releases/RELEASE_NOTES_v10_10.md) · [リリース索引](../releases/RELEASE_INDEX.md)

業務データベース、SQLite ファイル、スキャン、キャッシュ、個人文書は GitHub リリースに含まれません。更新時に業務データを再入力する必要はありません。

## 10.10 の新機能

- **PyMuPDF を廃止。** 活動確認書（PDF/JPG）、第340号レポートの日付スタンプ、PDF の表示・印刷は寛容なライセンスのライブラリ（pypdfium2、reportlab、pypdf）で動作し、出力は以前のバージョンとピクセル単位で同一です。
- **正しいバージョン表示** — ウィンドウタイトル、情報ダイアログ、PDF ヘッダー、バックアップのマニフェスト。
- **バックアップ**がデータベースのみを含む場合に明示的に警告します。
- **インフラ：** 古い公開ワークフローを無効化、テストを業務用ストレージから分離、全ビルドでライセンス検査。
- 10.4 … 10.9 の全系列を含む：運行全期間の車両書類の有効性、発行済み運行日誌と番号の保護、労働・休息管理の強化、60日登録簿、人員バランス、整備、署名済み命令の不変性、SQLite スキーマ互換性。

## 主な機能

従業員とドライバーの履歴；個別・周期的な勤務表；計画/実績の労働時間と分割勤務；労働・運転・休憩・休息の管理；60日活動登録簿；車両、走行距離、整備、書類；定期・不定期の運行日誌；活動確認書；アナログタコグラフ点検；保護された命令とドライバー→車両の割当；PDF/Excel レポート；バックアップと SQLite 互換性管理。

## 開発

正式な運用ドキュメントはウクライナ語で管理されています。[`START_HERE.md`](../../START_HERE.md) から始めてください。安定版 10.10 以降、新しいコードは現在の `main` から `10.10-r4` として始まります。発行済みリビジョンは変更されません。

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo はプロプライエタリソフトウェアです。
