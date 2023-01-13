import os
from imdb_scraper import Retrieved_item, ItemType
from bs4 import BeautifulSoup
from PIL import Image
from dataclasses import dataclass

BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Scraped movies</title>
</head>
<body>


</body>
</html>
"""
@dataclass
class HTML_page:
    path: str
    html_doc: str

class HTML_generator:

    PAGES_DIR_NAME = 'pages'

    def __init__(self) -> None:
        html_doc = BASE_HTML
        self.soup = BeautifulSoup(html_doc, 'html.parser')
        self.pages: list[HTML_page] = []
    
    def add_item(self, item: Retrieved_item, photo_paths):
        page_path = f'{self.PAGES_DIR_NAME}/{item.name}.html'
        link = self.soup.new_tag('a', href=page_path)
        self.soup.body.append(link)
        if photo_paths:
            thumbnail = self.soup.new_tag('img',src=photo_paths[0])
            link.append(thumbnail)
        else:
            link.string = item.name

        new_page_html = self.__generate_page_html(item, photo_paths)
        self.pages.append(HTML_page(page_path, new_page_html))
    
    def get_main_page(self):
        return self.soup.decode()
    
    def __generate_page_html(self, item: Retrieved_item, paths):
        def add_image(soup, path):
            img = soup.new_tag('img')
            img['src'] = path
            soup.body.append(img)
        
        def add_paragraph(soup, content):
            paragraph = soup.new_tag('p')
            soup.body.append(paragraph)
            paragraph.string = content

        def add_heading(soup, type, content):
            heading = soup.new_tag('h' + type)
            soup.body.append(heading)
            heading.string = content           

        soup = BeautifulSoup(BASE_HTML, 'html.parser')
        add_heading(soup, '1', item.name)
        add_paragraph(soup, item.plot + '\n')
        add_heading(soup, '2', 'Director')
        add_paragraph(soup, item.director + '\n')
        add_heading(soup, '2', 'Cast')
        add_paragraph(soup, ' ; '.join(item.cast) + '\n')
        add_heading(soup, '2', 'Photos')
        for path in paths:
            add_image(soup, path)

        return soup.decode()
