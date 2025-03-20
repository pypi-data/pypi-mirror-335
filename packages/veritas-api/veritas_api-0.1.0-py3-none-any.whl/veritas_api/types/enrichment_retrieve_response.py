# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["EnrichmentRetrieveResponse", "Candidate", "CandidateEducationHistory", "CandidateWorkHistory"]


class CandidateEducationHistory(BaseModel):
    degree: Optional[str] = None

    end_date: Optional[str] = None

    name: Optional[str] = None
    """Name of the school including location"""

    start_date: Optional[str] = None


class CandidateWorkHistory(BaseModel):
    end_date: Optional[str] = None

    name: Optional[str] = None
    """Name of the company including location"""

    role: Optional[str] = None

    start_date: Optional[str] = None


class Candidate(BaseModel):
    education_history: Optional[List[CandidateEducationHistory]] = None

    email: Optional[str] = None

    linkedin_id: Optional[str] = None

    location: Optional[str] = None

    name: Optional[str] = None

    phone: Optional[str] = None

    role: Optional[Literal["rn", "lpn", "cna", "allied_health", "other"]] = None

    specialty: Optional[str] = None

    work_history: Optional[List[CandidateWorkHistory]] = None


class EnrichmentRetrieveResponse(BaseModel):
    id: Optional[str] = None

    candidates: Optional[List[Candidate]] = None

    status: Optional[Literal["pending", "processing", "completed", "failed"]] = None
