# WP Final Backend APIs

本期末專案的後端API安裝與執行步驟如下：

#### Installation

1. 由於本專案的後端是使用Python Flask Framework，請確保本地伺服器有安裝Python 3.8以上的版本與Pip套件管理工具。安裝步驟如下：

```bash
cd backend
pip3 install -r requirements.txt
```

2. 由於專案會與資料庫[MongoDB Atlas](https://www.mongodb.com/)做連結，請先於ＭongoDB中新建Database（名稱為 `db`）以及Collection名稱為（名稱為 `test`）。
3. 為了與資料庫做連結，請新建本地的檔案 `.ini`：

```bash
touch .ini
```

4. 請編輯 `ini`檔案，請確認要在 `.net/`後面有 `db`：

```
[PROD]
DB_URI = mongodb+srv://<username>:<password>@<clustername>.<yourcode>.mongodb.net/db?retryWrites=true&w=majority
```

#### Execution

請執行以下指令：

```bash
python3 run.py
```
