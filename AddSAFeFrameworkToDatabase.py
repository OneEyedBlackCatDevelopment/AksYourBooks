import json
from tokenize import String
from bs4 import BeautifulSoup
import requests
import marqo

FRAMEWORK = "Scaled Agile Framework (SAFe)"
FRAMEWORK_VERSION = "6.0"
ROOT_LINK = "https://scaledagileframework.com/"


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/50.0.2661.102 Safari/537.36'
    }

index_name = "eBooks"
db_url = "http://localhost:8882"


# Function to fetch HTML content from a URL
def fetch_html_content(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the URL: {url}, Status Code: {response.status_code}")
        return None
    return response.text


def parse_SAFe_glossary( entry_callback, page_url ):
    
    html_content = fetch_html_content(page_url, headers) 
    if not html_content:
        return
    
    
    soup = BeautifulSoup(html_content, 'html.parser')
    documents = []

    item_count = 0;
    for item in soup.find_all('li'):
        title_tag = item.find('h3')
        description_tag = item.find('p', class_='content')

        if title_tag:# and description_tag:
            title = title_tag.get_text(strip=True)
            print( title )
           
            link_tag = title_tag.find('a')
            if link_tag:
                article_url = "https://scaledagileframework.com" + link_tag.get('href')
                parse_SAFe_article( entry_callback, article_url, "Framework" )
            else: 
                 entry = {
                    "_id": FRAMEWORK + " > Glossary > " + title,
                    "Title": title,
                    "Description": description_tag.get_text(strip=True),
                    "Framework" : FRAMEWORK,
                    "Framework_Version" : FRAMEWORK_VERSION,
                    "Context": FRAMEWORK + " " + FRAMEWORK_VERSION + " > Glossary > " + title, 
                    "Type": "Glossary",
                    "Link": page_url
                    }
                 entry_callback( entry )
                 
            
            

            # item_count = item_count + 1
            # if item_count > 15:
            #      break
    return 


def parse_SAFe_extended( entry_callback, page_url ):
    
    html_content = fetch_html_content(page_url, headers)
 
    if not html_content:
        return
    
    
    soup = BeautifulSoup(html_content, 'html.parser')
    documents = []

    item_count = 0;
    glossary = soup.find('div', class_='glossary')
    
    for item in glossary.find_all('li'):
        link_tag = item.find('a')
        

        if link_tag:# and description_tag:
            title = link_tag.get_text(strip=True)
            print( title )
           
            if link_tag:
                article_url = link_tag.get('href')
                parse_SAFe_article( entry_callback, article_url, "Framework Extended" )
            
            

            # item_count = item_count + 1
            # if item_count > 15:
            #      break
           
    return 



def parse_SAFe_principles( entry_callback, page_url ):
    
    html_content = fetch_html_content( page_url, headers)
    if not html_content:
        return
    
    
    soup = BeautifulSoup(html_content, 'html.parser')
    documents = []

    item_count = 0;
    for title_tag in soup.find_all('h2'):
        link_tag = title_tag.find('a')

        if title_tag and link_tag:

            print( link_tag.get_text(strip=True) )

            article_url = "https://scaledagileframework.com" + link_tag.get('href')
            parse_SAFe_article( entry_callback, article_url, "Framework Principle" )
    
           
    return 



def parse_SAFe_article( entry_callback, url, article_type = "Article" ):
    html_content = fetch_html_content(url, headers)
    if not html_content:
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    
    if soup.title:
        title = soup.title.string
        meta_description_tag =  soup.find('meta', property='og:description')
        meta_image_tag = soup.find('meta', property='og:image')
    
        image_url = "";
        if meta_image_tag:
             image_url = meta_image_tag.get('content')

        entry = {
                    "_id": url,
                    "Title": title,
                    "Description": meta_description_tag.get('content'),
                    "Details": '\n'.join(SAFe_article_content_to_text(soup)),  
                    "Framework" : FRAMEWORK,
                    "Framework_Version" : FRAMEWORK_VERSION,
                    "Link" : url, 
                    "Image_Url": image_url,
                    "Context": FRAMEWORK + " " + FRAMEWORK_VERSION + " > " + title,
                    "Type": article_type
                }


     
        parse_SAFe_article_get_quote( entry_callback, entry, soup )
        entry_callback( entry )
    
    return


def parse_SAFe_article_get_quote( entry_callback, artice_entry,  soup ):

    blockquote = soup.find('blockquote')
    if blockquote:
        
        quote_context = "Quote for " + artice_entry["Title"]
        quote_text = "".join(blockquote.get_text(strip=True)) #if there are no p-tag in the quote 
        
        entry = {}

       
        entry["_id"] =  FRAMEWORK + " > " + quote_context
        entry["Title"] =  quote_text
        entry["Description"] =  quote_text + "\n - " + quote_context
        entry["Context"] =  FRAMEWORK + " " + FRAMEWORK_VERSION + " > " + quote_context
        entry["Type"] = "Quote"
        entry["Link"] = artice_entry["Link"]

        entry_callback(entry)
   
    return 


# Function to check if an element is visible
def is_visible(element):
    if element is None or element.parent is None:
        return False
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, str):
        return True
    if element.has_attr('style') and ('display:none' in element['style'] or 'visibility:hidden' in element['style']):
        return False
    if 'hidden' in element.get('class', []):
        return False
    return True

