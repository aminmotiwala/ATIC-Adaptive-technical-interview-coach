# Adaptive Technical Interview Coach (ATIC)

**Author:** Amin Motiwala  
**Version:** 1.0.0  
**Kaggle Track:** Agents for Good  

## 🎯 Project Overview

The Adaptive Technical Interview Coach (ATIC) is a sophisticated multi-agent system that revolutionizes technical interview preparation through real-time personalization and adaptive learning. Unlike static interview prep tools, ATIC dynamically identifies user weaknesses and customizes subsequent questions in real-time, accelerating interview readiness through contextualized, job-specific preparation.

## 🏆 Problem Statement

Traditional technical interview preparation tools suffer from:
- **Static questioning** that doesn't adapt to user performance
- **Generic preparation** that ignores specific job requirements
- **No learning retention** between sessions
- **Limited real-time feedback** and validation

ATIC solves these problems by providing:
- **Dynamic, personalized interview simulation** that adapts in real-time
- **Job description-driven contextualization** for targeted preparation
- **Persistent memory and learning adaptation** across sessions
- **Real-time research and validation** of technical concepts

## 🤖 Multi-Agent Architecture

ATIC implements a **Sequential Multi-Agent System** with internal loops, powered by **Gemini 2.5 Flash Lite** for the 5-point bonus:

### Agent 1: Interviewer Agent (Goal-Based)
- **Role:** Primary interview conductor and session orchestrator
- **Responsibilities:**
  - 4-step session initialization and context gathering
  - Dynamic question generation based on user profile and JD analysis
  - Real-time response evaluation and difficulty adjustment
  - Code execution management for technical assessments

### Agent 2: Researcher Agent (Utility-Based)
- **Role:** Real-time knowledge validation and industry research
- **Responsibilities:**
  - Technical concept validation and best practices lookup
  - Industry standard verification and market trend analysis
  - Company-specific engineering culture research
  - System design pattern and architecture validation

### Agent 3: Feedback Agent (Learning)
- **Role:** Performance synthesis and adaptive learning management
- **Responsibilities:**
  - Comprehensive performance analysis and scoring
  - Memory bank updates and learning progression tracking
  - Personalized feedback generation and improvement recommendations
  - Long-term adaptation strategy development

## 🎯 Key Features Implementation

### 1. Multi-Agent System (Sequential + Loops)
- **Sequential Execution:** Interviewer → Researcher → Feedback → Interviewer
- **Internal Loops:** Dynamic question adjustment based on performance feedback
- **Agent Coordination:** Seamless data flow and context sharing between agents

### 2. Sessions & Memory (Long-term Memory)
- **Memory Bank:** SQLite-based persistent storage for user profiles and performance history
- **Learning Agent Behavior:** Continuous adaptation based on historical performance data
- **Session Context:** Maintains user background, job targets, and progress across sessions

### 3. Tools Integration (Code Execution + Google Search)
- **Code Execution Tool:** Secure Python and Java code execution with timeout and security validation
- **Google Search Tool:** Real-time research capabilities for technical concept validation
- **Multi-language Support:** Python and Java with extensible architecture

## 🚀 Session Initialization Process

ATIC's sophisticated 4-step initialization maximizes personalization:

### Step 1: Experience and Field Assessment
- Professional experience years and technical specialization
- Self-assessment across relevant skill areas
- Current role and company context gathering

### Step 2: Goal Definition (Job Description Analysis)
- Complete job description text collection
- Target company and role specification
- Interview timeline and context capture

### Step 3: Context Engineering (JD Parsing)
- **Context Compaction:** Automated skill extraction from job descriptions
- **Requirement Analysis:** Required vs. preferred skills identification
- **Seniority Detection:** Experience level matching and gap analysis

### Step 4: Adaptive Preparation Launch
- **Personalized Interview Plan:** Tailored session structure based on user profile
- **Difficulty Calibration:** Initial difficulty matching user experience vs. job requirements
- **Focus Area Prioritization:** Interview phases based on JD analysis

## 🏗️ Project Structure

