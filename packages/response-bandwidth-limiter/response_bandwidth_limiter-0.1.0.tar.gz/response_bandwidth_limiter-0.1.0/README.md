# Response Bandwidth Limiter

FastAPIとStarlette用のレスポンス帯域制限ミドルウェア。特定のエンドポイントのレスポンス送信速度を制限することができます。

## インストール

pipを使用してインストールできます：

```bash
pip install response-bandwidth-limiter
```

### 依存関係

このライブラリは最小限の依存関係で動作しますが、実際の使用にはFastAPIまたはStarletteが必要です。
必要に応じて以下のようにインストールしてください：

```bash
# FastAPIと一緒に使用する場合
pip install fastapi

# Starletteと一緒に使用する場合
pip install starlette

# 開発やテストに必要な依存関係を含める場合
pip install response-bandwidth-limiter[dev]
```

## 基本的な使い方

### デコレータを使った方法（推奨）

```python
from fastapi import FastAPI, Request
from starlette.responses import FileResponse
from response_bandwidth_limiter import ResponseBandwidthLimiter, ResponseBandwidthLimitExceeded, _response_bandwidth_limit_exceeded_handler

# リミッターの初期化
limiter = ResponseBandwidthLimiter()
app = FastAPI()

# アプリケーションに登録
app.state.response_bandwidth_limiter = limiter
app.add_exception_handler(ResponseBandwidthLimitExceeded, _response_bandwidth_limit_exceeded_handler)

# エンドポイントのレスポンス帯域制限（1024 bytes/sec）
@app.get("/download")
@limiter.limit(1024)  # 1024 bytes/sec
async def download_file(request: Request):
    return FileResponse("path/to/large_file.txt")

# 別のエンドポイントに別の制限（2048 bytes/sec）
@app.get("/video")
@limiter.limit(2048)  # 2048 bytes/sec
async def stream_video(request: Request):
    return FileResponse("path/to/video.mp4")
```

### Starletteでの使用例

```python
from starlette.applications import Starlette
from starlette.responses import FileResponse
from starlette.routing import Route
from response_bandwidth_limiter import ResponseBandwidthLimiter

# デコレータ方式
limiter = ResponseBandwidthLimiter()

async def download_file(request):
    return FileResponse("path/to/large_file.txt")

# デコレータを適用
download_with_limit = limiter.limit(1024)(download_file)

# ルートを定義
routes = [
    Route("/download", endpoint=download_with_limit)
]

app = Starlette(routes=routes)

# リミッターをアプリに登録
limiter.init_app(app)
```

## 高度な使用例

### デコレータを使った帯域制限の設定（シンプルなケース）

シンプルに帯域制限を設定する場合は、`set_response_bandwidth_limit`デコレータを使用できます：

```python
from fastapi import FastAPI
from starlette.responses import FileResponse
from response_bandwidth_limiter import set_response_bandwidth_limit

app = FastAPI()

@app.get("/download")
@set_response_bandwidth_limit(1024)  # 1024 bytes/sec
async def download_file():
    return FileResponse("path/to/large_file.txt")
```

この方法では、`ResponseBandwidthLimiter`クラスを初期化せずに、直接エンドポイントに帯域制限を設定できます。
さらに、このデコレータを使用する場合は、ミドルウェアを明示的に追加する必要があります：

```python
from response_bandwidth_limiter import ResponseBandwidthLimiterMiddleware

app = FastAPI()
app.add_middleware(ResponseBandwidthLimiterMiddleware)

@app.get("/download")
@set_response_bandwidth_limit(1024)
async def download_file():
    return FileResponse("path/to/large_file.txt")
```

このシンプルなデコレータはグローバルな設定を使用するため、複数のアプリケーションで同じ関数名を使用する場合は注意してください。より複雑なシナリオでは、`ResponseBandwidthLimiter`クラスを使用するアプローチが推奨されます。

### シンプルデコレータと標準デコレータの違い

シンプルデコレータ (`set_response_bandwidth_limit`) と標準デコレータ (`ResponseBandwidthLimiter.limit`) の主な違い：

1. シンプルデコレータ:
   - グローバルな設定を使用
   - アプリインスタンスに依存しない
   - 複数アプリで同名の関数を使うと競合する可能性あり
   - 設定が簡単

2. 標準デコレータ:
   - アプリインスタンスごとに分離された設定
   - 複数のアプリで安全に使用可能
   - より明示的な初期化が必要
   - 大規模アプリに適している

### 両方のデコレータを併用する

同じアプリ内で両方のデコレータを使用することもできます：

```python
from fastapi import FastAPI, Request
from response_bandwidth_limiter import (
    ResponseBandwidthLimiter,
    set_response_bandwidth_limit,
    ResponseBandwidthLimiterMiddleware
)

app = FastAPI()
limiter = ResponseBandwidthLimiter()
app.state.response_bandwidth_limiter = limiter

# ミドルウェアは一度だけ追加
app.add_middleware(ResponseBandwidthLimiterMiddleware)

# 標準デコレータの使用例
@app.get("/video")
@limiter.limit(2048)
async def stream_video(request: Request):
    # ...

# シンプルデコレータの使用例
@app.get("/download")
@set_response_bandwidth_limit(1024)
async def download_file(request: Request):
    # ...
```

