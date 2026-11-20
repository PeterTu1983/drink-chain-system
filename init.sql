CREATE TABLE IF NOT EXISTS base_menu (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    price INTEGER NOT NULL
);

INSERT INTO base_menu (name, price) VALUES
    ('開心奶茶', 70),
    ('快樂紅茶', 55),
    ('烏龍綠茶', 60),
    ('茉莉花茶', 70),
    ('甘蔗青茶', 65)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS branch_special_drinks (
    id SERIAL PRIMARY KEY,
    branch_code VARCHAR(20) NOT NULL,
    name VARCHAR(50) NOT NULL,
    price INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    branch_code VARCHAR(20) NOT NULL,
    item_name VARCHAR(50) NOT NULL,
    amount INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
