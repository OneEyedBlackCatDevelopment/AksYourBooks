######################################################################
# Add PDF files to the index of a marqo database 
######################################################################


# pip install PyMuPDF
# pip install marqo


import fitz  # PyMuPDF
import json

from pymupdf.mupdf import PdfFontDesc



def read_pdf( entry_callback, pdf_path, source_type = "pdf" ):
    
    def get_breadcrumbs():
       crumbs_text = breadcrumbs[0]
       for i in range(1, len(breadcrumbs)):
            if( breadcrumbs[i] != "" ):
                crumbs_text += " > " +  str(breadcrumbs[i])
       return crumbs_text
   
    def create_pdf_page_link( pdf_path, page_number ):
        return( pdf_path ) + "#page=" + str(page_number) 

    breadcrumbs = [""] * 6;

    pdf_document = fitz.open(pdf_path)
    metadata =  pdf_document.metadata
    toc = pdf_document.get_toc()
    total_pages = pdf_document.page_count

    if metadata['title'] == "": 
        breadcrumbs[0] = pdf_path
    else:
        breadcrumbs[0] = metadata['author'] + " - " + metadata['title']

    for page_num in range(1, total_pages + 1):
        page = pdf_document.load_page(page_num - 1)  # Page numbers start from 0 in PyMuPDF
        breadcrumbs[5] = page_num
        text = page.get_text()

         # Check if the current page number matches any entry in the ToC
        for item in toc:
            level, title, toc_page_num = item
            if toc_page_num == page_num:
                indent = '  ' * (level - 1)
                breadcrumbs[level] = title
                print( get_breadcrumbs())
                
        if(text.strip() != "" ):
            
            entry = {
                        "_id": pdf_path + "/" + str(page_num),
                        "Title": metadata['title'],
                        "Author": metadata['author'], 
                        "Description": get_breadcrumbs(), #would be SE text for html
                        "Details": text,  
                        "Link" :  create_pdf_page_link( pdf_path, page_num ), # this does not work as ID for some reason
                        "Image_Url": "",
                        "Context": get_breadcrumbs(), 
                        "Type": source_type
                    }

            entry_callback( entry )



