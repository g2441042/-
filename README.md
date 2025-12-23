# GakuMeshi（学食レビュー＆投票アプリ）

## 1. アプリケーション企画 (Business Analyst)
### ペルソナ
- **ターゲット:** 学食のメニュー選びで失敗したくない学生
- **特徴:** 節約志向だが、美味しいものを食べたい欲求が強い。

### ストーリーボード
1. 昼休み前、本アプリで今日の「日替わり定食」の評価をチェック。
2. 先週の「ハンバーグ定食」が低評価（固かった）なのを知り、今日は「カレー」を選択。
3. 満足した結果を星5つで投稿。

## 2. システム構成図 (Architect)
```mermaid
graph TD
    User((ユーザー)) -- HTTPS --> Web[Web Server: Nginx]
    Web --> App[Application Server: Flask/Python]
    App --> DB[(Database: PostgreSQL)]
    
    subgraph "Web 3 Layer Architecture"
    Web
    App
    DB
    end
