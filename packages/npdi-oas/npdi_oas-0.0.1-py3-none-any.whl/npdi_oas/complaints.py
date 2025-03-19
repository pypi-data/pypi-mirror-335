from pydantic import BaseModel, Field
from typing import Any
from sources import Source
from officers import Officer
from pagination import PaginatedResponse


class Penalty(BaseModel):
    uid: str | None = Field(None, description="UUID for the penalty.")
    officer: Officer | None = Field(None, description="The officer who the penalty is associated with.")
    description: str | None = Field(None, description="A description of the penalty.")
    date_assessed: str | None = None


class CreatePenalty(BaseModel):
    officer_uid: str | None = Field(None, description="The UID of the officer the penalty is associated with.")
    description: str | None = Field(None, description="A description of the penalty.")


class BaseInvestigation(BaseModel):
    start_date: str | None = Field(None, description="The date the investigation started.")
    end_date: str | None = Field(None, description="The date the investigation ended.")


class CreateInvestigation(BaseInvestigation, BaseModel):
    start_date: str | None = Field(None, description="The date the investigation started.")
    end_date: str | None = Field(None, description="The date the investigation ended.")
    investigator_uid: str | None = Field(None, description="The UID of the officer who preformed the investigation.")


class Investigation(BaseInvestigation, BaseModel):
    start_date: str | None = Field(None, description="The date the investigation started.")
    end_date: str | None = Field(None, description="The date the investigation ended.")
    uid: str | None = Field(None, description="Unique identifier for the investigation.")
    investigator: Officer | None = Field(None, description="The officer who preformed the investigation.")


class Civilian(BaseModel):
    age: str | None = Field(None, description="Age range of the individual.")
    ethnicity: str | None = Field(None, description="The ethnicity of the individual.")
    gender: str | None = Field(None, description="The gender of the individual.")


class ReviewBoard(BaseModel):
    uid: str | None = Field(None, description="Unique identifier for the review board.")
    name: str | None = Field(None, description="The name of the review board.")
    city: str | None = Field(None, description="The city the review board is located in.")
    state: str | None = Field(None, description="The state the review board is located in.")
    url: str | None = Field(None, description="The website URL for the review board.")


class Attachments(BaseModel):
    type: str | None = Field(None, description="The type of attachment.")
    url: str | None = Field(None, description="The url of the attachment.")
    description: str | None = Field(None, description="A description of the attachment.")


class SourceDetails(BaseModel):
    record_type: str | None = Field(None, description="The type of record the complaint is associated with.")


class LegalCaseEvent(BaseModel):
    record_type: str | None = Field(None, description="The type of record the complaint is associated with.")
    court: str | None = Field(None, description="The court the legal action was filed in.")
    judge: str | None = Field(None, description="The judge who presided over the case.")
    docket_number: str | None = Field(None, description="The docket number of the case.")
    event_summary: str | None = Field(None, description="A summary of the event.")
    date_of_event: str | None = Field(None, description="The date the legal action was filed.")


class PersonalAccount(BaseModel):
    record_type: str | None = Field(None, description="The type of record the complaint is associated with.")


class GovernmentRecord(BaseModel):
    record_type: str | None = Field(None, description="The type of record the complaint is associated with.")
    reporting_agency: str | None = Field(None, description="The agency that reported the record.")
    reporting_agency_url: str | None = Field(None, description="The url of the agency that reported the record.")
    reporting_agency_email: str | None = Field(None, description="The email of the agency that reported the record.")


class NewsReport(BaseModel):
    record_type: str | None = Field(None, description="The type of record the complaint is associated with.")
    publication_name: str | None = Field(None, description="The name of the publication.")
    publication_date: str | None = Field(None, description="The date the publication was released.")
    publication_url: str | None = Field(None, description="The url of the publication.")
    author: str | None = Field(None, description="The author of the publication.")
    author_url: str | None = Field(None, description="The url of the author.")
    author_email: str | None = Field(None, description="The email of the author.")


