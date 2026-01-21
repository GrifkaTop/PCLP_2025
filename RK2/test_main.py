import unittest
from main import Book, Chapter, ChapterBook, query_g1, query_g2, query_g3

class TestLibraryQueries(unittest.TestCase):
    def setUp(self):
        # Инициализация тестовых данных
        self.books = [
            Book(1, 'Алгоритмы'),
            Book(2, 'Базы данных')
        ]
        self.chapters = [
            Chapter(1, 'Введение', 10, 1),
            Chapter(2, 'Сложность', 50, 1),
            Chapter(3, 'SQL', 30, 2)
        ]
        self.chapters_books = [
            ChapterBook(1, 1),
            ChapterBook(2, 3)
        ]

    def test_query_g1(self):
        """Тест запроса №1: Книги на букву 'А'"""
        result = query_g1(self.books, self.chapters)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 'Алгоритмы')

    def test_query_g2(self):
        """Тест запроса №2: Максимальные страницы"""
        result = query_g2(self.books, self.chapters)
        # У 'Алгоритмов' макс страницы 50, у 'Баз данных' 30
        self.assertEqual(result[0], ('Алгоритмы', 50))
        self.assertEqual(result[1], ('Базы данных', 30))

    def test_query_g3(self):
        """Тест запроса №3: Многие-ко-многим"""
        result = query_g3(self.books, self.chapters, self.chapters_books)
        self.assertEqual(result[0][1], 'Алгоритмы')
        self.assertEqual(result[1][1], 'Базы данных')

if __name__ == '__main__':
    unittest.main()