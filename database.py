# 01 - Imports

import sqlite3
import bcrypt
from pathlib import Path

# -------------------------------------------------
# 02 - Database Connection (shared by all pages)
# -------------------------------------------------

# Always use evaluation.db from this project folder
DB_PATH = Path(__file__).resolve().parent / "evaluation.db"


def connect_database():

    connection = sqlite3.connect(DB_PATH)

    return connection


# -------------------------------------------------
# 03 - Delete All Users / Tasks / Evaluations (utility - run directly with: python database.py)
# -------------------------------------------------


def delete_all_users():

    connection = connect_database()
    cursor = connection.cursor()

    # Delete all users
    cursor.execute("DELETE FROM users")

    # Delete all tasks
    cursor.execute("DELETE FROM tasks")

    # Delete all evaluations
    cursor.execute("DELETE FROM evaluations")

    # Reset ID sequences
    cursor.execute("DELETE FROM sqlite_sequence")

    connection.commit()
    connection.close()

    print("All data deleted successfully")


# To run the delete code:
# python database.py

# if __name__ == "__main__":
#   delete_all_users()
    


# -------------------------------------------------
# 04 - Create Users Table (Home.py - accounts)
# -------------------------------------------------


def create_users_table():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

    connection.commit()
    connection.close()


# -------------------------------------------------
# 05 - Create Tasks Table (1_Task_Management.py)
# -------------------------------------------------


def create_tasks_table():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            response_a TEXT NOT NULL,
            response_b TEXT NOT NULL,
            category TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
        """)

    connection.commit()
    connection.close()


# -------------------------------------------------
# 06 - Create Evaluations Table (2_Evaluation.py)
# -------------------------------------------------


def create_evaluations_table():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            evaluator_id INTEGER NOT NULL,

            a_correctness INTEGER,
            a_relevance INTEGER,
            a_clarity INTEGER,
            a_completeness INTEGER,
            a_instruction INTEGER,

            b_correctness INTEGER,
            b_relevance INTEGER,
            b_clarity INTEGER,
            b_completeness INTEGER,
            b_instruction INTEGER,

            preference TEXT,
            flags TEXT,
            justification TEXT,
            created_at TEXT NOT NULL
        )
        """)

    connection.commit()
    connection.close()


# -------------------------------------------------
# 07 - Create All Tables (one-time setup)
# -------------------------------------------------


def create_all_tables():

    create_users_table()

    create_tasks_table()

    create_evaluations_table()


# -------------------------------------------------
# 08 - Add User (used by Home.py - Register)
# -------------------------------------------------


def add_user(username, password):

    username = username.strip()

    if not 3 <= len(username) <= 50:
        raise ValueError("Username must be 3 to 50 characters.")

    if not password.strip() or len(password) < 6:
        raise ValueError("Use a password with at least 6 characters.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must be at most 72 UTF-8 bytes.")

    connection = connect_database()
    cursor = connection.cursor()

    # Convert the password into a secure hash
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    cursor.execute(
        """
        INSERT INTO users (
            username,
            password,
            created_at
        )
        VALUES (
            ?, ?,
            datetime('now')
        )
        """,
        (username, hashed_password),
    )

    connection.commit()
    connection.close()


# -------------------------------------------------
# 09 - Login User (used by Home.py - Login)
# -------------------------------------------------


def login_user(username, password):

    username = username.strip()

    if not username or not password or len(password.encode("utf-8")) > 72:
        return None

    connection = connect_database()
    cursor = connection.cursor()

    # Get the user ID and stored password
    cursor.execute(
        """
        SELECT
            user_id,
            password
        FROM users
        WHERE username = ?
        """,
        (username,),
    )

    user = cursor.fetchone()

    connection.close()

    # Check if the user exists
    if user:

        user_id = user[0]
        stored_password = user[1]

        # Check the entered password
        if bcrypt.checkpw(password.encode("utf-8"), stored_password):

            # Return the logged-in user ID
            return user_id

    # Wrong username or password
    return None


