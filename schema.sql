--  MySQL schema for Library Management
CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_db;

-- Students
CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(160) UNIQUE,
  roll_number VARCHAR(60) UNIQUE NOT NULL,
  course VARCHAR(80) NOT NULL,
  branch VARCHAR(80) NOT NULL,
  mobile VARCHAR(20),
  password_hash VARCHAR(255) NOT NULL,
  dob DATE,
  address TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admins
CREATE TABLE IF NOT EXISTS admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  user_id VARCHAR(60) UNIQUE NOT NULL,
  email VARCHAR(160) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books
CREATE TABLE IF NOT EXISTS books (
  id INT AUTO_INCREMENT PRIMARY KEY,
  category VARCHAR(80) NOT NULL,
  title VARCHAR(240) NOT NULL,
  author VARCHAR(160) NOT NULL,
  isbn VARCHAR(40) UNIQUE NOT NULL,
  branch VARCHAR(40) NOT NULL,
  date_of_purchase DATE,
  price DECIMAL(10,2),
  source ENUM('Purchased','Gifted') DEFAULT 'Purchased',
  rack_no VARCHAR(40),
  copies INT DEFAULT 1,
  remark VARCHAR(240),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Borrow transactions
CREATE TABLE IF NOT EXISTS borrows (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  book_id INT NOT NULL,
  issue_date DATE NOT NULL,
  due_date DATE NOT NULL,
  return_date DATE NULL,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Feedback
CREATE TABLE IF NOT EXISTS feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120),
  email VARCHAR(160),
  branch VARCHAR(80),
  feedback TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data (optional)
INSERT IGNORE INTO books (category,title,author,isbn,branch,date_of_purchase,price,source,rack_no,copies,remark) VALUES
('CS','Data Structures in C','Narasimha Karumanchi','9788192107554','CS','2024-01-10',550,'Purchased','R1',5,''),
('BCA','Web Development Basics','John Doe','9780000000002','BCA','2024-02-15',420,'Gifted','R2',3,''),
('MCA','Advanced DBMS','Korth','9780000000003','MCA','2024-03-05',650,'Purchased','R3',2,'');
