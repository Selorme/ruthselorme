from models import Base, SkillsReference, Job
from app import app, db
from sqlalchemy import func


def create_skills_database():
    """Create and populate the skill reference database"""

    skills_data = [
        # Technical Skills
        ('Python', 'Technical', 'Programming language widely used for web development, data science, and automation'),
        ('JavaScript', 'Technical', 'Programming language for web development and interactive websites'),
        ('Java', 'Technical', 'Object-oriented programming language used for enterprise applications'),
        ('C++', 'Technical', 'High-performance programming language for system programming'),
        ('C#', 'Technical', 'Microsoft programming language for .NET applications'),
        ('PHP', 'Technical', 'Server-side scripting language for web development'),
        ('Ruby', 'Technical', 'Dynamic programming language focused on simplicity'),
        ('Go', 'Technical', 'Google programming language for scalable applications'),
        ('Swift', 'Technical', 'Apple programming language for iOS development'),
        ('Kotlin', 'Technical', 'Modern programming language for Android development'),
        ('TypeScript', 'Technical', 'Typed superset of JavaScript'),
        ('R', 'Technical', 'Programming language for statistical computing'),
        ('MATLAB', 'Technical', 'Programming platform for mathematical computing'),
        ('Scala', 'Technical', 'Functional programming language for big data'),
        ('CRM Software', 'Technical', 'Customer relationship management software'),
        ('Google Analytics', 'Technical', 'Web analytics service by Google'),
        ('User Research', 'Technical', 'Research methods for understanding user needs'),
        ('Prototyping', 'Technical', 'Creating preliminary models of products'),
        ('InVision', 'Technical', 'Digital product design platform'),
        ('User Testing', 'Technical', 'Testing products with real users'),
        ('Analytics', 'Technical', 'Analysis of data to gain insights'),
        ('Computer Skills', 'Technical', 'Basic computer operation and software use'),
        ('Technical Support', 'Technical', 'Providing technical assistance to users'),
        ('Computer Hardware', 'Technical', 'Knowledge of computer components'),
        ('Documentation', 'Technical', 'Creating and maintaining documentation'),

        # Web Development
        ('HTML', 'Technical', 'Markup language for creating web pages'),
        ('CSS', 'Technical', 'Style sheet language for designing web pages'),
        ('React', 'Technical', 'JavaScript library for building user interfaces'),
        ('Angular', 'Technical', 'TypeScript framework for web applications'),
        ('Vue.js', 'Technical', 'Progressive JavaScript framework'),
        ('Node.js', 'Technical', 'JavaScript runtime for server-side development'),
        ('Express.js', 'Technical', 'Web framework for Node.js'),
        ('Django', 'Technical', 'Python web framework'),
        ('Flask', 'Technical', 'Lightweight Python web framework'),
        ('Bootstrap', 'Technical', 'CSS framework for responsive design'),
        ('jQuery', 'Technical', 'JavaScript library for DOM manipulation'),
        ('SASS', 'Technical', 'CSS preprocessor'),
        ('WordPress', 'Technical', 'Content management system'),
        ('Drupal', 'Technical', 'Content management framework'),

        # Database & Data
        ('SQL', 'Technical', 'Database query language for managing and analyzing data'),
        ('PostgresSQL', 'Technical', 'Advanced open-source relational database'),
        ('MySQL', 'Technical', 'Popular open-source relational database'),
        ('MongoDB', 'Technical', 'NoSQL document database'),
        ('Redis', 'Technical', 'In-memory data structure store'),
        ('Elasticsearch', 'Technical', 'Search and analytics engine'),
        ('Data Analysis', 'Technical', 'Examining datasets to draw conclusions and insights'),
        ('Data Visualization', 'Technical', 'Creating visual representations of data'),
        ('Excel', 'Technical', 'Spreadsheet application for data analysis'),
        ('Tableau', 'Technical', 'Data visualization software'),
        ('Power BI', 'Technical', 'Business analytics tool'),
        ('Apache Spark', 'Technical', 'Big data processing framework'),
        ('Hadoop', 'Technical', 'Big data storage and processing'),

        # Cloud & DevOps
        ('AWS', 'Technical', 'Amazon Web Services cloud platform'),
        ('Azure', 'Technical', 'Microsoft cloud computing platform'),
        ('Google Cloud', 'Technical', 'Google cloud computing services'),
        ('Docker', 'Technical', 'Containerization platform'),
        ('Kubernetes', 'Technical', 'Container orchestration system'),
        ('Jenkins', 'Technical', 'Continuous integration tool'),
        ('Git', 'Technical', 'Version control system'),
        ('Linux', 'Technical', 'Open-source operating system'),
        ('Unix', 'Technical', 'Multi-user operating system'),
        ('Terraform', 'Technical', 'Infrastructure as code tool'),
        ('Ansible', 'Technical', 'Automation platform'),
        ('CI/CD', 'Technical', 'Continuous integration and deployment'),

        # Mobile Development
        ('iOS Development', 'Technical', 'Creating applications for Apple devices'),
        ('Android Development', 'Technical', 'Creating applications for Android devices'),
        ('React Native', 'Technical', 'Cross-platform mobile development framework'),
        ('Flutter', 'Technical', 'UI toolkit for cross-platform development'),
        ('Xamarin', 'Technical', 'Microsoft cross-platform development tool'),

        # AI/ML
        ('Machine Learning', 'Technical', 'Algorithms that learn from data'),
        ('Deep Learning', 'Technical', 'Neural network-based machine learning'),
        ('TensorFlow', 'Technical', 'Machine learning framework'),
        ('PyTorch', 'Technical', 'Deep learning framework'),
        ('Natural Language Processing', 'Technical', 'AI for understanding human language'),
        ('Computer Vision', 'Technical', 'AI for interpreting visual information'),
        ('Statistical Analysis', 'Technical', 'Mathematical analysis of data patterns'),

        # Business & Management Skills
        ('Agile', 'Business', 'Agile project management methodology'),
        ('Team Leadership', 'Business', 'Ability to guide and motivate teams'),
        ('Project Management', 'Business', 'Planning, executing, and closing projects effectively'),
        ('Strategic Planning', 'Business', 'Long-term organizational planning'),
        ('Change Management', 'Business', 'Managing organizational transitions'),
        ('Performance Management', 'Business', 'Monitoring and improving employee performance'),
        ('Mentoring', 'Business', 'Guiding and developing others'),
        ('Coaching', 'Business', 'Helping others achieve their potential'),
        ('Operations Management', 'Business', 'Managing daily business operations'),
        ('Budget Management', 'Business', 'Planning and controlling budgets'),
        ('Process Improvement', 'Business', 'Identifying and implementing process enhancements'),
        ('Cash Handling', 'Business', 'Processing and managing cash transactions'),

        # Communication
        ('Patience', 'Soft Skills', 'Ability to remain calm and composed'),
        ('Grammar', 'Soft Skills', 'Knowledge of language rules and structure'),
        ('Creativity', 'Soft Skills', 'Ability to generate original ideas'),
        ('Cold Calling', 'Soft Skills', 'Making unsolicited sales calls to prospects'),
        ('Public Speaking', 'Soft Skills', 'Presenting information to audiences'),
        ('Technical Writing', 'Soft Skills', 'Creating clear technical documentation'),
        ('Content Writing', 'Soft Skills', 'Creating engaging written content'),
        ('Copywriting', 'Creative', 'Writing persuasive marketing content'),
        ('Presentation Skills', 'Soft Skills', 'Effectively presenting information'),
        ('Negotiation', 'Soft Skills', 'Reaching mutually beneficial agreements'),
        ('Client Relations', 'Soft Skills', 'Managing relationships with clients'),
        ('Communication', 'Soft Skills', 'Ability to convey information clearly and effectively'),

        # Marketing & Sales
        ('Digital Marketing', 'Business', 'Online marketing strategies and tactics'),
        ('Social Media Marketing', 'Business', 'Marketing through social media platforms'),
        ('SEO', 'Business', 'Search engine optimization'),
        ('SEM', 'Business', 'Search engine marketing'),
        ('Email Marketing', 'Business', 'Marketing through email campaigns'),
        ('Content Marketing', 'Business', 'Marketing through valuable content'),
        ('Sales', 'Business', 'Selling products or services to customers'),
        ('Lead Generation', 'Business', 'Identifying potential customers'),
        ('Market Research', 'Business', 'Analyzing market conditions and trends'),

        # Finance & Accounting
        ('Financial Analysis', 'Business', 'Analyzing financial data and performance'),
        ('Budgeting', 'Business', 'Planning and managing financial resources'),
        ('Forecasting', 'Business', 'Predicting future financial trends'),
        ('Accounting', 'Business', 'Recording and analyzing financial transactions'),
        ('Bookkeeping', 'Business', 'Maintaining financial records'),
        ('Tax Preparation', 'Business', 'Preparing tax returns and compliance'),
        ('Risk Management', 'Business', 'Identifying and managing potential risks'),
        ('Investment Analysis', 'Business', 'Evaluating investment opportunities'),

        # Creative Skills
        ('Adobe Premier', 'Creative', 'Video editing software by Adobe'),
        ('Content Creation', 'Creative', 'Creating various types of content'),
        ('Graphic Design', 'Creative', 'Visual communication through typography, imagery, and layout'),
        ('UI/UX Design', 'Creative', 'Designing user interfaces and experiences'),
        ('Web Design', 'Creative', 'Designing websites and web applications'),
        ('Adobe Photoshop', 'Creative', 'Image editing and graphic design software'),
        ('Adobe Illustrator', 'Creative', 'Vector graphics design software'),
        ('Figma', 'Creative', 'Collaborative design tool'),
        ('Sketch', 'Creative', 'Digital design tool for Mac'),
        ('InDesign', 'Creative', 'Desktop publishing software'),
        ('Video Editing', 'Creative', 'Editing and producing video content'),
        ('Photography', 'Creative', 'Capturing and editing photographs'),
        ('Videography', 'Creative', 'Creating video content'),
        ('Animation', 'Creative', 'Creating animated content'),
        ('3D Modeling', 'Creative', 'Creating three-dimensional digital models'),
        ('Creative Writing', 'Creative', 'Writing original creative content'),
        ('Storytelling', 'Creative', 'Crafting compelling narratives'),
        ('Brand Development', 'Creative', 'Creating and developing brand identity'),

        # Soft Skills
        ('Collaboration', 'Soft Skills', 'Working effectively with others'),
        ('Teamwork', 'Soft Skills', 'Contributing to team success'),
        ('Conflict Resolution', 'Soft Skills', 'Resolving disagreements constructively'),
        ('Empathy', 'Soft Skills', 'Understanding and sharing others feelings'),
        ('Cultural Sensitivity', 'Soft Skills', 'Awareness of cultural differences'),
        ('Customer Service', 'Soft Skills', 'Providing support and assistance to customers'),
        ('Networking', 'Soft Skills', 'Building professional relationships'),
        ('Problem Solving', 'Soft Skills', 'Finding solutions to challenges'),
        ('Critical Thinking', 'Soft Skills', 'Analyzing information objectively'),
        ('Adaptability', 'Soft Skills', 'Adjusting to changing circumstances'),
        ('Time Management', 'Soft Skills', 'Managing time effectively'),
        ('Organization', 'Soft Skills', 'Keeping things structured and orderly'),
        ('Attention to Detail', 'Soft Skills', 'Focusing on accuracy and precision'),
        ('Multitasking', 'Soft Skills', 'Managing multiple tasks simultaneously'),
        ('Self-Motivation', 'Soft Skills', 'Driving oneself to achieve goals'),

        # Industry-Specific
        ('Classroom Management', 'Education', 'Managing classroom environment and behavior'),
        ('Training Development', 'Education', 'Creating training programs and materials'),
        ('Instructional Design', 'Education', 'Designing educational experiences'),
        ('Basic Math', 'Academic', 'Fundamental mathematical skills'),
        ('Teaching', 'Education', 'Instructing and educating students'),
        ('Patient Care', 'Healthcare', 'Providing care and support to patients'),
        ('Medical Terminology', 'Healthcare', 'Knowledge of medical language and terms'),
        ('Exercise Physiology', 'Healthcare', 'Study of body responses to exercise'),
        ('Manual Therapy', 'Healthcare', 'Hands-on treatment techniques'),
        ('Healthcare Knowledge', 'Industry', 'Understanding of healthcare systems and practices'),
        ('Legal Research', 'Industry', 'Researching legal precedents and regulations'),
        ('Manufacturing Processes', 'Industry', 'Understanding of production and manufacturing'),
        ('Supply Chain Management', 'Industry', 'Managing the flow of goods and services'),
        ('Quality Assurance', 'Industry', 'Ensuring products meet quality standards'),
        ('Compliance', 'Industry', 'Ensuring adherence to regulations and standards'),
        ('Research Methods', 'Industry', 'Systematic investigation techniques'),
    ]

    try:
        print("Creating skills reference database...")

        for skill_name, category, description in skills_data:
            # Check if skill already exists
            existing_skill = db.session.query(SkillsReference).filter(
                SkillsReference.skill_name == skill_name
            ).first()

            if not existing_skill:
                new_skill = SkillsReference(
                    skill_name=skill_name,
                    category=category,
                    description=description
                )
                db.session.add(new_skill)

        db.session.commit()
        print(f"Successfully added {len(skills_data)} skills to the database!")

        # Print summary by category
        categories = db.session.query(SkillsReference.category, db.func.count(SkillsReference.id)).group_by(
            SkillsReference.category).all()
        print("\nSkills by category:")
        for category, count in categories:
            print(f"  {category}: {count} skills")

    except Exception as e:
        db.session.rollback()
        print(f"Error creating skills database: {e}")


