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

## 10.23-r1 の改善点

安定版10.23-r1は独自テンプレート、管理されたWord改訂版、PDF/印刷、DocumentVaultを備えています。任意の紙原本スキャンは追加・閲覧・除外・履歴付き交換が可能で、紙の署名状態は別に記録します。文書カタログには検索、絞り込み、並べ替え、種類/日付のツリー、ファイルを複製しない入れ子の独自フォルダーがあります。命令書では運転者–車両の組み合わせを明示的に作成・編集でき、運行記録は日付移動に対応します。PDF添付表の長い文字列は折り返されます。32の厳格なUI経路で機能を保護します。Windows、Windows 7、macOS Intel/Apple Silicon、STARTおよびセキュリティ/整合性検査は成功しました。全機能の保護と手動受入確認は未完了で、受発信文書の登録は計画段階です。テスト版10.23-r2の役割/注記編集と33番目のUI経路は安定版r1に含まれません。

## ダウンロード

安定版：10.23-r1。

[10.23-r1 の全ファイル](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r1) · [前の安定版 10.21-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.21-r2)

Windows 10/11 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r1/Taxo_v10_23_candidate_r1_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.23-r1/SHA256SUMS_v10_23_r1.txt)

テスト版: [10.23-r2](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r2).

## 初期設定とデータ

データベースと文書は別の作業フォルダーに保存し、更新前にバックアップしてください。完全バックアップには従業員書類と作成済み Word 文書が含まれます。車両書類、タコグラフ画像、Output ファイルは該当項目の選択が必要です。

[利用者ガイド（ウクライナ語）](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

## 開発

開始はこちら [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved. [LICENSE](../../LICENSE.md).
