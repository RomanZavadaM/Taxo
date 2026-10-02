# Taxo / Driver Worktime

[Українська](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo は、1つの運送事業者向けデスクトップシステムです。運転者と従業員、勤務予定、勤務時間表、運行票、活動証明、車両、文書管理、レポート、整備管理、アナログタコグラフディスクの確認を扱います。

> **Stable:** [Taxo 10.3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.3)  
> **`main` の最新統合チェックポイント:** [Taxo 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)  
> **最新の完全マルチプラットフォームチェックポイント:** [Taxo 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1)  
> **以前の stable / rollback:** [Taxo 10.1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.1)  
> `v10.9-r9` は自動的に stable にはなりません。stable への昇格は所有者の別途決定です。

## ダウンロード

### 最新統合チェックポイント — 10.9-r9

[START 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/Taxo_v10_9_candidate_r9_START.zip) · [SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r9/SHA256SUMS_v10_9_r9.txt) · [Release 10.9-r9](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r9)

10.9-r9 は最新の統合コードチェックポイントです。START パッケージは公開されていますが、r9 向けの完全な実行ファイル一式は再公開されていません。

### 最新の完全マルチプラットフォームチェックポイント — 10.9-r1

[Windows/macOS パッケージを含む Release 10.9-r1](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.9-r1) · [Combined SHA-256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.9-r1/SHA256SUMS_v10_9_r1_ALL.txt)

通常運用では `v10.9-r1` の Windows/macOS パッケージを使用してください。`START.bat` は主にテストと技術診断用です。

ユーザー DB、SQLite ファイル、スキャン、キャッシュ、個人文書は GitHub release に含まれません。

## 主な機能

- 従業員・運転者台帳と役割履歴;
- 個別および周期的な運転者スケジュール;
- 計画と実績を明確に分離した勤務時間表と分割勤務;
- 労働、運転、休憩、休息の管理;
- 不明時間を休息として捏造しない60日活動記録;
- 車両、走行距離、整備、車両文書管理;
- 定期・不定期の運行票;
- 改訂履歴付き活動証明;
- アナログタコグラフディスクの手動確認;
- 承認/署名済み業務命令と運転者→車両割当履歴の保護;
- PDF/Excel レポート;
- バックアップ、ワークスペース移行、SQLite スキーマ互換性管理.

## 10.9-r2 → 10.9-r9 に統合された内容

発行済み運行票番号の履歴保護、全行程を対象とした車両文書有効性確認、勤務/休息ルール強化、実データソース優先順位の安全化、従業員/P-5履歴修正、走行距離と整備予測の強化、承認/署名済み命令の不変性、`PRAGMA user_version` による SQLite スキーマ基準を含みます。

詳細: [10.9-r9 release notes](docs/releases/RELEASE_NOTES_v10.9-r9.md) · [release index](docs/releases/RELEASE_INDEX.md)

## 開発状態

運用文書の基準言語はウクライナ語です。新しい開発/復旧セッションでは `START_HERE.md` → `PROJECT_RULES.md` → `PROJECT_STATE.md` → `WORKLOG.md` → Issue #61 の順に確認します。公開済み revision は変更しません。`10.9-r9` の次のコード revision は **10.9-r10** です。

## 著作権とライセンス

**Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved.**

Taxo は proprietary software です。リポジトリが公開されていること自体は、オープンソースライセンス、再配布、販売、変更版・派生版の配布許可を意味しません。

[LICENSE.md](LICENSE.md) · [COPYRIGHT.md](COPYRIGHT.md) · [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
