from typing import Dict, List, Any, TypedDict, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolExecutor

from utils.config import settings
import json
import re
from datetime import datetime
import PyPDF2
import io
# import networkx as nx

# State definition for the resume scoring workflow
class ResumeState(TypedDict):
    resume_text: str
    job_description: str
    scoring_criteria: Dict[str, Any]
    extracted_info: Dict[str, Any]
    technical_score: float
    experience_score: float
    cultural_fit_score: float
    additional_score: float
    total_score: float
    detailed_feedback: Dict[str, Any]
    recommendations: List[str]
    pass_fail_status: str
    messages: List[Any]

class ResumeScorer:
    def __init__(self, model_name: str = "gpt-4"):
        self.llm = ChatOllama(
            model=model_name,
            base_url=settings.llm_url_ollama # Default Ollama endpoint
        )
        self.workflow = self._create_workflow()
        print(self.workflow.get_graph().draw_mermaid())

    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for resume scoring"""
        workflow = StateGraph(ResumeState)
        
        # Add nodes
        workflow.add_node("extract_resume_info", self.extract_resume_info)
        workflow.add_node("analyze_technical_qualifications", self.analyze_technical_qualifications)
        workflow.add_node("evaluate_experience", self.evaluate_experience)
        workflow.add_node("assess_cultural_fit", self.assess_cultural_fit)
        workflow.add_node("calculate_additional_factors", self.calculate_additional_factors)
        workflow.add_node("compute_final_score", self.compute_final_score)
        workflow.add_node("generate_feedback", self.generate_feedback)
        
        # Define the flow
        workflow.set_entry_point("extract_resume_info")
        workflow.add_edge("extract_resume_info", "analyze_technical_qualifications")
        workflow.add_edge("analyze_technical_qualifications", "evaluate_experience")
        workflow.add_edge("evaluate_experience", "assess_cultural_fit")
        workflow.add_edge("assess_cultural_fit", "calculate_additional_factors")
        workflow.add_edge("calculate_additional_factors", "compute_final_score")
        workflow.add_edge("compute_final_score", "generate_feedback")
        workflow.add_edge("generate_feedback", END)
        
        return workflow.compile()
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    def extract_resume_info(self, state: ResumeState) -> ResumeState:
        """Extract structured information from resume text"""
        system_prompt = """
        You are an expert resume parser. Extract structured information from the resume text.
        Focus on:
        1. Personal information (name, contact details)
        2. Education (degrees, institutions, graduation years)
        3. Work experience (companies, roles, dates, responsibilities)
        4. Technical skills
        5. Certifications
        6. Projects
        7. Achievements/awards
        
        Return the information in a structured JSON format.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Resume Text:\n{state['resume_text']}")
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                extracted_info = json.loads(json_match.group())
            else:
                extracted_info = {"error": "Could not parse resume structure"}
        except:
            extracted_info = {"error": "JSON parsing failed"}
        
        state["extracted_info"] = extracted_info
        state["messages"].append({"node": "extract_resume_info", "output": extracted_info})
        return state
    
    def analyze_technical_qualifications(self, state: ResumeState) -> ResumeState:
        """Analyze technical qualifications and assign score"""
        criteria = state["scoring_criteria"].get("technical", {})
        max_score = criteria.get("max_points", 35)
        required_skills = criteria.get("required_skills", [])
        preferred_skills = criteria.get("preferred_skills", [])
        min_experience = criteria.get("min_years_experience", 0)
        
        system_prompt = f"""
        Analyze the technical qualifications based on:
        
        Required Skills: {required_skills}
        Preferred Skills: {preferred_skills}
        Minimum Experience: {min_experience} years
        Job Description: {state['job_description']}
        
        Score out of {max_score} points based on:
        - Presence of required skills (60% of score)
        - Presence of preferred skills (25% of score)
        - Years of relevant experience (15% of score)
        
        Provide detailed reasoning for the score.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Resume Info:\n{json.dumps(state['extracted_info'], indent=2)}")
        ]
        
        response = self.llm.invoke(messages)
        
        # Extract score from response (simplified - in production, use more robust parsing)
        score_match = re.search(r'Score:\s*(\d+\.?\d*)', response.content)
        technical_score = float(score_match.group(1)) if score_match else 0
        
        state["technical_score"] = min(technical_score, max_score)
        state["messages"].append({"node": "technical_analysis", "score": technical_score, "reasoning": response.content})
        return state
    
    def evaluate_experience(self, state: ResumeState) -> ResumeState:
        """Evaluate work experience relevance"""
        criteria = state["scoring_criteria"].get("experience", {})
        max_score = criteria.get("max_points", 30)
        
        system_prompt = f"""
        Evaluate work experience relevance out of {max_score} points based on:
        - Direct industry experience (40%)
        - Similar role experience (35%)
        - Career progression (15%)
        - Achievement track record (10%)
        
        Job Description: {state['job_description']}
        
        Consider factors like:
        - Relevance of previous roles
        - Progression in responsibilities
        - Quantifiable achievements
        - Industry alignment
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Resume Info:\n{json.dumps(state['extracted_info'], indent=2)}")
        ]
        
        response = self.llm.invoke(messages)
        
        score_match = re.search(r'Score:\s*(\d+\.?\d*)', response.content)
        experience_score = float(score_match.group(1)) if score_match else 0
        
        state["experience_score"] = min(experience_score, max_score)
        state["messages"].append({"node": "experience_evaluation", "score": experience_score, "reasoning": response.content})
        return state
    
    def assess_cultural_fit(self, state: ResumeState) -> ResumeState:
        """Assess cultural fit indicators"""
        criteria = state["scoring_criteria"].get("cultural_fit", {})
        max_score = criteria.get("max_points", 20)
        company_values = criteria.get("company_values", [])
        
        system_prompt = f"""
        Assess cultural fit out of {max_score} points based on:
        - Company values alignment (40%)
        - Communication skills evident in resume (25%)
        - Leadership examples (20%)
        - Teamwork indicators (15%)
        
        Company Values: {company_values}
        Job Description: {state['job_description']}
        
        Look for evidence of:
        - Clear, professional communication
        - Leadership roles or initiatives
        - Collaborative projects
        - Values alignment through activities/roles
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Resume Info:\n{json.dumps(state['extracted_info'], indent=2)}")
        ]
        
        response = self.llm.invoke(messages)
        
        score_match = re.search(r'Score:\s*(\d+\.?\d*)', response.content)
        cultural_score = float(score_match.group(1)) if score_match else 0
        
        state["cultural_fit_score"] = min(cultural_score, max_score)
        state["messages"].append({"node": "cultural_fit_assessment", "score": cultural_score, "reasoning": response.content})
        return state
    
    def calculate_additional_factors(self, state: ResumeState) -> ResumeState:
        """Calculate additional factors score"""
        criteria = state["scoring_criteria"].get("additional", {})
        max_score = criteria.get("max_points", 15)
        
        system_prompt = f"""
        Evaluate additional factors out of {max_score} points:
        - Extra certifications (30%)
        - Volunteer work/side projects (25%)
        - Professional development (25%)
        - Publications/speaking (20%)
        
        Look for indicators of:
        - Continuous learning
        - Community involvement
        - Thought leadership
        - Innovation and initiative
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Resume Info:\n{json.dumps(state['extracted_info'], indent=2)}")
        ]
        
        response = self.llm.invoke(messages)
        
        score_match = re.search(r'Score:\s*(\d+\.?\d*)', response.content)
        additional_score = float(score_match.group(1)) if score_match else 0
        
        state["additional_score"] = min(additional_score, max_score)
        state["messages"].append({"node": "additional_factors", "score": additional_score, "reasoning": response.content})
        return state
    
    def compute_final_score(self, state: ResumeState) -> ResumeState:
        """Compute final score and pass/fail status"""
        total_score = (
            state["technical_score"] + 
            state["experience_score"] + 
            state["cultural_fit_score"] + 
            state["additional_score"]
        )
        
        # Determine pass/fail status
        pass_threshold = state["scoring_criteria"].get("pass_threshold", 70)
        pass_fail_status = "PASS" if total_score >= pass_threshold else "FAIL"
        
        state["total_score"] = total_score
        state["pass_fail_status"] = pass_fail_status
        
        return state
    
    def generate_feedback(self, state: ResumeState) -> ResumeState:
        """Generate detailed feedback and recommendations"""
        system_prompt = f"""
        Generate comprehensive feedback based on the resume scoring results:
        
        Total Score: {state['total_score']}/100
        Technical: {state['technical_score']}
        Experience: {state['experience_score']}
        Cultural Fit: {state['cultural_fit_score']}
        Additional: {state['additional_score']}
        Status: {state['pass_fail_status']}
        
        Provide:
        1. Overall assessment summary
        2. Strengths identified
        3. Areas for improvement
        4. Specific recommendations
        5. Interview focus areas (if pass)
        6. Development suggestions
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Resume Analysis Context:\n{json.dumps(state['messages'], indent=2)}")
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse feedback into structured format
        feedback_sections = {
            "overall_assessment": "",
            "strengths": [],
            "areas_for_improvement": [],
            "recommendations": [],
            "interview_focus": [],
            "development_suggestions": []
        }
        
        # Simple parsing (in production, use more sophisticated NLP)
        sections = response.content.split('\n\n')
        for section in sections:
            if 'strengths' in section.lower():
                feedback_sections["strengths"] = [line.strip('- ') for line in section.split('\n')[1:] if line.strip()]
            elif 'improvement' in section.lower():
                feedback_sections["areas_for_improvement"] = [line.strip('- ') for line in section.split('\n')[1:] if line.strip()]
            elif 'recommendation' in section.lower():
                feedback_sections["recommendations"] = [line.strip('- ') for line in section.split('\n')[1:] if line.strip()]
        
        state["detailed_feedback"] = feedback_sections
        state["recommendations"] = feedback_sections["recommendations"]
        
        return state
    
    def score_resume(self, resume_text: str, job_description: str, scoring_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to score a resume"""
        initial_state = {
            "resume_text": resume_text,
            "job_description": job_description,
            "scoring_criteria": scoring_criteria,
            "extracted_info": {},
            "technical_score": 0.0,
            "experience_score": 0.0,
            "cultural_fit_score": 0.0,
            "additional_score": 0.0,
            "total_score": 0.0,
            "detailed_feedback": {},
            "recommendations": [],
            "pass_fail_status": "",
            "messages": []
        }
        
        for i in self.workflow.stream(initial_state,mode = "updates"):
            yield i

# Example usage and configuration
def create_default_scoring_criteria():
    """Create default scoring criteria"""
    return {
        "technical": {
            "max_points": 35,
            "required_skills": ["Python", "SQL", "Data Analysis"],
            "preferred_skills": ["Machine Learning", "AWS", "Docker"],
            "min_years_experience": 3
        },
        "experience": {
            "max_points": 30,
            "target_industry": "Technology",
            "target_role_level": "Senior"
        },
        "cultural_fit": {
            "max_points": 20,
            "company_values": ["Innovation", "Collaboration", "Integrity"]
        },
        "additional": {
            "max_points": 15
        },
        "pass_threshold": 70
    }

# Example usage
