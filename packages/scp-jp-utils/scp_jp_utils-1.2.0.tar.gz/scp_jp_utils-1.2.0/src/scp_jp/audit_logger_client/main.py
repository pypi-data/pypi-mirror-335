import httpx


class AuditLoggerClient:
    def __init__(self, endpoint_url: str, app_name: str, api_key: str):
        self.endpoint_url = endpoint_url
        self.app_name = app_name
        self.api_key = api_key

    def log(
        self,
        action: str,
        message: str,
        notes: str = "",
        ip_address: str = "",
    ) -> bool:
        response = httpx.post(
            self.endpoint_url,
            headers={
                "X-AppName": self.app_name,
                "X-AppKey": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "app_name": self.app_name,
                "action": action,
                "message": message,
                "notes": notes,
                "ip_address": ip_address,
            },
        )

        # responseが201であることを確認
        if response.status_code != 201:
            raise Exception(f"Failed to log: {response.text}")

        return True


class PseudoAuditLoggerClient:
    def __init__(self):
        pass

    def log(
        self,
        action: str,
        message: str,
        notes: str = "",
        ip_address: str = "",
    ) -> bool:
        return True
