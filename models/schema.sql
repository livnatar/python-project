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
    copies_available INTEGER DEFAULT 1
);


-- Create book_genres junction table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS book_genres (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
    UNIQUE(book_id, genre_id)  -- Prevent duplicate entries
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);

CREATE INDEX IF NOT EXISTS idx_book_genres_book_id ON book_genres(book_id);
CREATE INDEX IF NOT EXISTS idx_book_genres_genre_id ON book_genres(genre_id);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE INDEX IF NOT EXISTS idx_loans_user_id ON loans(user_id);
CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_due_date ON loans(due_date);
CREATE INDEX IF NOT EXISTS idx_loans_returned_date ON loans(returned_date);


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
('Technology', 'Books about computing, engineering, and innovation'),
('Programming', 'Books about software development and coding'),
('Self-Help', 'Books for personal development and improvement')
ON CONFLICT (name) DO NOTHING;

-- Insert sample users
INSERT INTO users (username, email, password_hash, first_name, last_name, phone, address) VALUES
('john_doe', 'john@example.com', 'pbkdf2:sha256:260000$salt$hash', 'John', 'Doe', '555-0101', '123 Main St'),
('jane_smith', 'jane@example.com', 'pbkdf2:sha256:260000$salt$hash', 'Jane', 'Smith', '555-0102', '456 Oak Ave'),
('admin', 'admin@library.com', 'pbkdf2:sha256:260000$salt$hash', 'Library', 'Admin', '555-0100', 'Library Building')
ON CONFLICT (username) DO NOTHING;

-- Insert sample books
INSERT INTO books (isbn, title, author, publication_year, pages, description, copies_total, copies_available) VALUES
('9780134685991', 'Effective Java', 'Joshua Bloch', 2017, 412, 'Best practices for Java programming', 3, 3),
('9780321127426', 'Patterns of Enterprise Application Architecture', 'Martin Fowler', 2002, 560, 'Architecture patterns for enterprise applications', 2, 2),
('9780132350884', 'Clean Code', 'Robert C. Martin', 2008, 464, 'A handbook of agile software craftsmanship', 5, 5),
('9780544003415', 'The Lord of the Rings', 'J.R.R. Tolkien', 2012, 1216, 'Epic fantasy adventure', 2, 2),
('9780553103540', 'A Game of Thrones', 'George R.R. Martin', 1996, 694, 'Political fantasy epic', 3, 3)
ON CONFLICT (isbn) DO NOTHING;

-- Insert sample book-genre relationships
-- Get the IDs first, then insert relationships
DO $$
DECLARE
    effective_java_id INTEGER;
    patterns_id INTEGER;
    clean_code_id INTEGER;
    lotr_id INTEGER;
    got_id INTEGER;
    tech_genre_id INTEGER;
    prog_genre_id INTEGER;
    fiction_genre_id INTEGER;
    fantasy_genre_id INTEGER;
BEGIN
    -- Get book IDs
    SELECT id INTO effective_java_id FROM books WHERE isbn = '9780134685991';
    SELECT id INTO patterns_id FROM books WHERE isbn = '9780321127426';
    SELECT id INTO clean_code_id FROM books WHERE isbn = '9780132350884';
    SELECT id INTO lotr_id FROM books WHERE isbn = '9780544003415';
    SELECT id INTO got_id FROM books WHERE isbn = '9780553103540';

    -- Get genre IDs
    SELECT id INTO tech_genre_id FROM genres WHERE name = 'Technology';
    SELECT id INTO prog_genre_id FROM genres WHERE name = 'Programming';
    SELECT id INTO fiction_genre_id FROM genres WHERE name = 'Fiction';
    SELECT id INTO fantasy_genre_id FROM genres WHERE name = 'Fantasy';

    -- Insert book-genre relationships
    INSERT INTO book_genres (book_id, genre_id) VALUES
    (effective_java_id, tech_genre_id),
    (effective_java_id, prog_genre_id),
    (patterns_id, tech_genre_id),
    (patterns_id, prog_genre_id),
    (clean_code_id, tech_genre_id),
    (clean_code_id, prog_genre_id),
    (lotr_id, fiction_genre_id),
    (lotr_id, fantasy_genre_id),
    (got_id, fiction_genre_id),
    (got_id, fantasy_genre_id)
    ON CONFLICT (book_id, genre_id) DO NOTHING;
END $$;