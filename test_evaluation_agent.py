from agents.evaluation import ResumeScorer, create_default_scoring_criteria
if __name__ == "__main__":
    # Initialize the scorer
    scorer = ResumeScorer(model_name="gemma3:1b")
    
    # Example resume text (in practice, extract from PDF)
    sample_resume = """
    John Doe
    Senior Data Scientist
    john.doe@email.com | (555) 123-4567
    
    EXPERIENCE:
    Senior Data Scientist at Tech Corp (2021-2024)
    - Led machine learning projects using Python and SQL
    - Implemented AWS-based data pipelines
    - Mentored junior data scientists
    
    Data Analyst at StartupXYZ (2019-2021)
    - Performed statistical analysis using Python and R
    - Created dashboards and reports
    
    EDUCATION:
    MS in Data Science, University ABC (2019)
    BS in Computer Science, University XYZ (2017)
    
    SKILLS:
    Python, SQL, Machine Learning, AWS, Docker, Tableau
    
    CERTIFICATIONS:
    AWS Certified Solutions Architect
    """
    
    job_description = """
    We're seeking a Senior Data Scientist to join our AI team. 
    Requirements: 3+ years experience, Python, SQL, Machine Learning.
    Preferred: AWS, Docker, team leadership experience.
    """
    
    # Score the resume
    scoring_criteria = create_default_scoring_criteria()
    for result in scorer.score_resume(sample_resume, job_description, scoring_criteria):
        print(f"Criteria: {result}")
    # result = scorer.score_resume(sample_resume, job_description, scoring_criteria)
    result = result["generate_feedback"]
    # Display results
    print(f"Final Score: {result['total_score']}/100")
    print(f"Status: {result['pass_fail_status']}")
    print(f"\nBreakdown:")
    print(f"Technical: {result['technical_score']}")
    print(f"Experience: {result['experience_score']}")
    print(f"Cultural Fit: {result['cultural_fit_score']}")
    print(f"Additional: {result['additional_score']}")