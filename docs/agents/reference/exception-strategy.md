# 例外戦略

## 設計方針

例外は **3 層に分離** し、各層で適切な例外を使い分ける。
上位層の例外が下位層に漏れないよう、Router で変換する。

## 例外クラス階層

```
Exception
├── DomainError          # Domain 層: 不変条件違反
└── ApplicationError     # Application 層: ビジネスロジックエラー
    ├── NotFoundError    # リソース未発見
    └── ConflictError    # リソース競合（重複等）
```

### DomainError

- **場所**: `src/core/shared/exceptions.py`
- **用途**: Entity の不変条件違反（バリデーションエラー）
- **属性**: `message: str`

```python
class DomainError(Exception):
    message: str
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
```

### ApplicationError

- **場所**: `src/core/shared/exceptions.py`
- **用途**: ビジネスロジックの失敗（リソース未発見、重複等）
- **属性**: `message: str`, `resource_id: str | None`

```python
class ApplicationError(Exception):
    message: str
    resource_id: str | None
    def __init__(self, message: str, resource_id: str | None = None) -> None:
        self.message = message
        self.resource_id = resource_id
        super().__init__(message)
```

### NotFoundError / ConflictError

`ApplicationError` のサブクラス。`resource_id` を必須にし、デフォルトメッセージを提供する。

```python
class NotFoundError(ApplicationError):
    def __init__(self, resource_id: str, message: str | None = None) -> None:
        resolved = message or f"指定されたリソースが見つかりません: {resource_id}"
        super().__init__(resolved, resource_id=resource_id)

class ConflictError(ApplicationError):
    def __init__(self, resource_id: str, message: str | None = None) -> None:
        resolved = message or f"指定されたリソースはすでに存在します: {resource_id}"
        super().__init__(resolved, resource_id=resource_id)
```

## Router での例外変換

Router で domain/application 例外を `HTTPException` に変換する。
`NoReturn` 型ヒント付きのヘルパー関数を使う。

```python
from typing import NoReturn
from fastapi import HTTPException, status

def _raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

def _raise_conflict(detail: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
```

Router 内での使用:

```python
try:
    entity = await usecase.execute(video_id)
except NotFoundError as exc:
    _raise_not_found(exc.message)
except ConflictError as exc:
    _raise_conflict(exc.message)
```

## 各層で使用する例外

| 層 | raise する例外 | catch する例外 |
|---|---|---|
| Domain (Entity) | `DomainError`, `ValueError`, `TypeError` | — |
| Application (Usecase) | `NotFoundError`, `ConflictError`, `ApplicationError` | `DomainError`（必要時） |
| Inbound Adapter (Router) | `HTTPException` | `NotFoundError`, `ConflictError`, `AlreadyExistsError` |
| Outbound Adapter | `ApplicationError` のサブクラス | I/O 例外 |

## やってはいけないこと

- Domain / Usecase で `HTTPException` を raise する
- Router 以外で `HTTPException` を catch/raise する
- `ApplicationError` を直接 raise せず、適切なサブクラスを使う
- `DomainError` を Router まで伝播させる（Usecase で catch して適切な `ApplicationError` に変換する）
