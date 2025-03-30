import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import pandas as pd
import time

def is_valid_year(date_string):
    try:
        date = datetime.strptime(date_string, '%b %d, %Y')
        return date.year in [2024, 2025]
    except ValueError:
        return False

def parse_page(page_url):
    print(f"Scraping page: {page_url}")
    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {page_url}: {e}")
        return [], None

    soup = BeautifulSoup(response.text, 'html.parser')
    dataset_info = []
    rows = soup.find_all('div', class_='row mrgn-bttm-xl mrgn-lft-md')
    
    for row in rows:
        link = row.find('a', href=True)
        if link:
            dataset_url = link['href']
            title = link.get_text(strip=True)
            
            record_modified_row = row.find_next('div', class_='row mrgn-tp-md')
            if record_modified_row:
                cols = record_modified_row.find_all('div', class_='col-sm-6')
                if len(cols) >= 2:
                    record_modified_text = cols[0].get_text(strip=True)
                    record_released_text = cols[1].get_text(strip=True)
                    
                    record_modified_date = record_modified_text.replace("Record Modified:", "").strip()
                    
                    if is_valid_year(record_modified_date):
                        dataset_info.append({
                            "Title": title,
                            "Dataset URL": dataset_url,
                            "Record Modified": record_modified_date,
                            "Record Released": record_released_text.replace("Record Released:", "").strip()
                        })

    return dataset_info, soup

def get_total_pages(soup):
    pagination = soup.find('ul', class_='pagination')
    if not pagination:
        return 1
    
    page_numbers = []
    for li in pagination.find_all('li'):
        a_tag = li.find('a')
        if a_tag and a_tag.get('onclick'):
            onclick = a_tag['onclick']
            if 'gotoPage' in onclick:
                try:
                    page_num = int(onclick.split("'")[1])
                    page_numbers.append(page_num)
                except (IndexError, ValueError):
                    continue
    
    if page_numbers:
        return max(page_numbers)
    
    next_button = pagination.find('li', class_='next')
    if next_button and 'disabled' not in next_button.get('class', []):
        return None
    
    return 1

def save_to_txt(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Title|Dataset URL|Record Modified|Record Released\n")
        for item in data:
            f.write(f"{item['Title']}|{item['Dataset URL']}|{item['Record Modified']}|{item['Record Released']}\n")

def scrape_search_term(search_term, filename_prefix):
    base_url = f'https://search.open.canada.ca/opendata/?portal_type=dataset&portal_type=info&sort=metadata_modified+desc&search_text={search_term.replace(" ", "+")}&page='
    
    results_dir = "search_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    all_data = []
    page = 1
    total_pages = None
    
    while True:
        page_url = f'{base_url}{page}'
        print(f"Scraping page {page} for '{search_term}'...")
        
        dataset_info, soup = parse_page(page_url)
        if dataset_info:
            all_data.extend(dataset_info)
        
        if page == 1 and total_pages is None:
            total_pages = get_total_pages(soup)
            print(f"Total pages for '{search_term}': {total_pages if total_pages else 'unknown'}")
        
        if total_pages:
            if page >= total_pages:
                break
            page += 1
        else:
            next_button = soup.find('li', class_='next') if soup else None
            if not next_button or 'disabled' in next_button.get('class', []):
                break
            page += 1
        
        time.sleep(1)
    
    if all_data:
        # Сохраняем в Excel
        excel_file = os.path.join(results_dir, f"{filename_prefix}.xlsx")
        df = pd.DataFrame(all_data)
        df.to_excel(excel_file, index=False)
        print(f"Saved {len(all_data)} records to {excel_file}")
        
        # Сохраняем в TXT
        txt_file = os.path.join(results_dir, f"{filename_prefix}.txt")
        save_to_txt(all_data, txt_file)
        print(f"Saved {len(all_data)} records to {txt_file}\n")
    else:
        print(f"No valid datasets found for '{search_term}'\n")

def main():
    search_terms = [
        ("artificial intelligence", "ai_research"),
        ("enhanced reality", "enhanced_reality"),
        ("bit coin", "bit_coin"),
        ("cloud computing", "cloud_computing"),
        ("cutting-edge technologies", "cutting_edge_tech")
    ]
    
    print("Starting scraping process...\n")
    
    for term, filename in search_terms:
        print(f"=== Processing: '{term}' ===")
        scrape_search_term(term, filename)
    
    print("All searches completed successfully!")

if __name__ == "__main__":
    main()