from csv_utils import read_csv
from scraper.custom_types import ResearchPaper
from typing import List, Dict, Optional

import pandas as pd
import csv
from urllib.parse import urlparse
from collections import Counter

import arxiv
import os
from tqdm.auto import tqdm

import requests
from semanticscholar import SemanticScholar
import time

from .preprocessing import get_all_research_papers, get_unique_papers, get_domain_count
from .database import upload_csv_to_supabase

def clean_filename(title: str) -> str:
    return "".join(x for x in title if x.isalnum() or x in " -_").strip()

def get_arxiv_id(url):
    """
    Extracts the arXiv ID from a URL.
    Examples: 
      - https://arxiv.org/pdf/2204.07682 -> 2204.07682
      - https://arxiv.org/abs/2204.07682 -> 2204.07682
    """
    if not isinstance(url, str):
        return None
    
    if 'arxiv.org' in url:
        return url.split('/')[-1].replace('.pdf', '')
    return None

def download_with_api(csv_file):
    df = pd.read_csv(csv_file)
    
    arxiv_df = df[df['paper_link'].str.contains('arxiv.org', case=False, na=False)].copy()
    
    arxiv_ids = arxiv_df['paper_link'].apply(get_arxiv_id).tolist()
    arxiv_ids = list(set([x for x in arxiv_ids if x]))
    
    print(f"Found {len(arxiv_ids)} unique arXiv IDs.")

    client = arxiv.Client(
        page_size=100,
        delay_seconds=3,
        num_retries=3
    )

    search = arxiv.Search(id_list=arxiv_ids)
    
    output_dir = "download_pdfs/arxiv_downloaded"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Starting download via arXiv API...")

    results = list(client.results(search))

    progress_bar = tqdm(results, desc="Downloading research papers", unit="paper")
    
    for result in progress_bar:
        try:
            safe_title = clean_filename(result.title)
            short_id = result.get_short_id().split('v')[0]
            paper_id = arxiv_df.loc[arxiv_df['paper_link'].str.contains(short_id, na=False), 'paper_id'].values[0]
            filename = f"{paper_id} {safe_title}.pdf"
            
            result.download_pdf(dirpath=output_dir, filename=filename)
            
        except Exception as e:
            print(f"Error downloading {result.entry_id}: {e}")

    print("\nAll done!")

def download_from_semantic_scholar(csv_file):
    sch = SemanticScholar()
    df = pd.read_csv(csv_file)
    
    output_dir = "download_pdfs/semantic_scholar"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Processing {len(df)} papers...")

    progress_bar = tqdm(total=len(df), desc="Downloading research papers")

    for index, row in df.iterrows():
        title = str(row['paper_title'])
        paper_id = str(row['paper_id'])
        progress_bar.update(1)

        progress_bar.set_description(f"Paper ID: {paper_id}")
        
        try:
            pdf_url = None

            if not pdf_url:
                pdf_url = row['paper_link']

            if pdf_url:
                if 'arxiv.org' in pdf_url or 'acm.org' in pdf_url:
                    continue
                
                response = requests.get(pdf_url, timeout=15)
                if not response.content.startswith(b'%PDF'):
                    continue
                if response.status_code == 200:
                    safe_title = clean_filename(title)
                    filename = f"{paper_id} {safe_title}.pdf"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
            
            time.sleep(3)

        except Exception as e:
            print(f"[Error] {title}: {e}")

def download_research_papers():

    # research_papers: List[ResearchPaper] = get_all_research_papers()
    # unique_research_papers: List[Dict] = get_unique_papers(research_papers=research_papers)
        
    # df = pd.DataFrame(unique_research_papers)
    # df.to_csv('download_pdfs/research_paper_unique.csv', index=False)

    # print(f'Saved {df.shape[0]} unique research papers to csv.')

    # get_domain_count()

    # download_with_api('download_pdfs/research_paper_unique.csv')

    # download_from_semantic_scholar('download_pdfs/research_paper_unique.csv')

    upload_csv_to_supabase('download_pdfs/research_paper_unique.csv')

