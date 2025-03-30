import pandas as pd
import openai
import time
import requests
from bs4 import BeautifulSoup

# Path to your Excel file
file_path = 'D:\\pythonParser\\analyze\\Check.xlsx'

# Your OpenAI API key
openai.api_key = 'Your OpenAI API key'
# Initialize OpenAI client
client = openai.OpenAI(api_key=openai.api_key)

# Function to extract more comprehensive website content
def scrape_website_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to get the title
            title = soup.title.string if soup.title else ""
            
            # Try to get main heading
            h1 = ""
            if soup.find('h1'):
                h1 = soup.find('h1').text.strip()
            
            # Try to get metadata descriptions
            meta_desc = ""
            if soup.find('meta', attrs={'name': 'description'}):
                meta_desc = soup.find('meta', attrs={'name': 'description'}).get('content', '')
            
            # Try to get paragraph content
            paragraphs = []
            priority_elements = soup.find_all(['div.field-name-field-description', 'div.field-item', 'div.dataset-description'])
            if priority_elements:
                for elem in priority_elements[:3]:
                    if elem.text.strip():
                        paragraphs.append(elem.text.strip())
            else:
                for p in soup.find_all(['p', 'h2', 'h3'])[:5]:
                    if p.text.strip():
                        paragraphs.append(p.text.strip())
            
            content = " ".join(paragraphs)
            if len(content) > 500:  # Allow more content
                content = content[:500] + "..."
                
            result = {
                "title": title,
                "h1": h1,
                "meta_desc": meta_desc,
                "content": content
            }
            
            return result
        else:
            return {"title": "", "h1": "", "meta_desc": "", "content": ""}
    except Exception as e:
        print(f"Error scraping website: {e}")
        return {"title": "", "h1": "", "meta_desc": "", "content": ""}

