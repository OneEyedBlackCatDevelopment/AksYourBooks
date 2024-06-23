######################################################################
# This is a web front end to a marqo.ai database and OpenAI backend
#
# usage: python AskYourBooks.py
#        Open your browser at "http://localhost:8884" 
#        ... or whatever you are using as webserver_port 
#
######################################################################




#from ftplib import error_perm
from flask import Flask, render_template, request # Webserver
import marqo # Database
import os # Operating System to get the API Key for ChatGPT
import warnings

from langchain_openai import OpenAI
from langchain.docstore.document import Document
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate




app = Flask(__name__)

db_client_url = "http://localhost:8882"
db_index_name = "agile"
webserver_port = 8884

######################################################################################
def qna_prompt():
    """ 
    prompt template for q and a type answering
    """

    template = """Given the following extracted parts of a long document ("SOURCES") and a question ("QUESTION"), create a final answer one paragraph long. 
    Don't try to make up an answer and use the text in the SOURCES only for the answer. Refere to the SOURCES in your answer.
    If you don't know the answer, just say that you don't know. 
    QUESTION: {question}
    =========
    SOURCES:
    {summaries}
    =========
    ANSWER:"""
    PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])
    return PROMPT

######################################################################################
def search_function(query):
    error_message = ""
    try:
        results = mq.index(db_index_name).search(q=query, limit=15)
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
            docs = [{"text": f"Source [{ind}]:" + t} for ind, t in enumerate(texts)]
            prompt = qna_prompt().format(summaries='\n'.join([doc['text'] for doc in docs]), question=query)
            chain_qa = LLMChain(llm=llm, prompt=qna_prompt())
            llm_results = chain_qa.invoke({"summaries": docs, "question": query }, return_only_outputs=True)
            summarized_text = llm_results['text']
        except Exception as e:
            error_message = f"""<h4>Something went wrong with the AI summary</h4>
            This is the error message:<br><tt>{e}</tt>"""
            print(error_message)
    else:
        error_message = "Nothing to summerize."    
    return summarized_text, error_message

######################################################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query=""
    error_message = ""
    summarized_text=""
    summary_disclaimer= ""
    
    if request.method == 'POST':
        query = request.form['query']

        if query:

            results, error_message = search_function(query)
       

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
                    #summarized_text = "AI summery was deactivated because it costs money!"
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
                           error_message=error_message )



######################################################################################
if __name__ == '__main__':
    
    # # Initialize Marqo Database client 
    mq = marqo.Client(url=db_client_url)
 

    # ### Set OPENAI_API_KEY in OS environment variables
    
    #OpenAI_key = os.environ.get("OPENAI_API_KEY")
    OpenAI_key = "" #For some reason chat_gpt works without API key for now. This might change. 
    
    if( OpenAI_key == "" ):
        print( "WARNING: You are using an empty string as OpenAI API key. This might not work.\n" )
        warnings.warn("You are using an empty string as OpenAI API key. This might not work.\n", UserWarning)
        
    
    llm = OpenAI(temperature=0.9, openai_api_key=OpenAI_key)

    
    app.run(debug=False, port=webserver_port)
