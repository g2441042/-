import os
# .envファイルを読み込むためのライブラリ
# データベースのパスワードや秘密鍵などの機密情報を環境変数として管理するために使用します
from dotenv import load_dotenv
load_dotenv()

# Flask: Webアプリを作るためのフレームワーク
# render_template_string: HTMLテンプレート（文字列）を表示する関数
# request: フォームから送られてきたデータを受け取る
# redirect, url_for: 別のページへ転送する
# flash: 一時的なメッセージ（「登録しました」など）を表示する
from flask import Flask, render_template_string, request, redirect, url_for, flash

# SQLAlchemy: データベースをPythonのクラスとして扱うためのライブラリ（ORM）
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# アプリケーション本体の作成
app = Flask(__name__)

# --- セキュリティと設定 ---
# セッション情報（ログイン状態など）やフラッシュメッセージを暗号化するためのキー
# 本番環境では推測されにくいランダムな文字列にする必要があります
app.config['SECRET_KEY'] = 'dev-secret-key'

# データベースの接続先設定
# 環境変数 'DATABASE_URL' があればそれを使い、なければローカルのPostgreSQLを使います
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/gakumeshi_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # メモリ節約のため変更追跡機能をオフ

# データベース操作用オブジェクトの作成
db = SQLAlchemy(app)

# ==========================================
# データベースのモデル定義 (テーブルの設計図)
# ==========================================

class Menu(db.Model):
    """
    メニュー（料理）情報を保存するテーブル
    """
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)      # メニューID (自動で連番が振られる)
    name = db.Column(db.String(100), nullable=False)  # 料理名 (必須入力)
    price = db.Column(db.Integer, nullable=False)     # 価格 (必須入力)
    category = db.Column(db.String(50))               # カテゴリ（定食、カレー、麺類など）

class Review(db.Model):
    """
    各メニューに対するレビュー（口コミ）を保存するテーブル
    """
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)      # レビューID
    user_name = db.Column(db.String(80))              # 投稿者名
    
    # どのメニューへのレビューかを紐付けるための外部キー (menusテーブルのidを参照)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'))
    
    rating = db.Column(db.Integer, nullable=False)    # 評価 (1〜5の星の数)
    comment = db.Column(db.Text)                      # コメント本文
    likes = db.Column(db.Integer, default=0)          # 「いいね」の数 (初期値は0)
    
    # リレーション設定: 
    # これにより、menu.reviews でそのメニューに関連するレビュー一覧を取得できるようになる
    menu = db.relationship('Menu', backref='reviews')

# ==========================================
# フロントエンド (HTMLテンプレート)
# ==========================================

