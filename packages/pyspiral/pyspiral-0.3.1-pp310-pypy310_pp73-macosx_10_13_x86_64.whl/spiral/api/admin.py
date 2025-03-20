from pydantic import BaseModel

from . import OrganizationId, Paged, PagedRequest, PagedResponse, ServiceBase


class SyncOrgs:
    class Request(PagedRequest): ...

    class Response(PagedResponse[OrganizationId]): ...


class Membership(BaseModel):
    user_id: str
    organization_id: str


class SyncMemberships:
    class Request(PagedRequest):
        organization_id: OrganizationId | None = None

    class Response(PagedResponse[Membership]): ...


class AdminService(ServiceBase):
    def sync_orgs(self, request: SyncOrgs.Request) -> Paged[SyncOrgs.Response]:
        return self.client.paged("/admin/sync-orgs", request, SyncOrgs.Response)

    def sync_memberships(self, request: SyncMemberships.Request) -> Paged[Membership]:
        return self.client.paged("/admin/sync-memberships", request, SyncMemberships.Response)
