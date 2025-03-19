from pydantic import BaseModel, Field
from typing import Any
from officers import Officer
from pagination import PaginatedResponse


class Disposition(BaseModel):
    disposition: str = Field(..., description="The disposition of the litigation.")
    description: str | None = Field(None, description="A description of the disposition. This could include the terms of a settlement, the amount of a judgment, or other relevant information.")
    date: str = Field(..., description="The date when this disposition was reached.")


class BaseLitigation(BaseModel):
    case_title: str | None = Field(None, description="The case title or caption for this litigation. Should contain the names of the parties involved.")
    docket_number: str | None = Field(None, description="The docket number for this litigation. This is the unique identifier for the case in the court system.")
    court_level: str | None = Field(None, description="The level of the court where this litigation is being heard. This could be a state court, federal court, or other court system.")
    jurisdiction: str | None = Field(None, description="The geographical or subject matter jurisdiction (e.g.,  Eastern District, Northern District, County name for  state courts) of the court where litigation is being heard.")
    state: str | None = Field(None, description="The state where this litigation is being heard. This should be the two-letter abbreviation for the state.")
    description: str | None = Field(None, description="A description of the litigation. This could include a summary of the case, the legal issues involved, or other relevant information.")
    start_date: str | None = Field(None, description="The date when this litigation was filed or initiated.")
    dispositions: list[Disposition] | None = Field(None, description="A list of any dispositions in this litigation. This could include a settlement, judgment, or other outcome.")
    settlement_amount: float | None = Field(None, description="The amount of any settlement or judgment in this litigation. This should be in USD.")
    url: str | None = Field(None, description="A URL to more information about this litigation. This could be a link to a court website such as [Court Listener](https://www.courtlistener.com/), [PACER](https://www.pacer.gov/), or other legal research resources.")


class CreateLitigation(BaseLitigation, BaseModel):
    case_title: str | None = Field(None, description="The case title or caption for this litigation. Should contain the names of the parties involved.")
    docket_number: str | None = Field(None, description="The docket number for this litigation. This is the unique identifier for the case in the court system.")
    court_level: str | None = Field(None, description="The level of the court where this litigation is being heard. This could be a state court, federal court, or other court system.")
    jurisdiction: str | None = Field(None, description="The geographical or subject matter jurisdiction (e.g.,  Eastern District, Northern District, County name for  state courts) of the court where litigation is being heard.")
    state: str | None = Field(None, description="The state where this litigation is being heard. This should be the two-letter abbreviation for the state.")
    description: str | None = Field(None, description="A description of the litigation. This could include a summary of the case, the legal issues involved, or other relevant information.")
    start_date: str | None = Field(None, description="The date when this litigation was filed or initiated.")
    dispositions: list[Disposition] | None = Field(None, description="A list of any dispositions in this litigation. This could include a settlement, judgment, or other outcome.")
    settlement_amount: float | None = Field(None, description="The amount of any settlement or judgment in this litigation. This should be in USD.")
    url: str | None = Field(None, description="A URL to more information about this litigation. This could be a link to a court website such as [Court Listener](https://www.courtlistener.com/), [PACER](https://www.pacer.gov/), or other legal research resources.")
    defendants: list[str] | None = Field(None, description="A list containing the IDs of any officers who are named as defendants in the litigation.")


class UpdateLitigation(BaseLitigation, BaseModel):
    case_title: str | None = Field(None, description="The case title or caption for this litigation. Should contain the names of the parties involved.")
    docket_number: str | None = Field(None, description="The docket number for this litigation. This is the unique identifier for the case in the court system.")
    court_level: str | None = Field(None, description="The level of the court where this litigation is being heard. This could be a state court, federal court, or other court system.")
    jurisdiction: str | None = Field(None, description="The geographical or subject matter jurisdiction (e.g.,  Eastern District, Northern District, County name for  state courts) of the court where litigation is being heard.")
    state: str | None = Field(None, description="The state where this litigation is being heard. This should be the two-letter abbreviation for the state.")
    description: str | None = Field(None, description="A description of the litigation. This could include a summary of the case, the legal issues involved, or other relevant information.")
    start_date: str | None = Field(None, description="The date when this litigation was filed or initiated.")
    dispositions: list[Disposition] | None = Field(None, description="A list of any dispositions in this litigation. This could include a settlement, judgment, or other outcome.")
    settlement_amount: float | None = Field(None, description="The amount of any settlement or judgment in this litigation. This should be in USD.")
    url: str | None = Field(None, description="A URL to more information about this litigation. This could be a link to a court website such as [Court Listener](https://www.courtlistener.com/), [PACER](https://www.pacer.gov/), or other legal research resources.")
    defendants: list[str] | None = Field(None, description="A list containing the IDs of any officers who are named as defendants in the litigation.")


class Litigation(BaseLitigation, BaseModel):
    case_title: str = Field(..., description="The case title or caption for this litigation. Should contain the names of the parties involved.")
    docket_number: str = Field(..., description="The docket number for this litigation. This is the unique identifier for the case in the court system.")
    court_level: str = Field(..., description="The level of the court where this litigation is being heard. This could be a state court, federal court, or other court system.")
    jurisdiction: str = Field(..., description="The geographical or subject matter jurisdiction (e.g.,  Eastern District, Northern District, County name for  state courts) of the court where litigation is being heard.")
    state: str = Field(..., description="The state where this litigation is being heard. This should be the two-letter abbreviation for the state.")
    description: str | None = Field(None, description="A description of the litigation. This could include a summary of the case, the legal issues involved, or other relevant information.")
    start_date: str | None = Field(None, description="The date when this litigation was filed or initiated.")
    dispositions: list[Disposition] | None = Field(None, description="A list of any dispositions in this litigation. This could include a settlement, judgment, or other outcome.")
    settlement_amount: float | None = Field(None, description="The amount of any settlement or judgment in this litigation. This should be in USD.")
    url: str | None = Field(None, description="A URL to more information about this litigation. This could be a link to a court website such as [Court Listener](https://www.courtlistener.com/), [PACER](https://www.pacer.gov/), or other legal research resources.")
    uid: str | None = Field(None, description="The uid of the litigation")
    documents: str | None = Field(None, description="A link to retrieve the documents associated with this litigation")
    defendants: list[Officer] = Field(..., description="A list of any officers who are named as defendants in the litigation.")


class LitigationList(PaginatedResponse, BaseModel):
    results: list[Litigation] | None = None


class BaseDocument(BaseModel):
    title: str | None = Field(None, description="The title of the document")
    description: str | None = Field(None, description="A description of the document")
    url: str | None = Field(None, description="A URL to the document")


class CreateDocument(BaseDocument, BaseModel):
    title: str | None = Field(None, description="The title of the document")
    description: str | None = Field(None, description="A description of the document")
    url: str | None = Field(None, description="A URL to the document")


class Document(BaseDocument, BaseModel):
    title: str | None = Field(None, description="The title of the document")
    description: str | None = Field(None, description="A description of the document")
    url: str | None = Field(None, description="A URL to the document")
    uid: str | None = Field(None, description="The uid of the document")


class DocumentList(PaginatedResponse, BaseModel):
    results: list[Document] | None = None


