from fpdf import FPDF

class ResumePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'CAMPAIGN ANALYTICS RESUME', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, 'HSBC Apprentice Application', 0, 1, 'C')
        self.ln(5)
    
    def section_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(108, 92, 231)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.ln(3)
    
    def section_content(self, content):
        self.set_font('Arial', '', 11)
        for line in content.split('\n'):
            self.cell(0, 6, line, 0, 1)
        self.ln(2)

# Create PDF
pdf = ResumePDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Personal Info
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'YOUR NAME', 0, 1, 'C')
pdf.set_font('Arial', '', 10)
pdf.cell(0, 5, 'Email: mail@gmail.com | Phone: +91-XXXXXXXXXX', 0, 1, 'C')
pdf.cell(0, 5, 'LinkedIn: linkedin.com/in/yourprofile', 0, 1, 'C')
pdf.ln(5)

# Education
pdf.section_title('EDUCATION')
pdf.section_content('B.Tech Computer Engineering | VIT Pune | CGPA: X.XX | 2026\nRelevant Coursework: DBMS, Statistics, Data Structures')

# Skills
pdf.section_title('TECHNICAL SKILLS')
pdf.section_content('Data & Analytics: Python (Pandas, NumPy, Matplotlib), SQL, Tableau, Excel, Power BI\nCloud: AWS, Google Cloud, Docker\nMethods: Agile, Data Cleaning, A/B Testing')

# Projects
pdf.section_title('ANALYTICS PROJECTS')
pdf.section_content('BCG Data Science Simulation | Python, Pandas\n- Analyzed 10K+ customer records for churn prediction\n- Built model achieving 85% accuracy\n- Delivered actionable retention recommendations\n\nFITLIFE Analytics Dashboard | Python, Tableau, AWS\n- Built workout analytics dashboard\n- Identified user engagement patterns\n- Deployed on AWS EC2')

# Internship
pdf.section_title('INTERNSHIP')
pdf.section_content('Web Dev Intern | Opsnetic Cloud Consulting\n- Optimized SQL queries for faster data retrieval\n- Implemented Docker containers for scalability\n- Collaborated in Agile environment')

# Save
pdf.output('HSBC_Resume.pdf')
print("✅ Resume saved as 'HSBC_Resume.pdf'")