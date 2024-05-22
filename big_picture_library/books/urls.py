from django.urls import path
from . import views

urlpatterns = [
    path('isbn/<str:isbn>/', views.FetchBookDetailsView.as_view(), name='fetch_book_details'),
    path('books/', views.BookView.as_view(), name='book_view')
]
