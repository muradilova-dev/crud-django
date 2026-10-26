from django.test import TestCase
from django.urls import reverse

from .models import Item


class ItemModelTests(TestCase):
    """Тесты модели Item."""

    # __str__ возвращает название
    def test_str_returns_title(self):
        item = Item.objects.create(title='Заметка', description='Текст')
        self.assertEqual(str(item), 'Заметка')

    # get_absolute_url ведёт на детальную страницу
    def test_get_absolute_url(self):
        item = Item.objects.create(title='Заметка')
        self.assertEqual(item.get_absolute_url(), reverse('crud:detail', args=[item.pk]))


class ItemListTests(TestCase):
    """Тесты списка записей (Read - список)."""

    # Страница списка открывается и использует нужный шаблон
    def test_list_returns_200_and_template(self):
        response = self.client.get(reverse('crud:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crud/item_list.html')

    # Созданные записи видны в списке
    def test_list_shows_items(self):
        Item.objects.create(title='Первая')
        Item.objects.create(title='Вторая')
        response = self.client.get(reverse('crud:list'))
        self.assertContains(response, 'Первая')
        self.assertContains(response, 'Вторая')
        self.assertEqual(len(response.context['items']), 2)

    # Пустой список показывает заглушку
    def test_list_empty(self):
        response = self.client.get(reverse('crud:list'))
        self.assertContains(response, 'Записей пока нет.')


class ItemDetailTests(TestCase):
    """Тесты детальной страницы (Read - одна запись)."""

    def setUp(self):
        self.item = Item.objects.create(title='Заметка', description='Описание заметки')

    # Детальная страница показывает данные записи
    def test_detail_shows_item(self):
        response = self.client.get(reverse('crud:detail', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Заметка')
        self.assertContains(response, 'Описание заметки')

    # Несуществующий id даёт 404
    def test_detail_404(self):
        response = self.client.get(reverse('crud:detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class ItemCreateTests(TestCase):
    """Тесты создания записи (Create)."""

    # Форма создания открывается
    def test_create_form_opens(self):
        response = self.client.get(reverse('crud:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crud/item_form.html')

    # POST с корректными данными создаёт запись и делает редирект на detail
    def test_create_valid_post(self):
        response = self.client.post(reverse('crud:create'), {'title': 'Новая', 'description': 'Текст'})
        item = Item.objects.get(title='Новая')
        self.assertRedirects(response, reverse('crud:detail', args=[item.pk]))
        self.assertEqual(Item.objects.count(), 1)

    # POST без названия не создаёт запись и показывает ошибку формы
    def test_create_invalid_post(self):
        response = self.client.post(reverse('crud:create'), {'title': '', 'description': 'Текст'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('title', response.context['form'].errors)
        self.assertEqual(Item.objects.count(), 0)


class ItemUpdateTests(TestCase):
    """Тесты изменения записи (Update)."""

    def setUp(self):
        self.item = Item.objects.create(title='Старое', description='Старый текст')
        self.url = reverse('crud:update', args=[self.item.pk])

    # Форма изменения открывается и уже заполнена данными записи
    def test_update_form_is_prefilled(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Старое')

    # POST меняет данные записи в базе
    def test_update_valid_post(self):
        response = self.client.post(self.url, {'title': 'Новое', 'description': 'Новый текст'})
        self.assertRedirects(response, reverse('crud:detail', args=[self.item.pk]))
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, 'Новое')
        self.assertEqual(self.item.description, 'Новый текст')

    # Изменение несуществующей записи даёт 404
    def test_update_404(self):
        response = self.client.get(reverse('crud:update', args=[9999]))
        self.assertEqual(response.status_code, 404)


class ItemDeleteTests(TestCase):
    """Тесты удаления записи (Delete)."""

    def setUp(self):
        self.item = Item.objects.create(title='Удаляемая')
        self.url = reverse('crud:delete', args=[self.item.pk])

    # Страница подтверждения удаления открывается
    def test_delete_confirm_page_opens(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Удаляемая')

    # GET-запрос запись не удаляет, она удаляется только по POST
    def test_delete_get_does_not_delete(self):
        self.client.get(self.url)
        self.assertEqual(Item.objects.count(), 1)

    # POST удаляет запись и возвращает на список
    def test_delete_post_removes_item(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('crud:list'))
        self.assertEqual(Item.objects.count(), 0)

    # Удаление несуществующей записи даёт 404
    def test_delete_404(self):
        response = self.client.post(reverse('crud:delete', args=[9999]))
        self.assertEqual(response.status_code, 404)
