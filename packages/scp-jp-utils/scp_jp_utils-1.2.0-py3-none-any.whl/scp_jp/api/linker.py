from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


# Schema models
class DiscordAccountSchema(BaseModel):
    """
    Discordアカウントのスキーマ
    """

    id: str
    username: str
    avatar: str


class DiscordAccountSchemaForManage(BaseModel):
    """
    Discordアカウントの管理用スキーマ
    """

    id: str
    username: str
    avatar: str
    created_at: datetime
    updated_at: datetime
    unlinked_at: Optional[datetime] = None


class AccountResponseWikidotBaseSchema(BaseModel):
    """
    Botにレスポンスとして渡すためのWikidotアカウント情報のスキーマ
    """

    id: int
    username: str
    unixname: str
    is_jp_member: bool


class WikidotAccountSchemaForManage(BaseModel):
    """
    Wikidotアカウントの管理用スキーマ
    """

    id: int
    username: str
    unixname: str
    is_jp_member: bool
    created_at: datetime
    updated_at: datetime
    unlinked_at: Optional[datetime] = None


class FlowStartRequestSchema(BaseModel):
    """
    FlowStartのリクエスト
    """

    discord: DiscordAccountSchema


class FlowStartResponseSchema(BaseModel):
    """
    FlowStartのレスポンス
    """

    url: str


class FlowRecheckRequestSchema(BaseModel):
    """
    FlowRecheckのリクエスト
    """

    discord: DiscordAccountSchema


class FlowRecheckResponseSchema(BaseModel):
    """
    FlowRecheckのレスポンス
    """

    discord: DiscordAccountSchema
    wikidot: List[AccountResponseWikidotBaseSchema]


class AccountResponseFromDiscordSchema(BaseModel):
    """
    Discord IDを主語として、関連するアカウント情報を返す
    """

    discord: DiscordAccountSchema
    wikidot: List[AccountResponseWikidotBaseSchema]


class AccountListRequestSchema(BaseModel):
    """
    AccountCheckのリクエスト
    """

    discord_ids: List[str]


class AccountListResponseSchema(BaseModel):
    """
    AccountCheckのレスポンス
    """

    result: Dict[str, AccountResponseFromDiscordSchema]


class ListDiscordItemSchema(BaseModel):
    """
    Discordアカウントのリストの要素
    """

    discord: DiscordAccountSchema
    wikidot: List[WikidotAccountSchemaForManage]


class ListDiscordResponseSchema(BaseModel):
    """
    Discordアカウントのリスト
    """

    result: List[ListDiscordItemSchema]


class ListWikidotItemSchema(BaseModel):
    """
    Wikidotアカウントのリストの要素
    """

    discord: List[DiscordAccountSchemaForManage]
    wikidot: AccountResponseWikidotBaseSchema


class ListWikidotResponseSchema(BaseModel):
    """
    Wikidotアカウントのリスト
    """

    result: List[ListWikidotItemSchema]


