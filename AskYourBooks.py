######################################################################
# This is a web front end to a marqo.ai database and OpenAI backend
#
# usage: python AskYourBooks.py
#        Open your browser at "http://localhost:8884" 
#        ... or whatever you are using as webserver_port 
#
######################################################################

from re import L
from flask import Flask, render_template, request # Webserver
import marqo # Database
import os # Operating System to get the API Key for ChatGPT
import warnings

#from langchain_openai import OpenAI
#from langchain.docstore.document import Document
#from langchain.chains import LLMChain
#from langchain.prompts import PromptTemplate

from openai import OpenAI
from openai.resources.audio import translations


app = Flask(__name__)

db_client_url = "http://localhost:8882"
db_index_name = "eBooks"
webserver_port = 8884
llm_model = "gpt-4o"

######################################################################################
def qna_prompt(summaries, question):
    """ 
    Prompt template for Q and A type answering.
    """

    template = """Given the following extracted parts of a long document ("SOURCES") and a question ("QUESTION"), create a final answer one paragraph long. 
    Don't try to make up an answer and use the text in the "SOURCES" only for the answer. Refer to the "SOURCES" in your answer. If you enumerate them, start with 1. 
    If you don't know the answer, just say that you don't know. Allways reply in the languge of the "QUESTION".
    QUESTION: {question}
    =========
    SOURCES:
    {summaries}
    =========
    ANSWER:"""
    
    # Using f-string to format the template with the given summaries and question
    PROMPT = template.format(question=question, summaries=summaries)
    
    return PROMPT


######################################################################################
def query_translation_prompt( query, languages):
    """ 
    prompt template for tranlating a query
    """

    template = """You will get a query in any languge and a given list of languages. 
        Please reply only with the translation of the query in the given languages in the format <language>: <tranlation>

        QUERY: {query}
        LANGUAGES: {languages}"""
        

    PROMPT = template.format(query=query, languages=languages)
    return PROMPT


######################################################################################
def search_function(query):
    error_message = ""
    try:
        results = mq.index(db_index_name).search(q=query, limit=13)
        return results["hits"], ""
    except Exception as e:
        error_message = f"""<h4>Database Error: Could not connect to Marqo at <tt>'{db_client_url}'</tt> using index <tt>'{db_index_name}'</tt>.</h4>
        Possible solutions:<br>
        <tt>
        - Ensure Docker is running.<br>
        - Ensure the Marqo container is running and configured for '{db_client_url}'.<br>
        - Index your eBooks using the index name '{db_index_name}'.<br><br>
        </tt>
        This is the error message:<br><tt>{e}</tt>"""
        print(error_message)
       
    return [], error_message

######################################################################################
def create_ai_summary( texts, query ):
    error_message = ""
    summarized_text = ""
    
    if( texts ):
        try:
            docs = [{"text": f"Source [{ind+1}]:" + t} for ind, t in enumerate(texts)]
            prompt = qna_prompt( summaries='\n'.join([doc['text'] for doc in docs]), question=query)
            
            chat_completion = llm.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=llm_model,
            )

            summarized_text = chat_completion.choices[0].message.content
            

        except Exception as e:
            error_message = f"""<h4>Something went wrong with the AI summary</h4>
            This is the error message:<br><tt>{e}</tt>"""
            print(error_message)
    else:
        error_message = "Nothing to summerize."    
    return summarized_text, error_message


######################################################################################
def translate_query(query, languages):
    error_message = "" 
    query_list = [query]
    
    if languages.strip() != "" and query.strip() != "":
        try:
            prompt = query_translation_prompt(query=query, languages=languages)
            chat_completion = llm.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=llm_model,
            )

            answere = chat_completion.choices[0].message.content
            
            if answere: 
                # Get the translated queries
                lines = answere.splitlines()
                query_list = [line.split(": ", 1)[1] for line in lines if ": " in line]

            print("Splitted translations: ")
            print(query_list)
            
        except Exception as e:
            error_message = f"""<h4>Something went wrong with the AI translation</h4>
            This is the error message:<br><tt>{e}</tt>"""
            print(error_message)

    return query_list, error_message



######################################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query_list = []
    query=""
    error_message = ""
    summarized_text=""
    summary_disclaimer= ""
    languages_input = ""
    
    
    if request.method == 'POST':
        query = request.form['query']
        languages_input = request.form['languages']
        
        if query:
                
            query_list, error_message = translate_query( query, languages_input) 
        
            for q in query_list:
                results_part, error_message = search_function(q)
    
                # Check if there is an error message
                if error_message:
                    print(f"Error: {error_message}")
                else:
                    results.extend(results_part)

            results = sorted(results, key=lambda x: x['_score'], reverse=True)


            if results:      
                texts = []
                
                try:
                    # texts = [f"Title: {result['Title']}\nHighlights: {result['_highlights'][0]['Details']}\nContext: {result['Context']}\nLink: {result['Link']}\nDetails: {result['Details']}\n" for result in results]
                    texts = [f"Title: {result['Title']}\nHighlights: {result['_highlights'][0]['Details']}\nContext: {result['Context']}\nLink: {result['Link']}\n" for result in results]
                except Exception as e:
                    error_message = f"""<h4>You got some search results from <tt>'{db_client_url}'</tt> using index <tt>'{db_index_name}'</tt>, but they don't match the expected format.</h4>
                    Possible solutions:<br>
                    <tt>
                    - Delete index: '{db_index_name}'.<br>
                    - Index your eBooks using the index name '{db_index_name}'.<br><br>
                    </tt>
                    This is the error message:<br><tt>{e}</tt>"""
                    print(error_message)
                

                if(texts): #create AI sumary
                    summarized_text, error_message = create_ai_summary( texts=texts,query=query) # This costs money
                    if summarized_text != "":  # if an AI summery was created add an disclaimer
                        summary_disclaimer = "&#x26A0; This is an AI summary. It might not reflect the intention of the sources or may be just plain wrong. &#x26A0;"
        

               
                for result in results: # format results for html display
                    if "_highlights" in result:
                        for highlight in result["_highlights"]:
                            for key in highlight:
                                if isinstance(highlight[key], str):  # Ensure the value is a string
                                    highlight[key] = highlight[key].replace("\n", "<br>") #for html display
   
   
    
    return render_template('index.html', 
                           results=results, 
                           query=query, 
                           summarized_text=summarized_text, 
                           summary_disclaimer=summary_disclaimer, 
                           translations = query_list, 
                           error_message=error_message )



######################################################################################
if __name__ == '__main__':
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    mq = marqo.Client(url=db_client_url) # Initialize Marqo Database client 
 

    # ### Set OPENAI_API_KEY in OS environment variables ###
    
    OpenAI_key = os.environ.get("OPENAI_API_KEY").strip()
    
    if( OpenAI_key == "" ):
        warnings.warn("""
        WARNING:You are using an empty string as OpenAI API key. This might not work.
        """, UserWarning)
    

    llm = OpenAI( api_key=OpenAI_key ) 
    
    #llm = OpenAI(temperature=0.9, openai_api_key=OpenAI_key) #low temperature makes it less "creative"

    app.run(host='0.0.0.0', debug=False, port=webserver_port)