### 動的な帯域制限

実行時に帯域制限を変更したい場合：

```python
limiter = ResponseBandwidthLimiter()
app = FastAPI()
app.state.response_bandwidth_limiter = limiter

@app.get("/admin/set-limit")
async def set_limit(endpoint: str, limit: int):
    limiter.routes[endpoint] = limit
    return {"status": "success", "endpoint": endpoint, "limit": limit}
```

**重要な注意点**: 帯域制限の変更は永続的です。一度エンドポイントの帯域制限を変更すると、その変更はサーバーが再起動されるまで保持され、次回以降のすべてのリクエストに適用されます。一時的な変更ではなく、設定の更新として扱われます。

例えば、あるエンドポイントの制限を1000 bytes/secから2000 bytes/secに変更した場合、それ以降のすべてのリクエストは2000 bytes/secの制限で処理されます。元の速度に戻す場合は、明示的に再設定する必要があります。

### 特定のユーザーやIPに対する帯域制限

```python
@app.get("/download/{user_id}")
@limiter.limit(1024)
async def download_for_user(request: Request, user_id: str):
    # ユーザーごとに異なる制限を適用したい場合は、
    # ここでカスタム処理を行うことができます
    user_limits = {
        "premium": 5120,
        "basic": 1024
    }
    user_type = get_user_type(user_id)
    actual_limit = user_limits.get(user_type, 512)
    # ...レスポンス処理
```

## 制限事項と注意点

- 帯域制限はサーバーサイドで適用されるため、クライアント側の帯域幅やネットワーク状況によっては、実際の転送速度が変わる場合があります。
- 大きなファイル転送の場合は、メモリ使用量に注意してください。
- 分散システムの場合、各サーバーごとに制限が適用されます。

## APIリファレンス

このセクションでは、ライブラリが提供する主なクラスとメソッドの詳細なリファレンスを提供します。

### ResponseBandwidthLimiter

レスポンス帯域制限の機能を提供するメインクラスです。

```python
class ResponseBandwidthLimiter:
    def __init__(self, key_func=None):
        """
        レスポンス帯域幅制限機能を初期化します
        
        引数:
            key_func: 将来的な拡張用のキー関数（現在は使用されていません）
        """
        
    def limit(self, rate: int):
        """
        エンドポイントに対して帯域制限を適用するデコレータを返します
        
        引数:
            rate: 制限する速度（bytes/sec）
            
        戻り値:
            デコレータ関数
            
        例外:
            TypeError: rateが整数でない場合
        """
        
    def init_app(self, app):
        """
        FastAPIまたはStarletteアプリケーションにリミッターを登録します
        
        引数:
            app: FastAPIまたはStarletteアプリケーションインスタンス
        """
```

### ResponseBandwidthLimiterMiddleware

FastAPIおよびStarlette用のミドルウェアで、帯域制限を実際に適用します。

```python
class ResponseBandwidthLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        """
        帯域制限ミドルウェアを初期化します
        
        引数:
            app: FastAPIまたはStarletteアプリケーション
        """
        
    def get_handler_name(self, request, path):
        """
        パスに一致するハンドラー名を取得します
        
        引数:
            request: リクエストオブジェクト
            path: リクエストパス
            
        戻り値:
            str または None: エンドポイント名（存在する場合）
        """
        
    async def dispatch(self, request, call_next):
        """
        リクエストに対して帯域制限を適用します
        
        引数:
            request: リクエストオブジェクト
            call_next: 次のミドルウェア関数
            
        戻り値:
            レスポンスオブジェクト
        """
```

### set_response_bandwidth_limit

シンプルな帯域制限デコレータです。

```python
def set_response_bandwidth_limit(limit: int):
    """
    エンドポイントごとに帯域制限を設定するシンプルなデコレータ
    
    引数:
        limit: 制限する速度（bytes/sec）
        
    戻り値:
        デコレータ関数
    """
```

### ResponseBandwidthLimitExceeded

帯域制限超過時に発生する例外です。

```python
class ResponseBandwidthLimitExceeded(Exception):
    """
    帯域幅の制限を超過した場合に発生する例外
    
    引数:
        limit: 制限値（bytes/sec）
        endpoint: 制限が適用されたエンドポイント名
    """
```

### エラーハンドラ

```python
async def _response_bandwidth_limit_exceeded_handler(request, exc):
    """
    帯域幅制限超過時のエラーハンドラー
    
    引数:
        request: リクエストオブジェクト
        exc: ResponseBandwidthLimitExceeded例外
        
    戻り値:
        JSONResponse: HTTPステータスコード429と説明
    """
```

### ユーティリティ関数

```python
def get_endpoint_name(request):
    """
    リクエストからエンドポイント名を取得します
    
    引数:
        request: リクエストオブジェクト
    
    戻り値:
        str: エンドポイント名
    """
    
def get_route_path(request):
    """
    リクエストからルートパスを取得します
    
    引数:
        request: リクエストオブジェクト
        
    戻り値:
        str: ルートパス
    """
```

## 謝辞

このライブラリは [slowapi](https://github.com/laurentS/slowapi) (MIT Licensed) にインスパイアされました。

## ライセンス

MPL-2.0
