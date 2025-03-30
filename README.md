🚨 Important Note: This is a project completed under tight deadlines. Due to time constraints, I was unable to collect all the data and polish the project. The main goal was to fulfill the assignment requirements as quickly as possible. 🚨
🌎 Open Data Web Scraper
This project is a simple web scraper designed to collect open data from government portals. It works for some websites, but due to the dynamic architecture of others (such as React-based websites), a different approach is required. Additionally, the project includes AnalyzeAI, a tool that processes the collected data using OpenAI to generate key insights.

📌 Supported Websites
✅ 🇬🇧 data.gov.uk
✅ 🇦🇺 researchdata.edu.au
✅ 🇨🇦 search.open.canada.ca
✅ 🇳🇿 data.govt.nz
✅ 🇮🇪 data.gov.ie

Some of these websites use dynamic content loading (e.g., with React), so a different scraping method (such as Selenium or Puppeteer) is needed instead of BeautifulSoup.

🔍 AnalyzeAI – Data Processing with OpenAI
The AnalyzeAI script processes the datasets collected by the scraper and generates the following key information using OpenAI:

URL (link to the dataset)

Dataset Name

Topic (2-3 keywords/phrases)

🔧 Technologies Used
Python

BeautifulSoup / Scrapy – For static HTML scraping

Selenium – For scraping React-based websites with dynamic content

Requests – To fetch web pages

Pandas – For data processing

OpenAI API – For dataset analysis

📦 Installation
It is highly recommended to set up a virtual environment for this project:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
Then, install the necessary dependencies:

bash
Copy
Edit
pip install -r requirements.txt
🚀 Usage
To run the scraper:
bash
Copy
Edit
type witch file do you want for example python parser.py
To run the AnalyzeAI script:
bash
Copy
Edit
python analyze_ai.py
📜 License
This project is licensed under the MIT License.