class BaseComplaint(BaseModel):
    """Base complaint object"""
    record_id: str | None = Field(None, description="The ID that was given to this complaint by the original source of the data.")
    source_details: SourceDetails | None = None
    category: str | None = Field(None, description="The category of the complaint.")
    incident_date: str | None = Field(None, description="The date and time the incident occurred.")
    received_date: str | None = Field(None, description="The date and time the complaint was received by the reporting source.")
    closed_date: str | None = Field(None, description="The date and time the complaint was closed.")
    location: dict[str, Any] | None = None
    reason_for_contact: str | None = Field(None, description="The reason for the contact.")
    outcome_of_contact: str | None = Field(None, description="The outcome of the contact.")
    civilian_witnesses: list[Civilian] | None = Field(None, description="The civilian witnesses associated with the complaint.")
    attachments: list[Attachments] | None = Field(None, description="Documents and multimedia associated with the complaint.")


class BaseAllegation(BaseModel):
    record_id: str | None = Field(None, description="The ID that was given to this allegation by the original source of the data.")
    complaintant: Civilian | None = Field(None, description="Demographic information of the individual who filed the complaint.")
    allegation: str | None = Field(None, description="The allegation made by the complaintant.")
    type: str | None = Field(None, description="The type of allegation.")
    sub_type: str | None = Field(None, description="The sub type of the allegation.")
    recommended_finding: str | None = Field(None, description="The finding recommended by the review board.")
    recommended_outcome: str | None = Field(None, description="The outcome recommended by the review board.")
    finding: str | None = Field(None, description="The legal finding.")
    outcome: str | None = Field(None, description="The final outcome of the allegation.")


class CreateAllegation(BaseAllegation, BaseModel):
    record_id: str | None = Field(None, description="The ID that was given to this allegation by the original source of the data.")
    complaintant: Civilian | None = Field(None, description="Demographic information of the individual who filed the complaint.")
    allegation: str | None = Field(None, description="The allegation made by the complaintant.")
    type: str | None = Field(None, description="The type of allegation.")
    sub_type: str | None = Field(None, description="The sub type of the allegation.")
    recommended_finding: str | None = Field(None, description="The finding recommended by the review board.")
    recommended_outcome: str | None = Field(None, description="The outcome recommended by the review board.")
    finding: str | None = Field(None, description="The legal finding.")
    outcome: str | None = Field(None, description="The final outcome of the allegation.")
    perpetrator_uid: str | None = Field(None, description="The UID of the officer the allegation is made against.")


class Allegation(BaseAllegation, BaseModel):
    record_id: str | None = Field(None, description="The ID that was given to this allegation by the original source of the data.")
    complaintant: Civilian | None = Field(None, description="Demographic information of the individual who filed the complaint.")
    allegation: str | None = Field(None, description="The allegation made by the complaintant.")
    type: str | None = Field(None, description="The type of allegation.")
    sub_type: str | None = Field(None, description="The sub type of the allegation.")
    recommended_finding: str | None = Field(None, description="The finding recommended by the review board.")
    recommended_outcome: str | None = Field(None, description="The outcome recommended by the review board.")
    finding: str | None = Field(None, description="The legal finding.")
    outcome: str | None = Field(None, description="The final outcome of the allegation.")
    uid: str | None = Field(None, description="Unique identifier for the allegation.")
    perpetrator: Officer | None = Field(None, description="The officer who the allegation is made against.")


