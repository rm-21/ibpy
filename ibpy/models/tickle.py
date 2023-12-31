# generated by datamodel-codegen:
#   filename:  tickle.json
#   timestamp: 2023-08-25T10:35:59+00:00

from pydantic import BaseModel, Field


class Hmds(BaseModel):
    error: str


class ServerInfo(BaseModel):
    server_name: str = Field(..., alias="serverName")
    server_version: str = Field(..., alias="serverVersion")


class AuthStatus(BaseModel):
    authenticated: bool
    competing: bool
    connected: bool
    message: str
    mac: str = Field(..., alias="MAC")
    server_info: ServerInfo = Field(..., alias="serverInfo")


class Iserver(BaseModel):
    auth_status: AuthStatus = Field(..., alias="authStatus")


class Tickle(BaseModel):
    session: str
    sso_expires: int = Field(..., alias="ssoExpires")
    collission: bool
    user_id: int = Field(..., alias="userId")
    hmds: Hmds
    iserver: Iserver
