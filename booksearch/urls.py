from django.urls import path
from . import views

urlpatterns = [
    # 検索アプリのトップページと検索ページのpath
    path('search/', views.Search_books, name='search-books'),  # 検索ページ
    path('', views.Search_books, name='search'),  # 最初のページ（/）をSearch_booksビューに設定
    path('book/<str:book_id>/', views.Book_detail, name='detail-books'),  # 詳細ページのURL
    # お気に入りページの追加と削除
    path('remove_from_favorites/<str:google_book_id>/', views.RemoveFavorites, name='remove-from-favorites'),
    path('add_to_favorites/<str:google_book_id>/', views.AddFavorites, name='add_to_favorites'),
    path('favorites/', views.FavoriteList, name='favorite_list'),
]
