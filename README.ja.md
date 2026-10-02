# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo は、1つの運送事業者向けデスクトップシステムです。運転者と従業員、勤務予定、勤務時間表、運行票、活動証明、車両、文書管理、レポート、整備管理、アナログタコグラフディスクを扱います。

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
> **`main` の最新統合チェックポイント:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **最新の完全マルチプラットフォームチェックポイント:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **以前の stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1)

## ダウンロード — 10.9-r9

**Windows:** [x64 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows_x64.exe) · [x64 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows_x64_Portable.zip) · [Windows 7 SP1 Setup](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Setup_Windows7_x64.exe) · [Windows 7 SP1 Portable](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_Windows7_x64_Portable.zip)

**macOS:** [ARM64 / Apple Silicon](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_arm64_Portable.zip) · [Intel x86_64](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_macOS_x86_64_Portable.zip)

**テスト/診断:** [START](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [Release](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9) · [Release notes](docs/releases/RELEASE_NOTES_v10.9-r9.md)

通常運用では Windows/macOS の完成パッケージを使用してください。ユーザー DB、SQLite、スキャン、キャッシュ、個人文書は release に含まれません。

## 主な機能

従業員/運転者履歴、個別/周期的勤務予定、計画/実績勤務時間、分割勤務、労働・運転・休憩・休息管理、60日活動記録、車両/文書/整備、運行票、活動証明、アナログタコグラフ、承認/署名済み命令の保護、PDF/Excelレポート、バックアップ、SQLiteスキーマ互換性。

## 10.9-r2 → 10.9-r9

発行済み運行票番号の不変履歴、全行程の文書有効性確認、勤務/休息ルール強化、実データソース優先順位の安全化、従業員/P-5履歴修正、走行距離/整備予測、承認/署名済み命令の不変性、`PRAGMA user_version` による SQLite スキーマ基準が統合されています。

[10.9-r9 release notes](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [release index](docs/releases/RELEASE_INDEX.md)

## 開発状態

運用文書の基準言語はウクライナ語です。`10.9-r9` の次のコード revision は **10.9-r10** です。

## 著作権とライセンス

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.** Taxo は proprietary software です。
