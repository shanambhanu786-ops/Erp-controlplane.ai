from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class SecurityAction(str, Enum):
    ALLOW = "ALLOW_EXECUTION"
    CHALLENGE_MFA = "REQUIRE_STEP_UP_MFA"
    BLOCK = "BLOCK_AND_TERMINATE_SESSION"

class UserContext(BaseModel):
    user_id: str
    user_role: str
    department: str
    is_month_end: bool = False

class TransactionMetrics(BaseModel):
    query_cost_estimate: float = 0.0
    db_iops_spike: float = 0.0
    cloud_billing_delta_per_hr: float = 0.0

class PromptAnalysisRequest(BaseModel):
    session_id: str
    user_context: UserContext
    prompt: str
    metrics: Optional[TransactionMetrics] = Field(default_factory=TransactionMetrics)

class RiskBreakdown(BaseModel):
    security_score: float
    erp_score: float
    cloud_score: float
    finops_score: float

class AssessmentResponse(BaseModel):
    session_id: str
    turn_number: int
    detected_intent: str
    is_jailbreak_attempt: bool
    false_positive_suppressed: bool
    unified_risk_score: float
    risk_level: RiskLevel
    recommended_action: SecurityAction
    score_breakdown: RiskBreakdown
