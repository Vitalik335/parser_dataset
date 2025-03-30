🌎 Open Data Web Scraper
This project is a web scraper designed to collect open data from government portals. It works for some websites, while others require a different approach due to their React-based architecture. Additionally, the project includes AnalyzeAI, a tool that processes collected data using OpenAI.

📌 Supported Websites
✅ 🇬🇧 data.gov.uk
✅ 🇦🇺 researchdata.edu.au
✅ 🇨🇦 search.open.canada.ca
✅ 🇳🇿 data.govt.nz
✅ 🇮🇪 data.gov.ie

Some websites use dynamic content loading with React, requiring a different scraping approach (e.g., Selenium or Puppeteer instead of BeautifulSoup).

🔍 AnalyzeAI – Data Processing with OpenAI
The AnalyzeAI script processes the collected datasets and extracts key information using OpenAI. It generates:

URL (link to the dataset)

Dataset Name

Topic (2-3 keywords/phrases)

🔧 Technologies Used
Python

BeautifulSoup / Scrapy – For static HTML scraping

Selenium – For dynamic content scraping

Requests – To fetch web pages

Pandas – For data processing

OpenAI API – For dataset analysis

📦 Installation
It is recommended to use a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
Then, install the required dependencies:

bash
Copy
Edit
pip install -r requirements.txt
🚀 Usage
Run the scraper:
bash
Copy
Edit
python type witch file do you want for example parser.py
Run AnalyzeAI:
bash
Copy
Edit
python analyze_ai.py
