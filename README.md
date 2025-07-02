
#### Livnat Arama - livnatar@edu.jmc.ac.il and Ophek Alon - ophekal@edu.jmc.ac.il

# Library Management System

A comprehensive REST API-based library management system built with Python Flask. This system provides complete functionality for managing books, users, loans, genres, and integrates with external APIs for enhanced book information.

## Project Purpose

This Library Management System is designed to digitize and streamline library operations. It provides a robust backend API that can be used by library staff to:

- Manage book inventory with detailed cataloging
- Handle user registration and management
- Process book loans and returns with automatic due date tracking
- Organize books by genres and categories
- Generate comprehensive reports and export data
- Integrate with external book databases for additional information
- Track overdue books and calculate fines

## Key Features

### Book Management
- Add, update, and delete books with comprehensive metadata
- Search books by title, author, genre, or ISBN
- Track book availability and copies
- Support for multiple genres per book
- Integration with Open Library API for additional book information

### User Management
- User registration and authentication
- Profile management with contact information
- Customizable loan limits per user
- User search and filtering capabilities

### Loan Management
- Book checkout and return processing
- Automatic due date calculation
- Loan renewal functionality
- Overdue book tracking with fine calculation
- Comprehensive loan history and statistics

### Reporting & Analytics
- Export user-specific loan history to Excel
- Generate reports for overdue books
- Loan statistics and analytics
- Data export capabilities for all loans

### External Integrations
- Open Library API integration for book languages
- Same-author book discovery
- Enhanced book metadata retrieval

## Technology Stack

- **Backend Framework**: Flask (Python)
- **Database**: SQLAlchemy ORM (configurable database backend)
- **API**: RESTful API with JSON responses
- **Data Export**: Excel file generation
- **External APIs**: Open Library integration
- **Authentication**: Built-in user authentication system

## Prerequisites

Before running this project, ensure you have the following installed:

- Docker
- Python 3.7 or higher
- Postman (for testing API endpoints)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/livnatar/python-project.git
cd python-project
```

### 2. Start Docker Container

Turn on your Docker container to set up the development environment.
Make sure the database connection parameters in database.py match your Docker setup. Update them if needed.

### 3. Initialize the Database

**Important**: Before running the application, you must first create the database tables:

```bash
python database.py
```

This step creates all necessary tables in the database. This must be done before any other operations.

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 5. Test API Endpoints

Use Postman to test the various API endpoints. The application provides a comprehensive REST API for managing all library operations.

## API Documentation

### Book API Endpoints

#### 1. Get All Books
**GET** `localhost:5000/api/books`

Returns all books with pagination and filtering options

**Query params:**
- `?page=1&per_page=20`
- `?search=gatsby`
- `?genre_id=1`
- `?available_only=true`

#### 2. Get Book by ID
**GET** `localhost:5000/api/books/1`

Returns specific book by ID

#### 3. Get Book by ISBN
**GET** `localhost:5000/api/books/isbn/9781234567890`

Returns book by ISBN

#### 4. Create Book
**POST** `localhost:5000/api/books`

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

#### 5. Update Book
**PUT** `localhost:5000/api/books/1`

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

#### 6. Delete Book
**DELETE** `localhost:5000/api/books/1`

Deletes book by ID

#### 7. Search Books
**GET** `localhost:5000/api/books/search?q=gatsby`

**Query params:**
- `?q=search_term` (required)
- `&genre_id=1&genre_id=2` (optional)

#### 8. Get Available Books
**GET** `localhost:5000/api/books/available`

**Query params:**
- `?page=1&per_page=20`

#### 9. Add Genre to Book
**POST** `localhost:5000/api/books/1/genres`

**Body:**
```json
{
  "genre_id": 3
}
```

#### 10. Remove Genre from Book
**DELETE** `localhost:5000/api/books/1/genres/3`

Removes genre ID 3 from book ID 1

### Data Export API Endpoints

#### 1. Export User Loans
**GET** `localhost:5000/data/export/user-loans/{username}`

Exports all loans for a specific user to Excel file

**Example:**
`localhost:5000/data/export/user-loans/john_doe`

**Response:** Downloads Excel file with user's loan data

#### 2. Export All Loans
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

#### 3. Export Overdue Loans
**GET** `localhost:5000/data/export/overdue-loans`

Exports all overdue loans to Excel file

**Example:**
`localhost:5000/data/export/overdue-loans`

**Response:** Downloads Excel file with overdue loan data and total fines

### External Book API Endpoints

#### 1. Get Book Languages
**GET** `localhost:5000/api/external/languages`

Gets available languages for a book by title using Open Library API

**Query params (required):**
- `?title=book_title` - The title of the book to search for

**Examples:**
- `localhost:5000/api/external/languages?title=The Great Gatsby`
- `localhost:5000/api/external/languages?title=Harry Potter`
- `localhost:5000/api/external/languages?title=1984`

**Response:**
```json
{
  "title": "The Great Gatsby",
  "languages": ["eng", "spa", "fre"]
}
```

#### 2. Get Books by Same Author
**GET** `localhost:5000/api/external/same-author`

Gets other books by the same author using Open Library API

**Query params (required):**
- `?title=book_title` - The title of the book to find same-author books for

**Examples:**
- `localhost:5000/api/external/same-author?title=The Great Gatsby`
- `localhost:5000/api/external/same-author?title=Harry Potter and the Philosopher's Stone`
- `localhost:5000/api/external/same-author?title=To Kill a Mockingbird`

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

