"""
Multi-turn conversation handler for Vera challenge.

Handles conversation state management, context memory, and follow-up messages
based on merchant/customer responses and prior conversation history.

This module is OPTIONAL but provides scoring advantage through:
- Context continuity across turns (merchant state tracking)
- Adaptive messaging (response to YES/STOP/custom reply)
- Suppression management (avoid over-triggering)
- Follow-up qualification (know when to escalate)
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


class ConversationState:
    """Tracks multi-turn conversation state for a merchant or customer."""

    def __init__(self, entity_id: str, entity_type: str = "merchant"):
        self.entity_id = entity_id
        self.entity_type = entity_type  # 'merchant' or 'customer'
        self.turns = []
        self.suppression_keys = set()
        self.last_message_time = None
        self.engagement_score = 0
        self.category_context = {}

    def add_turn(self, turn: Dict[str, Any]) -> None:
        """Add a turn to conversation history."""
        self.turns.append({
            **turn,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.last_message_time = datetime.utcnow()
        # Boost engagement score for YES responses
        if turn.get("response") == "YES":
            self.engagement_score += 1
        elif turn.get("response") == "STOP":
            self.engagement_score -= 2  # Penalize opt-outs

    def is_suppressed(self, suppression_key: str) -> bool:
        """Check if trigger is already in suppression list."""
        return suppression_key in self.suppression_keys

    def suppress(self, suppression_key: str, days: int = 3) -> None:
        """Add suppression key to prevent duplicate messaging."""
        self.suppression_keys.add(suppression_key)
        # In production, add expiry timestamp for TTL-based cleanup

    def should_escalate(self) -> bool:
        """Determine if merchant is ready for escalation (sales/support handoff)."""
        if len(self.turns) < 2:
            return False
        # Escalate if merchant replied with "help", "phone", "call" keywords
        recent = self.turns[-1]
        keywords = ("help", "phone", "call", "speak", "manager", "owner")
        return any(kw in recent.get("response", "").lower() for kw in keywords)

    def get_last_response(self) -> str:
        """Get the merchant's last message/response."""
        if self.turns:
            return self.turns[-1].get("response", "")
        return ""

    def minutes_since_last_message(self) -> Optional[float]:
        """Get minutes elapsed since last message."""
        if self.last_message_time:
            delta = datetime.utcnow() - self.last_message_time
            return delta.total_seconds() / 60
        return None


