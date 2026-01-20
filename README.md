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

erDiagram
    %% 1つのメニューに対し、0個以上のレビューが存在する
    MENUS ||--o{ REVIEWS : "has"

    MENUS {
        int id PK "ID (主キー)"
        string name "メニュー名"
        int price "価格"
        string category "カテゴリ"
    }

    REVIEWS {
        int id PK "ID (主キー)"
        string user_name "投稿者名"
        int rating "星評価 (1-5)"
        string comment "コメント"
        int likes "いいね数"
        datetime created_at "投稿日時"
        int menu_id FK "メニューID (外部キー)"
    }
