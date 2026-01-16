import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# アプリケーション設定
app = Flask(__name__)

# データベース接続設定 (PostgreSQL)
# ※ローカルで動かす場合は自分の環境に合わせて書き換える必要があります
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/gakumeshi_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- データベースのモデル定義 (ER図と同じもの) ---
class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50))

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False) # 簡易化のためユーザーテーブル結合せず直接保存
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    
    # リレーション設定
    menu = db.relationship('Menu', backref='reviews')

# --- 画面表示 (HTML) ---
HTML_TEMPLATE = """
<!doctype html>
<html>
<head><title>GakuMeshi - 学食レビュー</title></head>
<body>
    <h1>🍛 GakuMeshi メニュー一覧</h1>
    
    <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 20px;">
        <h3>新メニュー登録</h3>
        <form method="POST" action="/add_menu">
            名前: <input type="text" name="name" required>
            価格: <input type="number" name="price" required>
            <input type="submit" value="追加">
        </form>
    </div>

    <ul>
        {% for menu in menus %}
        <li>
            <b>{{ menu.name }}</b> - {{ menu.price }}円
            (レビュー: {{ menu.reviews|length }}件)
            <ul>
                {% for review in menu.reviews %}
                    <li>★{{ review.rating }} : {{ review.comment }} (by {{ review.user_name }})</li>
                {% endfor %}
            </ul>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
"""

# --- ルーティング (CRUD操作) ---
@app.route('/')
def index():
    # 全てのメニューをDBから取得して表示 (Read)
    all_menus = Menu.query.all()
    return render_template_string(HTML_TEMPLATE, menus=all_menus)

@app.route('/add_menu', methods=['POST'])
def add_menu():
    # メニューをDBに追加 (Create)
    name = request.form.get('name')
    price = request.form.get('price')
    
    new_menu = Menu(name=name, price=price)
    db.session.add(new_menu)
    db.session.commit()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # テーブルが存在しなければ作成する
    with app.app_context():
        db.create_all()
    app.run(debug=True)
