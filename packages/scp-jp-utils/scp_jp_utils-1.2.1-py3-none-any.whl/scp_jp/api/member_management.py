from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, HttpUrl


class PermissionLevel(IntEnum):
    VISITOR = 10
    CONTRIBUTOR = 20
    MODERATOR = 30
    ADMIN = 40
    SYSTEM_ADMIN = 50


class Status(IntEnum):
    PENDING = 0
    APPROVED = 1
    DECLINED = 2
    CANCELLED_OR_MISSING = 9


class DeclineReasonType(IntEnum):
    INCORRECT_PASSWORD = 1
    REASON_NOT_SPECIFIED_OR_INAPPROPRIATE = 2
    ROLL_PLAYING = 3
    INCORRECT_JAPANESE = 4
    CONTAINING_SENSITIVE_INFORMATION = 5
    FOR_CONTACT = 6
    OTHER = 9


# Schema models
class Site(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class SiteCreate(BaseModel):
    id: int
    name: str


class SiteUpdate(BaseModel):
    name: str


class SiteWithMembersCount(BaseModel):
    id: int
    name: str
    members_count: int
    created_at: datetime
    updated_at: datetime


class DailyMemberCount(BaseModel):
    date: str
    count: int


class SiteMembersStats(BaseModel):
    current_count: int
    daily_counts: List[DailyMemberCount]


class SiteMemberPermissionUpdate(BaseModel):
    site_permission_level: PermissionLevel


class SiteMember(BaseModel):
    id: int
    site_id: int
    user_id: int
    is_resigned: bool = False
    site_permission_level: Optional[PermissionLevel] = None
    effective_permission_level: PermissionLevel
    joined_at: datetime
    created_at: datetime
    updated_at: datetime


class SiteMemberPrivilegeAction(BaseModel):
    action: str


class User(BaseModel):
    id: int
    name: str
    unix_name: str
    avatar_url: HttpUrl
    is_deleted: bool = False
    permission_level: PermissionLevel = PermissionLevel.VISITOR
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    id: int
    name: str
    unix_name: str
    avatar_url: HttpUrl
    is_deleted: bool = False
    permission_level: PermissionLevel = PermissionLevel.VISITOR


class UserUpdate(BaseModel):
    name: Optional[str] = None
    unix_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    is_deleted: Optional[bool] = None
    permission_level: Optional[PermissionLevel] = None


class UserPermissionUpdate(BaseModel):
    permission_level: PermissionLevel


class UserWithSiteMemberships(BaseModel):
    id: int
    name: str
    unix_name: str
    avatar_url: HttpUrl
    is_deleted: bool = False
    permission_level: PermissionLevel = PermissionLevel.VISITOR
    site_memberships: List[Any]
    created_at: datetime
    updated_at: datetime


class ApplicationPassword(BaseModel):
    id: int
    site_id: int
    password: str
    is_enabled: bool = True
    created_at: datetime
    updated_at: datetime


class ApplicationPasswordCreate(BaseModel):
    site_id: int
    password: str
    is_enabled: bool = True


class ApplicationPasswordUpdate(BaseModel):
    password: str


class SiteApplicationAccept(BaseModel):
    reviewer_id: int


class SiteApplicationDecline(BaseModel):
    reviewer_id: int
    decline_reason_type: DeclineReasonType
    decline_reason_detail: str


class SiteApplicationWithDetails(BaseModel):
    id: int
    status: Status
    acquired_at: datetime
    text: str
    decline_reason_type: Optional[DeclineReasonType] = None
    decline_reason_detail: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[Dict[str, Any]] = None
    site: Dict[str, Any]
    user: Dict[str, Any]
    password: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BatchStatusResponseSchema(BaseModel):
    name: str
    next_run_time: datetime


class BatchStatusesResponseSchema(BaseModel):
    statuses: List[BatchStatusResponseSchema]


class BatchForceStartResponseSchema(BaseModel):
    status: str


class MemberManagementAPIClient:
    """
    SCP-JP メンバー管理APIと連携するためのクライアント。
    """

    def __init__(self, base_url: str, api_key: str):
        """
        APIクライアントを初期化します。

        Args:
            base_url: メンバー管理APIのベースURL。
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

    # System endpoints
    async def get_batch_status(self) -> BatchStatusesResponseSchema:
        """
        バッチプロセスのステータスを取得します。

        Returns:
            バッチステータスのリスト
        """
        response = await self._make_request("GET", "/v1/system/batch/status")
        return BatchStatusesResponseSchema.model_validate(response.json())

    async def force_start_batch(self, task_name: str) -> BatchForceStartResponseSchema:
        """
        バッチプロセスを強制的に開始します。

        Args:
            task_name: 開始するタスクの名前

        Returns:
            強制開始のレスポンス

        Raises:
            httpx.HTTPStatusError: タスクが見つからない場合（404）
        """
        response = await self._make_request(
            "POST", f"/v1/system/batch/force_start/{task_name}"
        )
        return BatchForceStartResponseSchema.model_validate(response.json())

    # Sites endpoints
    async def get_sites(self) -> List[SiteWithMembersCount]:
        """
        すべてのサイトを取得します。

        Returns:
            メンバー数を含むサイトのリスト
        """
        response = await self._make_request("GET", "/v1/sites/")
        return [SiteWithMembersCount.model_validate(site) for site in response.json()]

    async def create_site(self, site_id: int, name: str) -> Site:
        """
        新しいサイトを作成します。

        Args:
            site_id: サイトのID
            name: サイトの名前

        Returns:
            作成されたサイト

        Raises:
            httpx.HTTPStatusError: 指定されたIDのサイトが既に存在する場合（400）
        """
        site_data = SiteCreate(id=site_id, name=name)
        response = await self._make_request(
            "POST", "/v1/sites/", json_data=site_data.model_dump()
        )
        return Site.model_validate(response.json())

    async def update_site(self, site_id: int, name: str) -> Site:
        """
        サイトを更新します。

        Args:
            site_id: 更新するサイトのID
            name: サイトの新しい名前

        Returns:
            更新されたサイト

        Raises:
            httpx.HTTPStatusError: 指定されたIDのサイトが見つからない場合（404）
        """
        site_data = SiteUpdate(name=name)
        response = await self._make_request(
            "PATCH", f"/v1/sites/{site_id}", json_data=site_data.model_dump()
        )
        return Site.model_validate(response.json())

    async def get_site_members_stats(
        self,
        site_id: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> SiteMembersStats:
        """
        サイトメンバーの統計を取得します。

        Args:
            site_id: サイトのID
            from_date: 統計の開始日（オプション）
            to_date: 統計の終了日（オプション）

        Returns:
            サイトメンバーの統計

        Raises:
            httpx.HTTPStatusError: 指定されたIDのサイトが見つからない場合（404）
        """
        params = {}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date

        response = await self._make_request(
            "GET", f"/v1/sites/{site_id}/members/stats", params=params
        )
        return SiteMembersStats.model_validate(response.json())

    async def update_site_member_permission(
        self, site_id: int, user_id: int, site_permission_level: PermissionLevel
    ) -> SiteMember:
        """
        サイトメンバーの権限を更新します。

        Args:
            site_id: サイトのID
            user_id: ユーザーのID
            site_permission_level: 設定する権限レベル

        Returns:
            更新されたサイトメンバー

        Raises:
            httpx.HTTPStatusError: サイトまたはユーザーが見つからない場合、またはユーザーがサイトのメンバーでない場合（404）
        """
        permission_data = SiteMemberPermissionUpdate(
            site_permission_level=site_permission_level
        )
        response = await self._make_request(
            "PATCH",
            f"/v1/sites/{site_id}/members/{user_id}/permission",
            json_data=permission_data.model_dump(),
        )
        return SiteMember.model_validate(response.json())

    async def check_site_member_permission(
        self, site_id: int, user_id: int, permission_level: PermissionLevel
    ) -> bool:
        """
        サイトメンバーが特定の権限レベルを持っているかどうかを確認します。

        Args:
            site_id: サイトのID
            user_id: ユーザーのID
            permission_level: 確認する権限レベル

        Returns:
            ユーザーが指定された権限レベルを持っている場合はTrue、そうでない場合はFalse

        Raises:
            httpx.HTTPStatusError: サイトまたはユーザーが見つからない場合、またはユーザーがサイトのメンバーでない場合（404）
        """
        response = await self._make_request(
            "GET",
            f"/v1/sites/{site_id}/members/{user_id}/permission/check",
            params={"permission_level": permission_level.value},
        )
        return response.json()["has_permission"]

    async def change_site_member_privilege(
        self, site_id: int, user_id: int, action: str
    ) -> Dict[str, str]:
        """
        サイトメンバーの権限を変更します。

        Args:
            site_id: サイトのID
            user_id: ユーザーのID
            action: 実行するアクション

        Returns:
            権限変更アクションの結果

        Raises:
            httpx.HTTPStatusError: 様々なエラー条件（400、403、404、500）
        """
        try:
            action_data = SiteMemberPrivilegeAction(action=action)
            response = await self._make_request(
                "POST",
                f"/v1/sites/{site_id}/members/{user_id}/privilege",
                json_data=action_data.model_dump(),
            )
            return response.json()
        except httpx.HTTPStatusError:
            # Handle specific error cases or re-raise
            raise

    # Users endpoints
    async def create_user(
        self,
        user_id: int,
        name: str,
        unix_name: str,
        avatar_url: str,
        is_deleted: bool = False,
        permission_level: PermissionLevel = PermissionLevel.VISITOR,
    ) -> User:
        """
        新しいユーザーを作成します。

        Args:
            user_id: ユーザーのID
            name: ユーザー名
            unix_name: Unixユーザー名
            avatar_url: アバター画像のURL
            is_deleted: 削除状態かどうか
            permission_level: 権限レベル

        Returns:
            作成されたユーザー

        Raises:
            httpx.HTTPStatusError: 指定されたIDのユーザーが既に存在する場合（400）
        """

        user_data = UserCreate(
            id=user_id,
            name=name,
            unix_name=unix_name,
            avatar_url=HttpUrl(url=avatar_url),
            is_deleted=is_deleted,
            permission_level=permission_level,
        )
        response = await self._make_request(
            "POST", "/v1/users/", json_data=user_data.model_dump()
        )
        return User.model_validate(response.json())

    async def get_users(
        self,
        per_page: int = 100,
        page: int = 1,
        order_by: str = "created_at",
        order: str = "desc",
        id: Optional[int] = None,
        name: Optional[str] = None,
        unix_name: Optional[str] = None,
        permission_levels: Optional[List[PermissionLevel]] = None,
        is_deleted: Optional[bool] = None,
        site_ids: Optional[List[int]] = None,
    ) -> List[UserWithSiteMemberships]:
        """
        フィルター条件に基づいてユーザーを取得します。

        Args:
            per_page: ページあたりのユーザー数
            page: ページ番号
            order_by: 並べ替えのフィールド
            order: 並べ替え順序（"asc"または"desc"）
            id: ユーザーIDでフィルタリング
            name: 名前でフィルタリング
            unix_name: Unixユーザー名でフィルタリング
            permission_levels: 権限レベルでフィルタリング
            is_deleted: 削除状態でフィルタリング
            site_ids: サイトIDでフィルタリング

        Returns:
            サイトメンバーシップ情報を含むユーザーのリスト
        """
        params = {
            "per_page": per_page,
            "page": page,
            "order_by": order_by,
            "order": order,
        }

        if id is not None:
            params["id"] = id
        if name is not None:
            params["name"] = name
        if unix_name is not None:
            params["unix_name"] = unix_name
        if permission_levels is not None:
            params["permission_levels"] = [level.value for level in permission_levels]
        if is_deleted is not None:
            params["is_deleted"] = is_deleted
        if site_ids is not None:
            params["site_ids"] = site_ids

        response = await self._make_request("GET", "/v1/users/", params=params)
        return [
            UserWithSiteMemberships.model_validate(user) for user in response.json()
        ]

    async def get_user(self, user_id: int) -> UserWithSiteMemberships:
        """
        IDでユーザーを取得します。

        Args:
            user_id: ユーザーのID

        Returns:
            サイトメンバーシップ情報を含むユーザー

        Raises:
            httpx.HTTPStatusError: 指定されたIDのユーザーが見つからない場合（404）
        """
        response = await self._make_request("GET", f"/v1/users/{user_id}")
        return UserWithSiteMemberships.model_validate(response.json())

    async def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        unix_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        is_deleted: Optional[bool] = None,
        permission_level: Optional[PermissionLevel] = None,
    ) -> User:
        """
        ユーザーを更新します。

        Args:
            user_id: 更新するユーザーのID
            name: 新しいユーザー名
            unix_name: 新しいUnixユーザー名
            avatar_url: 新しいアバター画像のURL
            is_deleted: 新しい削除状態
            permission_level: 新しい権限レベル

        Returns:
            更新されたユーザー

        Raises:
            httpx.HTTPStatusError: 指定されたIDのユーザーが見つからない場合（404）
        """
        user_data = UserUpdate()
        if name is not None:
            user_data.name = name
        if unix_name is not None:
            user_data.unix_name = unix_name
        if avatar_url is not None:
            user_data.avatar_url = HttpUrl(url=avatar_url)
        if is_deleted is not None:
            user_data.is_deleted = is_deleted
        if permission_level is not None:
            user_data.permission_level = permission_level

        response = await self._make_request(
            "PATCH",
            f"/v1/users/{user_id}",
            json_data=user_data.model_dump(exclude_unset=True),
        )
        return User.model_validate(response.json())

    async def update_user_permission(
        self, user_id: int, permission_level: PermissionLevel
    ) -> User:
        """
        ユーザーの権限レベルを更新します。

        Args:
            user_id: ユーザーのID
            permission_level: 設定する権限レベル

        Returns:
            更新されたユーザー

        Raises:
            httpx.HTTPStatusError: 指定されたIDのユーザーが見つからない場合（404）
        """
        permission_data = UserPermissionUpdate(permission_level=permission_level)
        response = await self._make_request(
            "PATCH",
            f"/v1/users/{user_id}/permission",
            json_data=permission_data.model_dump(),
        )
        return User.model_validate(response.json())

    async def check_user_permission(
        self, user_id: int, permission_level: PermissionLevel
    ) -> bool:
        """
        ユーザーが特定の権限レベルを持っているかどうかを確認します。

        Args:
            user_id: ユーザーのID
            permission_level: 確認する権限レベル

        Returns:
            ユーザーが指定された権限レベルを持っている場合はTrue、そうでない場合はFalse

        Raises:
            httpx.HTTPStatusError: 指定されたIDのユーザーが見つからない場合（404）
        """
        response = await self._make_request(
            "GET",
            f"/v1/users/{user_id}/permission/check",
            params={"permission_level": permission_level.value},
        )
        return response.json()["has_permission"]

    # Application password endpoints
    async def create_application_password(
        self, site_id: int, password: str, is_enabled: bool = True
    ) -> ApplicationPassword:
        """
        新しい合言葉を作成します。

        Args:
            site_id: サイトのID
            password: 合言葉のテキスト
            is_enabled: 有効かどうか

        Returns:
            作成された合言葉

        Raises:
            httpx.HTTPStatusError: 指定されたIDのサイトが見つからない場合（404）
        """
        password_data = ApplicationPasswordCreate(
            site_id=site_id, password=password, is_enabled=is_enabled
        )
        response = await self._make_request(
            "POST", "/v1/application/passwords/", json_data=password_data.model_dump()
        )
        return ApplicationPassword.model_validate(response.json())

    async def get_application_passwords(
        self,
        per_page: int = 100,
        page: int = 1,
        order_by: str = "created_at",
        order: str = "desc",
        site_id: Optional[int] = None,
        password: Optional[str] = None,
        is_enabled: Optional[bool] = None,
    ) -> List[ApplicationPassword]:
        """
        フィルター条件に基づいて合言葉を取得します。

        Args:
            per_page: ページあたりの合言葉数
            page: ページ番号
            order_by: 並べ替えのフィールド
            order: 並べ替え順序（"asc"または"desc"）
            site_id: サイトIDでフィルタリング
            password: 合言葉のテキストでフィルタリング
            is_enabled: 有効状態でフィルタリング

        Returns:
            合言葉のリスト
        """
        params = {
            "per_page": per_page,
            "page": page,
            "order_by": order_by,
            "order": order,
        }

        if site_id is not None:
            params["site_id"] = site_id
        if password is not None:
            params["password"] = password
        if is_enabled is not None:
            params["is_enabled"] = is_enabled

        response = await self._make_request(
            "GET", "/v1/application/passwords/", params=params
        )
        return [ApplicationPassword.model_validate(pw) for pw in response.json()]

    async def toggle_application_password(
        self, password_id: int
    ) -> ApplicationPassword:
        """
        合言葉の有効状態を切り替えます。

        Args:
            password_id: 切り替える合言葉のID

        Returns:
            更新された合言葉

        Raises:
            httpx.HTTPStatusError: 指定されたIDの合言葉が見つからない場合（404）
        """
        response = await self._make_request(
            "PATCH", f"/v1/application/passwords/{password_id}/toggle"
        )
        return ApplicationPassword.model_validate(response.json())

    async def update_application_password(
        self, password_id: int, password: str
    ) -> ApplicationPassword:
        """
        合言葉を更新します。

        Args:
            password_id: 更新する合言葉のID
            password: 新しい合言葉のテキスト

        Returns:
            更新された合言葉

        Raises:
            httpx.HTTPStatusError: 合言葉が見つからないか、既にユーザーに割り当てられている場合（404）
        """
        password_data = ApplicationPasswordUpdate(password=password)
        response = await self._make_request(
            "PATCH",
            f"/v1/application/passwords/{password_id}",
            json_data=password_data.model_dump(),
        )
        return ApplicationPassword.model_validate(response.json())

    # Application requests endpoints
    async def get_application_requests(
        self,
        per_page: int = 100,
        page: int = 1,
        order_by: str = "created_at",
        order: str = "desc",
        user_id: Optional[int] = None,
        site_id: Optional[int] = None,
        statuses: Optional[List[Status]] = None,
        decline_reason_types: Optional[List[DeclineReasonType]] = None,
    ) -> List[SiteApplicationWithDetails]:
        """
        フィルター条件に基づいて参加申請を取得します。

        Args:
            per_page: ページあたりの申請数
            page: ページ番号
            order_by: 並べ替えのフィールド
            order: 並べ替え順序（"asc"または"desc"）
            user_id: ユーザーIDでフィルタリング
            site_id: サイトIDでフィルタリング
            statuses: ステータスでフィルタリング
            decline_reason_types: 拒否理由タイプでフィルタリング

        Returns:
            詳細情報を含む参加申請のリスト
        """
        params = {
            "per_page": per_page,
            "page": page,
            "order_by": order_by,
            "order": order,
        }

        if user_id is not None:
            params["user_id"] = user_id
        if site_id is not None:
            params["site_id"] = site_id
        if statuses is not None:
            params["statuses"] = [status.value for status in statuses]
        if decline_reason_types is not None:
            params["decline_reason_types"] = [
                reason.value for reason in decline_reason_types
            ]

        response = await self._make_request(
            "GET", "/v1/application/requests/", params=params
        )
        return [
            SiteApplicationWithDetails.model_validate(req) for req in response.json()
        ]

    async def get_decline_reason_types(self) -> Dict[str, str]:
        """
        拒否理由タイプを取得します。

        Returns:
            拒否理由タイプIDから説明へのマップ
        """
        response = await self._make_request(
            "GET", "/v1/application/requests/decline_reason_types"
        )
        return response.json()

    async def get_application_request(
        self, request_id: int
    ) -> SiteApplicationWithDetails:
        """
        IDで参加申請を取得します。

        Args:
            request_id: 申請のID

        Returns:
            詳細情報を含む参加申請

        Raises:
            httpx.HTTPStatusError: 指定されたIDの申請が見つからない場合（404）
        """
        response = await self._make_request(
            "GET", f"/v1/application/requests/{request_id}"
        )
        return SiteApplicationWithDetails.model_validate(response.json())

    async def approve_application_request(
        self, request_id: int, reviewer_id: int
    ) -> Dict[str, str]:
        """
        参加申請を承認します。

        Args:
            request_id: 承認する申請のID
            reviewer_id: レビュアーのユーザーID

        Returns:
            結果メッセージ

        Raises:
            httpx.HTTPStatusError: 様々なエラー条件（400、403、404）
        """
        try:
            approval_data = SiteApplicationAccept(reviewer_id=reviewer_id)
            response = await self._make_request(
                "POST",
                f"/v1/application/requests/{request_id}/approve",
                json_data=approval_data.model_dump(),
            )
            return response.json()
        except httpx.HTTPStatusError:
            # 特定のエラーケースを処理するか、再度発生させる
            raise

    async def decline_application_request(
        self,
        request_id: int,
        reviewer_id: int,
        decline_reason_type: DeclineReasonType,
        decline_reason_detail: str,
    ) -> Dict[str, str]:
        """
        参加申請を拒否します。

        Args:
            request_id: 拒否する申請のID
            reviewer_id: レビュアーのユーザーID
            decline_reason_type: 拒否理由タイプ
            decline_reason_detail: 拒否理由の詳細

        Returns:
            結果メッセージ

        Raises:
            httpx.HTTPStatusError: 様々なエラー条件（400、403、404）
        """
        try:
            decline_data = SiteApplicationDecline(
                reviewer_id=reviewer_id,
                decline_reason_type=decline_reason_type,
                decline_reason_detail=decline_reason_detail,
            )
            response = await self._make_request(
                "POST",
                f"/v1/application/requests/{request_id}/decline",
                json_data=decline_data.model_dump(),
            )
            return response.json()
        except httpx.HTTPStatusError:
            # 特定のエラーケースを処理するか、再度発生させる
            raise
