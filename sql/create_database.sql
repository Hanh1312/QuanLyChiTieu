CREATE DATABASE QuanLyChiTieu;
GO

USE QuanLyChiTieu;
GO

CREATE TABLE Users
(
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(50) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL
);

INSERT INTO Users
VALUES
(
    'admin',
    'admin123'
);

CREATE TABLE Transactions
(
    TransactionID INT IDENTITY(1,1) PRIMARY KEY,
    TransactionDate DATE NOT NULL,
    Type NVARCHAR(10) NOT NULL,
    Category NVARCHAR(100) NOT NULL,
    Amount DECIMAL(18,2) NOT NULL,
    Note NVARCHAR(255)
);

CREATE TABLE DebtPay
(
    DebtID INT IDENTITY(1,1) PRIMARY KEY,
    PersonName NVARCHAR(100) NOT NULL,
    Amount DECIMAL(18,2) NOT NULL,
    DueDate DATE NOT NULL,
    Status NVARCHAR(20) DEFAULT 'Unpaid',
    Note NVARCHAR(255)
);

CREATE TABLE DebtReceive
(
    DebtID INT IDENTITY(1,1) PRIMARY KEY,
    PersonName NVARCHAR(100) NOT NULL,
    Amount DECIMAL(18,2) NOT NULL,
    DueDate DATE NOT NULL,
    Status NVARCHAR(20) DEFAULT 'Uncollected',
    Note NVARCHAR(255)
);

CREATE TABLE Budget
(
    BudgetID INT IDENTITY(1,1) PRIMARY KEY,
    BudgetMonth INT NOT NULL,
    BudgetYear INT NOT NULL,
    Amount DECIMAL(18,2) NOT NULL
);

SELECT *
FROM DebtPay
WHERE Status='Unpaid'
AND DATEDIFF(day,GETDATE(),DueDate) <= 3