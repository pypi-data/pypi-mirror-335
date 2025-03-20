from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from . import OrganizationId, Paged, PagedRequest, PagedResponse, ServiceBase


class OrganizationRole(Enum):
    OWNER = "owner"
    MEMBER = "member"
    GUEST = "guest"


class Organization(BaseModel):
    id: OrganizationId
    name: str | None = Field(
        default=None,
        description="Optional human-readable name for the organization",
    )


class OrganizationMembership(BaseModel):
    organization: Organization
    role: str = Field(description="The user's role in the organization")


class CreateOrganization:
    class Request(BaseModel):
        name: str | None = Field(
            default=None,
            description="Optional human-readable name for the organization",
        )

    class Response(BaseModel):
        organization: Organization


class ListUserMemberships:
    class Request(PagedRequest):
        """List the organization memberships of the current user."""

    class Response(PagedResponse[OrganizationMembership]):
        """The user's organization memberships."""


class PortalLink:
    class Intent(Enum):
        SSO = "sso"
        DIRECTORY = "directory"
        AUDIT_LOGS = "audit-logs"
        LOG_STREAMS = "log-streams"
        DOMAIN_VERIFICATION = "domain-verification"

    class Request(BaseModel):
        intent: "PortalLink.Intent"

    class Response(BaseModel):
        url: str


class InviteUser:
    class Request(BaseModel):
        email: EmailStr
        role: OrganizationRole
        expires_in_days: int = 7

    class Response(BaseModel):
        invite_id: str


class OrganizationService(ServiceBase):
    def create_organization(self, request: CreateOrganization.Request) -> CreateOrganization.Response:
        """Create a new organization."""
        return self.client.post("/organization/create", request, CreateOrganization.Response)

    def list_user_memberships(self) -> Paged[OrganizationMembership]:
        """List organizations that the user is a member of."""
        return self.client.paged(
            "/organization/list-user-memberships",
            ListUserMemberships.Request(),
            ListUserMemberships.Response,
        )

    def portal_link(self, request: PortalLink.Request) -> PortalLink.Response:
        """Get a link to the organization configuration portal."""
        return self.client.put("/organization/portal-link", request, PortalLink.Response)

    def invite_user(self, request: InviteUser.Request) -> InviteUser.Response:
        """Invite a user to the organization."""
        return self.client.post("/organization/invite-user", request, InviteUser.Response)
