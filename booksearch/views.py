import requests  # HTTPリクエストを送るためのライブラリをインポート
from .models import Book, Favorite  # DBをインポート
from django.shortcuts import render, redirect  # Djangoのショートカット関数をインポート（renderはテンプレートの表示、redirectはリダイレクト）
from django.contrib.auth.decorators import login_required  # ログインしていないユーザーを制限するためのデコレーター
from django.contrib.auth.models import AnonymousUser  # 匿名ユーザーをチェックするためにインポート
from django.utils.timezone import now

# Google Books APIキー
API_KEY = "AIzaSyD5-MxY44zGd0aZ367o6ey8SCoZ4wCoZvI"  # Google Books APIを呼び出すためのキー


@login_required  # ログインユーザのみ
def AddFavorites(request, google_book_id):
    
    try:
        # 既にデータベースに登録されている本を取得
        book = Book.objects.get(google_book_id=google_book_id)
        print(f" 既存の本を取得: {book.title}")  # 確認用に本のタイトルを取得する
    except Book.DoesNotExist:  # 本がデータベースに存在しない場合
        print(f" 本がデータベースにない: {google_book_id}")  # データが取れているかの確認
        url = f"https://www.googleapis.com/books/v1/volumes/{google_book_id}?key={API_KEY}"  # Google Books APIのURLを作成
        response = requests.get(url)  # APIリクエストを送信
        if response.status_code == 200:  # レスポンスが正常の場合
            data = response.json()  # JSON形式でレスポンスを取得
            book_info = data.get("volumeInfo", {})  # 本の詳細情報を取り出す
            book = Book.objects.create(  # 新しい本をデータベースに追加
                google_book_id=google_book_id,
                title=book_info.get("title", "タイトル不明"),  # タイトルを取得
                authors=", ".join(book_info.get("authors", ["不明"])),  # 著者情報を取得
                description=book_info.get("description", "説明なし"),  # 説明部分を取得
                thumbnail=book_info.get("imageLinks", {}).get("thumbnail", ""),  # 画像を取得
            )
            print(f" 本をデータベースに追加: {book.title}")  # データが取れている確認
        else:
            print(" Google Books API から本を取得できなかった")  # APIから本を取得できなかった場合
            return render(request, 'booksearch/error.html', {'error': '本が見つかりませんでした。'})  # エラーページ

    # お気に入り登録
    favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)  # お気に入り登録を取得または新規作成
    if created: # ちゃんと取得できるか確認
        print(f" お気に入りに登録成功: {book.title}")
    else:
        print(f" すでにお気に入り登録済み: {book.title}") 

    return redirect(request.META.get('HTTP_REFERER', 'favorite_list'))  # 前のページにリダイレクト（リファラが無ければお気に入りリストページにリダイレクト）


# お気に入り一覧を表示するビュー
@login_required  
def FavoriteList(request):
    favorites = Favorite.objects.filter(user=request.user)  # 現在のユーザーのお気に入りを取得
    books = [favorite.book for favorite in favorites]  # お気に入りリストから本のオブジェクトを取得
    print(" お気に入り取得:", books)  # ちゃんと取得できているか確認
    return render(request, 'books/favorite.html', {'books': books})  # お気に入りページを表示


@login_required
def RemoveFavorites(request, google_book_id):
    user = request.user  # 現在のユーザーを取得

    # book_id を使って Book オブジェクトを取得
    try:
        book = Book.objects.get(google_book_id=google_book_id)  # book_idから本を取得
    except Book.DoesNotExist:  # 本が見つからなかったら検索ページにリダイレクトする
        return redirect('search-books')

    # お気に入りを削除
    Favorite.objects.filter(user=user, book=book).delete()  # お気に入りテーブルから指定された本を削除

    # 押したページにリダイレクト（HTTP_REFERER がなければデフォルトで 'favorite_list' に戻る）
    return redirect(request.META.get('HTTP_REFERER', 'favorite_list'))

def Search_books(request):
    query = request.GET.get("q", "")  # 検索キーワードを取得（GETリクエストの'q'パラメータ）
    books = []  # 検索結果の本を格納するリスト
    
    # now()で現在時刻HMSS?を取得して、strtimeで表示する形式を指定。%(英字指定)で表示指定
    current_time = now().strftime("%H時%M分")  # 時刻表示
    
    if query:  # クエリが指定されていた場合
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}"  # 検索結果を取得するためのURLを作成
        response = requests.get(url)  # Google Books APIにリクエストを送信
        if response.status_code == 200:  # レスポンスが正常（ステータスコード200）の場合
            data = response.json()  # JSONレスポンスを取得
            books = data.get("items", [])  # 検索結果の本を取得

    # ログインしていない場合は空のリストを返す
    if isinstance(request.user, AnonymousUser):  # ログインしていない場合
        favorite_book_ids = []  # お気に入りリストは空
    else:
        # ログインしている場合にお気に入りを取得
        favorite_books = Favorite.objects.filter(user=request.user)  # 現在のユーザーのお気に入り本を取得
        favorite_book_ids = [fav.book.google_book_id for fav in favorite_books]  # お気に入りの本のGoogle Book IDをリストに

    return render(request, "books/search.html", {
        "books": books,  # 検索結果の本
        "query": query,  # 検索キーワード
        "favorite_book_ids": favorite_book_ids,  # ログインしているユーザーのお気に入りID
        "current_time": current_time,
    })


# 本の詳細情報を取得するビュー
def Book_detail(request, book_id):
    url = f"https://www.googleapis.com/books/v1/volumes/{book_id}?key={API_KEY}"  # 本の詳細情報を取得するURLを作成
    response = requests.get(url)  # Google Books APIにリクエストを送信
    book_details = {}  # 本の詳細情報を格納するための辞書

    if response.status_code == 200:  # レスポンスが正常（ステータスコード200）の場合
        book_details = response.json()  # JSON形式で詳細情報を取得

    return render(request, "books/detail.html", {"book": book_details})  # 本の詳細情報を表示
