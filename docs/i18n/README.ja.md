# Taxo / Driver Worktime

[Українська](../../README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [한국어](README.ko.md) · [日本語](README.ja.md)

Taxo は運送事業者向けのデスクトップアプリです。従業員と車両、運転者の勤務予定・労働時間、業務文書と帳票を管理します。

## 主な機能

- 従業員と運転者：台帳、役割の履歴、書類、有効期限、欠落したローカル添付ファイルの確認。
- 予定と労働時間：路線、勤務シフト、勤務表、予定時間と実績時間の分離。
- 運転者の管理：運転・労働・休憩・休息、個別帳票、60日間の活動記録。
- 車両と整備：車両情報、走行距離、書類、保守と修理。
- 運行業務：運行記録、命令書、運転者と車両の割当て、活動証明書と文書印刷。
- 安全教育と研修：編集可能な Word 教育資料、署名簿、研修様式と基本的な文書カタログ。
- アナログタコグラフ：スキャン、表示、手動確認を伴う補助的な認識。
- 帳票とバックアップ：PDF/Excel 帳票と作業データのバックアップ。

## 10.20-r5 の改善点

安定版 10.20-r5 では、ユーザー独自テンプレート、準備済み文書の管理された改訂履歴、DOCX/PDF/印刷出力、通常の「文書」一覧に統合された DocumentVault、任意の紙原本スキャン（PDF/JPG/PNG/TIFF）を整合性確認付きで保存する基盤が追加されています。スキャンの追加・一覧表示 UI は安定版 r5 には含まれず、テスト版 r6 で初めて提供されます。r5 は 1400 件の回帰テストに加え、Windows、Windows 7、macOS Intel／Apple Silicon のビルドとセキュリティ／整合性検査に合格しました。

## ダウンロード

安定版：10.20-r5。

[10.20-r5 の全ファイル](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.20-r5) · [前の安定版 10.18-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.18-r3)

Windows 10/11 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.20-r5/Taxo_v10_20_candidate_r5_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.20-r5/SHA256SUMS_v10_20_r5.txt)

## 初期設定とデータ

データベースと文書は別の作業フォルダーに保存し、更新前にバックアップしてください。完全バックアップには従業員書類と作成済み Word 文書が含まれます。車両書類、タコグラフ画像、Output ファイルは該当項目の選択が必要です。

[利用者ガイド（ウクライナ語）](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

## 開発

開始はこちら [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved. [LICENSE](../../LICENSE.md).
