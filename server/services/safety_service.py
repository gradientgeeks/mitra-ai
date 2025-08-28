"""
Safety service for crisis detection and intervention in Mitra AI.
"""

import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from enum import Enum

from core.config import settings
from models.chat import ChatMessage, SafetyStatus, CrisisResponse

logger = logging.getLogger(__name__)


class CrisisSeverity(str, Enum):
    """Crisis severity levels."""
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class SafetyService:
    """Service for detecting crisis situations and providing appropriate interventions."""
    
    def __init__(self):
        """Initialize safety service."""
        self.crisis_keywords = settings.crisis_keywords
        self.helplines = settings.crisis_helplines
        self.confidence_threshold = settings.crisis_confidence_threshold
        
        # Compile regex patterns for more sophisticated detection
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for crisis detection."""
        # High-risk patterns (immediate intervention needed)
        self.high_risk_patterns = [
            r'\b(?:want|going|plan)(?:ing)?\s+to\s+(?:kill|hurt|harm)\s+(?:myself|me)\b',
            r'\b(?:suicide|kill myself|end (?:my )?life|no (?:point|reason) (?:to )?liv(?:e|ing))\b',
            r'\beveryone would be better (?:off )?without me\b',
            r'\b(?:cutting|burning|hurting) myself\b',
            r'\b(?:आत्महत्या|खुद को मारना|जान देना|मरना चाहता)\b',  # Hindi terms
        ]
        
        # Medium-risk patterns (need support and monitoring)
        self.medium_risk_patterns = [
            r'\b(?:can\'?t take it|don\'?t want to be here|nothing matters|no hope)\b',
            r'\b(?:tired of|sick of) (?:everything|life|living|trying)\b',
            r'\b(?:nobody|no one) (?:cares|loves|understands) (?:about )?me\b',
            r'\b(?:feel(?:ing)?|am) (?:so )?(?:hopeless|worthless|useless|empty)\b',
            r'\b(?:नहीं रह सकता|कोई परवाह नहीं|मरना बेहतर)\b',  # Hindi terms
        ]
        
        # Low-risk patterns (general distress, needs gentle support)
        self.low_risk_patterns = [
            r'\b(?:very )?(?:sad|depressed|down|stressed|anxious|overwhelmed)\b',
            r'\b(?:having (?:a )?hard time|struggling|difficult|tough)\b',
            r'\b(?:feel(?:ing)?|am) (?:alone|lonely|isolated|lost)\b',
            r'\b(?:can\'?t sleep|not eating|losing weight)\b',
        ]
        
        # Compile patterns
        self.compiled_high_risk = [re.compile(pattern, re.IGNORECASE) for pattern in self.high_risk_patterns]
        self.compiled_medium_risk = [re.compile(pattern, re.IGNORECASE) for pattern in self.medium_risk_patterns]
        self.compiled_low_risk = [re.compile(pattern, re.IGNORECASE) for pattern in self.low_risk_patterns]

    async def assess_safety(self, message: str, conversation_history: Optional[List[ChatMessage]] = None) -> Tuple[SafetyStatus, float, Optional[CrisisSeverity]]:
        """
        Assess safety level of a message and conversation.
        
        Args:
            message: Current message to assess
            conversation_history: Previous conversation context
            
        Returns:
            Tuple of (safety_status, confidence_score, crisis_severity)
        """
        try:
            # Analyze current message
            message_score, message_severity = self._analyze_message_risk(message)
            
            # Analyze conversation context if available
            context_score = 0.0
            if conversation_history:
                context_score = self._analyze_conversation_context(conversation_history)
            
            # Combine scores with weighting
            combined_score = (message_score * 0.7) + (context_score * 0.3)
            
            # Determine safety status and severity
            if combined_score >= 0.8:
                status = SafetyStatus.CRISIS
                severity = CrisisSeverity.SEVERE
            elif combined_score >= 0.6:
                status = SafetyStatus.CRISIS
                severity = CrisisSeverity.HIGH
            elif combined_score >= 0.4:
                status = SafetyStatus.WARNING
                severity = CrisisSeverity.MODERATE
            else:
                status = SafetyStatus.SAFE
                severity = None
            
            logger.info(f"Safety assessment: status={status}, score={combined_score:.2f}, severity={severity}")
            return status, combined_score, severity
            
        except Exception as e:
            logger.error(f"Error in safety assessment: {e}")
            # Default to safe if assessment fails
            return SafetyStatus.SAFE, 0.0, None

    def _analyze_message_risk(self, message: str) -> Tuple[float, Optional[CrisisSeverity]]:
        """Analyze risk level of a single message."""
        message_lower = message.lower()
        
        # Check for high-risk patterns
        high_risk_matches = sum(1 for pattern in self.compiled_high_risk if pattern.search(message))
        if high_risk_matches > 0:
            return min(0.9, 0.6 + (high_risk_matches * 0.15)), CrisisSeverity.SEVERE
        
        # Check for medium-risk patterns
        medium_risk_matches = sum(1 for pattern in self.compiled_medium_risk if pattern.search(message))
        if medium_risk_matches > 0:
            return min(0.7, 0.4 + (medium_risk_matches * 0.1)), CrisisSeverity.HIGH
        
        # Check for low-risk patterns
        low_risk_matches = sum(1 for pattern in self.compiled_low_risk if pattern.search(message))
        if low_risk_matches > 0:
            return min(0.5, 0.2 + (low_risk_matches * 0.05)), CrisisSeverity.MODERATE
        
        return 0.0, None

    def _analyze_conversation_context(self, messages: List[ChatMessage]) -> float:
        """Analyze conversation context for escalating risk patterns."""
        if len(messages) < 2:
            return 0.0
        
        risk_indicators = 0
        total_messages = len(messages)
        
        # Look for escalating negative sentiment
        user_messages = [msg for msg in messages[-10:] if msg.role.value == "user"]
        
        for i, message in enumerate(user_messages):
            if message.content.text:
                # Check for repeated crisis keywords
                crisis_count = sum(1 for keyword in self.crisis_keywords 
                                 if keyword.lower() in message.content.text.lower())
                if crisis_count > 0:
                    risk_indicators += crisis_count * (1 + i * 0.1)  # Weight recent messages more
        
        # Normalize score
        max_possible_score = total_messages * 3
        context_score = min(1.0, risk_indicators / max(max_possible_score, 1))
        
        return context_score

    async def generate_crisis_response(self, severity: CrisisSeverity, user_message: str) -> CrisisResponse:
        """
        Generate appropriate crisis intervention response.
        
        Args:
            severity: Crisis severity level
            user_message: User's message that triggered crisis detection
            
        Returns:
            CrisisResponse with intervention details
        """
        try:
            # Select appropriate message based on severity
            if severity == CrisisSeverity.SEVERE:
                message = self._get_severe_crisis_message()
                immediate_actions = self._get_severe_crisis_actions()
            elif severity == CrisisSeverity.HIGH:
                message = self._get_high_crisis_message()
                immediate_actions = self._get_high_crisis_actions()
            else:  # MODERATE
                message = self._get_moderate_crisis_message()
                immediate_actions = self._get_moderate_crisis_actions()
            
            return CrisisResponse(
                crisis_detected=True,
                severity=severity.value,
                message=message,
                helplines=self.helplines,
                immediate_actions=immediate_actions,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating crisis response: {e}")
            # Return basic crisis response
            return CrisisResponse(
                crisis_detected=True,
                severity=severity.value,
                message="I'm concerned about your safety. Please reach out for help.",
                helplines=self.helplines,
                immediate_actions=["Contact a trusted person immediately", "Call a crisis helpline"],
                timestamp=datetime.utcnow()
            )

    def _get_severe_crisis_message(self) -> str:
        """Get message for severe crisis situations."""
        return """
        I'm very concerned about what you've shared. Your safety is the most important thing right now.

        🚨 **Immediate Help Available:**
        
        Please reach out to a crisis helpline right now - they have trained counselors available 24/7:
        
        **AASRA**: 91-22-27546669
        **Vandrevala Foundation**: 9999666555 (Free)
        **iCall**: 9152987821
        
        You don't have to go through this alone. These counselors are specifically trained to help 
        people in crisis situations and can provide immediate support.
        
        If you're in immediate danger, please contact emergency services or go to the nearest hospital.
        
        💙 Remember: Crisis feelings are temporary, but ending your life is permanent. 
        Help is available, and things can get better.
        """

    def _get_high_crisis_message(self) -> str:
        """Get message for high crisis situations.""" 
        return """
        I can see that you're going through something really difficult right now, and I'm concerned about you.
        
        🆘 **You're Not Alone:**
        
        It's important that you talk to someone who can provide professional support:
        
        **AASRA**: 91-22-27546669 (24/7 emotional support)
        **Vandrevala Foundation**: 9999666555 (Free helpline)
        **iCall**: 9152987821 (Psychosocial helpline)
        
        These are confidential, non-judgmental spaces where you can share what you're feeling.
        
        💚 Please remember: What you're feeling right now is real and valid, but it's not permanent. 
        With the right support, things can improve.
        
        Is there a trusted friend, family member, or counselor you could reach out to today?
        """

    def _get_moderate_crisis_message(self) -> str:
        """Get message for moderate crisis situations."""
        return """
        I hear that you're struggling, and I want you to know that reaching out shows real strength.
        
        🤗 **Support is Available:**
        
        While I'm here to listen, talking to a trained counselor can provide additional support:
        
        **AASRA**: 91-22-27546669
        **Vandrevala Foundation**: 9999666555
        **iCall**: 9152987821
        
        These helplines are confidential and staffed by people who understand what you're going through.
        
        💙 Remember: Difficult feelings are temporary. You've gotten through hard times before, 
        and you can get through this too. You matter, and your life has value.
        
        What's one small thing that might help you feel a little better today?
        """

    def _get_severe_crisis_actions(self) -> List[str]:
        """Get immediate actions for severe crisis."""
        return [
            "Call a crisis helpline immediately (numbers provided above)",
            "Contact emergency services if in immediate danger",
            "Reach out to a trusted person right now",
            "Go to the nearest hospital emergency room if needed",
            "Remove any means of self-harm from your immediate area",
            "Stay with someone until you feel safer"
        ]

    def _get_high_crisis_actions(self) -> List[str]:
        """Get immediate actions for high crisis."""
        return [
            "Call one of the crisis helplines today",
            "Tell a trusted friend or family member how you're feeling",
            "Consider visiting a mental health professional",
            "Create a safety plan with specific people to contact",
            "Avoid being alone for extended periods",
            "Engage in grounding activities (deep breathing, etc.)"
        ]

    def _get_moderate_crisis_actions(self) -> List[str]:
        """Get immediate actions for moderate crisis."""
        return [
            "Consider talking to a counselor or helpline",
            "Reach out to a supportive friend or family member",
            "Practice self-care activities you usually enjoy",
            "Try grounding techniques (5-4-3-2-1 sensory method)",
            "Avoid isolation - stay connected with others",
            "Consider professional mental health support"
        ]

    async def is_safe_to_continue_conversation(self, safety_status: SafetyStatus) -> bool:
        """
        Determine if it's safe to continue normal conversation.
        
        Args:
            safety_status: Current safety assessment
            
        Returns:
            True if safe to continue, False if intervention needed
        """
        return safety_status != SafetyStatus.CRISIS

    async def log_safety_incident(self, user_id: str, message: str, assessment: Dict[str, Any]):
        """
        Log safety incident for monitoring and analysis.
        
        Args:
            user_id: User ID (anonymized)
            message: Message that triggered assessment (anonymized)
            assessment: Safety assessment details
        """
        try:
            # In production, log to secure monitoring system
            # For now, log locally with anonymization
            anonymized_message = self._anonymize_message(message)
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id_hash": hash(user_id),  # Simple hash for privacy
                "safety_status": assessment.get("status"),
                "confidence": assessment.get("confidence"),
                "severity": assessment.get("severity"),
                "message_length": len(message),
                "patterns_detected": assessment.get("patterns", [])
            }
            
            logger.warning(f"Safety incident logged: {log_entry}")
            
        except Exception as e:
            logger.error(f"Error logging safety incident: {e}")

    def _anonymize_message(self, message: str) -> str:
        """Anonymize message for logging purposes."""
        # Replace potential identifying information
        anonymized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', message)
        anonymized = re.sub(r'\b\d{10}\b', '[PHONE]', anonymized)
        anonymized = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', anonymized)
        
        return anonymized[:100] + "..." if len(anonymized) > 100 else anonymized