class CreateComplaint(BaseComplaint, BaseModel):
    record_id: str | None = Field(None, description="The ID that was given to this complaint by the original source of the data.")
    source_details: SourceDetails | None = None
    category: str | None = Field(None, description="The category of the complaint.")
    incident_date: str | None = Field(None, description="The date and time the incident occurred.")
    received_date: str | None = Field(None, description="The date and time the complaint was received by the reporting source.")
    closed_date: str | None = Field(None, description="The date and time the complaint was closed.")
    location: dict[str, Any] | None = None
    reason_for_contact: str | None = Field(None, description="The reason for the contact.")
    outcome_of_contact: str | None = Field(None, description="The outcome of the contact.")
    civilian_witnesses: list[Civilian] | None = Field(None, description="The civilian witnesses associated with the complaint.")
    attachments: list[Attachments] | None = Field(None, description="Documents and multimedia associated with the complaint.")
    source_uid: str | None = Field(None, description="The UID of the source that reported the complaint.")
    civilian_review_board_uid: str | None = Field(None, description="The UID of the civilian review board that reviewed the complaint.")
    police_witnesses: list[str] | None = Field(None, description="The UID of any police witnesses associated with the complaint.")
    allegations: list[CreateAllegation] | None = Field(None, description="The allegations associated with the complaint.")
    investigations: list[CreateInvestigation] | None = Field(None, description="The investigations associated with the complaint.")
    penalties: list[CreatePenalty] | None = Field(None, description="The penalties associated with the complaint.")


class UpdateComplaint(BaseComplaint, BaseModel):
    record_id: str | None = Field(None, description="The ID that was given to this complaint by the original source of the data.")
    source_details: SourceDetails | None = None
    category: str | None = Field(None, description="The category of the complaint.")
    incident_date: str | None = Field(None, description="The date and time the incident occurred.")
    received_date: str | None = Field(None, description="The date and time the complaint was received by the reporting source.")
    closed_date: str | None = Field(None, description="The date and time the complaint was closed.")
    location: dict[str, Any] | None = None
    reason_for_contact: str | None = Field(None, description="The reason for the contact.")
    outcome_of_contact: str | None = Field(None, description="The outcome of the contact.")
    civilian_witnesses: list[Civilian] | None = Field(None, description="The civilian witnesses associated with the complaint.")
    attachments: list[Attachments] | None = Field(None, description="Documents and multimedia associated with the complaint.")
    civilian_review_board_uid: str | None = Field(None, description="The UID of the civilian review board that reviewed the complaint.")
    police_witnesses: list[str] | None = Field(None, description="The uid of any police witnesses associated with the complaint.")
    allegations: list[CreateAllegation] | None = Field(None, description="The allegations associated with the complaint.")
    investigations: list[CreateInvestigation] | None = Field(None, description="The investigations associated with the complaint.")
    penalties: list[CreatePenalty] | None = Field(None, description="The penalties associated with the complaint.")


class Complaint(BaseComplaint, BaseModel):
    record_id: str | None = Field(None, description="The ID that was given to this complaint by the original source of the data.")
    source_details: SourceDetails | None = None
    category: str = Field(..., description="The category of the complaint.")
    incident_date: str = Field(..., description="The date and time the incident occurred.")
    received_date: str = Field(..., description="The date and time the complaint was received by the reporting source.")
    closed_date: str | None = Field(None, description="The date and time the complaint was closed.")
    location: dict[str, Any] = ...
    reason_for_contact: str | None = Field(None, description="The reason for the contact.")
    outcome_of_contact: str | None = Field(None, description="The outcome of the contact.")
    civilian_witnesses: list[Civilian] = Field(..., description="The civilian witnesses associated with the complaint.")
    attachments: list[Attachments] | None = Field(None, description="Documents and multimedia associated with the complaint.")
    uid: str = Field(..., description="Unique identifier for the complaint.")
    created_at: str = Field(..., description="Date and time the complaint was created.")
    updated_at: str = Field(..., description="Date and time the complaint was last updated.")
    source: Source | None = Field(None, description="The source that reported the complaint.")
    civilian_review_board: ReviewBoard | None = Field(None, description="The civilian review board that reviewed the complaint.")
    police_witnesses: list[Officer] = Field(..., description="The police witnesses associated with the complaint.")
    allegations: list[Allegation] = Field(..., description="The allegations associated with the complaint.")
    investigations: list[Investigation] = Field(..., description="The investigations associated with the complaint.")
    penalties: list[Penalty] = Field(..., description="The penalties associated with the complaint.")


class ComplaintList(PaginatedResponse, BaseModel):
    results: list[Complaint] | None = Field(None, description="List of complaints.")


