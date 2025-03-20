# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["EnrichmentCreateBulkParams", "Candidate"]


class EnrichmentCreateBulkParams(TypedDict, total=False):
    candidates: Required[Iterable[Candidate]]


class Candidate(TypedDict, total=False):
    name: Required[str]

    email: str

    linkedin_id: str

    location: str

    phone: str

    role: Literal["rn", "lpn", "cna", "allied_health", "other"]

    specialty: str
