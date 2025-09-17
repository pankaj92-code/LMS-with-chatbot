# flask_backend.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector as mysql
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime, timedelta

# --- CONFIG: adjust these to your MySQL setup ---
DB = dict(host='localhost', user='root', password='', database='library_db', autocommit=True)

app = Flask(__name__)
CORS(app)

# ---------- Helper: DB connection ----------
def get_conn():
    return mysql.connect(**DB)

# ---------- Books helpers (used by chat proxy too) ----------
def find_by_author(cur, author):
    cur.execute("""SELECT title, author, branch, isbn FROM books WHERE author LIKE %s ORDER BY title""", (f"%{author}%",))
    return cur.fetchall()

def find_by_title(cur, title):
    cur.execute("""SELECT title, author, branch, isbn FROM books WHERE title LIKE %s ORDER BY title""", (f"%{title}%",))
    return cur.fetchall()

def find_by_isbn(cur, isbn):
    cur.execute("""SELECT title, author, branch, isbn FROM books WHERE isbn LIKE %s""", (f"%{isbn}%",))
    return cur.fetchall()

# ---------- API: books.php?action=search|list ----------
@app.route("/api/books.php", methods=["GET", "POST"])
def api_books():
    action = request.args.get("action", "").lower()
    data = (request.get_json() or {})
    try:
        con = get_conn()
        cur = con.cursor(dictionary=True)
        if action == "search":
            q = (data.get("q") or "").strip()
            branch = (data.get("branch") or "").strip()
            # simple search: title contains OR isbn contains OR author contains
            params = []
            where = []
            if q:
                where.append("(title LIKE %s OR isbn LIKE %s OR author LIKE %s)")
                params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
            if branch:
                where.append("branch = %s")
                params.append(branch)
            sql = "SELECT title, author, isbn, category, branch, copies FROM books"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY title LIMIT 200"
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            return jsonify({"ok": True, "data": rows})
        elif action == "list":
            cur.execute("SELECT title, author, isbn, category, branch, copies FROM books ORDER BY title LIMIT 500")
            rows = cur.fetchall()
            return jsonify({"ok": True, "data": rows})
        else:
            return jsonify({"ok": False, "message": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500
    finally:
        try:
            cur.close(); con.close()
        except: pass

# ---------- API: members.php?action=status ----------
@app.route("/api/members.php", methods=["GET","POST"])
def api_members():
    action = request.args.get("action", "").lower()
    data = (request.get_json() or {})
    try:
        if action == "status":
            member_id = data.get("member_id") or data.get("id") or ""
            if not member_id:
                return jsonify({"ok": False, "message": "member_id required"}), 400
            con = get_conn(); cur = con.cursor(dictionary=True)
            # fetch basic member info
            cur.execute("SELECT id, name, roll_number FROM students WHERE roll_number=%s OR id=%s LIMIT 1", (member_id, member_id))
            mb = cur.fetchone()
            if not mb:
                return jsonify({"ok": False, "message": "Member not found"},), 404
            # current holdings
            cur.execute("SELECT COUNT(*) as current_count FROM issues WHERE student_id=%s AND return_date IS NULL", (mb['id'],))
            cc = cur.fetchone().get('current_count', 0)
            # total issued
            cur.execute("SELECT COUNT(*) as total_issued FROM issues WHERE student_id=%s", (mb['id'],))
            ti = cur.fetchone().get('total_issued', 0)
            return jsonify({"ok": True, "data": {"name": mb['name'], "roll_number": mb['roll_number'], "current_count": cc, "total_issued": ti}})
        else:
            return jsonify({"ok": False, "message": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500
    finally:
        try:
            cur.close(); con.close()
        except: pass

# ---------- API: borrow.php?action=lookup ----------
@app.route("/api/borrow.php", methods=["GET","POST"])
def api_borrow():
    action = request.args.get("action", "").lower()
    data = (request.get_json() or {})
    try:
        if action == "lookup":
            member_id = data.get("member_id") or ""
            if not member_id:
                return jsonify({"ok": False, "message": "member_id required"}), 400
            con = get_conn(); cur = con.cursor(dictionary=True)
            # find student id
            cur.execute("SELECT id FROM students WHERE roll_number=%s OR id=%s LIMIT 1", (member_id, member_id))
            s = cur.fetchone()
            if not s:
                return jsonify({"ok": False, "message": "Member not found"}), 404
            sid = s['id']
            # fetch issues (including returned ones)
            cur.execute("""SELECT i.id, b.title, i.issue_date, i.due_date, i.return_date,
                           COALESCE(i.fine,0) as fine
                           FROM issues i
                           LEFT JOIN books b ON i.book_id=b.id
                           WHERE i.student_id=%s ORDER BY i.issue_date DESC""", (sid,))
            rows = cur.fetchall()
            # convert dates to iso
            out = []
            for r in rows:
                out.append({
                    "id": r['id'],
                    "title": r['title'],
                    "issue_date": (r['issue_date'].isoformat() if r['issue_date'] else None),
                    "due_date": (r['due_date'].isoformat() if r['due_date'] else None),
                    "return_date": (r['return_date'].isoformat() if r['return_date'] else None),
                    "fine": float(r['fine'] or 0)
                })
            return jsonify({"ok": True, "data": out})
        else:
            return jsonify({"ok": False, "message": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500
    finally:
        try:
            cur.close(); con.close()
        except: pass

# ---------- API: report.php?action=history ----------
@app.route("/api/report.php", methods=["GET","POST"])
def api_report():
    action = request.args.get("action", "").lower()
    data = (request.get_json() or {})
    try:
        if action == "history":
            member_id = data.get("member_id") or ""
            if not member_id:
                return jsonify({"ok": False, "message": "member_id required"}), 400
            con = get_conn(); cur = con.cursor(dictionary=True)
            cur.execute("SELECT id,name,roll_number FROM students WHERE roll_number=%s OR id=%s LIMIT 1", (member_id, member_id))
            mb = cur.fetchone()
            if not mb:
                return jsonify({"ok": False, "message": "Member not found"}), 404
            cur.execute("""SELECT b.title, i.issue_date, i.due_date, i.return_date, COALESCE(i.fine,0) as fine
                           FROM issues i
                           LEFT JOIN books b ON i.book_id=b.id
                           WHERE i.student_id=%s ORDER BY i.issue_date DESC""", (mb['id'],))
            rows = cur.fetchall()
            out = []
            for r in rows:
                out.append({
                    "title": r['title'],
                    "issue_date": (r['issue_date'].isoformat() if r['issue_date'] else None),
                    "due_date": (r['due_date'].isoformat() if r['due_date'] else None),
                    "return_date": (r['return_date'].isoformat() if r['return_date'] else None),
                    "fine": float(r['fine'] or 0)
                })
            return jsonify({"ok": True, "member": {"name": mb['name'], "roll_number": mb['roll_number']}, "data": out})
        else:
            return jsonify({"ok": False, "message": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500
    finally:
        try:
            cur.close(); con.close()
        except: pass

# ---------- API: feedback.php (save feedback) ----------
@app.route("/api/feedback.php", methods=["POST"])
def api_feedback():
    data = (request.get_json() or {})
    name = data.get("name"); email = data.get("email"); branch = data.get("branch"); feedback = data.get("feedback")
    if not (name and email and feedback):
        return jsonify({"ok": False, "message": "name, email and feedback required"}), 400
    try:
        con = get_conn(); cur = con.cursor()
        cur.execute("INSERT INTO feedback (name,email,branch,feedback,created_at) VALUES (%s,%s,%s,%s,%s)",
                    (name,email,branch,feedback, datetime.utcnow()))
        return jsonify({"ok": True, "message": "Saved"})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500
    finally:
        try:
            cur.close(); con.close()
        except: pass

# ---------- API: auth.php?action=student_register|student_login|admin_register|admin_login ----------
@app.route("/api/auth.php", methods=["POST"])
def api_auth():
    action = request.args.get("action", "").lower()
    data = (request.get_json() or {})
    try:
        con = get_conn(); cur = con.cursor(dictionary=True)
        if action == "student_register":
            # expected fields: name, email, roll_number, course, branch, mobile, password, dob, address
            email = data.get("email"); roll = data.get("roll_number"); pwd = data.get("password")
            if not (email and roll and pwd): return jsonify({"ok": False, "message": "email, roll_number and password required"}), 400
            # check exists
            cur.execute("SELECT id FROM students WHERE roll_number=%s OR email=%s LIMIT 1", (roll, email))
            if cur.fetchone():
                return jsonify({"ok": False, "message": "Student already exists"}), 409
            pwd_hash = generate_password_hash(pwd)
            cur.execute("""INSERT INTO students (name,email,roll_number,course,branch,mobile,password_hash,dob,address,created_at)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (data.get("name"), email, roll, data.get("course"), data.get("branch"), data.get("mobile"),
                         pwd_hash, data.get("dob"), data.get("address"), datetime.utcnow()))
            return jsonify({"ok": True, "message": "Registered"})
        elif action == "student_login":
            roll = data.get("roll_number"); pwd = data.get("password")
            if not (roll and pwd): return jsonify({"ok": False, "message": "roll_number and password required"}), 400
            cur.execute("SELECT id,name,password_hash FROM students WHERE roll_number=%s LIMIT 1", (roll,))
            user = cur.fetchone()
            if not user or not check_password_hash(user.get("password_hash",""), pwd):
                return jsonify({"ok": False, "message": "Invalid credentials"}), 401
            # simple response (no session implemented). Frontend can store info if needed.
            return jsonify({"ok": True, "message": "Login success", "data": {"id": user['id'], "name": user['name']}})
        elif action == "admin_register":
            uid = data.get("user_id"); email = data.get("email"); pwd = data.get("password")
            if not (uid and email and pwd): return jsonify({"ok": False, "message": "user_id,email,password required"}), 400
            cur.execute("SELECT id FROM admins WHERE user_id=%s LIMIT 1", (uid,))
            if cur.fetchone():
                return jsonify({"ok": False, "message": "Admin exists"}), 409
            cur.execute("INSERT INTO admins (name,user_id,email,password_hash,created_at) VALUES (%s,%s,%s,%s,%s)",
                        (data.get("name"), uid, email, generate_password_hash(pwd), datetime.utcnow()))
            return jsonify({"ok": True, "message": "Admin registered"})
        elif action == "admin_login":
            uid = data.get("user_id"); pwd = data.get("password")
            if not (uid and pwd): return jsonify({"ok": False, "message": "user_id and password required"}), 400
            cur.execute("SELECT id,name,password_hash FROM admins WHERE user_id=%s LIMIT 1", (uid,))
            admin = cur.fetchone()
            if not admin or not check_password_hash(admin.get("password_hash",""), pwd):
                return jsonify({"ok": False, "message": "Invalid credentials"}), 401
            return jsonify({"ok": True, "message": "Login success", "data": {"id": admin['id'], "name": admin['name']}})
        else:
            return jsonify({"ok": False, "message": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500
    finally:
        try:
            cur.close(); con.close()
        except: pass

# ---------- API: chat_proxy.php (wraps the chatbot logic you had) ----------
# --- Time-based greeting ---
def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greet = "🌅 Good Morning!"
    elif 12 <= hour < 17:
        greet = "☀️ Good Afternoon!"
    elif 17 <= hour < 21:
        greet = "🌇 Good Evening!"
    else:
        greet = "🌙 Good Night!"
    return f"{greet}\nHi! You can ask me about library books or anything else."

# --- Greeting endpoint ---
@app.route("/greeting", methods=["GET"])
def greeting():
    return jsonify({"reply": get_greeting()})

# --- Load pre-trained DialoGPT ---
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

# --- Store chat histories per user ---
chat_histories = {}  # {user_id: chat_history_ids}

# --- Chat endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    user_id = request.json.get("user_id", "default")  # <-- frontend se bhejna hoga
    
    if not user_input:
        return jsonify({"reply": "⚠️ Please enter a valid message."})

    user_input_lower = user_input.lower()

    # --- Greeting detection ---
    greeting_keywords = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "good night"]
    if any(word in user_input_lower for word in greeting_keywords):
        return jsonify({"reply": get_greeting()})

    # --- DialoGPT chatbot flow ---
    try:
        new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")

        if user_id in chat_histories:
            bot_input_ids = torch.cat([chat_histories[user_id], new_input_ids], dim=-1)
        else:
            bot_input_ids = new_input_ids

        chat_history_ids = model.generate(
            bot_input_ids,
            max_length=1000,
            pad_token_id=tokenizer.eos_token_id
        )

        chat_histories[user_id] = chat_history_ids

        reply = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Error: {str(e)}"})


@app.route("/api/chat_proxy.php", methods=["POST"])
def chat_proxy():
    data = (request.get_json() or {})
    q = (data.get("q") or "").strip()
    if not q:
        return jsonify({"answer":"Ask me about books, authors, titles, ISBNs, or branches."})
    try:
        con = get_conn(); cur = con.cursor()
        qlow = q.lower()

        # Author-based
        m = re.search(r'author\s*(?:is|=)?\s*([\w .,\-:;!?]+)', qlow)
        if 'author' in qlow and m:
            author = m.group(1).strip()
            rows = find_by_author(cur, author)
            if not rows: return jsonify({"answer":f'No books found by author \"{author}\".'})
            lines = [f'• {t} — {a} ({b}) ISBN:{i}' for (t,a,b,i) in rows[:20]]
            return jsonify({"answer":'Books by author:\n' + '\n'.join(lines)})

        # Title-based
        if 'book' in qlow or 'title' in qlow:
            mt = re.search(r'(?:book|title)\s*(?:is|=)?\s*([\w .,\-:;!?]+)', qlow)
            if mt:
                title = mt.group(1).strip()
                rows = find_by_title(cur, title)
                if not rows: return jsonify({"answer":f'No matches for title \"{title}\".'})
                lines = [f'• {t} — {a} ({b}) ISBN:{i}' for (t,a,b,i) in rows[:20]]
                return jsonify({"answer":'Matching titles:\n' + '\n'.join(lines)})

        # ISBN-based
        misbn = re.search(r'(?:isbn\s*(?:is|=)?\s*)?(\d{5,13})', qlow)
        if misbn:
            isbn = misbn.group(1)
            rows = find_by_isbn(cur, isbn)
            if not rows: return jsonify({"answer":f'No book found with ISBN {isbn}.'})
            t,a,b,i = rows[0]
            return jsonify({"answer":f'{t} — {a} ({b}) ISBN:{i}'})

        # Branch listing like "show cs books"
        mbr = re.search(r'\b(cs|bca|mca|others)\b', qlow)
        if 'show' in qlow and mbr:
            br = mbr.group(1).upper()
            cur.execute("SELECT title, author, branch, isbn FROM books WHERE branch=%s ORDER BY title LIMIT 50", (br,))
            rows = cur.fetchall()
            if not rows: return jsonify({"answer":f'No books in {br} branch.'})
            lines = [f'• {t} — {a} ISBN:{i}' for (t,a,b,i) in rows]
            return jsonify({"answer":f'{br} branch books:\n' + '\n'.join(lines)})

        # Generic fallback: try author first, then title, then isbn
        rows = find_by_author(cur, q) or find_by_title(cur, q) or find_by_isbn(cur, q)
        if not rows:
            return jsonify({"answer":'I can help with authors, titles, ISBNs, and branch-wise lists.'})
        lines = [f'• {t} — {a} ({b}) ISBN:{i}' for (t,a,b,i) in rows[:20]]
        return jsonify({"answer":'Here is what I found:\n' + '\n'.join(lines)})
    except Exception as e:
        return jsonify({"answer": "Error: "+str(e)})
    finally:
        try: cur.close(); con.close()
        except: pass

# ---------- Run ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
