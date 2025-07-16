from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from django.db.models import Count, Q, Value
from django.db.models.functions import Concat

from .models import Book, Borrow, Review
from .serializers import (
    BookSerializer,
    BookCreateSerializer,
    BorrowSerializer,
    UserSerializer,
    GenreSerializer,
    AuthorSerializer
)

class BorrowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        user = request.user
        try:
            print(book_id)
            book = Book.objects.get(id=book_id)

            already_borrowed = Borrow.objects.filter(user=user, book=book, returned=False).exists()
            if already_borrowed:
                return Response({'detail': 'You already borrowed this book.'}, status=400)

            if not book.available:
                return Response({'detail': 'Book is not available.'}, status=400)

            Borrow.objects.create(user=user, book=book)
            book.available = False
            book.read_count += 1
            book.save()

            return Response({'detail': 'Book borrowed successfully.'})
        except Book.DoesNotExist:
            return Response({'detail': 'Book not found.'}, status=404)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_books(request):
    user = request.user
    borrows = Borrow.objects.filter(user=user)
    if borrows.exists():
        genres = borrows.values_list('book__genre', flat=True).distinct()
        books = Book.objects.filter(genre__in=genres, available=True).order_by('-read_count')[:5]
    else:
        books = Book.objects.filter(available=True).order_by('-read_count')[:5]
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

class AddBookView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookCreateSerializer
    # permission_classes = [IsAuthenticated]  # Optional: use IsAdminUser for admin-only


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Number of results per page
    page_size_query_param = 'page_size'
    max_page_size = 100
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = StandardResultsSetPagination  # ✅ use your pagination

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(genre__icontains=search)
            )

        availability = self.request.query_params.get('available')
        if availability == 'true':
            qs = qs.filter(available=True)
        elif availability == 'false':
            qs = qs.filter(available=False)

        return qs
class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        book = Book.objects.get(pk=pk)
        if not book.available:
            return Response({'error': 'Book not available'}, status=400)

        if Borrow.objects.filter(user=request.user, book=book, returned=False).exists():
            return Response({'error': 'Already borrowed'}, status=400)

        Borrow.objects.create(user=request.user, book=book)
        book.available = False
        book.read_count += 1
        book.save()
        return Response({'message': 'Book borrowed'})

class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            borrow = Borrow.objects.get(pk=pk, user=request.user, returned=False)
            borrow.returned = True
            borrow.save()

            book = borrow.book
            book.available = True
            book.save()

            return Response({'detail': 'Book returned successfully.'})
        except Borrow.DoesNotExist:
            return Response({'detail': 'Borrow record not found or already returned.'}, status=status.HTTP_404_NOT_FOUND)
class UserBorrowedBooksView(generics.ListAPIView):
    serializer_class = BorrowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Borrow.objects.filter(user=self.request.user, returned=False)

class RecommendBooksView(APIView):
    permission_classes = [AllowAny]  # ✅ Allow all users

    def get(self, request):
        user = request.user
        books = None

        if user and user.is_authenticated:
            borrows = Borrow.objects.filter(user=user).select_related('book')
            if borrows.exists():
                genres = borrows.values_list('book__genre', flat=True)
                books = Book.objects.filter(genre__in=genres, available=True).order_by('-read_count')

        # If not authenticated or no history fallback
        if books is None or not books.exists():
            books = Book.objects.filter(available=True).order_by('-read_count')

        serializer = BookSerializer(books[:5], many=True)
        return Response(serializer.data)
    



class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        
        # Apply filters
        genre = self.request.query_params.get('genre', None)
        author = self.request.query_params.get('author', None)
        available = self.request.query_params.get('available', None)

        if genre:
            queryset = queryset.filter(genre__iexact=genre)
        if author:
            queryset = queryset.filter(author__iexact=author)
        if available == 'true':
            queryset = queryset.filter(available=True)
        
        return queryset

    def list(self, request, *args, **kwargs):
        # Get paginated response
        response = super().list(request, *args, **kwargs)
        # For simplicity, we're not implementing proper pagination here
        # But you can add it if needed
        return response

class GenreListView(generics.ListAPIView):
    serializer_class = GenreSerializer

    def get_queryset(self):
        return Book.objects.values('genre').annotate(
            genre_display=Concat('genre', Value(''))
        ).values('genre').distinct().order_by('genre')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        genres = [item['genre'] for item in queryset]
        return Response(genres)

class AuthorListView(generics.ListAPIView):
    serializer_class = AuthorSerializer

    def get_queryset(self):
        return Book.objects.values('author').annotate(
            author_display=Concat('author', Value(''))
        ).values('author').distinct().order_by('author')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        authors = [item['author'] for item in queryset]
        return Response(authors)
class UserReadStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only show books the user has borrowed and their read counts
        from .models import Borrow

        borrowed_books = Borrow.objects.filter(user=request.user).select_related('book')
        book_ids = borrowed_books.values_list('book__id', flat=True).distinct()
        books = Book.objects.filter(id__in=book_ids).order_by('-read_count')

        data = [
            {
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "read_count": book.read_count,
            }
            for book in books
        ]
        return Response(data)
    

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'username': request.user.username,
            'email': request.user.email,
        })