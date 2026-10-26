from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import ItemForm
from .models import Item


class ItemListView(ListView):          # R - список
    model = Item
    context_object_name = 'items'


class ItemDetailView(DetailView):      # R - одна запись
    model = Item
    context_object_name = 'item'


class ItemCreateView(CreateView):      # C - создание
    model = Item
    form_class = ItemForm


class ItemUpdateView(UpdateView):      # U - изменение
    model = Item
    form_class = ItemForm


class ItemDeleteView(DeleteView):      # D - удаление
    model = Item
    context_object_name = 'item'
    success_url = reverse_lazy('crud:list')
