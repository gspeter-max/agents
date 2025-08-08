from bs4 import BeautifulSoup 
import requests 
from langchain_core.docume  nts import Document 
from typing import List 

class get_url_data:
    def __init__( self, web_urls = ['https://en.wikipedia.org/wiki/Large_language_model'] ):
        self.web_urls = web_urls if isinstance(web_urls, list ) else [web_urls]

    def start_extracting_data(self, ReturnLangchainDocFormat : bool = False ):
        document_list = []
        for url in self.web_urls:
            response = requests.get(url)
            soup = BeautifulSoup( response.text, 'html.parser')
            
            text = '' 
            for value in soup.select('p'):
                text += value.getText(strip = True)

            if ReturnLangchainDocFormat is True:
                text = Document( page_content = text, metadata = {'source' : 'localsource'} ) 

            document_list.append(text) 
        return document_list
    
    def split_document( self , docs : List ):
        
web = get_url_data()
web.get_urls_data()

