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

# --- モデル定義 ---
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
# 編集画面も含めたHTMLテンプレート
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>GakuMeshi - 学食レビュー</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { font-family: "Helvetica Neue", Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f4f9; color: #333; }
        h1 { text-align: center; color: #2c3e50; }
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .btn { padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; color: white; text-decoration: none; font-size: 14px; }
        .btn-add { background-color: #27ae60; }
        .btn-del { background-color: #e74c3c; }
        .btn-edit { background-color: #f39c12; }
        .btn-sub { background-color: #3498db; }
        .menu-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }
        input[type="text"], input[type="number"], select { padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-right: 5px; }
        .review-list { list-style: none; padding: 0; }
        .review-list li { background: #fafafa; border-bottom: 1px solid #eee; padding: 8px; font-size: 0.9em; }
        .rating { color: #f1c40f; }
    </style>
</head>
<body>
    <h1>🍛 GakuMeshi Menu</h1>
    
    <div class="card">
        <h3>➕ 新メニュー登録</h3>
        <form method="POST" action="/add_menu">
            <input type="text" name="name" required placeholder="メニュー名 (例: カツ丼)">
            <input type="number" name="price" required placeholder="価格 (例: 500)">
            <input type="submit" value="追加" class="btn btn-add">
        </form>
    </div>

    {% for menu in menus %}
    <div class="card">
        <div class="menu-header">
            <div>
                <h2 style="margin: 0; display: inline;">{{ menu.name }}</h2>
                <span style="font-size: 1.2em; color: #555; margin-left: 10px;">¥{{ menu.price }}</span>
            </div>
            <div>
                <a href="/edit_menu/{{ menu.id }}" class="btn btn-edit">編集</a>
                
                <form action="/delete_menu/{{ menu.id }}" method="POST" style="display:inline;" onsubmit="return confirm('本当に削除しますか？');">
                    <input type="submit" value="削除" class="btn btn-del">
                </form>
            </div>
        </div>
        
        <p>📊 レビュー: {{ menu.reviews|length }}件</p>
        
        <ul class="review-list">
            {% for review in menu.reviews %}
                <li>
                    <span class="rating">{{ "★" * review.rating }}</span> 
                    {{ review.comment }} <small style="color: #777;">(by {{ review.user_name }})</small>
                    <form action="/delete_review/{{ review.id }}" method="POST" style="display:inline; float:right;">
                        <button type="submit" style="background:none; border:none; color:#999; cursor:pointer;" onclick="return confirm('レビューを消しますか？');">×</button>
                    </form>
                </li>
            {% else %}
                <li style="color: #999;">まだレビューはありません。一番乗りしよう！</li>
            {% endfor %}
        </ul>

        <div style="margin-top: 15px; border-top: 1px dashed #ddd; padding-top: 10px;">
            <form method="POST" action="/add_review/{{ menu.id }}">
                <input type="text" name="user_name" placeholder="名前" required size="10">
                <select name="rating">
                    <option value="5">★★★★★</option>
                    <option value="4">★★★★</option>
                    <option value="3">★★★</option>
                    <option value="2">★★</option>
                    <option value="1">★</option>
                </select>
                <input type="text" name="comment" placeholder="感想を入力..." size="25">
                <input type="submit" value="投稿" class="btn btn-sub">
            </form>
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

# 編集用画面テンプレート
EDIT_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>メニュー編集</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background-color: #f4f4f9; }
        .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input[type="text"], input[type="number"] { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        .btn { padding: 10px 20px; border: none; cursor: pointer; color: white; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>✏️ メニュー情報の編集</h2>
        <form method="POST">
            <label>メニュー名:</label>
            <input type="text" name="name" value="{{ menu.name }}" required>
            <label>価格:</label>
            <input type="number" name="price" value="{{ menu.price }}" required>
            <div style="margin-top: 20px;">
                <input type="submit" value="更新する" class="btn" style="background-color: #27ae60;">
                <a href="/" class="btn" style="background-color: #7f8c8d; text-decoration: none;">キャンセル</a>
            </div>
        </form>
    </div>
</body>
</html>
"""

# --- ルーティング ---
@app.route('/')
def index():
    all_menus = Menu.query.order_by(Menu.id.desc()).all() # 新しい順に表示
    return render_template_string(HTML_TEMPLATE, menus=all_menus)

@app.route('/add_menu', methods=['POST'])
def add_menu():
    name = request.form.get('name')
    price = request.form.get('price')
    new_menu = Menu(name=name, price=price)
    db.session.add(new_menu)
    db.session.commit()
    return redirect(url_for('index'))

# ★追加機能: 編集画面の表示と更新 (Update)
@app.route('/edit_menu/<int:id>', methods=['GET', 'POST'])
def edit_menu(id):
    menu = Menu.query.get_or_404(id)
    if request.method == 'POST':
        # 更新処理
        menu.name = request.form.get('name')
        menu.price = request.form.get('price')
        db.session.commit()
        return redirect(url_for('index'))
    # 編集画面を表示
    return render_template_string(EDIT_TEMPLATE, menu=menu)

@app.route('/delete_menu/<int:id>', methods=['POST'])
def delete_menu(id):
    menu = Menu.query.get_or_404(id)
    Review.query.filter_by(menu_id=id).delete()
    db.session.delete(menu)
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
