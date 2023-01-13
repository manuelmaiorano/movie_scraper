import os
import json
from dataclasses import dataclass
from imdb_scraper import Retrieved_item
import pickle


@dataclass 
class Cached_item:
    item: Retrieved_item
    photo_paths: list[str]

class Item_cache:
    def __init__(self, name):
        self.name = name
        try:
            os.makedirs(f'{name}/img')
        except FileExistsError:
            pass
        if os.path.isfile(f'{name}/cached'):
            with open(f'{name}/cached', mode='rb') as file:
                retrieved_items = pickle.load(file)
        else:
            retrieved_items = {}
        
        self.retrieved_items = retrieved_items
    
    def add(self, query, item: Retrieved_item, images):
        
        paths = []
        dirname = os.path.dirname(__file__)
        for i, image in enumerate(images):
            path = f'{self.name}/img/{item.name}_{i}.jpg'
            absolute_path = os.path.join(dirname, path)
            image.save(absolute_path) 
            paths.append(absolute_path)
        
        cached_item = Cached_item(item, paths)

        self.retrieved_items[query] = cached_item

    def get_new_queries(self, queries, delete_old=False):
        cached_queries = self.retrieved_items.keys()
        queries_set = set(queries)
        new_queries = queries_set - cached_queries
        old_queries = cached_queries - queries_set
        if not delete_old: return list(new_queries), list(old_queries)

        def delete_from_paths(paths):
            for path in paths:
                if not os.path.exists(path): continue
                os.remove(path)

        for query in old_queries:
            cached_item = self.retrieved_items[query]
            delete_from_paths(cached_item.photo_paths)
            self.retrieved_items.pop(query)

        return list(new_queries), list(old_queries)

    def save(self):
        with open(f'{self.name}/cached', mode='wb') as file:
            pickle.dump(self.retrieved_items, file)