def create_jobs_database():
    """Create and populate the job database"""

    jobs_data = [
        # Technology Jobs
        {
            'job_name': 'Junior Software Developer',
            'description': 'Develop and maintain web applications using modern technologies. Work with cross-functional teams to deliver high-quality software solutions.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Python': 6, 'JavaScript': 5, 'SQL': 4, 'Git': 5, 'Problem Solving': 7, 'React': 4, 'Docker': 3, 'AWS': 3},
            'industry': 'Technology'
        },
        {
            'job_name': 'Senior Software Engineer',
            'description': 'Lead development of complex software systems. Mentor junior developers and make architectural decisions.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Python': 8, 'JavaScript': 7, 'SQL': 7, 'Team Leadership': 7, 'System Design': 8, 'AWS': 6, 'Docker': 6, 'Kubernetes': 5},
            'industry': 'Technology'
        },
        {
            'job_name': 'Data Scientist',
            'description': 'Analyze large datasets to extract insights and build predictive models. Collaborate with business teams to solve complex problems.',
            'minimum_degree_required': 'Master\'s',
            'required_skills': {'Python': 8, 'Machine Learning': 7, 'Statistical Analysis': 8, 'SQL': 7,
                                'Data Visualization': 6,'R': 5, 'TensorFlow': 6, 'Tableau': 5},
            'industry': 'Technology'
        },
        {
            'job_name': 'Frontend Developer',
            'description': 'Create responsive and interactive user interfaces. Work closely with designers and backend developers.',
            'minimum_degree_required': 'Associate',
            'required_skills': {'JavaScript': 8, 'HTML': 8, 'CSS': 8, 'React': 7, 'UI/UX Design': 6, 'TypeScript': 5, 'SASS': 4, 'Figma': 4},
            'industry': 'Technology'
        },
        {
            'job_name': 'DevOps Engineer',
            'description': 'Manage cloud infrastructure and deployment pipelines. Ensure system reliability and scalability.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Linux': 8, 'Docker': 7, 'AWS': 7, 'CI/CD': 7, 'Python': 6, 'Kubernetes': 6, 'Terraform': 5, 'Ansible': 5},
            'industry': 'Technology'
        },
        {
            'job_name': 'Mobile App Developer',
            'description': 'Develop native mobile applications for iOS and Android platforms',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Swift': 8, 'iOS Development': 8, 'Mobile Development': 8, 'Problem Solving': 7, 'Git': 6},
            'industry': 'Technology'
        },

        # Business & Management Jobs
        {
            'job_name': 'Project Manager',
            'description': 'Lead cross-functional teams to deliver projects on time and within budget. Manage stakeholder expectations and project scope.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Project Management': 9, 'Team Leadership': 8, 'Communication': 8, 'Time Management': 8,
                                'Excel': 6, 'Agile': 6, 'Risk Management': 5, 'Budgeting': 5},
            'industry': 'Consulting'
        },
        {
            'job_name': 'Marketing Manager',
            'description': 'Develop and execute marketing strategies across digital channels. Analyze campaign performance and optimize for ROI.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Digital Marketing': 8, 'Social Media Marketing': 7, 'Content Marketing': 7, 'SEO': 6,
                                'Team Leadership': 7, 'Google Analytics': 6, 'Email Marketing': 5, 'Copywriting': 5},
            'industry': 'Marketing'
        },
        {
            'job_name': 'Sales Representative',
            'description': 'Generate leads and close deals with new and existing clients. Build strong customer relationships and exceed sales targets.',
            'minimum_degree_required': 'High School',
            'required_skills': {'Sales': 8, 'Communication': 9, 'Negotiation': 8, 'Customer Service': 8,
                                'Lead Generation': 6, 'CRM Software': 4, 'Cold Calling': 5, 'Presentation Skills': 6},
            'industry': 'Sales'
        },
        {
            'job_name': 'Business Analyst',
            'description': 'Analyze business processes and systems to identify improvement opportunities. Create detailed reports and recommendations.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Data Analysis': 8, 'Excel': 8, 'SQL': 6, 'Critical Thinking': 8, 'Communication': 7, 'Power BI': 5, 'Process Improvement': 5, 'Documentation': 6},
            'industry': 'Consulting'
        },
        {
            'job_name': 'Human Resources Specialist',
            'description': 'Recruit talent, manage employee relations, ensure compliance with regulations',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'HR Management': 8, 'Communication': 8, 'Conflict Resolution': 7, 'Employment Law': 6, 'Interviewing': 7},
            'industry': 'All industries'
        },

        # Creative Jobs
        {
            'job_name': 'Graphic Designer',
            'description': 'Create visual designs for print and digital media. Collaborate with marketing team on brand campaigns.',
            'minimum_degree_required': 'Associate',
            'required_skills': {'Adobe Photoshop': 9, 'Adobe Illustrator': 8, 'Graphic Design': 9,
                                'Creative Thinking': 8, 'Brand Development': 6, 'InDesign': 6, 'Web Design': 5, 'Typography': 6},
            'industry': 'Creative'
        },
        {
            'job_name': 'UX Designer',
            'description': 'Design user experiences for web and mobile applications. Conduct user research and create wireframes and prototypes.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'UI/UX Design': 9, 'Figma': 8, 'User Research': 7, 'Prototyping': 7,
                                'Adobe Photoshop': 6, 'Sketch': 6, 'InVision': 5, 'User Testing': 6},
            'industry': 'Technology'
        },
        {
            'job_name': 'Content Writer',
            'description': 'Create engaging content for websites, blogs, and marketing materials. Research topics and optimize content for SEO.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Content Writing': 9, 'SEO': 7, 'Research Methods': 7, 'Creative Writing': 8,
                                'Grammar': 9, 'WordPress': 5, 'Social Media': 5, 'Copywriting': 6},
            'industry': 'Marketing'
        },
        {
            'job_name': 'Video Editor',
            'description': 'Edit video content, add effects and transitions, ensure high production quality',
            'minimum_degree_required': 'Associate',
            'required_skills': {'Video Editing': 9, 'Adobe Premier': 8, 'Storytelling': 7, 'Creativity': 8, 'Attention to Detail': 8 },
            'industry': 'Media'
        },
        {
            'job_name': 'Social Media Manager',
            'description': 'Manage company social media presence across platforms. Create content calendar and engage with followers.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Social Media Marketing': 9, 'Content Creation': 8, 'Communication': 7, 'Creativity': 7,
                                'Analytics': 6, 'Adobe Photoshop': 5, 'Video Editing': 5, 'Copywriting': 6},
            'industry': 'Marketing'
        },
        # Healthcare jobs
        {
            'job_name': 'Registered Nurse',
            'description': 'Provide patient care, administer medications, monitor patient progress',
            'minimum_degree_required': 'Associate',
            'required_skills': {'Healthcare Knowledge': 9, 'Patient Care': 9, 'Medical Terminology': 8, 'Empathy': 8, 'Attention to Detail': 8},
            'industry': 'Healthcare'
        },
        {
            'job_name': 'Medical Assistant',
            'description': 'Support physicians, take vital signs, schedule appointments, maintain records',
            'minimum_degree_required': 'Certificate',
            'required_skills': {'Healthcare Knowledge': 7, 'Patient Care': 8, 'Medical Terminology': 7, 'Organization': 7, 'Computer Skills': 5},
            'industry': 'Healthcare'
        },
        {
            'job_name': 'Physical Therapist',
            'description': 'Help patients recover from injuries, develop treatment plans, monitor progress',
            'minimum_degree_required': 'Doctorate',
            'required_skills': {'Healthcare Knowledge': 9, 'Patient Care': 8, 'Exercise Physiology': 8, 'Communication': 8, 'Manual Therapy': 8},
            'industry': 'Healthcare'
        },
        #Customer Service jobs
        {
            'job_name': 'Customer Service Representative',
            'description': 'Provide excellent customer support via phone, email, and chat. Resolve customer issues and maintain satisfaction.',
            'minimum_degree_required': 'High School',
            'required_skills': {'Customer Service': 9, 'Communication': 8, 'Problem Solving': 8, 'Patience': 8,
                                'Computer Skills': 6, 'Multitasking': 6, 'CRM Software': 4, 'Conflict Resolution': 6},
            'industry': 'Service'
        },
        {
            'job_name': 'Technical Support Specialist',
            'description': 'Diagnose technical issues, provide solutions, guide users through troubleshooting',
            'minimum_degree_required': 'Associate',
            'required_skills': {'Technical Support': 8, 'Problem Solving': 9, 'Communication': 8, 'Patience': 8, 'Computer Hardware': 7},
            'industry': 'Service'
        },
        #Finance jobs
        {
            'job_name': 'Financial Analyst',
            'description': 'Analyze financial data and create reports for management. Support budgeting and forecasting processes.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Financial Analysis': 9, 'Excel': 8, 'Accounting': 7, 'Critical Thinking': 8,
                                'Attention to Detail': 8, 'SQL': 5, 'Power BI': 4, 'Investment Analysis': 5},
            'industry': 'Finance'
        },
        {
            'job_name': 'Accountant',
            'description': 'Prepare financial statements, manage accounts, ensure compliance with regulations.',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Accounting': 9, 'Tax Preparation': 8, 'Excel': 8, 'Attention to Detail':9, 'Financial Analysis': 7},
            'industry': 'Finance'
        },
        {
            'job_name': 'Bank Teller',
            'description': 'Process transactions, assist customers, maintain accurate records',
            'minimum_degree_required': 'High School',
            'required_skills': {'Customer Service': 8, 'Cash Handling': 8, 'Attention to Detail': 8, 'Communication': 7, 'Basic Math': 7},
            'industry': 'Finance'
        },
        #Education jobs
        {
            'job_name': 'Elementary Teacher',
            'description': 'Educate young students, develop lesson plans, assess student progress',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Teaching': 9, 'Communication': 8, 'Patience': 9, 'Creativity': 7, 'Classroom Management': 8},
            'industry': 'Education'
        },
        {
            'job_name': 'Training Specialist',
            'description': 'Design and deliver training programs, assess learning effectiveness',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Training Development': 8, 'Public Speaking': 8, 'Communication': 8, 'Instructional Design': 7, 'Presentation Skills': 8},
            'industry': 'Education'
        },
        #Operations and logistics jobs
        {
            'job_name': 'Supply Chain Coordinator',
            'description': 'Coordinate shipments, manage inventory, optimize supply chain processes',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Supply Chain Management': 8, 'Organization': 8, 'Excel': 7, 'Communication': 7, 'Problem Solving': 7},
            'industry': 'Operations and Logistics'
        },
        {
            'job_name': 'Quality Assurance Specialist',
            'description': 'Test products, ensure quality standards, document findings, suggest improvements',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Quality Assurance': 9, 'Attention to Detail': 9, 'Process Improvement': 7, 'Documentation': 7, 'Problem Solving': 8},
            'industry': 'Operations and Logistics'
        },
        {
            'job_name': 'Operations Manager',
            'description': 'Oversee daily operations, manage staff, optimize processes, control costs',
            'minimum_degree_required': 'Bachelor\'s',
            'required_skills': {'Operations Management': 8, 'Leadership': 8, 'Process Improvement': 7, 'Communication': 8, 'Budget Management': 7},
            'industry': 'Operations and Logistics'
        },
        # {
        #     'job_name': 'a',
        #     'description': 'b',
        #     'minimum_degree_required': 'c',
        #     'required_skills': 'd',
        #     'industry': 'e'
        # },
    ]

    try:
        print("Creating jobs database...")

        for job_data in jobs_data:
            # Check if the job already exists using SQLAlchemy 2.0 syntax
            existing_job = db.session.execute(
                db.select(Job).where(Job.job_name == job_data['job_name'])
            ).first()

            if not existing_job:
                new_job = Job(
                    job_name=job_data['job_name'],
                    description=job_data['description'],
                    minimum_degree_required=job_data['minimum_degree_required'],
                    required_skills=job_data['required_skills'],
                    industry=job_data['industry'],
                )
                db.session.add(new_job)

        db.session.commit()
        print(f"Successfully added jobs to the database!")

        # Print summary by industry using SQLAlchemy 2.0 syntax
        industries = db.session.execute(
            db.select(Job.industry, func.count(Job.id))
            .group_by(Job.industry)
        ).all()

        print("\nJobs by industry:")
        for industry, count in industries:
            print(f"  {industry}: {count} jobs")

    except Exception as e:
        db.session.rollback()
        print(f"Error creating jobs database: {e}")


def setup_database():
    """Main function to set up both databases"""
    print("Setting up job matching databases...")
    print("=" * 50)

    # Create tables if they don't exist - FIXED: Added bind parameter
    try:
        Base.metadata.create_all(bind=db.engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return

    # Create skills database
    create_skills_database()
    print()

    # Create the job database
    create_jobs_database()
    print()

    print("=" * 50)
    print("Database setup completed successfully!")


if __name__ == '__main__':
    with app.app_context():
        setup_database()