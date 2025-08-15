# Dooray MCP Server

NHN Doorayサービス用のMCP（Model Context Protocol）サーバーです。

## 主要機能

- **Wikiの管理**: Wiki閲覧、作成、編集、参照者管理
- **タスク管理**: タスク閲覧、作成、編集、ステータス変更
- **コメント管理**: タスクコメントの作成、閲覧、編集、削除
- **メッセンジャー管理**: メンバー検索、ダイレクトメッセージ、チャンネル管理、チャンネルメッセージ送信
- **JSON応答**: 規格化されたJSON形式の応答
- **例外処理**: 一貫したエラー応答の提供
- **Docker対応**: マルチプラットフォームDockerイメージの提供

## クイックスタート

### 環境変数の設定

以下の環境変数を設定する必要があります：

```bash
export DOORAY_API_KEY="your_api_key"
export DOORAY_BASE_URL="https://api.dooray.com"

# オプション: ログレベル制御
export DOORAY_LOG_LEVEL="WARN"         # DEBUG, INFO, WARN, ERROR (デフォルト: WARN)
export DOORAY_HTTP_LOG_LEVEL="WARN"    # HTTPクライアントログ (デフォルト: WARN)
```

#### ログ設定

**一般ログ (`DOORAY_LOG_LEVEL`)**

- `WARN` (デフォルト): 警告とエラーのみログ出力 - **MCP通信の安定性のため推奨**
- `INFO`: 一般情報を含むログ出力
- `DEBUG`: 詳細なデバッグ情報を含む

**HTTPログ (`DOORAY_HTTP_LOG_LEVEL`)**

- `WARN` (デフォルト): HTTPエラーのみログ出力 - **MCP通信の安定性のため推奨**
- `INFO`: 基本的なリクエスト/レスポンス情報のみログ出力
- `DEBUG`: 詳細なHTTP情報をログ出力

> ⚠️ **重要**: MCPサーバーはstdin/stdoutを通じて通信するため、すべてのログは**stderr**に出力されます。ログレベルを上げてもプロトコル通信に影響はありませんが、パフォーマンスに影響する可能性があります。

### ローカル実行

```bash
# 依存関係のインストールとビルド
./gradlew clean shadowJar

# ローカル実行 (.envファイルを使用)
./gradlew runLocal

# または直接実行
java -jar build/libs/dooray-mcp-server-0.2.1-all.jar
```

### Docker実行

```bash
# Docker Hubからイメージを取得
docker pull bifos/dooray-mcp:latest

# 環境変数と一緒に実行
docker run -e DOORAY_API_KEY="your_api_key" \
           -e DOORAY_BASE_URL="https://api.dooray.com" \
           bifos/dooray-mcp:latest
```

## Claude Desktopでの使用方法

Claude Desktop（Claude Code）でMCPサーバーを使用するには、設定ファイルに以下のように追加してください。

### 設定ファイルの場所

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

### 基本設定（推奨）

```json
{
  "mcpServers": {
    "dooray-mcp": {
      "command": "docker",
      "args": [
        "run",
        "--platform", "linux/amd64",
        "-i",
        "--rm",
        "-e", "DOORAY_API_KEY",
        "-e", "DOORAY_BASE_URL",
        "my13each/dooray-mcp:latest"
      ],
      "env": {
        "DOORAY_API_KEY": "{Your Dooray API Key}",
        "DOORAY_BASE_URL": "https://api.dooray.com"
      }
    }
  }
}
```

### 常に最新版を使用（オプション）

最新アップデートをすぐに反映したい場合は、`--pull=always`オプションを追加してください：

```json
{
  "mcpServers": {
    "dooray-mcp": {
      "command": "docker",
      "args": [
        "run",
        "--platform", "linux/amd64",
        "--pull=always",
        "-i",
        "--rm",
        "-e", "DOORAY_API_KEY",
        "-e", "DOORAY_BASE_URL",
        "my13each/dooray-mcp:latest"
      ],
      "env": {
        "DOORAY_API_KEY": "{Your Dooray API Key}",
        "DOORAY_BASE_URL": "https://api.dooray.com"
      }
    }
  }
}
```

