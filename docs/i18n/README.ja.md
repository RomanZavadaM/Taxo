# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo は単一の運送会社向けデスクトップシステムです：従業員とドライバー、勤務表、労働時間管理、運行日誌、活動確認書、車両、書類管理、整備、レポート、アナログタコグラフの点検。

> **安定版:** [Taxo 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.12-r10) — 所有者が安定版として承認。正確な r10 チェックポイントを Windows 10/11、Windows 7、macOS Intel、Apple Silicon で検証済みです。
> **以前の安定版 / ロールバック:** [Taxo 10.10-r5](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r5)
> **さらに以前のロールバック:** [Taxo 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r10)
> **旧ロールバック:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)

## ダウンロード — Taxo 10.9-r10（さらに以前のロールバック）

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.9-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/Taxo_v10_9_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r10/SHA256SUMS_v10_9_r10.txt) · [10.9-r10 リリースノート（ウクライナ語）](../releases/RELEASE_NOTES_v10.9-r10.md) · [リリース索引](../releases/RELEASE_INDEX.md)

## ダウンロード — Taxo 10.12-r10（安定版）

**Windows 10/11 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows_x64_Portable.zip)

**Windows 7 SP1 x64:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_macOS_x86_64_Portable.zip)

**Source/START:** [START 10.12-r10](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/Taxo_v10_12_candidate_r10_START.zip) · [SHA256SUMS](https://github.com/RomanZavadaM/Taxo/releases/download/v10.12-r10/SHA256SUMS_v10_12_r10.txt)

業務データベース、SQLite ファイル、スキャン、キャッシュ、個人文書は GitHub リリースに含まれません。更新時に業務データを再入力する必要はありません。

## 以前の安定版 10.9-r10 の内容

- 発行済み運行日誌と番号の恒久的な履歴；保存期間の整理で関連する事実を削除しない
- 計画された運行全期間の車両書類の有効性
- 労働・休息管理の強化：重複、3+9、週休・2週間休息
- 架空の休息を作らない60日登録簿；実績データを優先
- 人員バランス / P-5、2/2 と 3/3 の勤務形態
- 整備：走行距離の時系列と整備予測
- 承認・署名済み命令とドライバー→車両割当の不変性
- SQLite スキーマ互換性の管理
- 業務ロジックを変えないコード構造の整理

## テスト版（安定版ではありません）

**10.10-r5** は macOS の起動問題を修正し、現在は以前の安定版 / ロールバックです。**現在の安定版は 10.12-r10 です。**

[10.10-r1 … r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.10-r3) は実データで検証するためのプレリリースです：PyMuPDF 廃止、ウィンドウに正しいバージョン表示、DB のみのバックアップ警告、CI 強化。所有者の検証後にのみ安定版になります。

## 開発

正式な運用ドキュメントはウクライナ語で管理されています。[`START_HERE.md`](../../START_HERE.md) から始めてください。現在の安定版は `10.12-r10` です。より新しい `10.13-r1` は `main` に統合されていますが、安定版ではありません。次のコードリビジョンは `10.13-r2` です。

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo はプロプライエタリソフトウェアです。
