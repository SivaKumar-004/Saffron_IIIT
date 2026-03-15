import os
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

def run_tier2_crew(sensor_data: dict, anomaly_detected: bool = False):
    """
    Kicks off the Tier 2 Multi-Agent Crew to analyze the soil sensor data.
    """
    
    try:
        # Initialize Gemini LLM (Requires GOOGLE_API_KEY environment variable)
        gemini_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", verbose=True, temperature=0.5)

        # 1. Define Managers and Sub-Agents
        sensor_analyst = Agent(
            role='Sensor Analysis Agent',
            goal='Analyze raw telemetry from the soil sensors and flag any critical agricultural anomalies.',
            backstory='You are an expert agronomist specialized in predictive crop modeling and sensor data.',
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )
        
        irrigation_specialist = Agent(
            role='Irrigation & Fertilizer Agent',
            goal='Create precise watering and nutrient supply schedules based on soil analysis.',
            backstory='You are a water conservationist and soil chemist dedicated to maximizing farm yield.',
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )

        # 2. Define Tasks
        anomaly_status = "A CRITICAL DROUGHT ANOMALY HAS BEEN INJECTED/DETECTED!" if anomaly_detected else "Normal operating conditions."

        analysis_task = Task(
            description=f'Analyze the following sensor data: {sensor_data}. Current System Status: {anomaly_status}. Identify any risks to the crops.',
            expected_output='A brief bulleted report identifying if the soil is too dry, too hot, or lacking nutrients.',
            agent=sensor_analyst
        )

        action_task = Task(
            description='Based on the sensor analysis report, formulate a 24-hour irrigation schedule (in liters/hour) and fertilizer mix recommendation.',
            expected_output='A strict set of instructions for the farm hardware.',
            agent=irrigation_specialist
        )

        # 3. Form the Crew
        tier2_crew = Crew(
            agents=[sensor_analyst, irrigation_specialist],
            tasks=[analysis_task, action_task],
            process=Process.sequential,
            verbose=True
        )

        # Disable telemetry for cleaner logs in hackathon
        os.environ['CREWAI_TELEMETRY_OPT_OUT'] = 'true'
        result = tier2_crew.kickoff()
        return str(result)
        
    except Exception as e:
        # Return a cool fallback message for Hackathon Demos without an API Key
        return (
            f"🚨 [MOCK DEMO MODE - NO GOOGLE_API_KEY DETECTED]\n({str(e)})\n\n"
            "CrewAI Manager Analysis:\n"
            "- Soil Moisture is critically low.\n"
            "- Soil Temp is dangerously high.\n\n"
            "Tier 2 Automated Action Taken:\n"
            "- Triggering emergency irrigation valves (1.5L/hr) for the next 4 hours.\n"
            "- Alerting Tier 1 Manager to broadcast SMS warnings to neighboring farmers."
        )
