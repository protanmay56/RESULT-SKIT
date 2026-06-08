CREATE DATABASE IF NOT EXISTS skit_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skit_portal;

CREATE TABLE IF NOT EXISTS admins (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80)  NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL,
    name     VARCHAR(120) DEFAULT 'Examination Controller',
    created  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    college_id      VARCHAR(40)  NOT NULL UNIQUE,   -- login username
    dob             VARCHAR(20)  NOT NULL,            -- login password
    roll            VARCHAR(30)  NOT NULL,
    registration_no VARCHAR(50)  DEFAULT '',
    enrollment_no   VARCHAR(50)  DEFAULT '',
    abc_id          VARCHAR(50)  DEFAULT '',
    name            VARCHAR(120) NOT NULL,
    mother_name     VARCHAR(120) DEFAULT '',
    branch          VARCHAR(30)  NOT NULL,
    program         VARCHAR(60)  DEFAULT '',
    email           VARCHAR(120) DEFAULT '',
    created         DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS results (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    semester   INT NOT NULL,
    year       VARCHAR(20) NOT NULL,
    published  TINYINT(1) DEFAULT 1,
    uploaded   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_result (student_id, semester)
);

CREATE TABLE IF NOT EXISTS subjects (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    result_id INT NOT NULL,
    name      VARCHAR(120) NOT NULL,
    code      VARCHAR(30)  DEFAULT '',
    internal  INT DEFAULT 0,
    external  INT DEFAULT 0,
    int_max   INT DEFAULT 30,
    ext_max   INT DEFAULT 70,
    FOREIGN KEY (result_id) REFERENCES results(id) ON DELETE CASCADE
);
