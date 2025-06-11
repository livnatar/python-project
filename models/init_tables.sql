-- Create genres table first (no dependencies)
CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Create users table (no dependencies)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    membership_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    max_loans INTEGER DEFAULT 5
);

-- Create books table (depends on genres)
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(13) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(200) NOT NULL,
    publication_year INTEGER,
    pages INTEGER,
    language VARCHAR(50) DEFAULT 'English',
    description TEXT,
    copies_total INTEGER DEFAULT 1,
    copies_available INTEGER DEFAULT 1,
    genre_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE RESTRICT
);

-- Create loans table (depends on users and books)
CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    loan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    returned_date TIMESTAMP,
    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Create reservations table (depends on users and books)
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);


-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_books_genre_id ON books(genre_id);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE INDEX IF NOT EXISTS idx_loans_user_id ON loans(user_id);
CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_due_date ON loans(due_date);
CREATE INDEX IF NOT EXISTS idx_loans_returned_date ON loans(returned_date);

CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON reservations(user_id);
CREATE INDEX IF NOT EXISTS idx_reservations_book_id ON reservations(book_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);


-- Insert sample data
INSERT INTO genres (name, description) VALUES
('Fiction', 'Fictional literature including novels and short stories'),
('Non-Fiction', 'Factual books including biographies, history, and science'),
('Science Fiction', 'Speculative fiction dealing with futuristic concepts'),
('Mystery', 'Fiction dealing with puzzles, crimes, and detective work'),
('Romance', 'Fiction focused on romantic relationships'),
('Fantasy', 'Fiction involving magical and supernatural elements'),
('Biography', 'Life stories of real people'),
('History', 'Books about past events and civilizations'),
('Science', 'Books about scientific discoveries and principles'),
('Technology', 'Books about computing, engineering, and innovation')
ON CONFLICT (name) DO NOTHING;

-- Insert sample users
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, address) VALUES
('john_doe', 'john@example.com', 'pbkdf2:sha256:260000$salt$hash', 'John', 'Doe', '555-0101', '123 Main St'),
('jane_smith', 'jane@example.com', 'pbkdf2:sha256:260000$salt$hash', 'Jane', 'Smith', '555-0102', '456 Oak Ave'),
('admin', 'admin@library.com', 'pbkdf2:sha256:260000$salt$hash', 'Library', 'Admin', '555-0100', 'Library Building')
ON CONFLICT (username) DO NOTHING;

-- Insert sample books
INSERT INTO books (isbn, title, author, publication_year, pages, description, copies_total, copies_available, genre_id) VALUES
('9780134685991', 'Effective Java', 'Joshua Bloch', 2017, 412, 'Best practices for Java programming', 3, 3, 10),
('9780321127426', 'Patterns of Enterprise Application Architecture', 'Martin Fowler', 2002, 560, 'Architecture patterns for enterprise applications', 2, 2, 10),
('9780132350884', 'Clean Code', 'Robert C. Martin', 2008, 464, 'A handbook of agile software craftsmanship', 5, 5, 10)
ON CONFLICT (isbn) DO NOTHING;