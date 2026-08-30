import numpy as np
from app.config import settings
from app.models.schemas import PromptAnalysisRequest, RiskBreakdown, RiskLevel, SecurityAction
from app.prompts.security_guardrails import check_static_guardrails

class ThreatDetectionEngine:
    def evaluate_request(self, req: PromptAnalysisRequest, history: list[dict]) -> dict:
        # Step 1: LLM Guardrail Check
        is_jailbreak = check_static_guardrails(req.prompt)
        
        # Step 2: Intent Inference (Rule-based Fallback Simulation)
        intent = self._infer_intent(req.prompt)
        
        # Step 3: Statistical & Behavioral Risk Calculation
        security_score = 90.0 if is_jailbreak else self._calc_security_score(intent, history)
        erp_score = self._calc_erp_score(intent, req.user_context)
        cloud_score = min(100.0, req.metrics.db_iops_spike * 1.5)
        finops_score = min(100.0, (req.metrics.cloud_billing_delta_per_hr / 1000.0) * 10.0)
        
        # Step 4: Contextual Suppression Pipeline (False-Positive Reduction)
        suppressed = False
        if req.user_context.is_month_end and req.user_context.user_role == "FINANCE_LEAD":
            if intent in ["BULK_EXFILTRATION", "DATA_QUERY"]:
                erp_score *= 0.2  # 80% reduction for month-end close operations
                suppressed = True

        # Step 5: Unified Risk Aggregate Matrix Equation
        unified_score = (
            (settings.WEIGHT_SECURITY * security_score) +
            (settings.WEIGHT_ERP * erp_score) +
            (settings.WEIGHT_CLOUD * cloud_score) +
            (settings.WEIGHT_FINOPS * finops_score)
        )
        
        # Round and clamp
        unified_score = round(max(0.0, min(100.0, unified_score)), 2)
        
        # Step 6: Determine SOC Playbook Execution Target
        if unified_score >= settings.RISK_THRESHOLD_HIGH:
            level = RiskLevel.HIGH
            action = SecurityAction.BLOCK
        elif unified_score >= settings.RISK_THRESHOLD_MED:
            level = RiskLevel.MEDIUM
            action = SecurityAction.CHALLENGE_MFA
        else:
            level = RiskLevel.LOW
            action = SecurityAction.ALLOW

        return {
            "intent": intent,
            "is_jailbreak": is_jailbreak,
            "suppressed": suppressed,
            "unified_score": unified_score,
            "level": level,
            "action": action,
            "breakdown": RiskBreakdown(
                security_score=security_score,
                erp_score=erp_score,
                cloud_score=cloud_score,
                finops_score=finops_score
            )
        }

    def _infer_intent(self, prompt: str) -> str:
        p = prompt.lower()
        if "export" in p or "download all" in p:
            return "BULK_EXFILTRATION"
        if "bank" in p or "ssn" in p or "salary" in p:
            return "PII_EXTRACTION"
        if "pay" in p or "transfer" in p:
            return "FINANCIAL_MUTATION"
        return "DATA_QUERY"

    def _calc_security_score(self, intent: str, history: list[dict]) -> float:
        base = 10.0
        # Multi-Turn Escalation tracking
        past_intents = [turn["intent"] for turn in history]
        if "PII_EXTRACTION" in past_intents and intent == "BULK_EXFILTRATION":
            base += 70.0  # Sequential Data Exfiltration Intercept
        elif intent == "BULK_EXFILTRATION":
            base += 40.0
        elif intent == "PII_EXTRACTION":
            base += 30.0
        return base

    def _calc_erp_score(self, intent: str, context) -> float:
        if context.user_role == "INTERN" and intent in ["PII_EXTRACTION", "BULK_EXFILTRATION"]:
            return 95.0
        return 20.0

detection_engine = ThreatDetectionEngine()
