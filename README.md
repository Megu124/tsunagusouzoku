# tsunagusouzoku

このリポジトリは Obsidian の Vault（保管庫）としても利用できるように構成しています。
リポジトリのルートフォルダをそのまま Obsidian の Vault として開いてください。

## フォルダ構成

- `manuscript/` — 執筆材料・原稿一式（構成案、メルマガアーカイブ、エピソード候補メモ、本文原稿）

## Obsidian Git 連携のセットアップ手順

1. Obsidian でこのリポジトリのルートフォルダを Vault として開く
   （「Open folder as vault」→ クローンしたこのフォルダを選択）
2. 設定 → コミュニティプラグイン → 「Obsidian Git」を検索してインストール
   （`.obsidian/community-plugins.json` に `obsidian-git` を登録済みなので、
   インストール後は自動的に有効化されます）
3. Obsidian Git の設定で以下を確認・調整
   - リモートURLがこのリポジトリを指していること
   - 自動コミット／自動プルの間隔（お好みで。例: 10分ごとなど）
   - コミットメッセージのテンプレート
4. 初回のみ、ターミナルなどでこのフォルダに対して `git remote -v` を確認し、
   このリポジトリの clone であることを確認してください

## 同期対象外にしているファイル

端末固有の状態（開いているタブやウィンドウ配置など）やキャッシュは
`.gitignore` で同期対象から除外しています。

- `.obsidian/workspace.json` / `.obsidian/workspace-mobile.json`
- `.obsidian/cache`
- `.obsidian/plugins/*/data.json`（プラグインごとのローカル設定）
- `.trash/`
