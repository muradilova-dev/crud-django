from django.test import TestCase
from django.urls import reverse

from .models import Blog


class BlogListViewTests(TestCase):
    """Тесты страницы со списком статей (List)."""

    def setUp(self):
        self.blog1 = Blog.objects.create(title='Первая статья', content='Текст первой статьи')
        self.blog2 = Blog.objects.create(title='Вторая статья', content='Текст второй статьи')
        self.url = reverse('blog:list')

    # 1. Страница открывается и отдаёт код 200
    def test_list_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # 2. Используется правильный шаблон
    def test_list_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'blog/blog_list.html')

    # 3. Контент есть: заголовки статей выводятся на странице
    def test_list_contains_titles(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Первая статья')
        self.assertContains(response, 'Вторая статья')

    # 4. Получаем id: в контексте есть все статьи и у каждой есть pk
    def test_list_context_has_blogs_with_ids(self):
        response = self.client.get(self.url)
        blogs = response.context['blogs']
        self.assertEqual(len(blogs), 2)
        pks = [b.pk for b in blogs]
        self.assertIn(self.blog1.pk, pks)
        self.assertIn(self.blog2.pk, pks)
        self.assertTrue(all(pk is not None for pk in pks))

    # 5. Ссылки на странице ведут на detail каждой статьи
    def test_list_contains_links_to_detail(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse('blog:detail', args=[self.blog1.pk]))
        self.assertContains(response, reverse('blog:detail', args=[self.blog2.pk]))

    # 6. Переход по ссылке из списка реально открывает статью
    def test_list_link_actually_opens_detail(self):
        detail_url = reverse('blog:detail', args=[self.blog1.pk])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Текст первой статьи')

    # 7. Контента нет: пустая база -> страница открывается, показывается заглушка
    def test_list_empty_database(self):
        Blog.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Статей пока нет.')
        self.assertEqual(len(response.context['blogs']), 0)


class BlogDetailViewTests(TestCase):
    """Тесты страницы одной статьи (Detail)."""

    def setUp(self):
        self.blog = Blog.objects.create(title='Тестовая статья', content='Содержимое статьи')
        self.url = reverse('blog:detail', args=[self.blog.pk])

    # 1. Существующая статья открывается (200)
    def test_detail_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # 2. Используется правильный шаблон
    def test_detail_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')

    # 3. Контент есть: заголовок и текст на странице
    def test_detail_contains_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Тестовая статья')
        self.assertContains(response, 'Содержимое статьи')

    # 4. Получаем нужный объект: id в контексте совпадает с запрошенным
    def test_detail_context_has_correct_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['blog'].pk, self.blog.pk)

    # 5. Несуществующий id -> 404
    def test_detail_nonexistent_id_returns_404(self):
        response = self.client.get(reverse('blog:detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    # 6. Разные статьи показывают разный контент (не путаются между собой)
    def test_detail_different_blogs_show_different_content(self):
        other = Blog.objects.create(title='Другая статья', content='Другой текст')
        response = self.client.get(reverse('blog:detail', args=[other.pk]))
        self.assertContains(response, 'Другая статья')
        self.assertNotContains(response, 'Тестовая статья')

    # 7. Ссылка "Назад к списку" на странице ведёт в список и он открывается
    def test_detail_back_link_works(self):
        response = self.client.get(self.url)
        list_url = reverse('blog:list')
        self.assertContains(response, list_url)
        self.assertEqual(self.client.get(list_url).status_code, 200)

    # 8. Неверный тип id в URL (не число) -> 404
    def test_detail_invalid_id_type_returns_404(self):
        response = self.client.get('/blog/abc/')
        self.assertEqual(response.status_code, 404)


class BlogLikesTests(TestCase):
    """Тесты счётчика лайков/просмотров."""

    def setUp(self):
        self.blog = Blog.objects.create(title='Статья для лайков', content='Текст')

    # Новый блог создаётся с нулём лайков
    def test_new_blog_has_zero_likes(self):
        self.assertEqual(self.blog.likes, 0)

    # После GET-запроса на detail лайки становятся равны 1
    def test_detail_view_increments_likes(self):
        self.client.get(reverse('blog:detail', args=[self.blog.pk]))
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.likes, 1)
