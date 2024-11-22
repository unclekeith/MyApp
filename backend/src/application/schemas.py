from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .models import ApplicationStatus


class ApplicationCreate(BaseModel):
    subject_ids: Optional[
        List[int]
    ] = []  # List of subject IDs to apply for, can be empty


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
    user_id: int


class ApplicationResponse(BaseModel):
    id: int
    status: ApplicationStatus
    subjects_ids: List[int]

    model_config = ConfigDict(from_attributes=True, extra="allow")
