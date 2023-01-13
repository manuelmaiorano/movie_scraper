from imdb_scraper import IMDB_scraper, NoSearchResultException
from html_generator import HTML_generator
from item_cache import Item_cache
import os

def read_queries():
    queries = []
    with open('queries.txt') as file:
        for line in file:
            line = line.replace('\n', '').replace(':', '')
            queries.append(line)
    return queries

def store_website(index, other_pages):
    try:
        os.makedirs(f'htmldoc/{HTML_generator.PAGES_DIR_NAME}')
    except FileExistsError:
        pass
    
    with open('htmldoc/index.html', 'w') as file:
        file.write(index)

    for page in other_pages:
        with open(f'htmldoc/{page.path}', 'w') as file:
            file.write(page.html_doc)

if __name__ == '__main__':
    scraper = IMDB_scraper()
    html_generator = HTML_generator()
    queries = read_queries()

    cache = Item_cache('htmldoc')

    new_queries, old_queries = cache.get_new_queries(queries, delete_old=True)
    print(f'new: {len(new_queries)}')
    print(f'old: {len(old_queries)}')

    for query in new_queries:
        try:
            item, photos = scraper.scrape_from_query(query)
        except NoSearchResultException as exception:
            print(exception.args)
            continue
        cache.add(query, item, photos)
    
    for cached_item in cache.retrieved_items.values():
        html_generator.add_item(cached_item.item, cached_item.photo_paths)

    store_website(html_generator.get_main_page(), html_generator.pages)

    cache.save()
