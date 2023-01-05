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

設定這三個參數的方法有三種：

* 已經寄給助教信箱（eewebprogramming@googlegroups.com）：請收信件，信件名稱 `[G15] backend ini`，請將信件中的 `.txt`檔案內文字附加進入您的 `.ini`中。
* 像專案開發者索取：請寄信至austenpsy@gmail.com索取。
* 請依照[此網站](https://github.com/twtrubiks/Flask-Mail-example)的步驟設定寄件者參數資訊。

6. 本後端之所有DB規範、API介面、以及後端其他功能，請參考此[API文件](https://hackmd.io/@judycpc/rk5wzFbdj)。

## Execution

請執行以下指令：

```python3
python3 run.py
```

## Testing

請依照此[API文件](https://hackmd.io/@judycpc/rk5wzFbdj)測試各類API。

##### 以下為預約寄信為範例，以在Postman中測試為例：

1. 創建治療師帳戶，請以 `POST` 方法中輸入 `127.0.0.1:5000/api/signup/`，在header中設定 `'Content-Type': 'application/json'`，並在 `body`中選擇 `raw`，輸入（記得刪除註解）：

```javascript
{
    "username": "therapistTA", // your therapist username
    "password": "123", // your password
    "name": "therapistTA", // your name
    "identity": "therapist",
    "email": "your.email.1@gmail.com" // your first email
}
```

2. 創建個案帳戶，請以 `POST` 方法中輸入 `127.0.0.1:5000/api/signup/`，在header中設定 `'Content-Type': 'application/json'`，並在 `body`中選擇 `raw`，輸入（記得刪除註解）：

```javascript
{
    "username": "clientTA", // your client username
    "password": "123", // your password
    "name": "clientTA", // your another name
    "identity": "client",
    "email": "your.email.2@gmail.com" // your another email
}
```

3. 創建預約，請以 `POST` 方法中輸入 `127.0.0.1:5000/api/appointments/create/`，在header中設定 `'Content-Type': 'application/json'`，並在 `body`中選擇 `raw`，輸入（記得刪除註解）：

```javascript
{
    "therapist": "therapistTA", // your therapist username
    "client": "clientTA", // your client username
    "time": "yyyy/mm/dd_hh", //your current time + 1 hour
    "meeting_code": "xyz-qwer-wef" //random code by format xxx-xxxx-xxx
}
```

4. 結果：上步驟結束後，可以在前端馬上發現預約記錄，並在一分鐘後，該預約記錄就會變成可以填寫的評論的狀態，於此同時您就會在兩個信箱中分別收到不同信件。
