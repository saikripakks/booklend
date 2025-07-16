from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('books/', BookListView.as_view()),
    path('books/add/', AddBookView.as_view()),
    path('return/<int:pk>/', ReturnBookView.as_view()),
    path('borrowed/', UserBorrowedBooksView.as_view()),
    path('recommend/', RecommendBooksView.as_view()),
    path('books/recommend/', recommend_books),
    path('books/borrow/<int:book_id>/', BorrowView.as_view()),
    path('books/genres/', GenreListView.as_view(), name='genre-list'),
    path('books/authors/', AuthorListView.as_view(), name='author-list'),
    path('user/read-stats/', UserReadStatsView.as_view()),
    path('auth/me/', CurrentUserView.as_view()),


]