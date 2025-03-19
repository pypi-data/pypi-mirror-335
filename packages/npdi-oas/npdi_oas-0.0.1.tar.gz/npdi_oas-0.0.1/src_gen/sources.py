from pydantic import BaseModel, Field
from typing import Any
from pagination import PaginatedResponse


class BaseSource(BaseModel):
    name: str | None = Field(None, description="Name of the source organization.")
    bio: str | None = Field(None, description="Description of the source organization.")
    website_url: str | None = Field(None, description="Website URL of the source.")
    contact_email: str | None = Field(None, description="Contact email for the source organization.")
    contact_phone: str | None = Field(None, description="Contact phone number for the source organization.")
    social_media: dict[str, Any] | None = Field(None, description="The user's social media profiles.")


class CreateSource(BaseSource, BaseModel):
    name: str | None = Field(None, description="Name of the source organization.")
    bio: str | None = Field(None, description="Description of the source organization.")
    website_url: str | None = Field(None, description="Website URL of the source.")
    contact_email: str | None = Field(None, description="Contact email for the source organization.")
    contact_phone: str | None = Field(None, description="Contact phone number for the source organization.")
    social_media: dict[str, Any] | None = Field(None, description="The user's social media profiles.")


class UpdateSource(BaseSource, BaseModel):
    name: str | None = Field(None, description="Name of the source organization.")
    bio: str | None = Field(None, description="Description of the source organization.")
    website_url: str | None = Field(None, description="Website URL of the source.")
    contact_email: str | None = Field(None, description="Contact email for the source organization.")
    contact_phone: str | None = Field(None, description="Contact phone number for the source organization.")
    social_media: dict[str, Any] | None = Field(None, description="The user's social media profiles.")


class Source(BaseSource, BaseModel):
    name: str | None = Field(None, description="Name of the source organization.")
    bio: str | None = Field(None, description="Description of the source organization.")
    website_url: str | None = Field(None, description="Website URL of the source.")
    contact_email: str | None = Field(None, description="Contact email for the source organization.")
    contact_phone: str | None = Field(None, description="Contact phone number for the source organization.")
    social_media: dict[str, Any] | None = Field(None, description="The user's social media profiles.")
    uid: str | None = Field(None, description="Unique identifier for the source.")
    members: str | None = Field(None, description="Url to get all members of the source.")
    reported_complaints: str | None = Field(None, description="Url to get all complaints reported by the source.")


class SourceList(PaginatedResponse, BaseModel):
    results: list[Source] | None = None


class MemberBase(BaseModel):
    source_uid: str | None = Field(None, description="Unique identifier for the source.")
    user_uid: str | None = Field(None, description="Unique identifier for the user.")
    role: str | None = Field(None, description="Role of the user.")
    is_active: bool | None = Field(None, description="Whether the user is active.")


class Member(MemberBase, BaseModel):
    source_uid: str | None = Field(None, description="Unique identifier for the source.")
    user_uid: str | None = Field(None, description="Unique identifier for the user.")
    role: str | None = Field(None, description="Role of the user.")
    is_active: bool | None = Field(None, description="Whether the user is active.")
    uid: str | None = Field(None, description="Unique identifier for the user.")
    date_joined: str | None = Field(None, description="Date the user joined the source organization.")


class AddMember(MemberBase, BaseModel):
    source_uid: str | None = Field(None, description="Unique identifier for the source.")
    user_uid: str | None = Field(None, description="Unique identifier for the user.")
    role: str | None = Field(None, description="Role of the user.")
    is_active: bool | None = Field(None, description="Whether the user is active.")


class MemberList(PaginatedResponse, BaseModel):
    results: list[Member] | None = None


