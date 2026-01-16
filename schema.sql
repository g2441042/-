-- テーブル作成（Users, Menus, Reviews）

-- ユーザーテーブル（今回は使っていませんが念のため定義）
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL
);

-- メニューテーブル（categoryを追加）
CREATE TABLE IF NOT EXISTS menus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL,
    category VARCHAR(50)
);

-- レビューテーブル（likesを追加、user_idをuser_nameに変更済み）
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(80),
    menu_id INTEGER REFERENCES menus(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- テストデータの投入（カテゴリ付き）
INSERT INTO menus (name, price, category) VALUES 
('日替わりA定食', 500, '定食'),
('カツカレー', 450, 'カレー'),
('醤油ラーメン', 380, '麺類');
