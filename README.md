# WP Final Backend APIs

WP1111第十五組，本期末專案的後端API安裝與執行步驟如下：

## Installation

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

4. 請編輯 `.ini`檔案，請確認要在 `.net/`後面有 `db`：

```
[PROD]
DB_URI = mongodb+srv://<username>:<password>@<clustername>.<yourcode>.mongodb.net/db?retryWrites=true&w=majority
```

5. 因為本專案有牽涉自動化EMAIL通知服務，請編輯 `.ini`檔案加入以下三行：

```
MAIL_SENDER = <sender-name>
MAIL_USERNAME = <your-gmail-account>@gmail.com
MAIL_PASSWORD = <16-digits-passwords>
```

設定這三個參數的方法有兩種：

* 像專案開發者索取：請寄信至austenpsy@gmail.com索取。
* 請依照[此網站](https://github.com/twtrubiks/Flask-Mail-example)的步驟設定寄件者參數資訊。

6. 本後端之所有DB規範、API介面、以及後端其他功能，請參考此[API文件](https://hackmd.io/@judycpc/rk5wzFbdj)（請登入並勿編輯該文件，謝謝）。



## Execution

請執行以下指令：

```bash
python3 run.py
```
