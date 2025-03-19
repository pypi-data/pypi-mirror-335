from pydantic import BaseModel, Field
from typing import Any
from pagination import PaginatedResponse


class NameFilter(BaseModel):
    """An advanced filter that can be applied to an officer list request.
"""
    first: str | None = Field(None, description="Filter officers by their first name. The value should be a string.")
    middle: str | None = Field(None, description="Filter officers by their middle name. The value should be a string.")
    last: str | None = Field(None, description="Filter officers by their last name. The value should be a string.")
    suffix: str | None = Field(None, description="Filter officers by their suffix. The value should be a string.")


class LocationFilter(BaseModel):
    """An advanced filter that can be applied to an officer list request.
"""
    state: str | None = Field(None, description="Filter locations by state. The value should be a string.")
    county: str | None = Field(None, description="Filter locations by county. The value should be a string.")
    city: str | None = Field(None, description="Filter locations by city. The value should be a string.")
    zip: str | None = Field(None, description="Filter locations by zip code. The value should be a string.")


class AllegationFilter(BaseModel):
    """An advanced filter that can be applied to an officer list request.
"""
    uid: list[str] | None = Field(None, description="Return officers who have any of the selected allegations.")
    status: list[str] | None = Field(None, description="Return officers who have allegations with the selected statuses.")
    category: list[str] | None = Field(None, description="Return officers who have allegations with the selected categories.")
    subcategory: list[str] | None = Field(None, description="Return officers who have allegations with the selected subcategory.")
    sustained: bool | None = Field(None, description="Return officers who have allegations that are either sustained not sustained. The value must be a boolean.")
    count__gte: int | None = Field(None, description="Return officers who have at least the selected number of allegations. The value must be an integer.")
    count__lte: int | None = Field(None, description="Return officers who have at most the selected number of allegations. The value must be an integer.")


class StateIdFilter(BaseModel):
    """An advanced filter that can be applied to an officer list request.
"""
    state: str | None = Field(None, description="Filter officers by their ID state. The value should be a string.")
    id_name: str | None = Field(None, description="Filter officers by their ID name. The value should be a string.")
    values: str | None = Field(None, description="Return officers with the selected ID values. Must be sent in tandem with the `id_name` and `state` properties.")


class OfficerFilter(BaseModel):
    """An advanced filter that can be applied to an officer list request.
"""
    names: list[NameFilter] | None = Field(None, description="Return officers whose name matches any of these filters.")
    location: LocationFilter | None = Field(None, description="Filter officers by locations in which they have worked. This is assessed based on the operating theatre of the units to which they've been assigned.")
    state_ids_sets: list[StateIdFilter] | None = Field(None, description="Filter officers by their state IDs. This can be used to filter by tax number, officer training number, or any other unique identifier used by a state.")
    ranks: list[str] | None = Field(None, description="Return officers who have obtained the selected ranks.")
    ethnicities: list[str] | None = Field(None, description="Return officers who have the selected ethnicities.")
    commanders: list[str] | None = Field(None, description="Return officers who have worked under the selected commanders.")
    allegations: AllegationFilter | None = Field(None, description="Filter officers by allegations made against them.")


class BaseEmployment(BaseModel):
    officer_uid: str | None = Field(None, description="The UID of the officer.")
    agency_uid: str | None = Field(None, description="The UID of the agency the officer is employed by.")
    unit_uid: str | None = Field(None, description="The UID of the unit the officer is assigned to.")
    earliest_employment: str | None = Field(None, description="The earliest known date of employment")
    latest_employment: str | None = Field(None, description="The latest known date of employment")
    badge_number: str | None = Field(None, description="The badge number of the officer")
    highest_rank: str | None = Field(None, description="The highest rank the officer has held during this employment.")
    commander: bool | None = Field(None, description="Indicates that the officer commanded the unit during this employment.")


class AddEmployment(BaseEmployment, BaseModel):
    officer_uid: str | None = Field(None, description="The UID of the officer.")
    agency_uid: str | None = Field(None, description="The UID of the agency the officer is employed by.")
    unit_uid: str | None = Field(None, description="The UID of the unit the officer is assigned to.")
    earliest_employment: str | None = Field(None, description="The earliest known date of employment")
    latest_employment: str | None = Field(None, description="The latest known date of employment")
    badge_number: str | None = Field(None, description="The badge number of the officer")
    highest_rank: str | None = Field(None, description="The highest rank the officer has held during this employment.")
    commander: bool | None = Field(None, description="Indicates that the officer commanded the unit during this employment.")


