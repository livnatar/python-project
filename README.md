# Book API Endpoints Reference

## 1. Get All Books
**GET** `localhost:5000/books`
Returns all books with pagination and filtering options

**Query params:**
- `?page=1&per_page=20`
- `?search=gatsby`
- `?genre_id=1`
- `?available_only=true`

## 2. Get Book by ID
**GET** `localhost:5000/books/1`
Returns specific book by ID

## 3. Get Book by ISBN
**GET** `localhost:5000/books/isbn/9781234567890`
Returns book by ISBN

## 4. Create Book
**POST** `localhost:5000/books`
**Body:**
```json
{
  "isbn": "9781234567890",
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "publication_year": 1925,
  "pages": 180,
  "language": "English",
  "description": "A classic novel",
  "copies_total": 5,
  "copies_available": 5,
  "genre_ids": [1, 2]
}
```

## 5. Update Book
**PUT** `localhost:5000/books/1`
**Body:**
```json
{
  "isbn": "9781234567890",
  "title": "Updated Title",
  "author": "F. Scott Fitzgerald",
  "publication_year": 1925,
  "pages": 200,
  "language": "English",
  "description": "Updated description",
  "copies_total": 10,
  "copies_available": 8,
  "genre_ids": [1, 2, 3]
}
```

## 6. Delete Book
**DELETE** `localhost:5000/books/1`
Deletes book by ID

## 7. Search Books
**GET** `localhost:5000/books/search?q=gatsby`
**Query params:**
- `?q=search_term` (required)
- `&genre_id=1&genre_id=2` (optional)

## 8. Get Available Books
**GET** `localhost:5000/books/available`
**Query params:**
- `?page=1&per_page=20`

## 9. Add Genre to Book
**POST** `localhost:5000/books/1/genres`
**Body:**
```json
{
  "genre_id": 3
}
```

## 10. Remove Genre from Book
**DELETE** `localhost:5000/books/1/genres/3`
Removes genre ID 3 from book ID 1

# Data Export API Endpoints Reference

## 1. Export User Loans
**GET** `localhost:5000/data/export/user-loans/{username}`
Exports all loans for a specific user to Excel file

**Example:**
`localhost:5000/data/export/user-loans/john_doe`

**Response:** Downloads Excel file with user's loan data

## 2. Export All Loans
**GET** `localhost:5000/data/export/all-loans`
Exports all loans in the system to Excel file

**Query params (optional):**
- `?status=active` - Only active loans
- `?status=returned` - Only returned loans  
- `?status=overdue` - Only overdue loans

**Examples:**
- `localhost:5000/data/export/all-loans` - All loans
- `localhost:5000/data/export/all-loans?status=active` - Active loans only
- `localhost:5000/data/export/all-loans?status=overdue` - Overdue loans only

**Response:** Downloads Excel file with loan data

## 3. Export Overdue Loans
**GET** `localhost:5000/data/export/overdue-loans`
Exports all overdue loans to Excel file

**Example:**
`localhost:5000/data/export/overdue-loans`

**Response:** Downloads Excel file with overdue loan data and total fines

# External Book API Endpoints Reference

## 1. Get Book Languages
**GET** `localhost:5000/external/languages`
Gets available languages for a book by title using Open Library API

**Query params (required):**
- `?title=book_title` - The title of the book to search for

**Examples:**
- `localhost:5000/external/languages?title=The Great Gatsby`
- `localhost:5000/external/languages?title=Harry Potter`
- `localhost:5000/external/languages?title=1984`

**Response:**
```json
{
  "title": "The Great Gatsby",
  "languages": ["eng", "spa", "fre"]
}
```

## 2. Get Books by Same Author
**GET** `localhost:5000/external/same-author`
Gets other books by the same author using Open Library API

**Query params (required):**
- `?title=book_title` - The title of the book to find same-author books for

**Examples:**
- `localhost:5000/external/same-author?title=The Great Gatsby`
- `localhost:5000/external/same-author?title=Harry Potter and the Philosopher's Stone`
- `localhost:5000/external/same-author?title=To Kill a Mockingbird`

**Response:**
```json
{
  "title": "The Great Gatsby",
  "same_author_books": [
    "This Side of Paradise",
    "The Beautiful and Damned",
    "Tender Is the Night"
  ]
}
```

## Error Responses

**Missing title parameter:**
```json
{
  "error": "Missing 'title' query parameter"
}
```

**Book not found:**
```json
{
  "error": "Book not found"
}
```

**Server error:**
```json
{
  "error": "Internal server error while getting languages: [error details]"
}
```

# Genre API Endpoints Reference

