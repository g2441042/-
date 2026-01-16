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
        <div class="header-area">
            <h2 style="margin: 0;">{{ menu.name }} <small>({{ menu.price }}円)</small></h2>
            
            <form action="/delete_menu/{{ menu.id }}" method="POST" onsubmit="return confirm('メニューを削除しますか？\\n(注: 関連するレビューも全て消えます)');">
                <input type="submit" value="メニュー削除" class="delete-btn">
            </form>
        </div>
        
        <p>レビュー数: {{ menu.reviews|length }}件</p>
        
        <ul>
            {% for review in menu.reviews %}
                <li>
                    <b style="color: #f39c12;">{{ "★" * review.rating }}</b> 
                    {{ review.comment }} <small>(by {{ review.user_name }})</small>

                    <form action="/delete_review/{{ review.id }}" method="POST" style="display:inline;">
                        <input type="submit" value="[×削除]" class="review-delete-btn" onclick="return confirm('このレビューを削除してもよろしいですか？');">
                    </form>
                </li>
            {% else %}
                <li style="color: #999;">まだレビューはありません。</li>
            {% endfor %}
        </ul>

        <div class="review-form">
            <b>このメニューのレビューを書く:</b>
            <form method="POST" action="/add_review/{{ menu.id }}">
                <input type="text" name="user_name" placeholder="あなたの名前" required size="10">
                <select name="rating">
                    <option value="5">★★★★★ (5)</option>
                    <option value="4">★★★★ (4)</option>
                    <option value="3">★★★ (3)</option>
                    <option value="2">★★ (2)</option>
                    <option value="1">★ (1)</option>
                </select>
                <input type="text" name="comment" placeholder="感想を一言！" size="30">
                <input type="submit" value="投稿">
            </form>
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

# --- ルーティング ---
@app.route('/')
def index():
    all_menus = Menu.query.all()
    return render_template_string(HTML_TEMPLATE, menus=all_menus)

@app.route('/add_menu', methods=['POST'])
def add_menu():
    name = request.form.get('name')
    price = request.form.get('price')
    new_menu = Menu(name=name, price=price)
    db.session.add(new_menu)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_review/<int:menu_id>', methods=['POST'])
def add_review(menu_id):
    user_name = request.form.get('user_name')
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    new_review = Review(menu_id=menu_id, user_name=user_name, rating=rating, comment=comment)
    db.session.add(new_review)
    db.session.commit()
    return redirect(url_for('index'))

# メニュー削除機能
@app.route('/delete_menu/<int:id>', methods=['POST'])
def delete_menu(id):
    menu = Menu.query.get_or_404(id)
    Review.query.filter_by(menu_id=id).delete()
    db.session.delete(menu)
    db.session.commit()
    return redirect(url_for('index'))

# レビュー削除機能
@app.route('/delete_review/<int:id>', methods=['POST'])
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