# -------------------------------------------------
# 10 - Add Task (used by 1_Task_Management.py)
# -------------------------------------------------


def add_task(prompt, response_a, response_b, category=None):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (
            prompt,
            response_a,
            response_b,
            category,
            status,
            created_at
        )
        VALUES (
            ?, ?, ?, ?,
            'Completed',
            datetime('now')
        )
        """,
        (prompt, response_a, response_b, category),
    )

    connection.commit()

    # Get the newly created task ID
    task_id = cursor.lastrowid

    connection.close()

    return task_id


# -------------------------------------------------
# 11 - Get All Tasks (used by 2_Evaluation.py)
# -------------------------------------------------


def get_all_tasks():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            task_id,
            prompt,
            response_a,
            response_b
        FROM tasks
        ORDER BY task_id DESC
        """)

    tasks = cursor.fetchall()

    connection.close()

    return tasks


# -------------------------------------------------
# 12 - Add Evaluation (used by 2_Evaluation.py)
# -------------------------------------------------


def add_evaluation(
    task_id,
    evaluator_id,
    a_correctness,
    a_relevance,
    a_clarity,
    a_completeness,
    a_instruction,
    b_correctness,
    b_relevance,
    b_clarity,
    b_completeness,
    b_instruction,
    preference,
    flags,
    justification,
):

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO evaluations (
            task_id,
            evaluator_id,

            a_correctness,
            a_relevance,
            a_clarity,
            a_completeness,
            a_instruction,

            b_correctness,
            b_relevance,
            b_clarity,
            b_completeness,
            b_instruction,

            preference,
            flags,
            justification,
            created_at
        )
        VALUES (
            ?, ?,

            ?, ?, ?, ?, ?,

            ?, ?, ?, ?, ?,

            ?, ?, ?,

            datetime('now')
        )
        """,
        (
            task_id,
            evaluator_id,
            # Response A ratings
            a_correctness,
            a_relevance,
            a_clarity,
            a_completeness,
            a_instruction,
            # Response B ratings
            b_correctness,
            b_relevance,
            b_clarity,
            b_completeness,
            b_instruction,
            # Final evaluation
            preference,
            # Convert the list into text
            ",".join(flags),
            justification,
        ),
    )

    connection.commit()

    # Get the newly created evaluation ID
    evaluation_id = cursor.lastrowid

    connection.close()

    return evaluation_id


# -------------------------------------------------
# 13 - Get All Evaluations (used by 3_Evaluation_History.py and 4_Dashboard.py)
# -------------------------------------------------


def get_all_evaluations():

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            evaluation_id,
            task_id,
            evaluator_id,

            a_correctness,
            a_relevance,
            a_clarity,
            a_completeness,
            a_instruction,

            b_correctness,
            b_relevance,
            b_clarity,
            b_completeness,
            b_instruction,

            preference,
            flags,
            justification,
            created_at

        FROM evaluations

        ORDER BY evaluation_id DESC
        """)

    evaluations = cursor.fetchall()

    connection.close()

    return evaluations


# -------------------------------------------------
# 14 - Get Dashboard Statistics (used by 4_Dashboard.py)
# -------------------------------------------------


def get_dashboard_stats():

    connection = connect_database()
    cursor = connection.cursor()

    # Total tasks
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    # Total evaluations
    cursor.execute("SELECT COUNT(*) FROM evaluations")
    total_evaluations = cursor.fetchone()[0]

    # Response A wins
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM evaluations
        WHERE preference = 'Response A'
        """
    )
    response_a_wins = cursor.fetchone()[0]

    # Response B wins
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM evaluations
        WHERE preference = 'Response B'
        """
    )
    response_b_wins = cursor.fetchone()[0]

    # Equal
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM evaluations
        WHERE preference = 'Equal'
        """
    )
    equal_count = cursor.fetchone()[0]

    connection.close()

    return {
        "total_tasks": total_tasks,
        "total_evaluations": total_evaluations,
        "response_a_wins": response_a_wins,
        "response_b_wins": response_b_wins,
        "equal_count": equal_count
    }
