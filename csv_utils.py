import csv
from typing import List, Dict, Tuple

from scraper.custom_types import UserID

def extract_from_csv(csv_file_path: str, rows: list[str]):
    data: List[Dict] = []
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for csv_row in csv_reader:
            row_data = {}
            for row_name in rows:
                row_data[row_name] = csv_row[row_name]
                data.append(row_data)

    return data

def extract_single_row_from_csv(csv_file_path: str, row: str):

    csv_dict_data = extract_from_csv(csv_file_path=csv_file_path, rows=[row])
    data = list(map(lambda x: x[row], csv_dict_data))

    return data

def read_csv(csv_file_path: str) -> Tuple[List[Dict], List[str]]:
    data: List[Dict] = []
    with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        fieldnames = list(csv_reader.fieldnames or [])
        for csv_row in csv_reader:
            data.append(csv_row)

    return data, fieldnames

def merge_csv(csv_path_1: str, csv_path_2: str, output_file: str, key_cols: List[str]):
    """
    Merge two CSV files based on key columns.

    Args:
        csv_path_1: Path to the first CSV file
        csv_path_2: Path to the second CSV file
        output_file: Path where the merged CSV will be written
        key_cols: List of column names to use as merge keys

    Example:
        merge_csv('uic_staff.csv', 'scholar_ids.csv', 'uic_staff_user_ids.csv', ['name'])
    """
    
    csv_data1, fieldnames1 = read_csv(csv_path_1)
    csv_data2, fieldnames2 = read_csv(csv_path_2)

    print(fieldnames1)
    print(fieldnames2)

    merged_data: List[Dict] = []

    for key_col in key_cols:
        if key_col not in fieldnames1 or key_col not in fieldnames2:
            raise ValueError(f"Key column '{key_col}' not found in CSV files.")

    fieldnames_without_keys1 = [col for col in fieldnames1 if col not in key_cols]
    fieldnames_without_keys2 = [col for col in fieldnames2 if col not in key_cols]

    for row in csv_data1:
        data = row
        row_in_csv2 = {}
        for row2 in csv_data2:
            found = True
            for key_col in key_cols:
                if row[key_col] != row2[key_col]:
                    found = False
                    break
            if found:
                row_in_csv2 = row2
                break
        
        for fieldname in fieldnames_without_keys2:
            data[fieldname] = row_in_csv2.get(fieldname, '')
        
        merged_data.append(data)

    output_fieldnames = fieldnames1 + fieldnames_without_keys2
        
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(merged_data)
    
    return merged_data

def read_user_ids(csv_file_path: str) -> List[UserID]:
    data: List[UserID] = []
    csv_data, _ = read_csv(csv_file_path)
    for row in csv_data:
        user_id_data: UserID = {
            'name': row.get('name', ''),
            'link': row.get('link', ''),
            'academic_title': row.get('academic_title', ''),
            'department': row.get('department', ''),
            'phone': row.get('phone', ''),
            'email': row.get('email', ''),
            'user_id': row.get('user_id', '')
        }
        data.append(user_id_data)
    return data

def extract_staff_names(csv_file_path: str) -> List[str]:
    csv_data, _ = read_csv(csv_file_path)
    return list(map(lambda x: x['name'], csv_data))

def compare_csv_files(csv_file_path_1: str, csv_file_path_2: str) -> List[str]:
    csv_data_1_staff_names = extract_staff_names(csv_file_path_1)
    csv_data_2_staff_names = extract_staff_names(csv_file_path_2)

    name_list: List[str] = []

    for csv_data_1_staff_name in csv_data_1_staff_names:
        if csv_data_1_staff_name not in csv_data_2_staff_names:
            name_list.append(csv_data_1_staff_name)
    
    return name_list

        

        