# メイン画面のHTML
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>GakuMeshi Pro - 学食レビュー</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* 全体のスタイル定義 */
        body { font-family: "Helvetica Neue", Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f0f2f5; color: #333; }
        
        /* ダッシュボード（上部の統計情報） */
        .dashboard { display: flex; justify-content: space-between; margin-bottom: 20px; gap: 15px; }
        .stat-card { background: white; flex: 1; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; border-bottom: 4px solid #3498db; }
        .stat-number { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; font-size: 0.9em; }

        /* フラッシュメッセージ（成功/失敗の通知） */
        .alert { padding: 15px; margin-bottom: 20px; border-radius: 5px; color: white; animation: fadeIn 0.5s; }
        .alert-success { background-color: #2ecc71; }
        .alert-error { background-color: #e74c3c; }

        /* 検索・フィルタエリア */
        .controls { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .category-tags a { display: inline-block; padding: 5px 12px; background: #eef2f7; border-radius: 20px; color: #555; text-decoration: none; margin-right: 5px; font-size: 0.9em; transition: 0.3s; }
        .category-tags a:hover, .category-tags a.active { background: #3498db; color: white; }

        /* メニューカードのデザイン */
        .card { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        
        .menu-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
        .price-tag { font-size: 1.3em; font-weight: bold; color: #2c3e50; }
        .category-badge { background: #9b59b6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; vertical-align: middle; margin-left: 10px; }

        /* ボタン類のスタイル */
        .btn { padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; color: white; text-decoration: none; font-size: 14px; }
        .btn-add { background: linear-gradient(135deg, #2ecc71, #27ae60); }
        .btn-edit { background-color: #f39c12; }
        .btn-del { background-color: #e74c3c; }
        .btn-sub { background-color: #3498db; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;}
        
        /* いいねボタン */
        .like-btn { background: none; border: 1px solid #ddd; color: #888; padding: 3px 8px; border-radius: 15px; cursor: pointer; transition: 0.2s; }
        .like-btn:hover { color: #e74c3c; border-color: #e74c3c; background: #fff0f0; }

        /* フォーム部品 */
        input, select { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <h1 style="text-align:center; color:#2c3e50;"><i class="fas fa-utensils"></i> GakuMeshi Dashboard</h1>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">
                    <i class="fas fa-info-circle"></i> {{ message }}
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <div class="dashboard">
        <div class="stat-card">
            <div class="stat-number">{{ stats.total_menus }}</div>
            <div class="stat-label">登録メニュー数</div>
        </div>
        <div class="stat-card" style="border-bottom-color: #e67e22;">
            <div class="stat-number">¥{{ stats.avg_price }}</div>
            <div class="stat-label">平均価格</div>
        </div>
        <div class="stat-card" style="border-bottom-color: #27ae60;">
            <div class="stat-number">{{ stats.total_reviews }}</div>
            <div class="stat-label">総レビュー数</div>
        </div>
    </div>

    <div class="controls">
        <div style="margin-bottom: 15px;" class="category-tags">
            <b>📂 カテゴリ:</b>
            <a href="/" class="{{ 'active' if not current_cat else '' }}">すべて</a>
            <a href="/?category=定食" class="{{ 'active' if current_cat == '定食' else '' }}">🍱 定食</a>
            <a href="/?category=カレー" class="{{ 'active' if current_cat == 'カレー' else '' }}">🍛 カレー</a>
            <a href="/?category=麺類" class="{{ 'active' if current_cat == '麺類' else '' }}">🍜 麺類</a>
            <a href="/?category=丼もの" class="{{ 'active' if current_cat == '丼もの' else '' }}">🍚 丼もの</a>
        </div>
        
        <form action="/" method="GET" style="display:flex; gap:10px;">
            <input type="hidden" name="category" value="{{ current_cat }}">
            <input type="text" name="search" placeholder="メニュー名で検索..." value="{{ search_query }}" style="flex:1;">
            <select name="sort">
                <option value="new" {% if sort_order == 'new' %}selected{% endif %}>新着順</option>
                <option value="price_asc" {% if sort_order == 'price_asc' %}selected{% endif %}>価格が安い順</option>
                <option value="rating" {% if sort_order == 'rating' %}selected{% endif %}>評価が高い順</option>
            </select>
            <button type="submit" class="btn btn-edit"><i class="fas fa-search"></i> 検索</button>
            <a href="/" class="btn" style="background:#95a5a6; display:inline-flex; align-items:center;">リセット</a>
        </form>
    </div>

    <div class="card" style="border-left: 5px solid #27ae60;">
        <h3>➕ 新メニュー登録</h3>
        <form method="POST" action="/add_menu">
            <input type="text" name="name" required placeholder="メニュー名" style="width:30%;">
            <input type="number" name="price" required min="0" placeholder="価格" style="width:20%;">
            <select name="category" required style="width:20%;">
                <option value="定食">🍱 定食</option>
                <option value="カレー">🍛 カレー</option>
                <option value="麺類">🍜 麺類</option>
                <option value="丼もの">🍚 丼もの</option>
                <option value="その他">🍴 その他</option>
            </select>
            <button type="submit" class="btn btn-add">追加</button>
        </form>
    </div>

    {% for menu in menus %}
    <div class="card">
        <div class="menu-header">
            <div>
                <h2 style="margin: 0; display: inline;">{{ menu.name }}</h2>
                <span class="category-badge">{{ menu.category }}</span>
                {% if menu.price == stats.max_price %}<span style="color:red; font-size:0.8em; margin-left:5px;">🔥最高値</span>{% endif %}
                {% if menu.price == stats.min_price %}<span style="color:green; font-size:0.8em; margin-left:5px;">💰最安値</span>{% endif %}
            </div>
            <div>
                <span class="price-tag">¥{{ menu.price }}</span>
                <a href="/edit_menu/{{ menu.id }}" style="color:#f39c12; margin-left:10px;"><i class="fas fa-edit"></i></a>
                <form action="/delete_menu/{{ menu.id }}" method="POST" style="display:inline;" onsubmit="return confirm('削除しますか？');">
                    <button type="submit" style="background:none; border:none; color:#e74c3c; cursor:pointer;"><i class="fas fa-trash"></i></button>
                </form>
            </div>
        </div>

        <ul style="list-style:none; padding:0;">
            {% for review in menu.reviews %}
                <li style="background:#fafafa; padding:10px; margin-bottom:5px; border-radius:5px; display:flex; justify-content:space-between;">
                    <div>
                        <span style="color:#f1c40f;">{{ "★" * review.rating }}</span>
                        <b>{{ review.user_name }}:</b> {{ review.comment }}
                    </div>
                    <div>
                        <form action="/like_review/{{ review.id }}" method="POST" style="display:inline;">
                            <button type="submit" class="like-btn">
                                <i class="fas fa-thumbs-up"></i> {{ review.likes }}
                            </button>
                        </form>
                        <form action="/delete_review/{{ review.id }}" method="POST" style="display:inline;">
                             <button type="submit" style="border:none; background:none; color:#ccc; cursor:pointer;">×</button>
                        </form>
                    </div>
                </li>
            {% else %}
                <li style="color:#aaa;">まだレビューはありません。</li>
            {% endfor %}
        </ul>

        <form method="POST" action="/add_review/{{ menu.id }}" style="margin-top:15px; display:flex; gap:5px;">
            <input type="text" name="user_name" placeholder="名前" required size="10">
            <select name="rating">
                <option value="5">★★★★★</option>
                <option value="4">★★★★</option>
                <option value="3">★★★</option>
                <option value="2">★★</option>
                <option value="1">★</option>
            </select>
            <input type="text" name="comment" placeholder="感想..." style="flex:1;">
            <button type="submit" class="btn btn-sub">投稿</button>
        </form>
    </div>
    {% endfor %}
</body>
</html>
"""

# 編集画面用のHTMLテンプレート（簡易版）
EDIT_TEMPLATE = """
<!doctype html>
<html>
<head><title>編集</title><style>body{padding:20px; font-family:sans-serif;}</style></head>
<body>
    <h2>✏️ 編集: {{ menu.name }}</h2>
    <form method="POST">
        <p>名前: <input type="text" name="name" value="{{ menu.name }}" required></p>
        <p>価格: <input type="number" name="price" value="{{ menu.price }}" required></p>
        <p>カテゴリ: 
            <select name="category">
                <option value="定食" {% if menu.category=='定食' %}selected{% endif %}>定食</option>
                <option value="カレー" {% if menu.category=='カレー' %}selected{% endif %}>カレー</option>
                <option value="麺類" {% if menu.category=='麺類' %}selected{% endif %}>麺類</option>
                <option value="丼もの" {% if menu.category=='丼もの' %}selected{% endif %}>丼もの</option>
                <option value="その他" {% if menu.category=='その他' %}selected{% endif %}>その他</option>
            </select>
        </p>
        <button type="submit">更新</button> <a href="/">キャンセル</a>
    </form>
</body>
</html>
"""

# ==========================================
# バックエンド処理 (ルーティング設定)
# ==========================================

# --- トップページ処理 ---
@app.route('/')
def index():
    # URLパラメータの取得 (?search=...&sort=...)
    search_query = request.args.get('search', '')
    sort_order = request.args.get('sort', 'new')
    current_cat = request.args.get('category', '')
    
    # データの取得とフィルタリング
    query = Menu.query
    if search_query: 
        query = query.filter(Menu.name.contains(search_query)) # 部分一致検索
    if current_cat: 
        query = query.filter(Menu.category == current_cat)     # カテゴリ一致
    
    # 並び替え処理
    if sort_order == 'price_asc': 
        query = query.order_by(Menu.price) # 価格昇順
    elif sort_order == 'rating': 
        # レビューテーブルと結合して、平均評価順に並べる (高度なSQL操作)
        query = query.outerjoin(Review).group_by(Menu.id).order_by(func.avg(Review.rating).desc().nullslast())
    else: 
        query = query.order_by(Menu.id.desc()) # 新着順(ID降順)
        
    all_menus = query.all()
    
    # 統計情報の計算 (ダッシュボード用)
    total_menus = Menu.query.count()
    total_reviews = Review.query.count()
    avg_price = db.session.query(func.avg(Menu.price)).scalar()
    avg_price = int(avg_price) if avg_price else 0
    max_price = db.session.query(func.max(Menu.price)).scalar()
    min_price = db.session.query(func.min(Menu.price)).scalar()
    
    stats = {
        'total_menus': total_menus, 'total_reviews': total_reviews,
        'avg_price': avg_price, 'max_price': max_price, 'min_price': min_price
    }

    # テンプレートを表示
    return render_template_string(HTML_TEMPLATE, menus=all_menus, stats=stats, search_query=search_query, sort_order=sort_order, current_cat=current_cat)

# --- メニュー追加処理 ---
@app.route('/add_menu', methods=['POST'])
def add_menu():
    try:
        # フォームからデータを受け取り、DBに保存
        new_menu = Menu(
            name=request.form.get('name'),
            price=request.form.get('price'),
            category=request.form.get('category')
        )
        db.session.add(new_menu)
        db.session.commit()
        flash(f'メニュー「{new_menu.name}」を追加しました！', 'success')
    except:
        flash('エラーが発生しました', 'error')
    return redirect(url_for('index'))

# --- メニュー編集処理 ---
@app.route('/edit_menu/<int:id>', methods=['GET', 'POST'])
def edit_menu(id):
    menu = Menu.query.get_or_404(id) # IDからメニュー検索 (なければ404エラー)
    if request.method == 'POST':
        # データの更新処理
        menu.name = request.form.get('name')
        menu.price = request.form.get('price')
        menu.category = request.form.get('category')
        db.session.commit()
        flash('メニュー情報を更新しました', 'success')
        return redirect(url_for('index'))
    return render_template_string(EDIT_TEMPLATE, menu=menu)

# --- メニュー削除処理 ---
@app.route('/delete_menu/<int:id>', methods=['POST'])
def delete_menu(id):
    menu = Menu.query.get_or_404(id)
    # 関連するレビューも一緒に削除 (外部キー制約エラー防止のため)
    Review.query.filter_by(menu_id=id).delete()
    db.session.delete(menu)
    db.session.commit()
    flash('メニューを削除しました', 'error')
    return redirect(url_for('index'))

# --- レビュー投稿処理 ---
@app.route('/add_review/<int:menu_id>', methods=['POST'])
def add_review(menu_id):
    new_review = Review(
        menu_id=menu_id,
        user_name=request.form.get('user_name'),
        rating=request.form.get('rating'),
        comment=request.form.get('comment')
    )
    db.session.add(new_review)
    db.session.commit()
    flash('レビューを投稿しました！ありがとうございます。', 'success')
    return redirect(url_for('index'))

# --- レビューへの「いいね」処理 ---
@app.route('/like_review/<int:id>', methods=['POST'])
def like_review(id):
    review = Review.query.get_or_404(id)
    review.likes += 1 # カウントアップ
    db.session.commit()
    return redirect(url_for('index'))

# --- レビュー削除処理 ---
@app.route('/delete_review/<int:id>', methods=['POST'])
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash('レビューを削除しました', 'error')
    return redirect(url_for('index'))

# ==========================================
# アプリケーションの起動
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        # データベースファイル(テーブル)が存在しなければ作成する
        db.create_all()
    # サーバーを起動 (debug=Trueにするとエラー時に詳細が表示される)
    app.run(debug=True, host='0.0.0.0')
