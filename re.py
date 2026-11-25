"""
✅ SIMPLE Resume Transformer for HSBC Campaign Analytics Apprentice
✅ Copy-paste ready output | Easy to customize | ATS-optimized
✅ Run with: python resume_transformer.py
"""

def generate_hsbc_resume():
    # ========== 📝 FILL IN YOUR DETAILS HERE ==========
    name = "YOUR FULL NAME"
    email = "mail@gmail.com"
    phone = "+91-XXXXXXXXXX"
    linkedin = "linkedin.com/in/yourprofile"
    portfolio = "yourportfolio.com (optional)"
    
    # Education (most recent first)
    education = [
        "B.Tech Computer Engineering | VIT Pune | CGPA: X.XX/10 | 2022–2026",
        "Relevant Coursework: DBMS, Probability & Statistics, Data Structures, ML Basics",
        "PGDAC | [Institute] | XX% | 2021–2022",
    ]
    
    # Technical Skills - PRIORITIZE ANALYTICS TOOLS
    skills = {
        "Data & Analytics": [
            "Python (Pandas, NumPy, Matplotlib)",
            "SQL (MySQL, Oracle)",
            "Tableau, Jupyter Notebook",
            "Excel (PivotTables, VLOOKUP) ✓",
            "Power BI / Looker (Familiar; quick learner)"
        ],
        "Cloud & Query": [
            "Google Cloud Platform", "AWS (EC2)", 
            "BigQuery SQL (Basic)", "Docker"
        ],
        "Programming": [
            "Python", "Java", "JavaScript", "REST APIs"
        ],
        "Methods & Soft Skills": [
            "Agile (Scrum)", "Data Cleaning", "A/B Testing Basics",
            "Stakeholder Communication", "Problem-Solving"
        ]
    }
    
    # Analytics Projects (MOST RELEVANT FIRST)
    analytics_projects = [
        {
            "title": "BCG Data Science Job Simulation",
            "tech": "Python, Pandas, NumPy, Scikit-learn",
            "desc": "Customer churn prediction & retention strategy analysis",
            "bullets": [
                "Analyzed 10K+ customer records to identify churn patterns using Pandas",
                "Performed feature engineering & exploratory data analysis (EDA)",
                "Built classification model achieving 85% accuracy in churn prediction",
                "Translated insights into actionable marketing recommendations"
            ],
            "result": "✅ Delivered data-driven retention strategy with measurable impact"
        },
        {
            "title": "FITLIFE – AI Workout Analytics Dashboard",
            "tech": "Python, Tableau, AWS EC2, PoseNet",
            "desc": "Cloud-based fitness app with posture detection & progress analytics",
            "bullets": [
                "Built analytics dashboard (Tableau/Jupyter) to visualize user workout trends",
                "Applied ML models to classify posture accuracy & track improvement",
                "Identified top 3 exercise patterns correlated with user retention",
                "Deployed on AWS EC2 for scalable data processing"
            ],
            "result": "✅ Enabled personalized insights that improved user engagement metrics"
        },
        {
            "title": "LETSPLAY – Turf Booking Analytics",
            "tech": "MySQL, Python, Spring Boot, Agile",
            "desc": "Full-stack booking platform with data-driven optimization features",
            "bullets": [
                "Designed MySQL schema optimized for querying booking patterns & peak-time analytics",
                "Analyzed historical booking data to recommend dynamic pricing strategies",
                "Built REST APIs for real-time data sync between frontend & analytics backend",
                "Collaborated in Agile sprints to deliver data-backed feature iterations"
            ],
            "result": "✅ Improved field utilization insights by 30% through data modeling"
        }
    ]
    
    # Internship (focus on data aspects)
    internship = {
        "role": "Web Dev Intern",
        "company": "Opsnetic Cloud Consulting",
        "bullets": [
            "Optimized SQL queries for faster data retrieval & reporting",
            "Implemented data validation & error logging for analytics-ready outputs",
            "Containerized services (Docker) for scalable cloud data processing (AWS)"
        ]
    }
    
    # Certifications
    certs = [
        "BCG Data Science Job Simulation – Forage (Completed)",
        "Google Cloud Associate Engineer Track (In Progress)",
        "JP Morgan Software Engineering Simulation – Forage"
    ]
    
    # ========== 🎯 GENERATE RESUME ==========
    resume = f"""{name.upper()}
Campaign Analytics Apprentice | HSBC Applicant
📧 {email} | 📱 {phone} | 🔗 {linkedin} | 💼 {portfolio}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFESSIONAL SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
B.Tech Computer Engineering graduate with hands-on experience in Python, SQL, and data analysis using Pandas, NumPy, and Tableau. Completed analytics projects including customer churn prediction (85% accuracy) and dashboard development. Passionate about transforming campaign data into actionable business insights. Eager to contribute to HSBC's data-driven marketing initiatives through the Apprentice program.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TECHNICAL SKILLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    for category, items in skills.items():
        resume += f"\n{category}:\n• " + " | ".join(items)
    
    resume += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYTICS PROJECTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    for proj in analytics_projects:
        resume += f"""
{proj['title']} | {proj['tech']}
→ {proj['desc']}
"""
        for bullet in proj['bullets']:
            resume += f"• {bullet}\n"
        resume += f"✨ {proj['result']}\n"
    
    resume += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERNSHIP EXPERIENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{internship['role']} | {internship['company']}
"""
    for bullet in internship['bullets']:
        resume += f"• {bullet}\n"
    
    resume += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EDUCATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for edu in education:
        resume += f"• {edu}\n"
    
    resume += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CERTIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for cert in certs:
        resume += f"• {cert}\n"
    
    # ATS Keywords (subtle footer)
    resume += f"""
──────────────────────────────────────────
Keywords: campaign analytics | data preparation | performance reporting | 
Power BI | Looker | SQL | Python | Excel | stakeholder collaboration | 
agile | actionable insights | process automation | data quality
──────────────────────────────────────────
Generated: March 2026 | Target: HSBC Campaign Analytics Apprentice (Job ID: 34891)
✅ Save as PDF before submitting | Keep to 1 page
"""
    
    return resume


# ========== 🚀 RUN ==========
if __name__ == "__main__":
    print(generate_hsbc_resume())
    
    # Optional: Save to file
    # with open("HSBC_Resume_Targeted.txt", "w", encoding="utf-8") as f:
    #     f.write(generate_hsbc_resume())
    # print("\n✅ Saved to 'HSBC_Resume_Targeted.txt'")