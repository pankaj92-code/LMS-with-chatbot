
# 📚 College Library — Full Stack Starter

Tech: **HTML, CSS, JavaScript, PHP (PDO), MySQL, Python (Flask chatbot)**

## 🔧 Setup (Local, XAMPP/WAMP)
1. **Clone/Copy** this folder `library_management_starter` into your web root, e.g. `C:/xampp/htdocs/library_management_starter`.
2. Start **Apache** and **MySQL** in XAMPP.
3. Open **phpMyAdmin** → run the SQL from `api/schema.sql` (or run `mysql -u root < api/schema.sql`). This creates DB `library_db` and tables.
4. Check DB config in `api/config.php` (user, password). Default is `root` with blank password.
5. Visit `http://localhost/library_management_starter/index.html`.

## 🔐 Logins
- Register a **student** and **admin** from the **Register/Login** modal.
- Admin panel: `admin.html` (after admin login from modal).

## 📦 PHP API Endpoints
- `api/auth.php` — student/admin register+login
- `api/books.php` — search/list/add/delete
- `api/members.php` — member status (current holdings, total issues)
- `api/borrow.php` — issue/return/lookup with **30 days due** and **₹5/day** fine calculation
- `api/report.php` — full history
- `api/feedback.php` — store feedback
- `api/chat_proxy.php` — proxies to Python chatbot

> Browser **Print** → **Save as PDF** is supported for reports.

## 🤖 Python Chatbot
1. Install deps:
   ```bash
   pip install flask mysql-connector-python
   ```
2. Run the bot:
   ```bash
   python chatbot.py
   ```
3. The frontend calls PHP → `chat_proxy.php` → Python (`http://127.0.0.1:5055/ask`).

**Policy**: Bot answers **only about books** (authors/titles/ISBN/branch). It never exposes student data.

## 🧮 Borrow Rules
- Issue → Due = Issue + **30 days**.
- Fine = **₹5/day** after due until returned.

## 🧰 Notes
- Catalogue table is scrollable.
- 3D-like animated background uses a lightweight **canvas particles** effect.
- You can customize theme in `styles.css`.
- Security hardening (sessions, CSRF, validation) can be added later for production.

——
Generated: 2025-08-29
