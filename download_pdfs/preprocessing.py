from csv_utils import read_csv
from scraper.custom_types import ResearchPaper
from typing import List, Dict

import csv
from urllib.parse import urlparse
from collections import Counter

from tqdm.auto import tqdm

def merge_papers(unique_research_papers: List[Dict], paper: ResearchPaper, matching_key: str):

    paper_dict = next((x for x in unique_research_papers if x[matching_key] == paper[matching_key]))

    if paper_dict is None:
        return
    
    if paper['name'] not in paper_dict['list_of_staff']:
        paper_dict['list_of_staff'].append(paper['name'])
        paper_dict['number_of_staff'] += 1
        next_index = paper_dict['number_of_staff']
        paper_dict[f'staff_name{next_index}'] = paper['name']
        paper_dict[f'staff_dept{next_index}'] = paper['department']
        paper_dict[f'staff_title{next_index}'] = paper['academic_title']

def get_all_research_papers() -> List[ResearchPaper]:
    research_papers: List[ResearchPaper] = []
    csv_data, _ = read_csv('research_paper.csv')
    for row in csv_data:
        research_paper: ResearchPaper = {
            'name': row.get('name', ''),
            'link': row.get('link', ''),
            'academic_title': row.get('academic_title', ''),
            'department': row.get('department', ''),
            'phone': row.get('phone', ''),
            'email': row.get('email', ''),
            'user_id': row.get('user_id', ''),
            'paper_title': row.get('paper_title', ''),
            'paper_link': row.get('paper_link', ''),
            'year': row.get('year', '')
        }
        research_papers.append(research_paper)
    return research_papers

def get_unique_papers(research_papers: List[ResearchPaper]) -> List[Dict]:

    unique_research_papers: List[Dict] = []

    matching_key = 'paper_link'
    paper_id = 1

    progress_bar = tqdm(total=len(research_papers), desc="Processing research papers")

    for paper in research_papers:

        progress_bar.update(1)
         
        if not paper['paper_link']:
            continue

        if paper[matching_key] not in map(lambda x: x[matching_key], unique_research_papers):
            new_paper = {
                'paper_id': str(paper_id),
                'paper_title': paper['paper_title'],
                'paper_link': paper['paper_link'],
                'year': paper['year'],
                'list_of_staff': [paper['name']],
                'number_of_staff': 1,
                'staff_name1': paper['name'],
                'staff_dept1': paper['department'],
                'staff_title1': paper['academic_title'],
            }
            unique_research_papers.append(new_paper)
            paper_id += 1
            continue

        ## Duplicate exists
        merge_papers(unique_research_papers=unique_research_papers, paper=paper, matching_key=matching_key)
        
    return unique_research_papers

def get_domain_from_link(link: str) -> str:
    parsed = urlparse(link)
    return parsed.netloc

def get_domain_count():

    domains = []
    with open('download_pdfs/research_paper_unique.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            domains.append(get_domain_from_link(row['paper_link']))

    file = open('download_pdfs/domains.txt', 'w', encoding='utf-8')

    counter = Counter(domains)
    for domain, count in counter.most_common(20):
        file.write(f'{count}\t{domain}\n')
    
    file.close()