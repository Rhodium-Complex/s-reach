# S-REACH

## English

### Description
S-REACH is a chemical compound database web application built with Django and RDKit, designed to facilitate chemical structure-based searching, compound registration, ordering, and management. It features advanced molecular structure search capabilities using SMILES notation and interactive structure drawing. The application is containerized using Docker for easy setup and deployment.

### Features
-   **Chemical Structure Search**: Advanced molecular structure search using SMILES notation and substructure matching
-   **Interactive Structure Editor**: Built-in JSME molecular editor for drawing and editing chemical structures
-   **Compound Database Management**: Create, update, and manage chemical compound records with spectroscopic data
-   **Analytical Data Storage**: Support for 1H NMR, 13C NMR, IR, UV-vis, and XRD spectral data
-   **Order Management System**: Inventory tracking and ordering system for chemical compounds
-   **RDKit Integration**: Powered by RDKit for chemical informatics and structure processing
-   **Containerized Deployment**: Dockerized application for consistency across environments

### Requirements
-   Docker
-   Docker Compose

### Installation & Usage
1.  Clone the repository.
2.  Navigate to the project root directory.
3.  Run the application using Docker Compose:
    ```bash
    docker-compose up -d --build
    ```
4.  Access the application at `http://localhost:80`.

### Technologies Used
-   **Backend:** Django, Python, RDKit (Chemical Informatics)
-   **Frontend:** HTML, CSS, JavaScript, JSME (Molecular Editor)
-   **Database:** PostgreSQL with RDKit extension
-   **Chemical Structure Processing:** SMILES, MOL format support
-   **Spectroscopic Data:** NMR, IR, UV-vis, XRD file storage
-   **Web Server:** Nginx
-   **Containerization:** Docker, Docker Compose

---

## 日本語 (Japanese)

### 概要
S-REACHは、DjangoとRDKitで構築された化学化合物データベースWebアプリケーションです。化学構造式に基づく検索、化合物登録、注文、管理を容易にするために設計されています。SMILES記法と対話的構造描画を使用した高度な分子構造検索機能を特徴としています。Dockerを使用してコンテナ化されており、簡単なセットアップとデプロイが可能です。

### 機能
-   **化学構造検索**: SMILES記法と部分構造マッチングを使用した高度な分子構造検索
-   **対話的構造エディタ**: 化学構造の描画と編集のための内蔵JSMEエディタ
-   **化合物データベース管理**: 分光データ付き化学化合物レコードの作成、更新、管理
-   **分析データ保存**: 1H NMR、13C NMR、IR、UV-vis、XRDスペクトルデータのサポート
-   **注文管理システム**: 化学化合物の在庫追跡と注文システム
-   **RDKit統合**: 化学情報学と構造処理のためのRDKitを基盤とした機能
-   **コンテナ化デプロイメント**: 環境間の一貫性を保つためのDockerアプリケーション

### 要件
-   Docker
-   Docker Compose

### インストールと使用方法
1.  リポジトリをクローンします。
2.  プロジェクトのルートディレクトリに移動します。
3.  Docker Composeを使用してアプリケーションを実行します:
    ```bash
    docker-compose up -d --build
    ```
4.  `http://localhost:80`でアプリケーションにアクセスします。

### 使用技術
-   **バックエンド:** Django, Python, RDKit（化学情報学）
-   **フロントエンド:** HTML, CSS, JavaScript, JSME（分子エディタ）
-   **データベース:** PostgreSQL with RDKit拡張
-   **化学構造処理:** SMILES、MOL形式サポート
-   **分光データ:** NMR、IR、UV-vis、XRDファイル保存
-   **Webサーバー:** Nginx
-   **コンテナ化:** Docker, Docker Compose
