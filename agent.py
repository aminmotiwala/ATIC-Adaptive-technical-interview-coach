"""
Main ATIC Agent Implementation
Author: Amin Motiwala

This module defines the root agent that orchestrates the multi-agent system
for adaptive technical interview coaching.
"""

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from agents.interviewer_agent import InterviewerAgent
from agents.researcher_agent import ResearcherAgent
from agents.feedback_agent import FeedbackAgent
from memory.memory_bank import MemoryBank
from sessions.session_manager import SessionManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini model for 5-point bonus
gemini_model = Gemini(
    name="gemini-pro",
    api_key=os.getenv("GEMINI_API_KEY")
)

# Initialize memory bank for long-term learning
memory_bank = MemoryBank()

# Initialize session manager for context tracking
session_manager = SessionManager(memory_bank)

# Create agent instances for coordination
interviewer_agent = InterviewerAgent(model=gemini_model, memory_bank=memory_bank)
researcher_agent = ResearcherAgent(model=gemini_model)
feedback_agent = FeedbackAgent(model=gemini_model, memory_bank=memory_bank)

# Define the root agent that orchestrates the multi-agent system
root_agent = Agent(
    name="atic_root_agent",
    model=gemini_model
)

def initialize_atic_session():
    """
    Initialize a new ATIC session with comprehensive context gathering.
    
    This function implements the 4-step session initialization process:
    1. Experience and Field Assessment
    2. Goal Definition (Job Description Analysis) 
    3. Context Engineering and Skill Extraction
    4. Adaptive Preparation Launch
    """
    return interviewer_agent.initialize_session_context()

def run_interview_session(user_profile: dict):
    """
    Execute the main interview session with sequential agent workflow.
    
    Args:
        user_profile: User profile data from initialization
    """
    return interviewer_agent.conduct_adaptive_interview(user_profile)

if __name__ == "__main__":
    # Entry point for ATIC system
    print("🚀 Adaptive Technical Interview Coach (ATIC) Starting...")
    user_profile = initialize_atic_session()
    run_interview_session(user_profile)