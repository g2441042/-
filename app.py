import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# データベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/gakumeshi_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- データベースのモデル定義 ---
class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50))

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80)) 
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    
    menu = db.relationship('Menu', backref='reviews')

# --- 画面表示 (HTML) ---
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>GakuMeshi - 学食レビュー</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .menu-item { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
        .review-form { background-color: #f9f9f9; padding: 10px; margin-top: 10px; border-radius: 5px; }
        .delete-btn { background-color: #ff4444; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 3px; }
        .review-delete-btn { color: red; border: none; background: none; cursor: pointer; font-weight: bold; margin-left: 5px; }
        .header-area { display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <h1>🍛 GakuMeshi メニュー一覧</h1>
    
    <div style="background-color: #eef; padding: 15px; margin-bottom: 30px; border-radius: 8px;">
        <h3>➕ 新しいメニューを追加</h3>
        <form method="POST" action="/add_menu">
            名前: <input type="text" name="name" required placeholder="例: カツ丼">
            価格: <input type="number" name="price" required placeholder="500">
            <input type="submit" value="追加">
        </form>
    </div>

    {% for menu in menus %}
    <div class="menu-item">
