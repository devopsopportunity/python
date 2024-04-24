# DevOps Opportunity - Search_data_google.py

import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import re

def extract_title_keywords(titles):
    # Dictionary to count keywords
    keyword_counts = {}

    # Loop through titles and add keywords to dictionary
    for title in titles:
        # Tokenize words in title
        tokens = word_tokenize(title.lower())
        
        # Remove stop words
        filtered_tokens = [word for word in tokens if word not in stopwords.words('italian')]
        
        # Count keywords
        for word in filtered_tokens:
            if word.isalpha() and len(word) > 1:  # Check if it's a word and has length greater than 1
                keyword_counts[word] = keyword_counts.get(word, 0) + 1
    
    # Return top 10 most common keywords
    return sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
# Function to extract additional information from a webpage
def extract_additional_info(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract meaningful text using BeautifulSoup
            target_tags = ['p']
            text_elements = soup.find_all(target_tags)
            additional_info = '\n'.join(element.get_text(strip=True) for element in text_elements)
            
            if additional_info:
                # Tokenize text
                tokens = word_tokenize(additional_info)
                
                # Remove stop words
                stop_words = set(stopwords.words('italian'))
                filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
                
                # Clean words using regular expressions
                cleaned_tokens = [word for word in filtered_tokens if re.match(r'^\w+$', word)]
                
                # Word frequency
                fdist = FreqDist(cleaned_tokens)
                
                # Return most common words
                return fdist.most_common(10)
            else:
                return "No additional information found"
        else:
            return "Unable to access the page"
    except Exception as e:
        return "Error accessing the page: " + str(e)
                
# Function to perform detailed search and save found information to a notepad file
def detailed_search_and_save(query):
    params = {
        "q": query,
        "hl": "en",
        "gl": "uk",
        "start": 0,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }

    page_limit = 10
    page_num = 0

    data = []

    try:
        while True:
            page_num += 1
            print(f"page: {page_num}")

            html = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)
            soup = BeautifulSoup(html.text, 'lxml')

            for result in soup.select(".tF2Cxc"):
                title = result.select_one(".DKV0Md").text
                snippet = result.select_one(".lEBKkf span").text if result.select_one(".lEBKkf span") else None
                links = result.select_one(".yuRUbf a")["href"]

                # Check if URL ends with ".pdf"
                if links.endswith(".pdf"):
                    print(f"Skipping PDF link: {links}")
                    continue

                print("Opening site:", links)  # Add log to indicate site opening
                additional_info = extract_additional_info(links)  # Extract additional information from the page
                
                if additional_info:
                    data.append({
                        "title": title,
                        "additional_info": additional_info,
                        "links": links
                    })
                
            # stop loop due to page limit condition
            if page_num == page_limit:
                break
            # stop the loop on the absence of the next page
            if soup.select_one(".d6cvqb a[id=pnnext]"):
                params["start"] += 10
            else:
                break

        return data

    except Exception as e:
        print("Error performing detailed search and saving information:", e)
        return []

# Perform detailed search and save information
query = "business on eco-friendly pet products"
data = detailed_search_and_save(query)

if data:
    # Extract page titles from the result list
    titles = [item["title"] for item in data]
    
    # Extract keywords from titles
    title_keywords = extract_title_keywords(titles)
    
    # Save results to notepad file
    with open('notes.txt', 'w') as file:
        file.write("Business search on eco-friendly pet products:\n\n")
        
        # Write extracted keywords from titles
        file.write("-" * 50 + "\n")
        file.write("Most common keywords from titles:\n")
        for keyword, freq in title_keywords:
            file.write(f"{keyword}: {freq}\n")
        file.write("-" * 50 + "\n\n")
        
        # Write page details
        for item in data:
            file.write("-" * 50 + "\n")
            file.write("Page Title: " + item["title"] + "\n")
            file.write("-" * 50 + "\n")
            file.write("Most common words:\n")
            for entry in item["additional_info"]:
                # Check if the word has length greater than 1 character
                if len(entry[0]) > 1:
                    file.write(f"{entry[0]}: {entry[1]}\n")
            file.write("-" * 50 + "\n")
            file.write("Page URL: " + item["links"] + "\n\n")
else:
    print("No data available. Check for any errors during search execution.")
