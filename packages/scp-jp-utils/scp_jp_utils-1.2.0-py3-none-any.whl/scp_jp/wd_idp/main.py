import base64
import hashlib
from dataclasses import dataclass

import httpx


@dataclass
class WikidotUserClass:
    name: str
    unix_name: str
    id: int


class WikidotIdPClient:
    def __init__(
        self,
        endpoint: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ):
        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @staticmethod
    def create_code_challenge(code_verifier: str, code_challenge_method: str) -> str:
        if code_challenge_method == "plain":
            return code_verifier

        elif code_challenge_method == "S256":
            sha256 = hashlib.sha256()
            sha256.update(code_verifier.encode())
            code_verifier_hash = sha256.digest()

            code_challenge_hash = (
                base64.urlsafe_b64encode(code_verifier_hash).decode().rstrip("=")
            )

            return code_challenge_hash

        else:
            raise ValueError("invalid code_challenge_method")

    def get_authorization_url(
        self,
        code_challenge_method: str,
        code_challenge: str,
        state: str,
    ) -> str:
        return (
            f"{self.endpoint}/authorize"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=identify"
            f"&state={state}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method={code_challenge_method}"
        )

    def get_user(self, code: str, code_verifier: str) -> WikidotUserClass:
        userinfo_request = httpx.post(
            f"{self.endpoint}/user",
            json={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "code_verifier": code_verifier,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            },
        )

        userinfo_request.raise_for_status()

        userinfo = userinfo_request.json()

        return WikidotUserClass(
            name=userinfo["name"],
            unix_name=userinfo["unix_name"],
            id=userinfo["id"],
        )
