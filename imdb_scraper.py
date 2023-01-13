from bs4 import BeautifulSoup
import requests_cache
from PIL import Image
import io
from dataclasses import dataclass
from enum import Enum

class ItemType(Enum):
    MOVIE=0
    TV_SHOW=1

@dataclass
class Retrieved_item:
    name: str
    movie_or_show: ItemType
    plot: str
    cast: list[str]
    director: str
    writers: list[str]

IMDB_URL = 'https://www.imdb.com'
QUERY_URL = '/find/?q='

def download_image(url, session):
    response = session.get(url, stream=True)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
    return image

class NoSearchResultException(Exception):
    pass

class IMDB_scraper:
    def __init__(self) -> None:
        self.headers = {'Accept-Language': 'en-US,en;q=0.8', 
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        
        self.session = requests_cache.CachedSession('http_cache')
    
    def scrape_from_query(self, query):
        first_result_url = self.__get_first_result_url(query)
        response = self.session.get(first_result_url, headers=self.headers)
        item, photos = self.__scrape_page(response.text)
        item.name = query

        return item, photos

    def __scrape_page(self, html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        name = self.__get_name(soup)
        plot = self.__get_plot(soup)
        director, cast, writers = self.__get_cast(soup)
        show_type = self.__get_type(soup)
        photos = self.__get_photos(soup)
        
        return Retrieved_item(name, show_type, plot, cast, director, writers), photos
    
    def __get_photos(self, soup):
        DIV_CLASS = 'ipc-media--photo-m'
        TO_COLLECT = 2
        def collect_links(soup):
            collected = 0
            links = []
            for div in soup.find_all('div'):
                if div.has_attr('class')  and DIV_CLASS in div['class']:
                    collected += 1
                    links.append(div.img['src'])
                    if collected == TO_COLLECT: break
            return links
        links = collect_links(soup)
        photos = []
        for link in links:
            photos.append(download_image(link, self.session))

        return photos

    
    def __get_name(self, soup):
        for header in soup.find_all('h1'):
            if header.has_attr('data-testid')\
               and header['data-testid'] == 'hero-title-block__title':
               return header.getText()
        return ''
        
    def __get_plot(self, soup):
        for paragraph in soup.body.find_all('p'):
            if paragraph.has_attr('data-testid')\
               and paragraph['data-testid'] == 'plot':
                return paragraph.span.getText()
        return ''
    
    def __get_cast(self, soup):
        cast = []
        writers = []
        director = ''
        items_found = 0
        for list_tag in soup.body.find_all('li'):
            if not(list_tag.has_attr('data-testid')\
               and list_tag['data-testid'] == 'title-pc-principal-credit'):
               continue
            if list_tag.button and list_tag.button.getText() == 'Director':
                items_found += 1
                director = list_tag.div.ul.a.getText()
            elif list_tag.button and list_tag.button.getText() == 'Writers':
                items_found += 1
                for sublist_tag in list_tag.div.ul.find_all('li'):
                    writers.append(sublist_tag.a.getText())
            elif list_tag.a and list_tag.a.getText() == 'Stars':
                items_found += 1
                for sublist_tag in list_tag.div.ul.find_all('li'):
                    cast.append(sublist_tag.a.getText())
            if items_found == 3: break
            
        return director, cast, writers

    def __get_first_result_url(self, query):
        response = self.session.get(IMDB_URL + QUERY_URL + query + '&ref_=nv_sr_sm', headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.body.find_all('a'):
            
            if link.has_attr('class') and link['class'][0] == 'ipc-metadata-list-summary-item__t':
                
                return IMDB_URL + link['href']
        raise NoSearchResultException(f'no result for: {query}')

    def __get_type(self, soup):
        return ItemType.MOVIE

