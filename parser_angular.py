from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_research_datasets(search_term, year_from, year_to, rows=100):
    formatted_search = search_term.replace(' ', '%20')
    base_url = "https://researchdata.edu.au"
    
    search_url = f"{base_url}/search/#!/rows={rows}/sort=score%20desc/class=collection/p=1/q={formatted_search}/year_from={year_from}/year_to={year_to}/"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Фоновый режим
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=options)
    driver.get(search_url)
    
    results = []
    try:
        wait = WebDriverWait(driver, 10)

        while True:
            time.sleep(2)  # Ждем загрузку страницы
            
            # Парсим HTML после рендеринга Angular
            soup = BeautifulSoup(driver.page_source, "html.parser")

            result_items = soup.find_all('div', class_='sresult')
            for item in result_items:
                title_tag = item.find('h2', class_='post-title')
                if not title_tag or not title_tag.find('a'):
                    continue
                link_tag = title_tag.find('a')
                title = link_tag.text.strip()
                link_url = link_tag['href']
                if link_url.startswith('/'):
                    link_url = base_url + link_url

                results.append({'URL': link_url, 'Title': title})

            # Проверяем пагинацию
            pagination = soup.find('ul', class_='pagi')
            if not pagination:
                break  # Если нет пагинации, завершаем
            
            active_page = pagination.find('li', class_='active')
            next_page = active_page.find_next_sibling('li') if active_page else None

            if next_page and next_page.find('a'):
                print(f"Переход на следующую страницу...")
                next_page_button = driver.find_element(By.LINK_TEXT, next_page.text.strip())
                driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(2)  # Ждем загрузку новой страницы
            else:
                break  # Если страниц больше нет — выходим

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        driver.quit()

    print(f"Найдено {len(results)} записей для '{search_term}'")
    return results

def save_results(data, filename_prefix):
    if not data:
        print(f"Нет данных для сохранения: {filename_prefix}")
        return
        
    if not os.path.exists('results2'):
        os.makedirs('results2')
    
    txt_path = f"results2/{filename_prefix}.txt"
    with open(txt_path, "w", encoding='utf-8') as f:
        for item in data:
            f.write(f"{item['URL']}\n")
    print(f"Сохранено в TXT: {txt_path}")

    csv_path = f"results2/{filename_prefix}.csv"
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Сохранено в CSV: {csv_path}")

    excel_path = f"results2/{filename_prefix}.xlsx"
    try:
        df.to_excel(excel_path, index=False)
        print(f"Сохранено в Excel: {excel_path}")
    except ModuleNotFoundError as e:
        if "openpyxl" in str(e):
            print("Excel экспорт пропущен – установите 'openpyxl'")

if __name__ == "__main__":
    print("Запуск парсинга...")

    search_terms = [
        "artificial intelligence",
        "enhanced reality",
        "bit coin",
        "cloud computing",
        "cutting-edge technologies"
    ]

    for term in search_terms:
        filename_prefix = term.replace(" ", "_").lower()
        print(f"\n==== Парсим '{term}' ====")
        datasets = scrape_research_datasets(term, 2024, 2026)
        save_results(datasets, filename_prefix)

    print("\nПарсинг завершен для всех запросов!")
