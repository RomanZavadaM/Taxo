# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md)

Taxo は、1つの運送事業者向けデスクトップシステムです。運転者と従業員、勤務予定、勤務時間、運行票、活動証明、車両、文書、整備、レポート、アナログタコグラフを扱います。

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
> **`main` に統合済みの最新 checkpoint:** **Taxo 10.9-r10**  
> **公開済みの最新フル・マルチプラットフォーム release:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **次のコード revision:** `10.10-r1`

`10.9-r10` はすでに `main` に統合されていますが、独立した完全な公開マルチプラットフォーム release としては公開されていません。すぐに使える Windows/macOS パッケージは `v10.9-r9` を使用してください。

## ダウンロード — 10.9-r9

**Windows 10/11:** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip)

**Windows 7 SP1:** [Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS:** [Apple Silicon / ARM64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**テスト/ソース:** [START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [10.9-r10 release notes](../releases/RELEASE_NOTES_v10.9-r10.md) · [Release index](../releases/RELEASE_INDEX.md)

ユーザー DB、SQLite、スキャン、キャッシュ、個人文書は GitHub release に含まれません。

## 10.9-r10 の変更

ビジネスロジックを変更せずにリポジトリ構造を整理しました。runtime モジュールは `src/taxo/`、テンプレートは `assets/`、有効な packaging 定義は `packaging/` に移動しました。ユーザーデータの移行は導入していません。

## 主な機能

従業員/運転者履歴、個別/周期的勤務予定、計画/実績と分割勤務、労働・運転・休憩・休息管理、60日活動記録、車両・走行距離・整備・文書、運行票、活動証明、アナログタコグラフ、保護された命令と運転者→車両割当、PDF/Excel レポート、バックアップ、SQLite 互換性管理。

## 開発

基準となる運用文書はウクライナ語で管理されます。開始点: [`START_HERE.md`](../../START_HERE.md)。`10.9-r10` の後、新しいコード作業は現在の `main` から `10.10-r1` として開始します。発行済み revision は変更しません。

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo は proprietary software です。
