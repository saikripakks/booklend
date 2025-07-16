# 📚 Book Lending & Recommendation System

A Django REST API for managing book lending and recommendations based on user history or popularity. Comes with optional React + Bootstrap frontend.

---

## 🚀 Features

- ✅ User Registration & JWT Authentication
- ✅ Browse, Borrow & Return Books
- ✅ Filter by Genre, Author, Availability
- ✅ Book Recommendations (based on genre or popularity)
- ✅ Track how many times a book has been read
- ✅ User dashboard with borrowed & read statistics
- ✅ Admin access to add books
- ✅ Open to further extension (reviews, ratings, etc.)

---

## 🧱 Tech Stack

- **Backend:** Python 3, Django, Django REST Framework, Simple JWT
- **Frontend :** React.js, Axios, Bootstrap 5
- **Database:** SQLite (default), switchable to PostgreSQL/MySQL

---
pip install django djangorestframework djangorestframework-simplejwt corsheaders
pip freeze > requirements.txt
📬 Sample Postman API Requests
Replace 127.0.0.1:8000 with your actual host and port.

🔐 Register

POST /api/register/
{
    "username": "john",
    "password": "johnpassword"
}
🔐 Login (JWT)

POST /api/token/
{
    "username": "john",
    "password": "johnpassword"
}
🔎 List Books

GET /api/books/
📚 Add Book (authenticated)

POST /api/books/add/
Headers: Authorization: Bearer <access_token>
{
    "title": "Django Mastery",
    "author": "Jane Doe",
    "genre": "Programming"
}
📥 Borrow Book

POST /api/books/borrow/1/
Headers: Authorization: Bearer <access_token>
📤 Return Book

POST /api/return/3/
Headers: Authorization: Bearer <access_token>
👓 My Borrowed Books

GET /api/borrowed/
Headers: Authorization: Bearer <access_token>
🤝 Recommend Books (authenticated or anonymous)

GET /api/recommend/
📊 User Reading Stats

GET /api/user/read-stats/
Headers: Authorization: Bearer <access_token>  please write without using code colummn


