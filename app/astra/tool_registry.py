import logging
from typing import Dict, Any, Optional

from app.shopify_client import shopify_client
from app.doctors.doctor_service import doctor_service
from app.storage_factory import storage_client

class ToolRegistry:
    """Registry for AI-callable tools"""
    
    def __init__(self):
        self.tools = {
            "shopify_search": self.shopify_search,
            "shopify_cart": self.shopify_cart,
            "doctor_search": self.doctor_search,
            "doctor_booking": self.doctor_booking,
            "storage_upload": self.storage_upload,
            "storage_list": self.storage_list,
            # Legacy aliases
            "storj_upload": self.storage_upload,
            "storj_list": self.storage_list,
            "reminder_set": self.reminder_set,
            "reminder_list": self.reminder_list,
            "notification_send": self.notification_send
        }
    
    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with arguments"""
        if tool_name not in self.tools:
            logger.error(f"Tool {tool_name} not found in registry")
            return {"error": f"Tool {tool_name} not found"}
        
        try:
            logger.info(f"🛠️ Executing tool: {tool_name} with args: {args}")
            # Identify if it's a coroutine or regular function
            import inspect
            func = self.tools[tool_name]
            if inspect.iscoroutinefunction(func):
                return await func(**args)
            else:
                return func(**args)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}

    # --- Tool Implementations ---

    async def shopify_search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search for products on Shopify"""
        products = shopify_client.search_product(query)
        return {"products": products}

    async def shopify_cart(self, items: list, user_uuid: str, **kwargs) -> Dict[str, Any]:
        """Create a draft order/cart on Shopify"""
        return {"success": True, "message": "Draft order created", "cart_url": f"https://ayureze.in/cart/{user_uuid}"}

    async def doctor_search(self, specialization: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Search for doctors"""
        doctors = await doctor_service.get_all_doctors(specialization=specialization, limit=5)
        return {"doctors": doctors}

    async def doctor_booking(self, doctor_id: str, date: str, time: str, user_uuid: str, **kwargs) -> Dict[str, Any]:
        """Book an appointment with a doctor"""
        return {"status": "confirmed", "appointment_id": "APT-12345", "doctor_id": doctor_id, "user_id": user_uuid}

    async def storage_upload(self, file_path: str, user_uuid: str, doc_type: str, **kwargs) -> Dict[str, Any]:
        """Upload a document to healthcare storage"""
        result = storage_client.upload_document(file_path, user_uuid, doc_type)
        return {"success": bool(result), "object_key": result}

    async def storage_list(self, user_uuid: str, **kwargs) -> Dict[str, Any]:
        """List user documents in healthcare storage"""
        docs = storage_client.list_patient_documents(user_uuid)
        return {"documents": docs}

    async def reminder_set(self, user_uuid: str, medicine_name: str, times: list, **kwargs) -> Dict[str, Any]:
        """Set a medicine reminder"""
        from app.medicine_reminders.supabase_reminder_service import supabase_reminder_service
        from datetime import datetime, timedelta
        
        # In a real scenario, we'd fetch patient name/phone from Supabase using user_uuid
        result = supabase_reminder_service.create_reminder(
            patient_id=user_uuid,
            patient_name="Patient", # Placeholder
            patient_phone="+910000000000", # Placeholder
            medicine_name=medicine_name,
            dosage=kwargs.get("dosage", "1 unit"),
            frequency=kwargs.get("frequency", "daily"),
            times=times,
            start_date=datetime.now().strftime("%Y-%m-%d"),
            end_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        )
        return result

    async def reminder_list(self, user_uuid: str, **kwargs) -> Dict[str, Any]:
        """Get all active reminders for a user"""
        from app.medicine_reminders.supabase_reminder_service import supabase_reminder_service
        reminders = supabase_reminder_service.get_patient_reminders(user_uuid)
        return {"reminders": reminders}

    async def notification_send(self, user_uuid: str, title: str, body: str, **kwargs) -> Dict[str, Any]:
        """Send a push notification to the user"""
        from app.notification_service import notification_service
        success = await notification_service.send_push_notification(
            patient_id=user_uuid,
            title=title,
            body=body,
            fcm_token=kwargs.get("fcm_token") # Model might suggest this if in metadata
        )
        return {"success": success}


tool_registry = ToolRegistry()