class LinkerAPIClient:
    """
    SCP-JP アカウント連携APIと連携するためのクライアント。
    """

    def __init__(self, base_url: str, api_key: str):
        """
        APIクライアントを初期化します。

        Args:
            base_url: アカウント連携APIのベースURL。
            api_key: 認証用APIキー。
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}"}

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        APIにHTTPリクエストを送信します。

        Args:
            method: 使用するHTTPメソッド（GET、POSTなど）
            endpoint: 呼び出すAPIエンドポイント
            params: クエリパラメータ
            json_data: リクエストボディのJSONデータ

        Returns:
            HTTPレスポンス
        """
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=self._headers,
                timeout=30.0,
            )

            response.raise_for_status()
            return response

    # Flow endpoints
    async def flow_start(
        self, discord_id: str, discord_username: str, discord_avatar: str
    ) -> FlowStartResponseSchema:
        """
        連携フローを開始します。

        Args:
            discord_id: DiscordのユーザーID
            discord_username: Discordのユーザー名
            discord_avatar: Discordのアバター画像URL

        Returns:
            連携フロー開始レスポンス
        """
        discord_data = DiscordAccountSchema(
            id=discord_id, username=discord_username, avatar=discord_avatar
        )
        request_data = FlowStartRequestSchema(discord=discord_data)
        response = await self._make_request(
            "POST", "/v1/start", json_data=request_data.model_dump()
        )
        return FlowStartResponseSchema.model_validate(response.json())

    async def flow_auth(self, token: str) -> Dict[str, Any]:
        """
        連携フローの認証を行います。

        Args:
            token: 認証トークン

        Returns:
            認証結果
        """
        response = await self._make_request("GET", "/v1/auth", params={"token": token})
        return response.json()

    async def flow_callback(self, code: str, state: str) -> Dict[str, Any]:
        """
        連携フローのコールバックを処理します。

        Args:
            code: 認証コード
            state: 状態パラメータ

        Returns:
            コールバック処理結果
        """
        response = await self._make_request(
            "GET", "/v1/callback", params={"code": code, "state": state}
        )
        return response.json()

    async def flow_recheck(
        self, discord_id: str, discord_username: str, discord_avatar: str
    ) -> FlowRecheckResponseSchema:
        """
        連携状態を再確認します。

        Args:
            discord_id: DiscordのユーザーID
            discord_username: Discordのユーザー名
            discord_avatar: Discordのアバター画像URL

        Returns:
            連携状態再確認レスポンス
        """
        discord_data = DiscordAccountSchema(
            id=discord_id, username=discord_username, avatar=discord_avatar
        )
        request_data = FlowRecheckRequestSchema(discord=discord_data)
        response = await self._make_request(
            "POST", "/v1/recheck", json_data=request_data.model_dump()
        )
        return FlowRecheckResponseSchema.model_validate(response.json())

    # Account listing endpoints
    async def account_list(self, discord_ids: List[str]) -> AccountListResponseSchema:
        """
        Discord IDに紐づくアカウント情報を取得します。

        Args:
            discord_ids: 取得するDiscord IDのリスト

        Returns:
            アカウントリストレスポンス
        """
        request_data = AccountListRequestSchema(discord_ids=discord_ids)
        response = await self._make_request(
            "POST", "/v1/list", json_data=request_data.model_dump()
        )
        return AccountListResponseSchema.model_validate(response.json())

    async def discord_account_list(self) -> ListDiscordResponseSchema:
        """
        すべてのDiscordアカウント情報を取得します。

        Returns:
            Discordアカウントリストレスポンス
        """
        response = await self._make_request("GET", "/v1/list/discord")
        return ListDiscordResponseSchema.model_validate(response.json())

    async def wikidot_account_list(self) -> ListWikidotResponseSchema:
        """
        すべてのWikidotアカウント情報を取得します。

        Returns:
            Wikidotアカウントリストレスポンス
        """
        response = await self._make_request("GET", "/v1/list/wikidot")
        return ListWikidotResponseSchema.model_validate(response.json())

    # Account link management endpoints
    async def unlink_account(self, discord_id: int, wikidot_id: int) -> Dict[str, Any]:
        """
        Discord IDとWikidot IDの連携を解除します。

        Args:
            discord_id: Discord ID
            wikidot_id: Wikidot ID

        Returns:
            連携解除結果
        """
        response = await self._make_request(
            "PATCH",
            "/v1/unlink",
            params={"discord_id": discord_id, "wikidot_id": wikidot_id},
        )
        return response.json()

    async def relink_account(self, discord_id: int, wikidot_id: int) -> Dict[str, Any]:
        """
        Discord IDとWikidot IDの連携を復活させます。

        Args:
            discord_id: Discord ID
            wikidot_id: Wikidot ID

        Returns:
            連携復活結果
        """
        response = await self._make_request(
            "PATCH",
            "/v1/relink",
            params={"discord_id": discord_id, "wikidot_id": wikidot_id},
        )
        return response.json()

    # System endpoints
    async def healthcheck(self) -> Dict[str, Any]:
        """
        システムのヘルスチェックを行います。

        Returns:
            ヘルスチェック結果
        """
        response = await self._make_request("GET", "/system/healthcheck/")
        return response.json()
