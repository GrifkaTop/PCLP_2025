import json
from operator import itemgetter

class Chapter:
    def __init__(self, id, title, pages, book_id):
        self.id = id
        self.title = title
        self.pages = pages
        self.book_id = book_id

class Book:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class ChapterBook:
    def __init__(self, book_id, chapter_id):
        self.book_id = book_id
        self.chapter_id = chapter_id

# Логика запросов, вынесенная для тестирования
def query_g1(books, chapters):
    """Список книг на 'А' и их глав (один-ко-многим)"""
    one_to_many = [(c.title, b.name) for b in books for c in chapters if c.book_id == b.id]
    return [(b_name, c_title) for c_title, b_name in one_to_many if b_name.startswith('А')]

def query_g2(books, chapters):
    """Книги и макс. страницы в их главах (один-ко-многим)"""
    res = []
    for b in books:
        b_chapters_pages = [c.pages for c in chapters if c.book_id == b.id]
        if b_chapters_pages:
            res.append((b.name, max(b_chapters_pages)))
    return sorted(res, key=itemgetter(1), reverse=True)

def query_g3(books, chapters, chapters_books):
    """Связи многие-ко-многим, сортировка по книгам"""
    many_to_many_temp = [(b.name, cb.chapter_id) for b in books for cb in chapters_books if b.id == cb.book_id]
    res = [(c.title, book_name) for book_name, c_id in many_to_many_temp for c in chapters if c.id == c_id]
    return sorted(res, key=itemgetter(1))

def main():
    pass

if __name__ == '__main__':
    main()