```
atic-agent/
├── agent.py                 # Root agent and main entry point
├── __init__.py             # Package initialization
├── .env                    # Environment configuration
├── requirements.txt        # Python dependencies
├── agents/                 # Multi-agent implementations
│   ├── interviewer_agent.py    # Goal-based interview conductor
│   ├── researcher_agent.py     # Utility-based research agent
│   └── feedback_agent.py       # Learning agent for adaptation
├── sessions/               # Session management
│   └── session_manager.py      # 4-step initialization process
├── memory/                 # Long-term memory system
│   └── memory_bank.py          # SQLite-based persistent storage
├── tools/                  # ADK tools integration
│   ├── code_execution.py       # Secure code execution
│   └── google_search.py        # Real-time search capabilities
└── config/                 # Configuration management
    └── settings.py             # Centralized configuration
```

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.9+
- Java 17+ (for Java code execution)
- Google Gemini API access
- Google Search API (optional, for enhanced research)

### Installation Steps

1. **Clone and Navigate:**
```bash
git clone <repository-url>
cd atic-agent
```

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure Environment:**
```bash
cp .env.example .env
# Edit .env with your API keys:
# GEMINI_API_KEY=your_gemini_api_key_here
# GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here (optional)
# GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here (optional)
```

4. **Run ATIC:**
```bash
python agent.py
```

## 🎮 Usage Example

```python
from atic_agent import initialize_atic_session, run_interview_session

# Start adaptive interview session
session_id = initialize_atic_session()
# This triggers the 4-step initialization:
# 1. Experience assessment
# 2. Job description analysis
# 3. Context engineering
# 4. Adaptive preparation launch

# Run personalized interview
results = run_interview_session(session_id)
# Sequential agent workflow:
# InterviewerAgent → ResearcherAgent → FeedbackAgent → Adaptation
```

## 🎯 Value Proposition

### For Interview Candidates:
- **Personalized Preparation:** Every question adapted to your experience and target role
- **Real-time Learning:** Immediate feedback and difficulty adjustment
- **Job-Specific Focus:** Preparation targeted to actual job requirements
- **Progress Tracking:** Persistent memory of improvement areas and strengths

### For Technical Innovation:
- **Advanced Agent Coordination:** Sophisticated multi-agent orchestration with learning loops
- **Context-Aware AI:** Deep job description analysis and user profiling
- **Adaptive Learning System:** Continuous improvement through memory-based adaptation
- **Real-time Research Integration:** Live validation of technical concepts and industry standards

## 🏆 Competitive Advantages

1. **Dynamic Adaptation:** Unlike static prep tools, ATIC adjusts in real-time based on performance
2. **Job-Specific Context:** Deep integration of actual job requirements into preparation
3. **Multi-Agent Intelligence:** Sophisticated agent coordination for comprehensive assessment
4. **Learning Persistence:** Memory-based improvement tracking across multiple sessions
5. **Technical Depth:** Real code execution and live research capabilities

## 🔧 Configuration

ATIC uses `gemini-2.5-flash-lite` throughout the project for optimal performance and cost efficiency. Key configuration options:

- **Model:** Gemini 2.5 Flash Lite (5-point Kaggle bonus)
- **Code Execution:** Python and Java support with security validation
- **Search Integration:** Real-time Google Search with fallback mock results
- **Memory Persistence:** SQLite database with configurable retention
- **Adaptive Parameters:** Customizable difficulty adjustment thresholds

## 🚀 Future Enhancements

- **Additional Programming Languages:** C++, JavaScript, Go support
- **Video Interview Simulation:** Real-time video interaction capabilities
- **Company-Specific Question Banks:** Curated questions by company engineering culture
- **Advanced Analytics Dashboard:** Comprehensive performance visualization
- **API Integration:** REST API for external platform integration

## 📄 License

This project is developed for the Kaggle Agents competition. Please refer to competition guidelines for usage terms.

---

**Ready to revolutionize your technical interview preparation? Start your adaptive learning journey with ATIC today!** 🚀