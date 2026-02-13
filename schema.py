from pydantic import BaseModel, Field
from typing import List


class SiemensSOP(BaseModel):
    """
    Standardized Siemens SOP schema.
    The LLM must populate every field when migrating an old document.
    """

    title: str = Field(
        description="The standardized, professional title of the procedure"
    )
    document_id: str = Field(
        description="A unique document identifier (e.g., SOP-2024-001)"
    )
    version: str = Field(
        description="The new standardized version number (e.g., 2.0)"
    )
    department: str = Field(
        description="The responsible department or area (e.g., Manufacturing, Quality Control)"
    )
    safety_warnings: List[str] = Field(
        description="Complete list of ALL safety precautions and warnings extracted from the document"
    )
    equipment: List[str] = Field(
        description="List of all tools, instruments, and equipment required"
    )
    steps: List[str] = Field(
        description="Sequential, clearly written execution steps — cleaned, numbered, and professional"
    )
    confidence_score: int = Field(
        ge=1,
        le=10,
        description=(
            "Self-assessed confidence score (1-10) indicating how completely "
            "and accurately the AI extracted all information from the source document. "
            "10 = all information captured perfectly, 1 = significant data likely missing."
        ),
    )