class AddEmploymentFailed(BaseModel):
    agency_uid: str | None = Field(None, description="The uid of the agency that could not be added.")
    reason: str | None = Field(None, description="The reason the employment record could not be added")


class AddEmploymentList(BaseModel):
    agencies: list[AddEmployment] | None = Field(None, description="The units to add to the officer's employment history.")


class Employment(BaseEmployment, BaseModel):
    officer_uid: str | None = Field(None, description="The UID of the officer.")
    agency_uid: str | None = Field(None, description="The UID of the agency the officer is employed by.")
    unit_uid: str | None = Field(None, description="The UID of the unit the officer is assigned to.")
    earliest_employment: str | None = Field(None, description="The earliest known date of employment")
    latest_employment: str | None = Field(None, description="The latest known date of employment")
    badge_number: str | None = Field(None, description="The badge number of the officer")
    highest_rank: str | None = Field(None, description="The highest rank the officer has held during this employment.")
    commander: bool | None = Field(None, description="Indicates that the officer commanded the unit during this employment.")


class AddEmploymentResponse(BaseModel):
    created: list[Employment] = ...
    failed: list[AddEmploymentFailed] = ...
    total_created: int = ...
    total_failed: int = ...


class EmploymentList(PaginatedResponse, BaseModel):
    results: list[Employment] | None = None


class StateId(BaseModel):
    uid: str | None = Field(None, description="The UUID of this state id")
    state: str | None = Field(None, description="The state of the state id")
    id_name: str | None = Field(None, description="The name of the id. For example, Tax ID, Driver's License, etc.")
    value: str | None = Field(None, description="The value of the id.")


class BaseOfficer(BaseModel):
    first_name: str | None = Field(None, description="First name of the officer")
    middle_name: str | None = Field(None, description="Middle name of the officer")
    last_name: str | None = Field(None, description="Last name of the officer")
    suffix: str | None = Field(None, description="Suffix of the officer's name")
    ethnicity: str | None = Field(None, description="The ethnicity of the officer")
    gender: str | None = Field(None, description="The gender of the officer")
    date_of_birth: str | None = Field(None, description="The date of birth of the officer")
    state_ids: list[StateId] | None = Field(None, description="The state ids of the officer")


class CreateOfficer(BaseOfficer, BaseModel):
    first_name: str | None = Field(None, description="First name of the officer")
    middle_name: str | None = Field(None, description="Middle name of the officer")
    last_name: str | None = Field(None, description="Last name of the officer")
    suffix: str | None = Field(None, description="Suffix of the officer's name")
    ethnicity: str | None = Field(None, description="The ethnicity of the officer")
    gender: str | None = Field(None, description="The gender of the officer")
    date_of_birth: str | None = Field(None, description="The date of birth of the officer")
    state_ids: list[StateId] | None = Field(None, description="The state ids of the officer")


class UpdateOfficer(BaseOfficer, BaseModel):
    first_name: str | None = Field(None, description="First name of the officer")
    middle_name: str | None = Field(None, description="Middle name of the officer")
    last_name: str | None = Field(None, description="Last name of the officer")
    suffix: str | None = Field(None, description="Suffix of the officer's name")
    ethnicity: str | None = Field(None, description="The ethnicity of the officer")
    gender: str | None = Field(None, description="The gender of the officer")
    date_of_birth: str | None = Field(None, description="The date of birth of the officer")
    state_ids: list[StateId] | None = Field(None, description="The state ids of the officer")


class Officer(BaseOfficer, BaseModel):
    first_name: str | None = Field(None, description="First name of the officer")
    middle_name: str | None = Field(None, description="Middle name of the officer")
    last_name: str | None = Field(None, description="Last name of the officer")
    suffix: str | None = Field(None, description="Suffix of the officer's name")
    ethnicity: str | None = Field(None, description="The ethnicity of the officer")
    gender: str | None = Field(None, description="The gender of the officer")
    date_of_birth: str | None = Field(None, description="The date of birth of the officer")
    state_ids: list[StateId] | None = Field(None, description="The state ids of the officer")
    uid: str | None = Field(None, description="The uid of the officer")
    employment_history: str | None = Field(None, description="A link to retrieve the employment history of the officer")
    allegations: str | None = Field(None, description="A link to retrieve the allegations against the officer")
    litigation: str | None = Field(None, description="A link to retrieve the litigation against the officer")


class OfficerList(PaginatedResponse, BaseModel):
    results: list[Officer] | None = None


