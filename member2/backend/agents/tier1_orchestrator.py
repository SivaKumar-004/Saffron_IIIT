import os
from typing import Dict, Any
from dotenv import load_dotenv

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from agents.disaster_monitoring_agent import DisasterMonitoringAgent
from agents.farmer_alert_agent import FarmerAlertAgent

# Load environment variables (API Keys)
load_dotenv()

class Tier1Orchestrator:
    """
    Manages the True Agentic AI pipeline powered by Google Gemini:
    The AI dynamically uses tools to discover data and dispatch alerts.
    """
    def __init__(self):
        self.monitoring_agent = DisasterMonitoringAgent()
        self.alert_agent = FarmerAlertAgent()
        
        # Initialize Gemini
        load_dotenv(override=True)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment.")
        
        # Clean the key to prevent trailing newlines crashing the google library
        api_key = api_key.strip()
        genai.configure(api_key=api_key)
        
        # Define the tools the AI can use autonomously
        monitor_tool = FunctionDeclaration(
            name="monitor_region",
            description="Fetch real-time or mock weather data for a specific region.",
            parameters={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "The name of the region to monitor (e.g., 'Tamil Nadu', 'Kerala')."
                    }
                },
                "required": ["region"]
            }
        )
        
        dispatch_tool = FunctionDeclaration(
            name="dispatch_alert",
            description="Dispatch an SMS or Voice alert to farmers in a region regarding severe risks.",
            parameters={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "The region to dispatch alerts to."
                    },
                    "risks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of risks detected (e.g. ['Heat Wave Risk', 'Flood Risk']). Empty if no risks."
                    },
                    "advisory": {
                        "type": "string",
                        "description": "A farmer-friendly advisory explaining what to do."
                    }
                },
                "required": ["region", "risks", "advisory"]
            }
        )
        
        self.tools = Tool(function_declarations=[monitor_tool, dispatch_tool])
        
        # Core prompt commanding the AI behaviour
        self.system_prompt = (
            "You are the AgriSphere Tier 1 Rural Disaster & Climate Support Agent. "
            "Your job is to protect farmers who only have access to keypad phones. "
            "1. Always use the 'monitor_region' tool first to fetch weather data for the requested region.\n"
            "2. Analyze the data. Rainfall > 80mm implies floods. Temperature > 40C implies heatwaves. "
            "Humidity < 25 & Rainfall < 10mm implies drought. Wind speed > 15km/h is a strong wind warning.\n"
            "3. If ANY risks are detected, you must use the 'dispatch_alert' tool to send SMS alerts to the farmers.\n"
            "4. Generate a final farmer-friendly 'advisory' string."
        )

        # Initialize the model with tools
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=self.tools,
            system_instruction=self.system_prompt
        )

    def run_tier1_pipeline(self, region: str) -> Dict[str, Any]:
        """
        Executes the full LLM-powered Tier 1 workflow.
        """
        # Initial data structures to capture what the AI decides to do
        ai_metrics = {}
        ai_risks = []
        ai_advisory = "Analyzing data..."
        alert_result = {
            "alert_triggered": False,
            "dispatch_method": "None",
            "dispatch_log": "No alerts dispatched by AI.",
            "farmers_reached": 0
        }

        try:
            # Start the chat session
            chat = self.model.start_chat()
            
            user_message = f"Please execute the climate agent tracking and dispatch pipeline for {region}."
            print(f"🤖 [Agentic AI] Sending instruction: {user_message}")
            
            # Step 1: Tell the LLM to think
            response = chat.send_message(user_message)
            
            # Handle Tool Call Loop
            while any(hasattr(part, 'function_call') and part.function_call for part in response.parts):
                for part in response.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_name = part.function_call.name
                        
                        # Safely convert protobuf MapComposite to a normal dict
                        function_args = type(part.function_call).to_dict(part.function_call).get("args", {})
                        
                        print(f"🛠️ [Agentic AI] Tool invoked: {function_name} with args {function_args}")
                        
                        # Store tool execution result
                        tool_response_data = {}
                        
                        if function_name == "monitor_region":
                            tool_response_data = self.monitoring_agent.monitor_region(
                                region=function_args.get("region", region)
                            )
                            ai_metrics = tool_response_data.get("metrics", {})
                            
                        elif function_name == "dispatch_alert":
                            tool_response_data = self.alert_agent.dispatch_alert(
                                region=function_args.get("region"),
                                risks=function_args.get("risks", []),
                                advisory=function_args.get("advisory", "")
                            )
                            alert_result = tool_response_data
                            ai_risks = function_args.get("risks", [])
                            ai_advisory = function_args.get("advisory", "")

                        # Send result back to AI
                        print(f"↪️  [Agentic AI] Sending tool output back to model.")
                        response = chat.send_message(
                            genai.protos.Content(
                                role="user",
                                parts=[
                                    genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name=function_name,
                                            response=tool_response_data
                                        )
                                    )
                                ]
                            )
                        )

            print(f"🤖 [Agentic AI] Final conclusion: {response.text}")
        except Exception as e:
            print(f"⚠️ [Agentic AI Fallback] Google API Quota/Error hit: {e}")
            print("🔄 Falling back to deterministic local processing logic to keep demo alive...")
            
            # Deterministic Fallback Logic
            metrics_response = self.monitoring_agent.monitor_region(region)
            ai_metrics = metrics_response.get("metrics", {})
            
            t = ai_metrics.get("temperature", 0)
            r = ai_metrics.get("rainfall", 0)
            w = ai_metrics.get("wind_speed", 0)
            h = ai_metrics.get("humidity", 0)
            
            if r > 80: ai_risks.append("Flood Risk")
            elif 50 <= r <= 80: ai_risks.append("Heavy Rain Warning")
            
            if t > 40: ai_risks.append("Heat Wave Risk")
            if h < 25 and r < 10: ai_risks.append("Drought Risk")
            if w > 15: ai_risks.append("Strong Wind Warning")
            
            if ai_risks:
                ai_advisory = f"URGENT: {', '.join(ai_risks)} detected in {region}. Please take necessary agricultural precautions."
                alert_result = self.alert_agent.dispatch_alert(region, ai_risks, ai_advisory)
            else:
                ai_advisory = f"Weather conditions are stable in {region}. Continue normal farming operations."

        # Format output to AgriSphere UI Standard
        return {
            "tier": "Tier 1 - Rural Disaster & Climate Support (Agentic AI - Gemini)",
            "status": "ok",
            "data": {
                "region": region,
                "temperature": ai_metrics.get("temperature"),
                "humidity": ai_metrics.get("humidity"),
                "rainfall": ai_metrics.get("rainfall"),
                "wind_speed": ai_metrics.get("wind_speed"),
                "risks": ai_risks
            },
            "recommendation": ai_advisory,
            "alert_dispatch": alert_result
        }

def orchestrate_climate(region: str) -> Dict[str, Any]:
    """Helper for FastAPI direct endpoint call."""
    orchestrator = Tier1Orchestrator()
    return orchestrator.run_tier1_pipeline(region)

def simulate_tier1_region() -> Dict[str, Any]:
    """Helper for Hackathon demo triggering a severe risk scenario."""
    import random
    from unittest.mock import patch
    
    demo_regions = [
        "Tamil Nadu", "Maharashtra", "Punjab", 
        "Kerala", "Assam", "Gujarat", "Karnataka"
    ]
    random_region = random.choice(demo_regions)
    
    # Forcefully inject severe weather directly into the AI pipeline for the demo
    severe_mock_data = {
        "temperature": round(random.uniform(40.0, 48.0), 1),
        "humidity": round(random.uniform(85.0, 99.0), 1),
        "rainfall": round(random.uniform(90.0, 150.0), 1), # High rainfall guarantees Flood
        "wind_speed": round(random.uniform(30.0, 60.0), 1) # High wind guarantees Wind Warning
    }
    
    with patch('agents.disaster_monitoring_agent.get_weather', return_value=severe_mock_data):
        return orchestrate_climate(random_region)
