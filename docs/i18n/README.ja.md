# Taxo / Driver Worktime

🇺🇦 [Українська](../../README.md) · 🇬🇧 [English](README.en.md) · 🇩🇪 [Deutsch](README.de.md) · 🇪🇸 [Español](README.es.md) · 🇫🇷 [Français](README.fr.md) · 🇰🇷 [한국어](README.ko.md) · 🇯🇵 [日本語](README.ja.md)

Taxo は運送事業者向けのデスクトップアプリです。従業員・車両、勤務予定・労働時間、運行記録、命令書、文書、整備、帳票、バックアップを管理します。

## Stable 10.24-r3

**10.24-r3 は 2026年11月23日の所有者の明示的な決定により Stable/Latest に昇格しました。** 10.23-r4 の受け入れ済み機能に加え、r1–r3 の連絡文書機能を含みます。受信/送信ジャーナル、安全な番号付け、管理された添付、検索、日付/カレンダー、並べ替え、文書カード、作成・返信・添付・文書を開く操作があります。送信日が空なら、実際に送信済みとはみなしません。

37 の厳格な live UI 経路で表示・画面内配置・利用可能性・操作実行を検証します。START、Windows、Windows 7、macOS Intel/Apple Silicon は成功し、Windows/Win7 は Defender と整合性検査も通過しました。全機能の完全な網羅 (#556) と命令書のより広い end-to-end 監査 (#553) は引き続き未完了です。

## ダウンロード

**Stable / Latest: [Taxo 10.24-r3](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r3).** 前の安定版: [10.23-r4](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.23-r4).

Windows 10/11 x64 · Windows 7 SP1 x64 · macOS Intel / Apple Silicon · [START ZIP](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r3/Taxo_v10_24_candidate_r3_START.zip) · [SHA256](https://github.com/RomanZavadaM/Taxo/releases/download/v10.24-r3/SHA256SUMS_v10_24_r3.txt)

**Current Test:** [Taxo 10.24-r7](https://github.com/RomanZavadaM/Taxo/releases/tag/v10.24-r7)。8ファイルの prerelease、exact source は `4221b8baaeae4fad6ca8b6ebf4640a4a34050e2d` です。業務ルールを変えずに、命令書の **参加者 / 車両** ブロックを end-to-end で強化しました。検索/選択、役割・メモ編集、車両追加、選択削除、live preview 同期を保護し、DOCX/PDF は同じ frozen participant snapshot と照合され、full backup/restore は identity・role・note・snapshot・sequence を保持します。Taxo は合計 58 の strict live route、連絡文書 contract は exact 17 route のままです。Stable/Latest は 10.24-r3 のままです。

データベースと文書は別の作業フォルダーに保存し、更新前にバックアップしてください。[利用者ガイド（ウクライナ語）](../guides/USER_MANUAL.md) · [Quick Start](../guides/QUICK_START.md)

開発: [START_HERE.md](../../START_HERE.md).

Copyright © 2026 Roman Zavada (Роман Завада). All rights reserved. [LICENSE](../../LICENSE.md).