# Function for batch processing URLs
def process_batch(urls_batch):
    try:
        # Prepare prompt for batch processing
        prompt = "Analyze these Canadian open data URLs and provide descriptive dataset names and specific topics for each:\n\n"
        
        for i, url in enumerate(urls_batch):
            dataset_id = url.split('/')[-1]
            
            # Try to get content for each URL
            print(f"  Scraping content for URL {i+1}: {url}")
            content_data = scrape_website_content(url)
                
            prompt += f"URL {i+1}: {url}\n"
            prompt += f"Dataset ID {i+1}: {dataset_id}\n"
            
            if content_data["title"]:
                prompt += f"Title {i+1}: {content_data['title']}\n"
            if content_data["h1"]:
                prompt += f"Main Heading {i+1}: {content_data['h1']}\n"
            if content_data["meta_desc"]:
                prompt += f"Description {i+1}: {content_data['meta_desc']}\n"
            if content_data["content"]:
                prompt += f"Content {i+1}: {content_data['content']}\n"
            
            prompt += "\n"
        
        prompt += """For each URL, your task is to:

1. Create a CLEAR, DESCRIPTIVE dataset name that immediately tells what the dataset contains.
2. Provide 3 SPECIFIC topic keywords/phrases that would allow someone to understand the dataset's subject matter at a glance.

IMPORTANT GUIDELINES:
- DO NOT use generic terms like 'Canada', 'Open data', or 'Government data'
- DO NOT use "[Unavailable]" or similar placeholder text
- The topics should be INFORMATIVE ENOUGH that someone can understand what the dataset is about without visiting the URL
- Be SPECIFIC rather than generic - e.g. "Air Quality Measurements" is better than "Environmental Data"
- If the dataset appears to be technical or specialized, include the field or discipline in the topics

Format for each URL:
URL 1:
Dataset Name: [clear descriptive name]
Topic: [specific topic 1], [specific topic 2], [specific topic 3]

URL 2:
Dataset Name: [clear descriptive name]
Topic: [specific topic 1], [specific topic 2], [specific topic 3]

... and so on for all URLs."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst specializing in making complex government datasets understandable to the general public. You excel at creating clear, descriptive names and informative topic tags that help people immediately understand what information a dataset contains."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000  # Increased for more detailed responses
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error processing batch: {e}")
        return ""

# Function to parse batch results (keeping the same as before)
def parse_batch_results(batch_result, num_urls, urls_batch):
    results = []
    
    # Split response by "URL" substring
    parts = batch_result.split("URL ")
    
    # Skip first element as it's likely empty
    for i in range(1, len(parts)):
        if i > len(urls_batch):
            break
            
        part = parts[i].strip()
        current_data = {}
        
        # Get URL number
        url_num = part.split(":")[0].strip()
        current_data['url_num'] = url_num
        
        # Extract dataset name
        if "Dataset Name:" in part:
            dataset_name = part.split("Dataset Name:")[1].split("\n")[0].strip()
            
            # Check for undesired placeholders
            if "[Unavailable]" in dataset_name or dataset_name == "N/A" or dataset_name == "Unknown":
                # Extract dataset ID from URL to create a better name
                dataset_id = urls_batch[int(url_num) - 1].split('/')[-1]
                dataset_name = f"Canadian Government Dataset {dataset_id}"
            
            current_data['dataset_name'] = dataset_name
        else:
            # If no dataset name found, use the dataset ID
            dataset_id = urls_batch[int(url_num) - 1].split('/')[-1]
            current_data['dataset_name'] = f"Canadian Government Dataset {dataset_id}"
        
        # Extract topic
        if "Topic:" in part:
            topic = part.split("Topic:")[1].split("\n")[0].strip()
            
            # Check for undesired placeholders
            if "[Unavailable]" in topic or topic == "N/A" or topic == "Unknown":
                # Try to extract some meaning from the dataset ID
                dataset_id = urls_batch[int(url_num) - 1].split('/')[-1]
                if any(term in dataset_id.lower() for term in ['env', 'eco', 'nat']):
                    topic = "environmental data, natural resources, ecological monitoring"
                elif any(term in dataset_id.lower() for term in ['stat', 'data', 'survey']):
                    topic = "statistical analysis, survey results, population metrics"
                elif any(term in dataset_id.lower() for term in ['health', 'med', 'hosp']):
                    topic = "healthcare statistics, medical research, public health"
                else:
                    topic = "public records, government statistics, federal data"
            
            current_data['topic'] = topic
        else:
            # Try to extract some meaning from the dataset ID
            dataset_id = urls_batch[int(url_num) - 1].split('/')[-1]
            if any(term in dataset_id.lower() for term in ['env', 'eco', 'nat']):
                topic = "environmental data, natural resources, ecological monitoring"
            elif any(term in dataset_id.lower() for term in ['stat', 'data', 'survey']):
                topic = "statistical analysis, survey results, population metrics"
            elif any(term in dataset_id.lower() for term in ['health', 'med', 'hosp']):
                topic = "healthcare statistics, medical research, public health"
            else:
                topic = "public records, government statistics, federal data"
                
            current_data['topic'] = topic
        
        results.append(current_data)
    
    # If we didn't get enough results, generate some for the missing URLs
    while len(results) < num_urls:
        idx = len(results)
        if idx < len(urls_batch):
            dataset_id = urls_batch[idx].split('/')[-1]
            # Try to extract some meaning from the dataset ID
            if any(term in dataset_id.lower() for term in ['env', 'eco', 'nat']):
                topic = "environmental data, natural resources, ecological monitoring"
            elif any(term in dataset_id.lower() for term in ['stat', 'data', 'survey']):
                topic = "statistical analysis, survey results, population metrics"
            elif any(term in dataset_id.lower() for term in ['health', 'med', 'hosp']):
                topic = "healthcare statistics, medical research, public health"
            else:
                topic = "public records, government statistics, federal data"
                
            results.append({
                'url_num': str(idx + 1),
                'dataset_name': f"Canadian Government Dataset {dataset_id}",
                'topic': topic
            })
        else:
            results.append({
                'url_num': str(idx + 1),
                'dataset_name': "Canadian Government Dataset",
                'topic': "public records, government statistics, federal data"
            })
    
    return results[:num_urls]

# Load Excel file
print(f"Attempting to open file: {file_path}")
try:
    df = pd.read_excel(file_path)
    print("File opened successfully!")
except Exception as e:
    print(f"Error opening file: {e}")
    exit(1)

# Create columns B and C if they don't exist
if len(df.columns) < 2:
    df.insert(1, "B", "")  # Add column B
if len(df.columns) < 3:
    df.insert(2, "C", "")  # Add column C

# Track API usage
api_calls = 0
processed_count = 0
batch_size = 3  # Reduce batch size to 3 for more focused analysis

# Process URLs in batches
for batch_start in range(0, len(df), batch_size):
    batch_end = min(batch_start + batch_size, len(df))
    print(f"Processing batch {batch_start//batch_size + 1}: URLs {batch_start+1}-{batch_end}")
    
    # Get URLs for this batch
    urls_batch = []
    for i in range(batch_start, batch_end):
        if i < len(df):
            url = df.iloc[i, 0]
            if isinstance(url, str) and url.startswith("http"):
                urls_batch.append(url)
    
    if not urls_batch:
        continue
    
    # Process this batch
    try:
        batch_result = process_batch(urls_batch)
        api_calls += 1
        
        if batch_result:
            # Parse batch results
            parsed_results = parse_batch_results(batch_result, len(urls_batch), urls_batch)
            
            # Update DataFrame with results
            url_counter = 0
            for i in range(batch_start, batch_end):
                if i < len(df) and url_counter < len(parsed_results):
                    url = df.iloc[i, 0]
                    if isinstance(url, str) and url.startswith("http"):
                        result = parsed_results[url_counter]
                        
                        # Make sure we're not using "[Unavailable]" placeholders
                        dataset_name = result.get('dataset_name', '')
                        if "[Unavailable]" in dataset_name or dataset_name == "N/A" or dataset_name == "Unknown":
                            dataset_id = url.split('/')[-1]
                            dataset_name = f"Canadian Government Dataset {dataset_id}"
                        
                        topic = result.get('topic', '')
                        if "[Unavailable]" in topic or topic == "N/A" or topic == "Unknown":
                            # Try to extract some meaning from the dataset ID
                            dataset_id = url.split('/')[-1]
                            if any(term in dataset_id.lower() for term in ['env', 'eco', 'nat']):
                                topic = "environmental data, natural resources, ecological monitoring"
                            elif any(term in dataset_id.lower() for term in ['stat', 'data', 'survey']):
                                topic = "statistical analysis, survey results, population metrics"
                            elif any(term in dataset_id.lower() for term in ['health', 'med', 'hosp']):
                                topic = "healthcare statistics, medical research, public health"
                            else:
                                topic = "public records, government statistics, federal data"
                        
                        df.iloc[i, 1] = dataset_name
                        df.iloc[i, 2] = topic
                        processed_count += 1
                        
                        # Print progress
                        print(f"  → URL {i+1}: {url}")
                        print(f"  → Dataset: {dataset_name}")
                        print(f"  → Topic: {topic}")
                        print("-" * 30)
                        
                        url_counter += 1
        else:
            print("Failed to get results for this batch.")
            
            # Emergency fallback - at least put something in the fields
            for i in range(batch_start, batch_end):
                if i < len(df):
                    url = df.iloc[i, 0]
                    if isinstance(url, str) and url.startswith("http"):
                        dataset_id = url.split('/')[-1]
                        df.iloc[i, 1] = f"Canadian Government Dataset {dataset_id}"
                        
                        # Try to extract some meaning from the dataset ID
                        if any(term in dataset_id.lower() for term in ['env', 'eco', 'nat']):
                            topic = "environmental data, natural resources, ecological monitoring"
                        elif any(term in dataset_id.lower() for term in ['stat', 'data', 'survey']):
                            topic = "statistical analysis, survey results, population metrics"
                        elif any(term in dataset_id.lower() for term in ['health', 'med', 'hosp']):
                            topic = "healthcare statistics, medical research, public health"
                        else:
                            topic = "public records, government statistics, federal data"
                            
                        df.iloc[i, 2] = topic
                        processed_count += 1
    except Exception as e:
        print(f"Error processing batch: {e}")
    
    # Calculate estimated cost
    est_cost = api_calls * 0.002  # Rough estimate: $0.002 per API call
    print(f"Processed: {processed_count}/{len(df)} URLs, API calls: {api_calls}, Est. cost: ${est_cost:.3f}")
    
    # Add delay between batches
    time.sleep(2)
    
    # Budget limit
    if est_cost > 0.95:  # Set slightly below $1 to be safe
        print("Budget limit reached. Stopping processing.")
        break

# Save the updated Excel file
output_path = 'D:\\pythonParser\\Updated_Check.xlsx'
df.to_excel(output_path, index=False)
print(f'Excel file has been updated successfully! Saved to: {output_path}')
print(f'Final stats: Processed {processed_count}/{len(df)} URLs, API calls: {api_calls}')
print(f'Estimated total cost: ${api_calls * 0.002:.3f}')