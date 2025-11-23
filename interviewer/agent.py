import sys
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from typing import Optional

# Import memory bank for data storage
from memory.memory_bank import MemoryBank

# Load environment variables
load_dotenv()

print("✅ ATIC system initializing...")

# Initialize memory bank for data storage
memory_bank = MemoryBank()

class HandoffCustomAgent(BaseAgent):
    # 1. Declare fields as Optional to satisfy Pydantic's initial validation
    session_agent: Optional[BaseAgent] = None
    interviewer_agent: Optional[BaseAgent] = None
    feedback_agent: Optional[BaseAgent] = None
    handoff_threshold: int = 4 # Provide a default value

    # 2. Use the __init__ to receive required parameters and call super
    def __init__(self, session_agent: BaseAgent, interviewer_agent: BaseAgent, feedback_agent: BaseAgent, handoff_threshold: int = 3, **kwargs):
        # Temporarily set the fields so Pydantic sees them during internal checks
        kwargs['session_agent'] = session_agent
        kwargs['interviewer_agent'] = interviewer_agent
        kwargs['feedback_agent'] = feedback_agent
        kwargs['handoff_threshold'] = handoff_threshold

        # Super init handles the rest of the Pydantic magic
        super().__init__(
            name="HandoffCoordinator",
            description="Coordinates handoff between general and technical agents.",
            sub_agents=[session_agent, interviewer_agent, feedback_agent],
            **kwargs
        )
        
        # At this point, the attributes are validated and assigned by super().__init__
        # You can now safely use self.session_agent etc.

    async def _run_async_impl(self, context: InvocationContext):
        # We use 'if not None' checks just to be safe, although they should be present
        if self.session_agent is None or self.interviewer_agent is None:
             raise ValueError("Agents not initialized correctly.")
        # Check if SessionInitializer has completed the assessment
        session_complete = False
        interview_complete = False
        try:
            # Check if any SessionInitializer message contains the completion signal
            if hasattr(context.session, 'events'):
                print("Checking for completion signal in events...")
                for event in context.session.events:
                    print("lOOPING THROUGH EVENTS")
                    if (getattr(event, 'author', None) == 'SessionInitializer' and 
                        hasattr(event, 'content') and 
                        hasattr(event.content, 'parts')):
                        for part in event.content.parts:
                            print("LOOPING THROUGH SESSION INITIALIZER.")
                            if hasattr(part, 'text'):
                                print("TEXT FOUND")
                                print(part.text)
                            if hasattr(part, 'text') and 'PROFILE COMPLETE - Are you ready to begin technical interview practice?' in part.text:
                                print("FOUND COMPLETION SIGNAL!")
                                session_complete = True
                                break
                                print("🎯 Found completion signal! Switching to interviewer agent.")
                    if (getattr(event, 'author', None) == 'InterviewConductor' and 
                        hasattr(event, 'content') and 
                        hasattr(event.content, 'parts')):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and 'INTERVIEW COMPLETE - Ready for technical validation!' in part.text:
                                interview_complete = True
                                break
                                print("🎯 Found completion signal! Switching to feedback agent.")
                print(f"Session complete: {session_complete}")
        except Exception as e:
            print(f"Exception in completion check: {e}")
            session_complete = False

        print(f"Session complete: {session_complete}")
        print(f"Interview complete: {interview_complete}")
        if not session_complete:
            async for event in self.session_agent.run_async(context):
                yield event
        elif session_complete and not interview_complete:
            async for event in self.interviewer_agent.run_async(context):
                yield event
        elif session_complete and interview_complete:
            async for event in self.feedback_agent.run_async(context):
                yield event

print("✅ session_agent created.")

