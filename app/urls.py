from django.urls import path
from .views import Catalog, CreateBook, DetailBook

urlpatterns = [
    path('', Catalog.as_view(), name='catalog'),
    path('add_book/', CreateBook.as_view(), name='add_book'),
    path('book/<int:id>/', DetailBook.as_view(), name='book'),
]