import logging
import json

logger = logging.getLogger(__name__)

class CapabilityAgent:
    """
    The 'Hands' of Astra. 
    Parses the 'Brain's' text response for special commands to execute actions 
    or trigger escalation.
    """
    def __init__(self):
        self.tools = {
            "book_appointment": self.tool_book_appointment,
            "check_availability": self.tool_check_availability,
        }

    def process_response_actions(self, ai_response_text: str) -> dict:
        """
        Scans the AI response for [ESCALATE] or [ACTION:...] tags.
        Returns a dict with 'action_taken': bool, 'modified_response': str
        """
        result = {
            "action_taken": False, 
            "escalation": False,
            "modified_response": ai_response_text
        }
        
        # 1. Check for Escalation
        if "[ESCALATE]" in ai_response_text:
            logger.warning("⚠️ Escalation Triggered by AI")
            result["escalation"] = True
            # Remove the tag from the user-facing message
            result["modified_response"] = ai_response_text.replace("[ESCALATE]", "").strip()
            # In a real scenario, you would trigger a DB update or notification here
            return result

        # 2. Check for Automation Actions: [ACTION:json_data]
        if "[ACTION:" in ai_response_text and "]" in ai_response_text:
            try:
                # Extract content between [ACTION: and ]
                start = ai_response_text.find("[ACTION:") + 8
                end = ai_response_text.find("]", start)
                action_str = ai_response_text[start:end]
                
                # Parse JSON command: e.g. {"tool": "book_appointment", "data": {...}}
                # Note: The model must be prompted to output valid JSON inside the tag
                command = json.loads(action_str)
                
                tool_name = command.get("tool")
                if tool_name in self.tools:
                    logger.info(f"🛠️ Executing Tool: {tool_name}")
                    tool_output = self.tools[tool_name](command.get("data", {}))
                    
                    # Append tool output to response
                    result["action_taken"] = True
                    result["modified_response"] = ai_response_text.replace(f"[ACTION:{action_str}]", "").strip()
                    result["modified_response"] += f"\n\n(System: {tool_output})"
                
            except Exception as e:
                logger.error(f"❌ Failed to execute AI action: {e}")
        
        return result

    # --- Tool Implementations ---
    
    def tool_book_appointment(self, data: dict) -> str:
        # Placeholder for real database write
        date = data.get("date", "unknown date")
        return f"✅ Appointment successfully booked for {date}."

    def tool_check_availability(self, data: dict) -> str:
        return "Checking... Yes, Dr. Sharma is available at 10 AM."

    def allowed(self, intent: str) -> bool:
        return True