## 1. Get All Genres
**GET** `localhost:5000/genres`
Returns all genres with pagination and search options

**Query params:**
- `?page=1&per_page=20`
- `?search=fiction`

## 2. Get Genre by ID
**GET** `localhost:5000/genres/1`
Returns specific genre by ID with book count

## 3. Get Genre by Name
**GET** `localhost:5000/genres/Fiction`
Returns genre ID and details by genre name

## 4. Create Genre
**POST** `localhost:5000/genres`
**Body:**
```json
{
  "name": "Science Fiction",
  "description": "Books featuring futuristic concepts and technology"
}
```

## 5. Update Genre
**PUT** `localhost:5000/genres/1`
**Body:**
```json
{
  "name": "Updated Genre Name",
  "description": "Updated description"
}
```

## 6. Delete Genre
**DELETE** `localhost:5000/genres/1`
Deletes genre by ID (only if no books are associated)

## 7. Search Genres
**GET** `localhost:5000/genres/search?q=fiction`
**Query params:**
- `?q=search_term` (required)

## 8. Get Books in Genre
**GET** `localhost:5000/genres/1/books`
Returns all books in a specific genre with pagination

**Query params:**
- `?page=1&per_page=20`

# Loan API Endpoints Reference

## 1. Get All Loans
**GET** `localhost:5000/loans`
Returns all loans with pagination and optional status filtering

**Query params:**
- `?page=1&per_page=20`
- `?status=active` - Filter by status (active, returned, overdue)

## 2. Get Loan by ID
**GET** `localhost:5000/loans/1`
Returns specific loan by ID with full details

## 3. Create Loan (Borrow Book)
**POST** `localhost:5000/loans`
**Body:**
```json
{
  "user_id": 1,
  "book_id": 5
}
```

## 4. Return Book
**PUT** `localhost:5000/loans/1/return`
**Body (optional):**
```json
{
  "return_notes": "Book returned in good condition"
}
```

## 5. Renew Loan
**PUT** `localhost:5000/loans/1/renew`
**Body (optional):**
```json
{
  "renewal_reason": "Still reading"
}
```

## 6. Get Overdue Loans
**GET** `localhost:5000/loans/overdue`
Returns all loans that are past their due date

## 7. Get User Loans
**GET** `localhost:5000/loans/user/1`
Returns all loans for a specific user with pagination

**Query params:**
- `?page=1&per_page=20`

## 8. Get Book Loans
**GET** `localhost:5000/loans/book/1`
Returns all loans for a specific book with pagination

**Query params:**
- `?page=1&per_page=20`

## 9. Get Loan Statistics
**GET** `localhost:5000/loans/statistics`
Returns comprehensive loan statistics and metrics

## 10. Get User Active Loans
**GET** `localhost:5000/loans/user/1/active`
Returns only active loans for a specific user

## 11. Get Current Book Loans
**GET** `localhost:5000/loans/book/1/current`
Returns current active loans for a specific book

## 12. Delete Loan
**DELETE** `localhost:5000/loans/1`
Deletes a loan record (admin operation)

**Query params:**
- `?force=true` - Force delete active loans (admin override)

## 13. Get Book Availability
**GET** `localhost:5000/loans/book/1/availability`
Returns detailed availability information for a book


# User API Endpoints Reference

## 1. Create User
**POST** `localhost:5000/users`
**Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St, City, State",
  "max_loans": 5
}
```

## 2. Get User by ID
**GET** `localhost:5000/users/1`
Returns specific user by ID with full details

## 3. Get All Users
**GET** `localhost:5000/users`
Returns all users with pagination and optional search

**Query params:**
- `?page=1&per_page=20`
- `?search=john` - Search by username, email, or name

## 4. Get User by Username
**GET** `localhost:5000/users/username/john_doe`
Returns user by username

## 5. Update User
**PUT** `localhost:5000/users/1`
**Body:**
```json
{
  "username": "john_updated",
  "email": "john.updated@example.com",
  "first_name": "John",
  "last_name": "Updated",
  "phone": "+1987654321",
  "address": "456 New St, City, State",
  "max_loans": 10
}
```

## 6. Update User Password
**PUT** `localhost:5000/users/1/password`
**Body:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!"
}
```

## 7. Delete User
**DELETE** `localhost:5000/users/1`
Deletes user by ID

## 8. Search Users
**GET** `localhost:5000/users/search?q=john`
Search users by username, email, or name

**Query params:**
- `?q=search_term` (required)
- `?page=1&per_page=20`

## 9. Authenticate User
**POST** `localhost:5000/users/authenticate`
**Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

## 10. Get User Count
**GET** `localhost:5000/users/count`
Returns total user count