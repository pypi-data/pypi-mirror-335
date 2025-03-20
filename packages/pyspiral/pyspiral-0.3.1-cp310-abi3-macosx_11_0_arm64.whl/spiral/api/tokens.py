from pydantic import BaseModel

from . import Paged, PagedRequest, PagedResponse, ServiceBase


class Token(BaseModel):
    id: str
    project_id: str
    on_behalf_of: str


class ExchangeToken:
    class Request(BaseModel): ...

    class Response(BaseModel):
        token: str


class IssueToken:
    class Request(BaseModel): ...

    class Response(BaseModel):
        token: Token
        token_secret: str


class RevokeToken:
    class Request(BaseModel):
        token_id: str

    class Response(BaseModel):
        token: Token


class ListTokens:
    class Request(PagedRequest):
        project_id: str
        on_behalf_of: str | None = None

    class Response(PagedResponse[Token]): ...


class TokenService(ServiceBase):
    def exchange(self) -> ExchangeToken.Response:
        """Exchange a basic / identity token to a short-lived Spiral token."""
        return self.client.post("/token/exchange", ExchangeToken.Request(), ExchangeToken.Response)

    def issue(self) -> IssueToken.Response:
        """Issue an API token on behalf of a principal."""
        return self.client.post("/token/issue", IssueToken.Request(), IssueToken.Response)

    def revoke(self, request: RevokeToken.Request) -> RevokeToken.Response:
        return self.client.put("/token/revoke", request, RevokeToken.Response)

    def list(self, request: ListTokens.Request) -> Paged[Token]:
        return self.client.paged("/token/list", request, ListTokens.Response)