#### Error Responses

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

### Genre API Endpoints

#### 1. Get All Genres
**GET** `localhost:5000/api/genres`

Returns all genres with pagination and search options

**Query params:**
- `?page=1&per_page=20`
- `?search=fiction`

#### 2. Get Genre by ID
**GET** `localhost:5000/api/genres/1`

Returns specific genre by ID with book count

#### 3. Get Genre by Name
**GET** `localhost:5000/api/genres/Fiction`

Returns genre ID and details by genre name

#### 4. Create Genre
**POST** `localhost:5000/api/genres`

**Body:**
```json
{
  "name": "Science Fiction",
  "description": "Books featuring futuristic concepts and technology"
}
```

#### 5. Update Genre
**PUT** `localhost:5000/api/genres/1`

**Body:**
```json
{
  "name": "Updated Genre Name",
  "description": "Updated description"
}
```

#### 6. Delete Genre
**DELETE** `localhost:5000/api/genres/1`

Deletes genre by ID (only if no books are associated)

#### 7. Search Genres
**GET** `localhost:5000/api/genres/search?q=fiction`

**Query params:**
- `?q=search_term` (required)

#### 8. Get Books in Genre
**GET** `localhost:5000/api/genres/1/books`

Returns all books in a specific genre with pagination

**Query params:**
- `?page=1&per_page=20`

### Loan API Endpoints

#### 1. Get All Loans
**GET** `localhost:5000/api/loans`

Returns all loans with pagination and optional status filtering

**Query params:**
- `?page=1&per_page=20`
- `?status=active` - Filter by status (active, returned, overdue)

#### 2. Get Loan by ID
**GET** `localhost:5000/api/loans/1`

Returns specific loan by ID with full details

#### 3. Create Loan (Borrow Book)
**POST** `localhost:5000/loans`

**Body:**
```json
{
  "user_id": 1,
  "book_id": 5
}
```

#### 4. Return Book
**PUT** `localhost:5000/api/loans/1/return`

**Body (optional):**
```json
{
  "return_notes": "Book returned in good condition"
}
```

#### 5. Renew Loan
**PUT** `localhost:5000/api/loans/1/renew`

**Body (optional):**
```json
{
  "renewal_reason": "Still reading"
}
```

#### 6. Get Overdue Loans
**GET** `localhost:5000/api/loans/overdue`

Returns all loans that are past their due date

#### 7. Get User Loans
**GET** `localhost:5000/api/loans/user/1`

Returns all loans for a specific user with pagination

**Query params:**
- `?page=1&per_page=20`

#### 8. Get Book Loans
**GET** `localhost:5000/api/loans/book/1`

Returns all loans for a specific book with pagination

**Query params:**
- `?page=1&per_page=20`

#### 9. Get Loan Statistics
**GET** `localhost:5000/api/loans/statistics`

Returns comprehensive loan statistics and metrics

#### 10. Get User Active Loans
**GET** `localhost:5000/api/loans/user/1/active`

Returns only active loans for a specific user

#### 11. Get Current Book Loans
**GET** `localhost:5000/api/loans/book/1/current`

Returns current active loans for a specific book

#### 12. Delete Loan
**DELETE** `localhost:5000/api/loans/1`

Deletes a loan record (admin operation)

**Query params:**
- `?force=true` - Force delete active loans (admin override)

#### 13. Get Book Availability
**GET** `localhost:5000/api/loans/book/1/availability`

Returns detailed availability information for a book

### User API Endpoints

#### 1. Create User
**POST** `localhost:5000/api/users`

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

#### 2. Get User by ID
**GET** `localhost:5000/api/users/1`

Returns specific user by ID with full details

#### 3. Get All Users
**GET** `localhost:5000/api/users`

Returns all users with pagination and optional search

**Query params:**
- `?page=1&per_page=20`
- `?search=john` - Search by username, email, or name

#### 4. Get User by Username
**GET** `localhost:5000/api/users/username/john_doe`

Returns user by username

#### 5. Update User
**PUT** `localhost:5000/api/users/1`

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

#### 6. Update User Password
**PUT** `localhost:5000/api/users/1/password`

**Body:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!"
}
```

#### 7. Delete User
**DELETE** `localhost:5000/api/users/1`

Deletes user by ID

#### 8. Search Users
**GET** `localhost:5000/api/users/search?q=john`

Search users by username, email, or name

**Query params:**
- `?q=search_term` (required)
- `?page=1&per_page=20`

#### 9. Authenticate User
**POST** `localhost:5000/api/users/authenticate`

**Body:**
```json
{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

#### 10. Get User Count
**GET** `localhost:5000/api/users/count`

Returns total user count

## Usage Examples

### Testing with Postman

Once your application is running on `http://localhost:5000`, you can test all endpoints using Postman:

#### Adding a New Book

```
POST http://localhost:5000/api/books
Content-Type: application/json

Body:
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

#### Creating a Loan

```
POST http://localhost:5000/loans
Content-Type: application/json

Body:
{
  "user_id": 1,
  "book_id": 5
}
```

#### Searching Books

```
GET http://localhost:5000/api/books?search=gatsby&available_only=true
```
