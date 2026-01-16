# GakuMeshi（学食レビュー＆投票システム）

本プロジェクトは、大学内の学食メニューを可視化し、学生の食生活を豊かにするためのWebアプリケーションです。

---

## 1. 企画定義 (Business Analyst)

### ペルソナ (Persona)
- **名前:** 佐藤 健太 (21歳、大学3年生)
- **悩み:** 昼休みは混雑しており、メニュー選びで失敗したくない。限られた予算で満足度の高い昼食をとりたい。
- **目標:** 事前にメニューの評判を確認し、自分の好みに合った食事をスムーズに選びたい。

### モチベーション・グラフ (Motivation Graph)
ユーザーが本アプリを利用する動機を以下の3点に定義します。
1. **経済的動機:** 「安くてボリュームがあるメニューを知りたい」
2. **効率的動機:** 「混雑前に今日の当たりメニューを特定したい」
3. **社会的動機:** 「自分の美味しいという発見を他の学生にも共有したい」

### ストーリーボード (Story Board)
1. **確認:** 3限の授業中、スマホで今日の「日替わり定食」のレビューをチェック。
2. **判断:** 「今日の唐揚げは揚げたてで美味しい」というリアルタイムな口コミを見て、A食堂に行くことを決める。
3. **行動:** 食堂で実際に食べ、満足。
4. **共有:** 食べ終わった後、星4つの評価と「衣がサクサクでした！」というコメントを投稿する。

---

## 2. システム設計 (Architect)

### システム構成図 (System Architecture)
GitHubのMermaid機能を使用して、Web 3層構成を定義しています。

```mermaid
graph TD
    User((ユーザー)) -- HTTP/HTTPS --> Web[Web Server: Nginx]
    Web --> App[Application Server: Python/Flask]
    App --> DB[(Database: PostgreSQL)]
    
    subgraph "Web 3 Layer"
    Web
    App
    DB
    end


### 非機能要件
システム運用における目標値を以下のように定義します。
- **RPO (目標復旧時点):** 24時間（1日1回のフルバックアップを実施）
- **RTO (目標復旧時間):** 4時間以内（障害発生時の代替サーバー起動目標時間）
- **DR (災害対策):** データベースのダンプファイルを外部ストレージ(S3等)に保存。
- **Performance:** 昼休みピーク時（11:30-12:30）の同時接続500ユーザーに対し、応答速度2秒以内を維持。

---

## 3. データベース設計 (DBA)

### ER図 (Entity Relationship Diagram)
RDBを利用するため、以下のデータ構造を定義します。

```mermaid
erDiagram
    Users ||--o{ Reviews : writes
    Menus ||--o{ Reviews : has
    
    Users {
        int id PK "ユーザーID"
        string username "氏名"
        string email "連絡先"
    }
    
    Menus {
        int id PK "メニューID"
        string name "料理名"
        int price "価格"
        string category "分類"
    }

    Reviews {
        int id PK "レビューID"
        int user_id FK "ユーザーID"
        int menu_id FK "メニューID"
        int rating "星評価(1-5)"
        string comment "コメント"
        datetime created_at "投稿日"
    }
