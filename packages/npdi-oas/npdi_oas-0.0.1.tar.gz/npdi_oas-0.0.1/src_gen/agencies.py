from pydantic import BaseModel, Field
from typing import Any
from pagination import PaginatedResponse
from officers import Employment, Officer


class BaseAgency(BaseModel):
    name: str | None = Field(None, description="Name of the agency")
    hq_address: str | None = Field(None, description="Address of the agency")
    hq_city: str | None = Field(None, description="City of the agency")
    hq_state: str | None = Field(None, description="State of the agency")
    hq_zip: str | None = Field(None, description="Zip code of the agency")
    jurisdiction: str | None = Field(None, description="Jurisdiction of the agency")
    phone: str | None = Field(None, description="Phone number of the agency")
    email: str | None = Field(None, description="Email of the agency")
    website_url: str | None = Field(None, description="Website of the agency")


class CreateAgency(BaseAgency, BaseModel):
    name: str | None = Field(None, description="Name of the agency")
    hq_address: str | None = Field(None, description="Address of the agency")
    hq_city: str | None = Field(None, description="City of the agency")
    hq_state: str | None = Field(None, description="State of the agency")
    hq_zip: str | None = Field(None, description="Zip code of the agency")
    jurisdiction: str | None = Field(None, description="Jurisdiction of the agency")
    phone: str | None = Field(None, description="Phone number of the agency")
    email: str | None = Field(None, description="Email of the agency")
    website_url: str | None = Field(None, description="Website of the agency")


class UpdateAgency(BaseAgency, BaseModel):
    name: str | None = Field(None, description="Name of the agency")
    hq_address: str | None = Field(None, description="Address of the agency")
    hq_city: str | None = Field(None, description="City of the agency")
    hq_state: str | None = Field(None, description="State of the agency")
    hq_zip: str | None = Field(None, description="Zip code of the agency")
    jurisdiction: str | None = Field(None, description="Jurisdiction of the agency")
    phone: str | None = Field(None, description="Phone number of the agency")
    email: str | None = Field(None, description="Email of the agency")
    website_url: str | None = Field(None, description="Website of the agency")


class Agency(BaseAgency, BaseModel):
    name: str | None = Field(None, description="Name of the agency")
    hq_address: str | None = Field(None, description="Address of the agency")
    hq_city: str | None = Field(None, description="City of the agency")
    hq_state: str | None = Field(None, description="State of the agency")
    hq_zip: str | None = Field(None, description="Zip code of the agency")
    jurisdiction: str | None = Field(None, description="Jurisdiction of the agency")
    phone: str | None = Field(None, description="Phone number of the agency")
    email: str | None = Field(None, description="Email of the agency")
    website_url: str | None = Field(None, description="Website of the agency")
    uid: str | None = Field(None, description="Unique identifier for the agency")
    officers_url: str | None = Field(None, description="URL to get a list of officers for this agency")
    units_url: str | None = Field(None, description="URL to get a list of units for this agency")


class BaseUnit(BaseModel):
    """Base properties for a unit"""
    name: str | None = Field(None, description="Name of the unit")
    website_url: str | None = Field(None, description="Website of the unit")
    phone: str | None = Field(None, description="Phone number of the unit")
    email: str | None = Field(None, description="Email of the unit")
    description: str | None = Field(None, description="Description of the unit")
    address: str | None = Field(None, description="Street address of the unit")
    zip: str | None = Field(None, description="Zip code of the unit")
    date_established: str | None = Field(None, description="The date that this unit was established by its parent agency.")


class Unit(BaseUnit, BaseModel):
    name: str | None = Field(None, description="Name of the unit")
    website_url: str | None = Field(None, description="Website of the unit")
    phone: str | None = Field(None, description="Phone number of the unit")
    email: str | None = Field(None, description="Email of the unit")
    description: str | None = Field(None, description="Description of the unit")
    address: str | None = Field(None, description="Street address of the unit")
    zip: str | None = Field(None, description="Zip code of the unit")
    date_established: str | None = Field(None, description="The date that this unit was established by its parent agency.")
    uid: str | None = Field(None, description="Unique identifier for the unit")
    commander: Officer | None = Field(None, description="The current commander of the unit.")
    commander_history_url: str | None = Field(None, description="-| URL that returns the past commanders of the unit and the period of their respective commands.")
    agency_url: str | None = Field(None, description="URL to get the agency that this unit belongs to.")
    officers_url: str | None = Field(None, description="URL to get a list of officers for this unit.")


class UnitList(PaginatedResponse, BaseModel):
    results: list[Unit] | None = None


class AddOfficer(BaseModel):
    officer_uid: str = Field(..., description="The uid of the officer")
    earliest_employment: str | None = Field(None, description="The earliest date of employment")
    latest_employment: str | None = Field(None, description="The latest date of employment")
    badge_number: str = Field(..., description="The badge number of the officer")
    unit_uid: str = Field(..., description="The UID of the unit the officer is assigned to.")
    highest_rank: str | None = Field(None, description="The highest rank the officer has held during their employment.")
    commander: bool | None = Field(None, description="-| If true, this officer will be added as the commander of the unit for the specified time period.")


class AddOfficerList(BaseModel):
    officers: list[AddOfficer] = ...


class AddOfficerFailed(BaseModel):
    officer_uid: str | None = Field(None, description="The uid of the officer")
    reason: str | None = Field(None, description="The reason the employment record could not be added")


class AddOfficerResponse(BaseModel):
    created: list[Employment] = ...
    failed: list[AddOfficerFailed] = ...
    total_created: int = ...
    total_failed: int = ...


class AgencyList(PaginatedResponse, BaseModel):
    results: list[Agency] | None = None


class CreateUnit(BaseUnit, BaseModel):
    name: str = Field(..., description="Name of the unit")
    website_url: str | None = Field(None, description="Website of the unit")
    phone: str | None = Field(None, description="Phone number of the unit")
    email: str | None = Field(None, description="Email of the unit")
    description: str | None = Field(None, description="Description of the unit")
    address: str | None = Field(None, description="Street address of the unit")
    zip: str | None = Field(None, description="Zip code of the unit")
    date_established: str | None = Field(None, description="The date that this unit was established by its parent agency.")
    commander_uid: str | None = Field(None, description="The UID of the unit's current commander.")


class UpdateUnit(BaseUnit, BaseModel):
    name: str | None = Field(None, description="Name of the unit")
    website_url: str | None = Field(None, description="Website of the unit")
    phone: str | None = Field(None, description="Phone number of the unit")
    email: str | None = Field(None, description="Email of the unit")
    description: str | None = Field(None, description="Description of the unit")
    address: str | None = Field(None, description="Street address of the unit")
    zip: str | None = Field(None, description="Zip code of the unit")
    date_established: str | None = Field(None, description="The date that this unit was established by its parent agency.")
    commander_uid: str | None = Field(None, description="The UID of the unit's current commander.")