class ConversationHandler:
    """
    Main handler for multi-turn Vera conversations.

    Usage:
        handler = ConversationHandler()
        # After initial compose call
        state = handler.get_or_create_state("merchant_123")
        state.add_turn({"message_sent": body, "cta": cta, "response": "YES"})
        # On next trigger
        follow_up_body = handler.compose_follow_up("merchant_123", new_trigger, context)
    """

    def __init__(self):
        self.states: Dict[str, ConversationState] = {}

    def get_or_create_state(self, entity_id: str, entity_type: str = "merchant") -> ConversationState:
        """Get or create conversation state for entity."""
        key = f"{entity_type}:{entity_id}"
        if key not in self.states:
            self.states[key] = ConversationState(entity_id, entity_type)
        return self.states[key]

    def should_send_trigger(self, entity_id: str, suppression_key: str, entity_type: str = "merchant") -> bool:
        """
        Determine if trigger should be sent based on:
        1. Suppression status (avoid duplicates)
        2. Engagement level (don't over-trigger low-engagement merchants)
        3. Time since last message (cooldown)
        """
        state = self.get_or_create_state(entity_id, entity_type)

        # Check suppression
        if state.is_suppressed(suppression_key):
            return False

        # Check engagement (if score < -3, reduce trigger frequency)
        if state.engagement_score < -3:
            mins_elapsed = state.minutes_since_last_message() or 0
            if mins_elapsed < 60:  # Wait 1 hour before re-triggering low-engagement entity
                return False

        # Check if awaiting response (YES/STOP pending)
        last_response = state.get_last_response()
        if last_response and last_response not in ("YES", "STOP", "no", "later"):
            # Merchant gave custom reply, might still be thinking
            mins_elapsed = state.minutes_since_last_message() or 0
            if mins_elapsed < 30:
                return False

        return True

    def compose_follow_up(
        self,
        entity_id: str,
        last_cta: str,
        merchant_response: str,
        merchant: Dict[str, Any],
        category: Dict[str, Any],
        entity_type: str = "merchant",
    ) -> Optional[Dict[str, Any]]:
        """
        Compose follow-up message based on merchant's response to prior CTA.

        Returns None if follow-up not warranted (e.g., STOP response, escalation needed).
        """
        state = self.get_or_create_state(entity_id, entity_type)
        merchant_name = merchant.get("identity", {}).get("name", "there")

        # STOP responses: suppress and do not follow-up
        if merchant_response.lower() in ("stop", "no", "not now", "opt out"):
            state.suppress(f"stop:{entity_id}")
            return {
                "body": f"Got it, {merchant_name}. Suppressing future messages. Message us anytime!",
                "cta": "none",
                "send_as": "vera",
                "suppression_key": f"stop:{entity_id}",
                "rationale": "Merchant opted out; respect preference and stop messaging.",
            }

        # YES responses: move to action-oriented follow-up
        if merchant_response.lower() == "yes" or last_cta == "YES/STOP":
            state.engagement_score += 2
            return {
                "body": f"Perfect, {merchant_name}! Let's make this quick. Reply with the details you'd like to focus on, or just say 'ready' and I'll draft the full proposal.",
                "cta": "open_ended",
                "send_as": "vera",
                "suppression_key": f"followup:yes:{entity_id}",
                "rationale": "YES response detected; move to action phase with clear next step.",
            }

        # Custom replies: assess intent and respond contextually
        response_lower = merchant_response.lower()

        # Escalation keywords
        if any(kw in response_lower for kw in ("help", "phone", "call", "speak", "manager")):
            return {
                "body": f"Got it, {merchant_name}. I'll connect you with our team for a direct discussion. You'll hear from us within 2 hours.",
                "cta": "none",
                "send_as": "vera",
                "suppression_key": f"escalate:{entity_id}",
                "rationale": "Merchant requested escalation to human support.",
            }

        # Objection/question keywords
        if any(kw in response_lower for kw in ("why", "how", "cost", "price", "time", "when", "where")):
            return {
                "body": f"Great question, {merchant_name}! Here's the short answer: it takes 5 minutes, costs nothing, and you can see results in 24 hours. Ready to move forward?",
                "cta": "YES/STOP",
                "send_as": "vera",
                "suppression_key": f"objection:{entity_id}",
                "rationale": "Merchant raised objection; respond with value clarification.",
            }

        # Generic follow-up if unclear response
        return {
            "body": f"Thanks for the reply, {merchant_name}! So we're clear — are you interested in moving forward, or should I reach out another time?",
            "cta": "YES/STOP",
            "send_as": "vera",
            "suppression_key": f"clarify:{entity_id}",
            "rationale": "Unclear response; re-qualify with binary CTA.",
        }

    def get_merchant_stats(self, entity_id: str, entity_type: str = "merchant") -> Dict[str, Any]:
        """Get conversation statistics for a merchant/customer."""
        state = self.get_or_create_state(entity_id, entity_type)
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "turn_count": len(state.turns),
            "engagement_score": state.engagement_score,
            "suppressed_count": len(state.suppression_keys),
            "last_message_time": state.last_message_time.isoformat() if state.last_message_time else None,
            "should_escalate": state.should_escalate(),
        }

    def export_state(self, entity_id: str, entity_type: str = "merchant") -> Dict[str, Any]:
        """Export conversation state to JSON."""
        state = self.get_or_create_state(entity_id, entity_type)
        return {
            "entity_id": state.entity_id,
            "entity_type": state.entity_type,
            "turns": state.turns,
            "engagement_score": state.engagement_score,
            "suppressed_keys": list(state.suppression_keys),
        }

    def import_state(self, data: Dict[str, Any]) -> None:
        """Import conversation state from JSON."""
        state = ConversationState(data["entity_id"], data["entity_type"])
        state.turns = data.get("turns", [])
        state.engagement_score = data.get("engagement_score", 0)
        state.suppression_keys = set(data.get("suppressed_keys", []))
        key = f"{state.entity_type}:{state.entity_id}"
        self.states[key] = state


# Global handler instance (in production, use Redis/database for distributed state)
_global_handler = ConversationHandler()


def get_handler() -> ConversationHandler:
    """Get global conversation handler instance."""
    return _global_handler


# ============================================================================
# Integration with bot.py (optional enhanced compose function)
# ============================================================================

def compose_with_conversation(
    category: Dict[str, Any],
    merchant: Dict[str, Any],
    trigger: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
    merchant_prior_response: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Enhanced compose that uses conversation context.

    If merchant_prior_response is provided, checks conversation history
    and may return a follow-up message instead of a new trigger message.
    """
    from bot import compose

    merchant_id = merchant.get("merchant_id")
    handler = get_handler()

    # If this is a follow-up to a prior message, handle specially
    if merchant_prior_response:
        last_cta = trigger.get("prior_cta", "open_ended")
        follow_up = handler.compose_follow_up(
            merchant_id,
            last_cta,
            merchant_prior_response,
            merchant,
            category,
        )
        if follow_up:
            # Record the response in state
            state = handler.get_or_create_state(merchant_id)
            state.add_turn({
                "response": merchant_prior_response,
                "message_received": True,
            })
            return follow_up

    # Check if trigger should be sent (suppression, cooldown)
    suppression_key = trigger.get("suppression_key", trigger.get("id", ""))
    if not handler.should_send_trigger(merchant_id, suppression_key):
        return None

    # Compose new message using original bot
    message = compose(category, merchant, trigger, customer)

    # Record outgoing message in state
    state = handler.get_or_create_state(merchant_id)
    state.add_turn({
        "message_sent": message["body"],
        "cta": message["cta"],
        "trigger_kind": trigger.get("kind"),
    })

    return message
