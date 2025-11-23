"""
Session Manager Implementation
Author: Amin Motiwala

Manages the complete session lifecycle including initialization, context gathering,
and coordination between agents in the sequential workflow.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


class SessionManager:
    """
    Manages session lifecycle and coordinates multi-agent interactions.
    
    This class implements:
    - 4-step session initialization process
    - Context gathering and user profiling
    - Session state management
    - Agent coordination for sequential workflow
    - Session persistence and recovery
    """
    
    def __init__(self, memory_bank):
        self.memory_bank = memory_bank
        self.active_sessions = {}
        self.session_history = []
    
    def initialize_session(self) -> str:
        """
        Initialize a new ATIC session with comprehensive context gathering.
        
        Implements the 4-step process:
        1. Experience and Field Assessment (Context Gathering)
        2. Goal Definition (Job Description Analysis)  
        3. Context Engineering (JD parsing and skill extraction)
        4. Adaptive Preparation Launch
        
        Returns:
            session_id: Unique identifier for the created session
        """
        session_id = self._generate_session_id()
        
        print("🚀 Starting Adaptive Technical Interview Coach (ATIC)")
        print("=" * 60)
        print("Welcome! Let's personalize your interview preparation experience.\n")
        
        # Initialize session structure
        session_data = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'status': 'initializing',
            'user_profile': {},
            'context_data': {},
            'interview_plan': {},
            'agent_interactions': []
        }
        
        try:
            # Step 1: Experience and Field Assessment
            print("🔍 STEP 1: Experience & Field Assessment")
            experience_data = self._gather_experience_assessment()
            session_data['user_profile']['experience'] = experience_data
            
            # Step 2: Goal Definition (Job Description Analysis)
            print("\n🎯 STEP 2: Goal Definition")
            job_data = self._gather_job_description_analysis()
            session_data['user_profile']['target_job'] = job_data
            
            # Step 3: Context Engineering & Skill Extraction
            print("\n⚙️ STEP 3: Context Engineering & Skill Extraction")
            extracted_skills = self._perform_context_engineering(job_data['description'])
            session_data['context_data']['extracted_requirements'] = extracted_skills
            
            # Step 4: Adaptive Preparation Launch Setup
            print("\n🚀 STEP 4: Adaptive Preparation Launch Setup")
            interview_plan = self._create_adaptive_interview_plan(
                experience_data, job_data, extracted_skills
            )
            session_data['interview_plan'] = interview_plan
            
            # Finalize session initialization
            session_data['status'] = 'initialized'
            session_data['user_profile']['difficulty_level'] = self._calculate_initial_difficulty(
                experience_data, extracted_skills
            )
            
            # Store session in active sessions and memory bank
            self.active_sessions[session_id] = session_data
            self.memory_bank.store_session_initialization(session_data)
            
            print("\n✅ Session initialization complete!")
            print(f"📊 Your profile: {experience_data['field']} developer with {experience_data['years']} years experience")
            print(f"🎯 Target role: {job_data['role']} at {job_data['company']}")
            print(f"📈 Initial difficulty: {session_data['user_profile']['difficulty_level']}")
            print(f"🔗 Session ID: {session_id}\n")
            
            return session_id
            
        except Exception as e:
            print(f"❌ Session initialization failed: {str(e)}")
            session_data['status'] = 'failed'
            session_data['error'] = str(e)
            self.active_sessions[session_id] = session_data
            return session_id
    
    def _gather_experience_assessment(self) -> Dict[str, Any]:
        """
        Step 1: Comprehensive experience and field assessment.
        
        Gathers detailed information about:
        - Years of professional experience
        - Primary technical field/specialization
        - Current role and responsibilities
        - Previous interview experience
        - Self-assessed skill levels
        """
        print("Please provide information about your professional background:")
        
        # Core experience information
        while True:
            try:
                years_input = input("💼 Years of professional experience: ")
                years_experience = int(years_input) if years_input.isdigit() else 0
                break
            except ValueError:
                print("Please enter a valid number.")
        
        technical_field = input("🔧 Primary technical field (e.g., front-end, back-end, data science, DevOps, full-stack): ").strip().lower()
        current_role = input("👔 Current job title: ").strip()
        
        # Additional context
        print("\nOptional additional context:")
        company_size = input("🏢 Current company size (startup/mid-size/enterprise) [Optional]: ").strip()
        previous_interviews = input("📊 Recent technical interviews attempted (number) [Optional]: ").strip()
        
        # Self-assessment of technical areas
        print("\n📋 Quick self-assessment (1-5 scale, 5 being expert):")
        self_assessment = {}
        
        skill_areas = self._get_skill_areas_for_field(technical_field)
        for skill in skill_areas[:5]:  # Limit to top 5 relevant skills
            while True:
                try:
                    score_input = input(f"   {skill} (1-5): ")
                    if score_input.strip() == "":
                        score = 3  # Default to intermediate
                    else:
                        score = int(score_input)
                        if 1 <= score <= 5:
                            break
                        else:
                            print("Please enter a number between 1 and 5.")
                            continue
                    self_assessment[skill] = score
                    break
                except ValueError:
                    print("Please enter a valid number.")
        
        return {
            'years': years_experience,
            'field': technical_field,
            'current_role': current_role,
            'company_size': company_size,
            'previous_interviews': previous_interviews,
            'self_assessment': self_assessment,
            'proficiency_areas': skill_areas,
            'experience_level': self._categorize_experience_level(years_experience)
        }
    
    def _gather_job_description_analysis(self) -> Dict[str, Any]:
        """
        Step 2: Comprehensive job description collection and initial analysis.
        
        Collects:
        - Target company information
        - Complete job description text
        - Role-specific details
        - Application timeline
        """
        print("Please provide details about your target position:")
        
        target_company = input("🏢 Company name: ").strip()
        target_role = input("💼 Job title: ").strip()
        interview_timeline = input("📅 Expected interview timeline (e.g., '2 weeks', 'next month') [Optional]: ").strip()
        
        print("\n📄 Job Description Analysis:")
        print("Please paste the complete job description below.")
        print("💡 Tip: Include requirements, responsibilities, and preferred qualifications")
        print("Press Enter twice when finished, or type 'DONE' on a new line:")
        
        job_description_lines = []
        consecutive_empty = 0
        
        while True:
            line = input()
            
            if line.strip().upper() == 'DONE':
                break
                
            if line == "":
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    break
            else:
                consecutive_empty = 0
                job_description_lines.append(line)
        
        job_description = "\n".join(job_description_lines)
        
        if not job_description.strip():
            print("⚠️ No job description provided. Using generic technical role template.")
            job_description = f"Generic {target_role} position requiring technical skills and problem-solving abilities."
        
        return {
            'company': target_company,
            'role': target_role,
            'description': job_description,
            'timeline': interview_timeline,
            'description_length': len(job_description),
            'collected_at': datetime.now().isoformat()
        }
    
    def _perform_context_engineering(self, job_description: str) -> Dict[str, Any]:
        """
        Step 3: Advanced context engineering and skill extraction.
        
        Implements context compaction to extract:
        - Required technical skills (must-have)
        - Preferred skills (nice-to-have)
        - Expected seniority level
        - Key technical responsibilities
        - Interview focus areas
        - Technology stack
        """
        print("Analyzing job description for key requirements...")
        
        # Initialize extraction results
        extraction_results = {
            'required_technical_skills': [],
            'preferred_skills': [],
            'seniority_indicators': [],
            'responsibility_categories': [],
            'technology_stack': [],
            'soft_skills': [],
            'interview_focus_areas': [],
            'complexity_level': 'intermediate'
        }
        
        if not job_description.strip():
            return self._get_default_extraction_template()
        
        # Convert to lowercase for analysis
        jd_lower = job_description.lower()
        
        # Extract technical skills using keyword matching
        technical_keywords = {
            'programming_languages': ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'typescript', 'php', 'ruby'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel', 'rails'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb'],
            'cloud_platforms': ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'jenkins', 'ci/cd', 'microservices', 'api', 'rest', 'graphql']
        }
        
        for category, keywords in technical_keywords.items():
            found_skills = [skill for skill in keywords if skill in jd_lower]
            extraction_results['technology_stack'].extend(found_skills)
        
        # Determine seniority level
        seniority_indicators = {
            'senior': ['senior', 'lead', 'principal', 'architect', '5+ years', 'mentor', 'leadership'],
            'mid': ['mid-level', '3-5 years', 'experienced', 'solid experience'],
            'junior': ['junior', 'entry-level', '0-2 years', 'new graduate', 'recent graduate']
        }
        
        detected_seniority = 'mid'  # default
        for level, indicators in seniority_indicators.items():
            if any(indicator in jd_lower for indicator in indicators):
                detected_seniority = level
                extraction_results['seniority_indicators'].extend(
                    [indicator for indicator in indicators if indicator in jd_lower]
                )
                break
        
        # Extract responsibility categories
        responsibility_keywords = {
            'system_design': ['system design', 'architecture', 'scalable', 'distributed', 'microservices'],
            'coding': ['coding', 'programming', 'development', 'implementation', 'algorithms'],
            'collaboration': ['collaborate', 'team', 'cross-functional', 'communication'],
            'leadership': ['mentor', 'lead', 'guide', 'technical leadership']
        }
        
        for category, keywords in responsibility_keywords.items():
            if any(keyword in jd_lower for keyword in keywords):
                extraction_results['responsibility_categories'].append(category)
        
        # Determine interview focus areas based on extracted data
        focus_areas = []
        if extraction_results['technology_stack']:
            focus_areas.append('technical_knowledge')
        if 'coding' in extraction_results['responsibility_categories']:
            focus_areas.append('coding_problems')
        if 'system_design' in extraction_results['responsibility_categories']:
            focus_areas.append('system_design')
        if 'leadership' in extraction_results['responsibility_categories']:
            focus_areas.append('behavioral_leadership')
        
        extraction_results['interview_focus_areas'] = focus_areas or ['general_technical']
        
        # Set complexity level based on seniority and responsibilities
        if detected_seniority == 'senior' or len(extraction_results['responsibility_categories']) > 3:
            extraction_results['complexity_level'] = 'advanced'
        elif detected_seniority == 'junior':
            extraction_results['complexity_level'] = 'beginner'
        
        # Separate required vs preferred skills (simplified heuristic)
        all_skills = extraction_results['technology_stack']
        extraction_results['required_technical_skills'] = all_skills[:6]  # First 6 as required
        extraction_results['preferred_skills'] = all_skills[6:]  # Rest as preferred
        
        print(f"✅ Extracted {len(all_skills)} technical skills")
        print(f"📊 Detected seniority level: {detected_seniority}")
        print(f"🎯 Interview focus areas: {', '.join(focus_areas)}")
        
        return extraction_results
    
    def _create_adaptive_interview_plan(self, experience_data: Dict, job_data: Dict, extracted_skills: Dict) -> Dict[str, Any]:
        """
        Step 4: Create comprehensive adaptive interview plan.
        
        Creates a personalized interview plan based on:
        - User's experience level vs job requirements
        - Identified skill gaps
        - Interview focus areas from JD analysis
        - Adaptive difficulty progression
        """
        print("Creating your personalized interview plan...")
        
        interview_plan = {
            'session_structure': {},
            'question_categories': [],
            'difficulty_progression': {},
            'focus_areas': [],
            'estimated_duration': 0,
            'adaptive_parameters': {}
        }
        
        # Determine session structure based on seniority and focus areas
        user_seniority = experience_data['experience_level']
        job_seniority = extracted_skills.get('complexity_level', 'intermediate')
        focus_areas = extracted_skills.get('interview_focus_areas', ['general_technical'])
        
        # Create session structure
        session_phases = []
        
        if 'coding_problems' in focus_areas:
            session_phases.append({
                'phase': 'coding_assessment',
                'duration_minutes': 30,
                'question_count': 2,
                'difficulty': self._match_difficulty_to_gap(user_seniority, job_seniority)
            })
        
        if 'system_design' in focus_areas:
            session_phases.append({
                'phase': 'system_design',
                'duration_minutes': 25,
                'question_count': 1,
                'difficulty': job_seniority
            })
        
        if 'technical_knowledge' in focus_areas:
            session_phases.append({
                'phase': 'technical_concepts',
                'duration_minutes': 15,
                'question_count': 3,
                'difficulty': user_seniority
            })
        
        if 'behavioral_leadership' in focus_areas or user_seniority in ['mid', 'senior']:
            session_phases.append({
                'phase': 'behavioral',
                'duration_minutes': 10,
                'question_count': 2,
                'difficulty': user_seniority
            })
        
        interview_plan['session_structure'] = session_phases
        interview_plan['estimated_duration'] = sum(phase['duration_minutes'] for phase in session_phases)
        
        # Set adaptive parameters
        interview_plan['adaptive_parameters'] = {
            'initial_difficulty': self._calculate_initial_difficulty(experience_data, extracted_skills),
            'adjustment_threshold': 0.3,  # Score threshold for difficulty adjustment
            'max_difficulty_jumps': 1,    # Maximum difficulty level changes per session
            'personalization_factors': {
                'experience_years': experience_data['years'],
                'field_expertise': experience_data['field'],
                'target_role_complexity': job_seniority,
                'self_assessed_confidence': self._calculate_confidence_score(experience_data)
            }
        }
        
        # Set focus areas for questioning
        interview_plan['focus_areas'] = focus_areas
        interview_plan['question_categories'] = self._map_focus_to_question_categories(focus_areas)
        
        print(f"📋 Interview plan created:")
        print(f"   Duration: ~{interview_plan['estimated_duration']} minutes")
        print(f"   Phases: {len(session_phases)}")
        print(f"   Focus areas: {', '.join(focus_areas)}")
        print(f"   Initial difficulty: {interview_plan['adaptive_parameters']['initial_difficulty']}")
        
        return interview_plan
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete session data by ID."""
        return self.active_sessions.get(session_id)
    
    def update_session_status(self, session_id: str, status: str, additional_data: Dict = None) -> bool:
        """Update session status and optionally add additional data."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['status'] = status
            self.active_sessions[session_id]['last_updated'] = datetime.now().isoformat()
            
            if additional_data:
                self.active_sessions[session_id].update(additional_data)
            
            return True
        return False
    
    def record_agent_interaction(self, session_id: str, agent_name: str, interaction_data: Dict) -> bool:
        """Record an agent interaction in the session log."""
        if session_id in self.active_sessions:
            interaction_record = {
                'timestamp': datetime.now().isoformat(),
                'agent': agent_name,
                'interaction_type': interaction_data.get('type', 'unknown'),
                'data': interaction_data
            }
            
            self.active_sessions[session_id]['agent_interactions'].append(interaction_record)
            return True
        return False
    
    def finalize_session(self, session_id: str) -> Dict[str, Any]:
        """Finalize session and move to history."""
        if session_id in self.active_sessions:
            session_data = self.active_sessions[session_id]
            session_data['status'] = 'completed'
            session_data['completed_at'] = datetime.now().isoformat()
            
            # Move to history
            self.session_history.append(session_data)
            del self.active_sessions[session_id]
            
            # Store final session record in memory bank
            self.memory_bank.store_completed_session(session_data)
            
            return session_data
        return {}
    
    # Helper methods
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        return f"atic_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    def _get_skill_areas_for_field(self, field: str) -> List[str]:
        """Get relevant skill areas for technical field assessment."""
        field_skills = {
            'front-end': ['JavaScript/TypeScript', 'React/Vue/Angular', 'CSS/Styling', 'Web Performance', 'Testing'],
            'back-end': ['System Design', 'Database Design', 'API Development', 'Scalability', 'Security'],
            'full-stack': ['Frontend Development', 'Backend Development', 'Database Design', 'System Architecture', 'DevOps'],
            'data science': ['Machine Learning', 'Statistics', 'Python/R', 'Data Processing', 'Visualization'],
            'devops': ['Infrastructure', 'CI/CD', 'Monitoring', 'Cloud Platforms', 'Automation'],
            'mobile': ['iOS/Android Development', 'Mobile UI/UX', 'Performance', 'Testing', 'App Store'],
            'qa': ['Test Automation', 'Manual Testing', 'Performance Testing', 'Security Testing', 'Tools']
        }
        return field_skills.get(field, ['Problem Solving', 'Algorithms', 'Data Structures', 'System Design', 'Communication'])
    
    def _categorize_experience_level(self, years: int) -> str:
        """Categorize experience level based on years."""
        if years <= 2:
            return 'junior'
        elif years <= 5:
            return 'mid'
        else:
            return 'senior'
    
    def _get_default_extraction_template(self) -> Dict[str, Any]:
        """Return default extraction template when JD analysis fails."""
        return {
            'required_technical_skills': ['Problem Solving', 'Programming', 'System Design'],
            'preferred_skills': ['Communication', 'Teamwork'],
            'seniority_indicators': ['mid-level'],
            'responsibility_categories': ['coding', 'collaboration'],
            'technology_stack': ['General Programming'],
            'soft_skills': ['Communication'],
            'interview_focus_areas': ['coding_problems', 'technical_knowledge'],
            'complexity_level': 'intermediate'
        }
    
    def _calculate_initial_difficulty(self, experience_data: Dict, extracted_skills: Dict) -> str:
        """Calculate appropriate initial difficulty level."""
        user_level = experience_data['experience_level']
        job_complexity = extracted_skills.get('complexity_level', 'intermediate')
        
        # Simple mapping logic
        if user_level == 'senior' and job_complexity == 'advanced':
            return 'advanced'
        elif user_level == 'junior' or job_complexity == 'beginner':
            return 'beginner'
        else:
            return 'intermediate'
    
    def _match_difficulty_to_gap(self, user_seniority: str, job_seniority: str) -> str:
        """Match difficulty based on gap between user and job requirements."""
        seniority_levels = {'junior': 1, 'mid': 2, 'senior': 3}
        
        user_score = seniority_levels.get(user_seniority, 2)
        job_score = seniority_levels.get(job_seniority, 2)
        
        if job_score > user_score:
            return job_seniority  # Challenge user with target level
        else:
            return user_seniority  # Match user's current level
    
    def _calculate_confidence_score(self, experience_data: Dict) -> float:
        """Calculate confidence score based on self-assessment."""
        self_assessment = experience_data.get('self_assessment', {})
        if not self_assessment:
            return 0.5  # Default moderate confidence
        
        avg_score = sum(self_assessment.values()) / len(self_assessment)
        return avg_score / 5.0  # Normalize to 0-1 scale
    
    def _map_focus_to_question_categories(self, focus_areas: List[str]) -> List[str]:
        """Map focus areas to specific question categories."""
        category_mapping = {
            'coding_problems': ['algorithms', 'data_structures', 'problem_solving'],
            'system_design': ['scalability', 'architecture', 'trade_offs'],
            'technical_knowledge': ['concepts', 'best_practices', 'tools'],
            'behavioral_leadership': ['leadership', 'teamwork', 'communication'],
            'general_technical': ['algorithms', 'concepts', 'problem_solving']
        }
        
        categories = []
        for focus in focus_areas:
            categories.extend(category_mapping.get(focus, ['general']))
        
        return list(set(categories))  # Remove duplicates