> ⚠️ **注意**: `--pull=always`オプションは、Claude起動時に毎回最新イメージをダウンロードするため、起動時間が長くなる可能性があります。

### Dooray API Key発行方法

1. [Dooray管理者ページ](https://dooray.com)にログイン
2. **管理 > API管理**メニューに移動
3. **新しいAPI Key作成**をクリック
4. 必要な権限を設定後、作成
5. 生成されたAPI Keyを設定ファイルの`{Your Dooray API Key}`部分に入力

## 使用可能なツール（合計23個）

### Wiki関連ツール（8個）

#### 1. dooray_wiki_list_projects

Doorayでアクセス可能なWikiプロジェクト一覧を取得します。

#### 2. dooray_wiki_list_pages

特定のDooray Wikiプロジェクトのページ一覧を取得します。

#### 3. dooray_wiki_get_page

特定のDooray Wikiページの詳細情報を取得します。

#### 4. dooray_wiki_create_page

新しいWikiページを作成します。

#### 5. dooray_wiki_update_page

既存のWikiページを編集します。

#### 6. dooray_wiki_update_page_title

Wikiページのタイトルのみを編集します。

#### 7. dooray_wiki_update_page_content

Wikiページの内容のみを編集します。

#### 8. dooray_wiki_update_page_referrers

Wikiページの参照者を編集します。

### プロジェクト関連ツール（1個）

#### 9. dooray_project_list_projects

アクセス可能なプロジェクト一覧を取得します。

### タスク関連ツール（6個）

#### 10. dooray_project_list_posts

プロジェクトのタスク一覧を取得します。

#### 11. dooray_project_get_post

特定タスクの詳細情報を取得します。

#### 12. dooray_project_create_post

新しいタスクを作成します。

#### 13. dooray_project_update_post

既存のタスクを編集します。

#### 14. dooray_project_set_post_workflow

タスクのステータス（ワークフロー）を変更します。

#### 15. dooray_project_set_post_done

タスクを完了状態に変更します。

### タスクコメント関連ツール（4個）

#### 16. dooray_project_create_post_comment

タスクにコメントを作成します。

#### 17. dooray_project_get_post_comments

タスクのコメント一覧を取得します。

#### 18. dooray_project_update_post_comment

タスクコメントを編集します。

#### 19. dooray_project_delete_post_comment

タスクコメントを削除します。

### メッセンジャー関連ツール（6個）

#### 20. dooray_messenger_search_members

Dooray組織のメンバーを検索します。名前、メール、ユーザーコードなどで検索できます。

#### 21. dooray_messenger_send_direct_message

特定メンバーに1対1ダイレクトメッセージを送信します。

#### 22. dooray_messenger_get_channels

アクセス可能なメッセンジャーチャンネル一覧を取得します。最近N ヶ月以内に更新されたチャンネルのみフィルタリングして大容量結果を防ぐことができます。

#### 23. dooray_messenger_get_simple_channels

簡易チャンネル一覧を取得します。チャンネル検索用でID、タイトル、タイプ、ステータス、更新日時、参加者数のみ含み、すべてのチャンネルを安全に取得できます。

#### 24. dooray_messenger_get_channel

特定チャンネルの詳細情報を取得します。チャンネルIDを通じて該当チャンネルのすべてのメンバー、設定などの詳細情報を確認できます。

#### 25. dooray_messenger_create_channel

新しいメッセンジャーチャンネルを作成します。（privateまたはdirectタイプ対応）

#### 26. dooray_messenger_send_channel_message

メッセンジャーチャンネルにメッセージを送信します。

> ⚠️ **注意**: チャンネルメッセージの取得は、Dooray APIでセキュリティ上の理由により対応していません。

## 使用例

### Wikiページ取得

```json
{
  "name": "dooray_wiki_list_projects",
  "arguments": {
    "page": 0,
    "size": 20
  }
}
```

### タスク作成

```json
{
  "name": "dooray_project_create_post",
  "arguments": {
    "project_id": "your_project_id",
    "subject": "新しいタスク",
    "body": "タスク内容",
    "to_member_ids": ["member_id_1", "member_id_2"],
    "priority": "high"
  }
}
```

### コメント作成

```json
{
  "name": "dooray_project_create_post_comment",
  "arguments": {
    "project_id": "your_project_id",
    "post_id": "your_post_id",
    "content": "コメント内容",
    "mime_type": "text/x-markdown"
  }
}
```

### メンバー検索

```json
{
  "name": "dooray_messenger_search_members",
  "arguments": {
    "name": "田中太郎",
    "size": 10
  }
}
```

### ダイレクトメッセージ送信

```json
{
  "name": "dooray_messenger_send_direct_message",
  "arguments": {
    "organization_member_id": "member_id_from_search",
    "text": "こんにちは！メッセージ送信テストです。"
  }
}
```

### 簡易チャンネル一覧取得

```json
{
  "name": "dooray_messenger_get_simple_channels",
  "arguments": {
    "recentMonths": 3,
    "size": 50
  }
}
```

### 特定チャンネル詳細取得

```json
{
  "name": "dooray_messenger_get_channel",
  "arguments": {
    "channelId": "2692783199335294539"
  }
}
```

### チャンネル作成

```json
{
  "name": "dooray_messenger_create_channel",
  "arguments": {
    "type": "private",
    "title": "新プロジェクトチャンネル",
    "member_ids": ["member_id_1", "member_id_2"],
    "capacity": "50"
  }
}
```

### チャンネルメッセージ送信

```json
{
  "name": "dooray_messenger_send_channel_message",
  "arguments": {
    "channel_id": "channel_id_from_list",
    "text": "チャンネルにメッセージを送信します。"
  }
}
```

## 開発

### テスト実行

```bash
# すべてのテストを実行（環境変数がある場合）
./gradlew test

# CI環境では統合テストを自動除外
CI=true ./gradlew test
```

### ビルド

```bash
# JARビルド
./gradlew clean shadowJar

# Dockerイメージビルド
docker build -t dooray-mcp:local --build-arg VERSION=0.2.1 .
```

## Dockerマルチプラットフォームビルド

### 現在の状況

現在のDockerイメージは**AMD64のみ対応**しています。ARM64ビルドはQEMUエミュレーションでGradle依存関係ダウンロード段階で停止する問題があり、一時的に無効化されています。

### ARM64ビルド有効化

ARM64ビルドを再度有効化するには、`.github/workflows/docker-publish.yml`で以下の設定を変更してください：

```yaml
env:
  ENABLE_ARM64: true # falseからtrueに変更
```

### ARM64ビルド問題解決方法

1. **ネイティブARM64ランナー使用**（推奨）
2. **QEMUタイムアウト増加**
3. **Gradleキャッシュ最適化**
4. **依存関係事前ダウンロード**

現在は安定性のためAMD64のみビルドしており、ARM64対応は今後のアップデートで提供予定です。

## 環境変数

| 変数名          | 説明                | 必須 |
| --------------- | ------------------- | ---- |
| DOORAY_API_KEY  | Dooray API キー     | 必須 |
| DOORAY_BASE_URL | Dooray API Base URL | 必須 |

## ライセンス

このプロジェクトはオープンソースであり、自由にご利用いただけます。

## 貢献

プロジェクトに貢献したい場合は、issueを登録するかpull requestを送ってください。

## 📚 参考資料

- [Dooray API](https://helpdesk.dooray.com/share/pages/9wWo-xwiR66BO5LGshgVTg/2939987647631384419)
- [Kotlin MCP Server サンプル](https://github.com/modelcontextprotocol/kotlin-sdk/blob/main/samples/weather-stdio-server/src/main/kotlin/io/modelcontextprotocol/sample/server/McpWeatherServer.kt)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)