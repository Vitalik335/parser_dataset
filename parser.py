import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import os
import time

def parse_date(date_str):
    try:
        for fmt in ['%d %B %Y', '%B %Y', '%Y']:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None

def is_recent_enough(date_str, year_threshold):
    date_obj = parse_date(date_str)
    if date_obj and date_obj.year >= year_threshold:
        return True
    return False

def scrape_datasets(search_term, year_filter):
    base_url = "https://www.data.gov.uk"
    search_url = f"{base_url}/search?q={search_term}+{year_filter}"
    
    results = []
    current_page = search_url
    page_num = 1
    
    print(f"Starting scraping from {search_url}")
    
    while current_page:
        print(f"Scraping page {page_num}: {current_page}")
        
        try:
            response = requests.get(current_page)
            if response.status_code != 200:
                print(f"Failed to fetch page {page_num}. Status code: {response.status_code}")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all result items
            result_items = soup.find_all('div', class_='dgu-results__result')
            print(f"Found {len(result_items)} results on page {page_num}")
            
            for item in result_items:
                # Extract link
                link_tag = item.find('a', class_='govuk-link')
                if not link_tag:
                    continue
                    
                link_url = base_url + link_tag['href'] if link_tag['href'].startswith('/') else link_tag['href']
                
                # Extract metadata
                metadata = item.find('dl', class_='dgu-metadata__box')
                if not metadata:
                    continue
                    
                # Extract last updated date
                date_tag = None
                for dt in metadata.find_all('dt'):
                    if "Last updated" in dt.text:
                        date_tag = dt.find_next('dd')
                        break
                        
                last_updated = date_tag.text.strip() if date_tag else "Unknown"
                
                # Check if the date is recent enough
                if last_updated != "Unknown" and not is_recent_enough(last_updated, year_filter):
                    continue
                
                # Add only URL to results
                results.append({
                    'URL': link_url
                })
            
            # Check if there are more pages
            next_page = None
            pagination = soup.find('a', rel='next')
            if pagination:
                next_href = pagination['href']
                next_page = base_url + next_href if next_href.startswith('/') else next_href
                
            if not next_page:
                break
                
            current_page = next_page
            page_num += 1
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error on page {page_num}: {e}")
            break
    
    print(f"Finished scraping. Found {len(results)} datasets from {year_filter}")
    return results

def save_results(data, filename_prefix):
    if not data:
        print(f"No data to save for {filename_prefix}")
        return
        
    # Create 'results' directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Save as text file
    txt_path = f"results/{filename_prefix}.txt"
    with open(txt_path, "w") as f:
        for item in data:
            f.write(f"{item['URL']}\n")
    print(f"URLs saved to {txt_path}")
    
    # Save as CSV
    csv_path = f"results/{filename_prefix}.csv"
    pd.DataFrame(data).to_csv(csv_path, index=False)
    print(f"Data saved as CSV: {csv_path}")
    
    # Try to save as Excel
    try:
        excel_path = f"results/{filename_prefix}.xlsx"
        pd.DataFrame(data).to_excel(excel_path, index=False)
        print(f"Data saved to Excel: {excel_path}")
    except ModuleNotFoundError as e:
        if "openpyxl" in str(e):
            print("Excel export skipped - openpyxl module missing")
        else:
            raise
# ("type here what do you want", 'year','type of save document'),
def run_all_searches():
    # Define all search combinations
    search_combinations = [
        # Format: (search_term, year_filter, filename_prefix)
        ("type here what do you want", 'year','type of save document'),
        ("type here what do you want", 'year','type of save document')
    ]
    
    for search_term, year_filter, filename_prefix in search_combinations:
        print(f"\n{'='*50}")
        print(f"Processing search: {search_term} - {year_filter}")
        print(f"{'='*50}")
        
        datasets = scrape_datasets(search_term, year_filter)
        save_results(datasets, filename_prefix)

if __name__ == "__main__":
    print("Starting comprehensive scraper for UK Data Gov datasets")
    try:
        run_all_searches()
        print("\nAll searches completed successfully!")
    except Exception as e:
        print(f"\nAn error occurred during execution: {e}")
