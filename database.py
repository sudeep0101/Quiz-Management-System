import hashlib
import secrets
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "quiz_management.db"
CATEGORIES = ["Python", "Programming", "Database", "Web Development", "General Knowledge"]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = None
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL,
            option_a TEXT NOT NULL, option_b TEXT NOT NULL,
            option_c TEXT NOT NULL, option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL CHECK(correct_option IN ('A','B','C','D')),
            marks INTEGER NOT NULL DEFAULT 1 CHECK(marks > 0),
            category TEXT NOT NULL DEFAULT 'General Knowledge')""")
        conn.execute("""CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT NOT NULL,
            score INTEGER NOT NULL, total_marks INTEGER NOT NULL,
            percentage REAL NOT NULL, taken_at TEXT NOT NULL,
            quiz_category TEXT NOT NULL DEFAULT 'Uncategorized',
            quiz_mode TEXT NOT NULL DEFAULT 'Legacy')""")
        qcols = {r[1] for r in conn.execute("PRAGMA table_info(questions)")}
        if "category" not in qcols:
            conn.execute("ALTER TABLE questions ADD COLUMN category TEXT NOT NULL DEFAULT 'General Knowledge'")
        rcols = {r[1] for r in conn.execute("PRAGMA table_info(results)")}
        if "quiz_category" not in rcols:
            conn.execute("ALTER TABLE results ADD COLUMN quiz_category TEXT NOT NULL DEFAULT 'Uncategorized'")
        if "quiz_mode" not in rcols:
            conn.execute("ALTER TABLE results ADD COLUMN quiz_mode TEXT NOT NULL DEFAULT 'Legacy'")
        if "student_username" not in rcols:
            conn.execute("ALTER TABLE results ADD COLUMN student_username TEXT")
        # Populate categories for existing questions only when they have the migration default.
        rows = conn.execute("SELECT id, question FROM questions WHERE category='General Knowledge'").fetchall()
        for qid, question in rows:
            conn.execute("UPDATE questions SET category=? WHERE id=?", (infer_category(question), qid))
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if count == 0:
            seed = [
                ("Which keyword defines a function in Python?", "func", "define", "def", "function", "C", 1, "Python"),
                ("Which data type stores True or False?", "int", "bool", "str", "list", "B", 1, "Python"),
                ("Which function displays output in Python?", "input()", "print()", "show()", "display()", "B", 1, "Python"),
                ("Which collection stores key-value pairs?", "List", "Tuple", "Dictionary", "Set", "C", 1, "Python"),
                ("Which symbol starts a Python comment?", "//", "/*", "#", "<!--", "C", 1, "Python"),
                ("What is the result of 3 ** 2?", "6", "9", "8", "5", "B", 1, "Python"),
                ("Which method adds an item to a list?", "add()", "append()", "push()", "attach()", "B", 1, "Python"),
                ("Which loop repeats while a condition is true?", "if", "switch", "while", "try", "C", 1, "Python"),
                ("Which module supports SQLite in Python?", "sqlite3", "sql", "database", "dbconnect", "A", 1, "Database"),
                ("Which keyword handles an exception?", "catch", "except", "error", "final", "B", 1, "Python"),
            ]
            conn.executemany("INSERT INTO questions(question,option_a,option_b,option_c,option_d,correct_option,marks,category) VALUES(?,?,?,?,?,?,?,?)", seed)


def infer_category(question):
    text = str(question).casefold()
    if any(w in text for w in ("sqlite", "database", "sql", "query", "table", "key-value")): return "Database"
    if any(w in text for w in ("html", "css", "javascript", "web page", "website")): return "Web Development"
    if any(w in text for w in ("python", "def ", "list", "tuple", "dictionary", "exception", "loop", "comment", "function", "print()", "bool", " **")): return "Python"
    if any(w in text for w in ("program", "algorithm", "compiler", "code", "java", "variable")): return "Programming"
    return "General Knowledge"


def get_questions():
    with get_connection() as conn:
        return conn.execute("SELECT id,question,option_a,option_b,option_c,option_d,correct_option,marks FROM questions ORDER BY id").fetchall()


def get_questions_with_category():
    with get_connection() as conn:
        return conn.execute("SELECT id,question,option_a,option_b,option_c,option_d,correct_option,marks,category FROM questions ORDER BY id").fetchall()


def get_question_category(question_id):
    with get_connection() as conn:
        row = conn.execute("SELECT category FROM questions WHERE id=?", (question_id,)).fetchone()
        return row[0] if row else "General Knowledge"


def add_question(question, a, b, c, d, correct, marks, category="General Knowledge"):
    with get_connection() as conn:
        conn.execute("INSERT INTO questions(question,option_a,option_b,option_c,option_d,correct_option,marks,category) VALUES(?,?,?,?,?,?,?,?)", (question,a,b,c,d,correct,marks,category))


def update_question_category(question_id, category):
    with get_connection() as conn:
        conn.execute("UPDATE questions SET category=? WHERE id=?", (category, question_id))


def delete_question(question_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM questions WHERE id=?", (question_id,))


def save_result(name, score, total, percentage, quiz_category="Uncategorized",
                quiz_mode="Legacy", student_username=None):
    """Save a quiz attempt, optionally linked to a student's unique username."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO results
               (student_name, score, total_marks, percentage, taken_at,
                quiz_category, quiz_mode, student_username)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name, score, total, percentage,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                quiz_category, quiz_mode,
                student_username.lower() if student_username else None
            )
        )


def get_results():
    with get_connection() as conn:
        return conn.execute(
            """SELECT id, student_name, score, total_marks, percentage,
                      taken_at, quiz_category, quiz_mode
               FROM results ORDER BY id DESC"""
        ).fetchall()
def get_results_for_student(username, display_name=None):
    """Return one student's results, retaining matching unlinked legacy attempts."""
    if not username:
        return []
    with get_connection() as conn:
        return conn.execute(
            """SELECT id, student_name, score, total_marks, percentage,
                      taken_at, quiz_category, quiz_mode
               FROM results
               WHERE lower(student_username) = lower(?)
                  OR (
                      student_username IS NULL
                      AND lower(student_name) = lower(?)
                  )
               ORDER BY id DESC""",
            (username, display_name or "")
        ).fetchall()



# -------------------- STUDENT ACCOUNTS --------------------
_STUDENT_HASH_ITERATIONS = 240_000
def initialize_student_accounts():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS student_accounts (
                username TEXT PRIMARY KEY COLLATE NOCASE,
                display_name TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
def register_student(username, display_name, password):
    username = username.strip().lower()
    display_name = display_name.strip()
    if not username or not display_name or not password:
        return False
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt,
        _STUDENT_HASH_ITERATIONS
    )
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO student_accounts
                (username, display_name, password_salt, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                username, display_name, salt.hex(), password_hash.hex(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        return True
    except sqlite3.IntegrityError:
        return False
def authenticate_student(username, password):
    username = username.strip().lower()
    with get_connection() as conn:
        row = conn.execute("""
            SELECT display_name, password_salt, password_hash
            FROM student_accounts WHERE username = ?
        """, (username,)).fetchone()
    if not row:
        return None
    display_name, salt_hex, stored_hash = row
    calculated = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex),
        _STUDENT_HASH_ITERATIONS
    ).hex()
    if secrets.compare_digest(calculated, stored_hash):
        return display_name
    return None

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")
    print(f"Database location: {DB_PATH}")
    print(f"Questions available: {len(get_questions())}")
