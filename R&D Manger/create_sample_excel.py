import pandas as pd

def create_sample_excel():
    data = {
        'Paper Title': [
            'Advancements in AI Filtering', 
            'Deep Learning for Image Processing', 
            'Blockchain in Supply Chain',
            'Quantum Computing Basics',
            'Cybersecurity Trends 2025',
            'Renewable Energy Systems',
            'Smart Grid Technology',
            'Network Security Protocols',
            'Robotics in Manufacturing',
            'Cloud Infrastructure Design'
        ],
        'Journal Name': [
            'AI Review', 
            'IEEE Transactions', 
            'Journal of Business',
            'Physics Today',
            'Security Ledger',
            'Energy Reports',
            'Power Systems',
            'Comm Networks',
            'Robotics Journal',
            'Cloud Computing'
        ],
        'Author Name': [
            'Dr. Alice', 
            'Dr. Bob', 
            'Dr. Charlie',
            'Dr. David',
            'Dr. Eve',
            'Dr. Frank',
            'Dr. Grace',
            'Dr. Henry',
            'Dr. Ivy',
            'Dr. Jack'
        ],
        'Department': [
            'AIDS',
            'AIML',
            'CSBS',
            'CSE',
            'CYS',
            'ECE',
            'IT',
            'MECH',
            'RA',
            'S&H'
        ],
        'Publication Type': [
            'Journal', 
            'Paper', 
            'Book',
            'Journal',
            'Paper',
            'Journal',
            'Paper',
            'Book',
            'Journal',
            'Paper'
        ],
        'Status': [
            'Published', 
            'Submitted', 
            'Working Process',
            'Published',
            'Submitted',
            'Published',
            'Submitted',
            'Working Process',
            'Published',
            'Submitted'
        ],
        'Author Position': [
            'First Author',
            'Corresponding Author',
            'Co-Author',
            'First Author',
            'Co-Author',
            'First Author',
            'Corresponding Author',
            'Co-Author',
            'First Author',
            'Co-Author'
        ],
        'Publisher': [
            'Springer',
            'IEEE',
            'Wiley',
            'Oxford',
            'Elsevier',
            'Springer',
            'IEEE',
            'Wiley',
            'Oxford',
            'Elsevier'
        ],
        'Month/Year': [
            'Jan 2025',
            'Feb 2025',
            'Mar 2025',
            'Apr 2025',
            'May 2025',
            'Jun 2025',
            'Jul 2025',
            'Aug 2025',
            'Sep 2025',
            'Oct 2025'
        ],
        'ISSN': [
            '1234-5678',
            '8765-4321',
            '1122-3344',
            '5566-7788',
            '9900-1122',
            '3344-5566',
            '7788-9900',
            '2233-4455',
            '6677-8899',
            '1029-3847'
        ],
        'Scopus': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        'SCI': [0, 1, 0, 0, 1, 0, 1, 0, 0, 1],
        'WoS': [1, 0, 1, 0, 0, 1, 0, 1, 0, 0]
    }
    
    df = pd.DataFrame(data)
    df.to_excel('sample_research_data.xlsx', index=False)
    print("✓ Created sample_research_data.xlsx")

if __name__ == '__main__':
    create_sample_excel()
