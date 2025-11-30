import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, Any, cast, List
import numpy as np

load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_existing_paper_ids() -> set:
    """
    Get all existing paper_ids from the database.
    Fetches all rows by paginating through results.

    Returns:
        Set of existing paper_ids
    """
    try:
        all_paper_ids = set()
        page_size = 1000
        offset = 0

        while True:

            response = supabase.table('research_papers')\
                .select('paper_id')\
                .range(offset, offset + page_size - 1)\
                .execute()
            data = cast(List[Dict[str, Any]], response.data)

            if not data:
                break

            all_paper_ids.update(row['paper_id'] for row in data)

            # If we got fewer results than page_size, we've reached the end
            if len(data) < page_size:
                break

            offset += page_size

        return all_paper_ids
    except Exception as e:
        print(f"Error fetching existing paper IDs: {e}")
        return set()


def prepare_row_for_insert(row: pd.Series) -> Dict[str, Any]:
    """
    Prepare a CSV row for insertion into Supabase.
    Handles NaN values and converts data types appropriately.

    Args:
        row: A pandas Series representing a CSV row

    Returns:
        Dictionary ready for Supabase insertion
    """
    data = {}
    for key, value in row.items():
        if pd.isna(value):
            data[key] = None
        elif isinstance(value, (int, np.integer)):
            data[key] = int(value)
        elif isinstance(value, (float, np.floating)):
            data[key] = int(value) if value.is_integer() else float(value)
        else:
            data[key] = str(value) if value else None

    return data


def upload_csv_to_supabase(csv_path: str, batch_size: int = 100):
    """
    Upload research_paper_unique.csv to Supabase database.

    Args:
        csv_path: Path to the CSV file
        batch_size: Number of rows to insert in each batch
    """
    print(f"Reading CSV file from: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Total rows in CSV: {len(df)}")

    print("Fetching existing paper IDs from database...")
    existing_ids = get_existing_paper_ids()
    print(f"Found {len(existing_ids)} existing papers in database")

    df_new = df[~df['paper_id'].isin(existing_ids)]
    print(f"New papers to insert: {len(df_new)}")

    if len(df_new) == 0:
        print("No new papers to insert. All papers already exist in database.")
        return

    # Insert in batches
    total_inserted = 0
    total_failed = 0

    for i in range(0, len(df_new), batch_size):
        batch = df_new.iloc[i:i + batch_size]
        batch_data = [prepare_row_for_insert(row) for _, row in batch.iterrows()]

        response = supabase.table('research_papers').insert(batch_data).execute()
        batch_inserted = len(response.data)
        total_inserted += batch_inserted
        print(f"Batch {i // batch_size + 1}: Inserted {batch_inserted} rows")

    print(f"\n{'='*60}")
    print(f"Upload complete!")
    print(f"Total inserted: {total_inserted}")
    print(f"Total failed: {total_failed}")
    print(f"Total skipped (duplicates): {len(df) - len(df_new)}")
    print(f"{'='*60}")