def SAFe_article_content_to_text( soup ):
    
    h1_element = soup.find('h1')
    
    # Find the first <h1> element with non-empty text
    while h1_element and not h1_element.get_text(strip=True):
        h1_element = h1_element.find_next('h1')

       # If no valid <h1> is found, return empty list
    if not h1_element:
        return []

    # Initialize variables to collect text
    extracted_texts = []

    # Add the H1 text at the beginning
    #extracted_texts.append(h1_element.get_text().strip())

    # Traverse through all elements after the <h1> element
    for element in h1_element.find_all_next(string=True):
        if 'Last update' in element or 'Last Update' in element or 'Download SAFe Posters' in element or 'entry-content' in element:
            break

        parent = element.parent
        if is_visible(parent) and is_visible(element):
            text = element.strip();
            if( text != "" ):
                extracted_texts.append(text)

    return extracted_texts


# Function to add a single document
def add_single_entry_to_index( entry ):
    mq.index(index_name).add_documents([entry], tensor_fields=["Details"])

index_settings = {
    "model": "flax-sentence-embeddings/all_datasets_v4_MiniLM-L6",
    "normalizeEmbeddings": True,
    "textPreprocessing": {
        "splitLength": 4,
        "splitOverlap": 1,
        "splitMethod": "sentence"
    },
}

# # Initialize Marqo client and create index if it doesn't exist
mq = marqo.Client(url=db_url)

entry_callback = add_single_entry_to_index

documents = parse_SAFe_principles( entry_callback, 'https://scaledagileframework.com/safe-lean-agile-principles/' )
documents = parse_SAFe_glossary( entry_callback, 'https://scaledagileframework.com/glossary/' )
documents = parse_SAFe_glossary( entry_callback, 'https://scaledagileframework.com/glossary?lang=de' )

documents = parse_SAFe_article( entry_callback, 'https://scaledagile.com/blog/solution-areas-a-more-dynamic-form-of-agility/', "Blog")
documents = parse_SAFe_article( entry_callback, 'https://scaledagile.com/blog/large-solution-refinement-paving-the-super-highway-of-value-delivery/',"Blog")

documents = parse_SAFe_extended( entry_callback,  'https://scaledagileframework.com/advanced-topics/community-contributions/')
documents = parse_SAFe_extended( entry_callback,  'https://scaledagileframework.com/advanced-topics/')
documents = parse_SAFe_extended( entry_callback,  'https://scaledagileframework.com/advanced-topics/extended-safe-guidance/')
