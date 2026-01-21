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

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        books = [Book(b['id'], b['name']) for b in data['books']]
        chapters = [Chapter(c['id'], c['title'], c['pages'], c['book_id'])
                    for c in data['chapters']]
        chapters_books = [ChapterBook(cb['book_id'], cb['chapter_id'])
                          for cb in data['chapters_books']]

        return books, chapters, chapters_books
    except FileNotFoundError:
        print(f"Ошибка: Файл {filename} не найден.")
        return [], [], []

def main():
    # Загружаем данные
    books, chapters, chapters_books = load_data('data.json')

    if not books:
        return

    # 1. Соединение данных один-ко-многим [cite: 103]
    one_to_many = [(c.title, c.pages, b.name)
                   for b in books
                   for c in chapters
                   if c.book_id == b.id]

    # 2. Соединение данных многие-ко-многим [cite: 108, 109, 113, 114]
    many_to_many_temp = [(b.name, cb.book_id, cb.chapter_id)
                         for b in books
                         for cb in chapters_books
                         if b.id == cb.book_id]

    many_to_many = [(c.title, c.pages, book_name)
                    for book_name, book_id, chapter_id in many_to_many_temp
                    for c in chapters if c.id == chapter_id]

    print('Задание Г1')
    res_1 = [(b_name, c_title)
             for c_title, _, b_name in one_to_many
             if b_name.startswith('А')]
    print(res_1)

    print('\nЗадание Г2')
    res_2_unsorted = []
    for b in books:
        b_chapters = list(filter(lambda i: i[2] == b.name, one_to_many))
        if len(b_chapters) > 0:
            b_pages = [pages for _, pages, _ in b_chapters]
            res_2_unsorted.append((b.name, max(b_pages)))

    res_2 = sorted(res_2_unsorted, key=itemgetter(1), reverse=True)
    print(res_2)

    print('\nЗадание Г3')
    res_3 = sorted(many_to_many, key=itemgetter(2))
    print(res_3)

if __name__ == '__main__':
    main()