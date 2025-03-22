# EXPLANATION# - This file centralizes all Pydantic models and enums used throughout the package.
# - TextInput is for API endpoint handling
# - SRSWTIResponse/SRSWTIRoute are for route suggestions and responses
# - SignupPhase tracks the progression of user onboarding 
# - Additional enums for pool and connection management

from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime

class TextInput(BaseModel):
    """Pydantic model for handling text input from users."""
    text_input: str
    canvas_id: str
    user_id: str

class SRSWTIRoute(str, Enum):
    """Enum representing valid routes in the SRSWTI system."""
    ABOUT = "www.srswti.com/about-us"
    REVERSE = "www.srswti.com/reverse"
    SEARCH = "www.srswti.com/search"
    BLOGS = "www.srswti.com/blogs"

class SRSWTIResponse(BaseModel):
    """Pydantic model for standardized responses from the SRSWTI system."""
    response: str
    suggested_route: Optional[SRSWTIRoute] = None
    confidence: float = 0.0  # Added confidence field as required by the frontend

    @field_validator('suggested_route')
    @classmethod
    def validate_route(cls, v: Optional[SRSWTIRoute]) -> Optional[SRSWTIRoute]:
        """Validate that the route is among the permitted values."""
        if v and v not in SRSWTIRoute:
            raise ValueError(f"Invalid route. Must be one of: {[route.value for route in SRSWTIRoute]}")
        return v

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate that confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    def to_json(self) -> str:
        """Serialize the model to JSON string."""
        return self.model_dump_json()

class SignupPhase(Enum):
    """Enum representing different phases of the signup process."""
    INTRO = "intro"
    EQ = "eq"
    PERSONALITY = "personality"
    ASSISTANT_ALIGNMENT = "assistant_alignment"
    COMPLETE = "complete"

@dataclass
class SignupState:
    """Dataclass for tracking state during signup."""
    phase: SignupPhase
    current_question_index: int
    responses: Dict[str, str]
    last_interaction: datetime
    follow_up_asked: bool = False