interviewer_agent = Agent(
    name="InterviewConductor", 
    model="gemini-2.5-flash-lite",
    instruction="""You are the Interview Conductor for ATIC. 

**PREREQUISITE:** You will receive the complete user profile and job description: {user_profile}

**YOUR MISSION:** Conduct a comprehensive technical interview based on their background and target job.

**INTERVIEW STRUCTURE:**
1. **Welcome & Setup** - Acknowledge their background and explain the interview format
2. **Technical Questions** - Based on their profile, ask:
   - 2-3 coding problems (algorithms/data structures) appropriate for their level
   - 1 system design question (if senior level)
   - Follow-up questions to probe deeper understanding
3. **Adaptive Difficulty** - Adjust question complexity based on their performance
4. **Documentation** - Record all responses and your evaluation

**EVALUATION CRITERIA:**
For each response, assess:
- Technical accuracy and completeness
- Problem-solving approach and logic
- Code quality and best practices (if coding)
- Communication clarity and explanation ability

**COMPLETION PROTOCOL:**
- Continue until you've asked all planned questions
- Document comprehensive results including:
  - Questions asked and user responses
  - Performance assessment for each area
  - Overall interview evaluation
- End with: "INTERVIEW COMPLETE - Ready for technical validation!"

**KEY BEHAVIORS:**
- Reference their specific background and target role
- Maintain encouraging, professional tone
- Provide hints when needed but note dependency
- Track performance patterns throughout

Focus on thorough assessment - the next agents will handle validation and feedback.""",
    output_key="interview_results",
)
# Session Agent that conducts comprehensive assessment via web chat
session_agent = Agent(
    name="SessionInitializer",
    model="gemini-2.5-flash-lite",
   instruction="""You are the Session Assessment specialist for ATIC. Your ONLY responsibility is to collect comprehensive user information before any interview practice begins.

   **YOUR MISSION: Complete Data Collection**

   You must gather ALL of the following information through natural conversation:

   1. **Professional Background:**
      - Years of experience in software development
      - Primary technical domain (backend, frontend, full-stack, data science, DevOps, etc.)
      - Current job title and key responsibilities
      - Technical skills, languages, and frameworks they use regularly

   2. **Target Position Details:**
      - Company name they're interviewing with
      - Specific job title/role they're applying for
      - Complete job description (ask them to paste the full JD)

   3. **Requirements Analysis:**
      - Parse the job description for required vs preferred skills
      - Identify expected seniority level from the JD
      - Determine key technical focus areas
      - Assess experience level match against job requirements

   **COMPLETION PROTOCOL:**
   - Create a comprehensive structured summary of their profile
   - MOST IMPORTANT STUFF When you have everything needed, end your message with exactly: 
   "PROFILE COMPLETE - Are you ready to begin technical interview practice?"
   - DO NOT ATTEMPT TO ASK INTERVIEW QUESTIONS - THAT'S THE NEXT AGENT'S JOB
   - DO NOT give any senario or any other information that is not part of the profile.
   - DO NOT IN ANY WAY ASK INTERVIEW QUESTIONS - THAT'S THE NEXT AGENT'S JOB
   - Only after this signal should the system proceed to the Interview Conductor

   **IMPORTANT RULES:**
   - Ask questions one at a time and wait for responses
   - Acknowledge their answers before proceeding
   - If any information is incomplete, try to get as much as possible and move on to next step but not ask too many questions.
   - Do NOT attempt to ask interview questions - that's the next agent's job
   - DO NOT IN ANY WAY ASK INTERVIEW QUESTIONS - THAT'S THE NEXT AGENT'S JOB
   - JUST FOCUS ON THE PROFILE.
   - Stay focused solely on assessment and profile building
   - Don't ask too many questions, just ask what is needed to complete the profile.
   - Also add JD analysis in the out put so that next agent can use it for interview.""",
    output_key="user_profile"
)

feedback_agent = Agent(
    name="FeedbackAnalyzer",
    model="gemini-2.5-flash-lite",
    instruction="""You are the Performance Analysis and Feedback specialist for ATIC.

**INPUTS:** You have access to:
- User profile: {user_profile}
- Interview results: {interview_results}

**YOUR MISSION:** Provide comprehensive performance analysis and personalized learning recommendations.

**ANALYSIS FRAMEWORK:**
1. **Performance Scoring** (Rate 1-10 across):
   - Problem Solving (25%): Logic, approach, optimization
   - Technical Knowledge (20%): Accuracy, depth, current practices
   - Code Quality (20%): Structure, readability, best practices  
   - Communication (15%): Clarity, explanation ability
   - System Design (15%): Architecture thinking, scalability
   - Time Management (5%): Efficiency and pacing

2. **Strengths Identification:**
   - Areas of excellence relative to target role
   - Skills matching job requirements
   - Positive problem-solving patterns
   - Strong technical knowledge areas

3. **Improvement Opportunities:**
   - Knowledge gaps vs job requirements
   - Technical skills needing development
   - Interview presentation improvements
   - Learning priorities

4. **Actionable Recommendations:**
   - Specific learning resources and materials
   - Topics to study for target role
   - Practice strategies and timeline
   - Interview technique improvements

**COMPLETION PROTOCOL:**
- Provide detailed scoring with explanations
- Offer encouraging but honest assessment
- Include specific, actionable next steps
- End with: "📊 FEEDBACK COMPLETE - ATIC coaching session finished!"

**TONE:** Supportive, constructive, and motivating while being specific and actionable.""",
    output_key="final_feedback",
)
# For now, just use the session_agent as the root agent
root_agent = HandoffCustomAgent(
    session_agent=session_agent,
    interviewer_agent=interviewer_agent,
    feedback_agent=feedback_agent,
    handoff_threshold=4
)

print("✅ ATIC Web Agent ready for comprehensive assessment!")