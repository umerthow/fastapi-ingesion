CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,       -- 
    first_name VARCHAR(100) NOT NULL,          -- [cite: 49]
    last_name VARCHAR(100) NOT NULL,           -- [cite: 50]
    email VARCHAR(255) NOT NULL,               -- [cite: 51]
    phone VARCHAR(20),                         -- [cite: 52]
    address TEXT,                              -- [cite: 53]
    date_of_birth DATE,                        -- [cite: 54]
    account_balance DECIMAL(15, 2),            -- 
    created_at TIMESTAMP                       -- [cite: 56]
);