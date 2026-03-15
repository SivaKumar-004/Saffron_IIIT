import os
import json
from dotenv import load_dotenv

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from database.farmer_db import register_farmer

load_dotenv(override=True)

class FarmerCallOrchestrator:
    """
    Listens to incoming calls/texts from farmers, extracts their details natively using Gemini,
    and calls the internal database tool to register them for automated alerts.
    """
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
        
        genai.configure(api_key=api_key.strip())
        
        # Tool: Register Farmer
        register_tool = FunctionDeclaration(
            name="register_farmer",
            description="Register a new farmer into the AgriSphere disaster alert database.",
            parameters={
                "type": "object",
                "properties": {
                    "phone": {
                        "type": "string",
                        "description": "The farmer's mobile phone number."
                    },
                    "region": {
                        "type": "string",
                        "description": "The state, region, or city the farmer is in (e.g. 'Goa', 'Tamil Nadu')."
                    },
                    "name": {
                        "type": "string",
                        "description": "The farmer's name, if provided."
                    },
                    "crop": {
                        "type": "string",
                        "description": "The type of crop the farmer grows, if provided."
                    }
                },
                "required": ["phone", "region"]
            }
        )
        
        self.tools = Tool(function_declarations=[register_tool])
        
        # System instructions
        self.system_prompt = (
            "You are the AgriSphere AI Call Center Operator. A farmer is communicating with you. "
            "Your job is to identify their mobile phone number and the region they live in. "
            "Also look for their name and crop type. Once you have their phone number and region, "
            "you MUST call the 'register_farmer' tool. "
            "After calling the tool, respond to the farmer politely in normal conversational language. "
            "If they did not provide enough info (like phone or region), politely ask them for it."
        )

        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=self.tools,
            system_instruction=self.system_prompt
        )

    def process_call(self, transcript: str):
        """
        Process the transcript using the LLM. If the LLM uses the tool, run it.
        Return the final text response.
        """
        print(f"📞 [Call Center Agent] Received transcript: {transcript}")
        try:
            chat = self.model.start_chat()
            response = chat.send_message(transcript)
            
            # Determine if the AI decided to invoke the Registration Tool based on the transcript
            while any(hasattr(part, 'function_call') and part.function_call for part in response.parts):
                for part in response.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_name = part.function_call.name
                        function_args = type(part.function_call).to_dict(part.function_call).get("args", {})
                        
                        print(f"🛠️ [Call Center Agent] Extracted Details - Calling Tool: {function_name} with {function_args}")
                        
                        if function_name == "register_farmer":
                            # Execute the python action
                            success = register_farmer(
                                phone=function_args.get("phone"),
                                region=function_args.get("region"),
                                name=function_args.get("name", "Unknown"),
                                crop=function_args.get("crop", "Unknown")
                            )
                            result = {"status": "success", "message": "Registered"} if success else {"status": "error"}
                            
                            # Return to AI
                            response = chat.send_message(
                                genai.protos.Content(
                                    role="user",
                                    parts=[
                                        genai.protos.Part(
                                            function_response=genai.protos.FunctionResponse(
                                                name=function_name,
                                                response=result
                                            )
                                        )
                                    ]
                                )
                            )
                        else:
                            break

            print(f"📞 [Call Center Agent] Responding: {response.text}")
            return {"reply": response.text}

        except Exception as e:
            print(f"⚠️ [Call Center Fallback] Gemini API Error: {e}")
            print("🔄 Falling back to basic regex parsing...")
            import re
            
            # Simple fallback regex for phone numbers (supports +91 or 10 digits)
            phone_match = re.search(r'(?:\+?91)?\s*?\d{10}', transcript)
            
            # Simple fallback region detection
            common_states = ["GOA", "KERALA", "PUNJAB", "TAMIL NADU", "ASSAM", "GUJARAT", "MAHARASHTRA", "KARNATAKA", "ERNAKULAM", "KOCHI", "DELHI", "HARYANA"]
            detected_region = "Unknown"
            for state in common_states:
                if state.lower() in transcript.lower():
                    detected_region = state.title()
                    break
                    
            if phone_match:
                # Clean the phone number (strip whitespace and +91 if present for standard 10 digit)
                raw_phone = phone_match.group(0).replace(" ", "")
                if raw_phone.startswith("+91"):
                    phone = raw_phone[3:]
                elif raw_phone.startswith("91") and len(raw_phone) == 12:
                    phone = raw_phone[2:]
                else:
                    phone = raw_phone
                    
                register_farmer(phone=phone, region=detected_region, name="Fallback User", crop="Unknown")
                
                # If they didn't provide a region, let them know we saved their number anyway
                if detected_region == "Unknown":
                    return {"reply": f"(Fallback Auto-Reply): We saved your number {phone}, but couldn't detect your state/region from your message. You will receive general network alerts."}
                else:
                    return {"reply": f"(Fallback Auto-Reply): We detected your phone number {phone} and region {detected_region}. You are now registered for alerts."}
            else:
                return {"reply": "(Fallback Auto-Reply): We could not understand your 10-digit phone number in that message. Please try again with just your number and state."}
