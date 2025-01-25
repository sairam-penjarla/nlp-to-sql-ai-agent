import sqlite3
import json
from typing import List, Dict, Optional
from custom_logger import logger

class SessionUtilities:
    def __init__(self, db_name: str = "sessions.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enables dict-like access
        logger.info(f"Connected to the database: {self.db_name}")
        self.create_tables()

    def create_tables(self):
        logger.info("Creating tables if they don't exist...")
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    prompt TEXT,
                    sql_query TEXT,
                    chatbot_assistant TEXT,
                    session_icon TEXT
                )
            ''')
        logger.info("Tables created or already exist.")

    def add_data(self, session_id: str, prompt: str, sql_query: str, chatbot_assistant: str, session_icon: str):
        logger.info(f"Adding data to session: {session_id}...")
        with self.conn:
            self.conn.execute(
                '''INSERT INTO sessions 
                   (session_id, prompt, sql_query, chatbot_assistant, session_icon) 
                   VALUES (?, ?, ?, ?, ?)''',
                (session_id, prompt, sql_query, chatbot_assistant, session_icon)
            )

    def get_session_data(self, session_id: str) -> List[Dict[str, str]]:
        logger.info(f"Retrieving session data for session: {session_id}")
        session_data = []
        with self.conn:
            results = self.conn.execute(
                '''SELECT prompt, sql_query, chatbot_assistant
                FROM sessions
                WHERE session_id = ?''', (session_id,)
            ).fetchall()
            if results:
                logger.info(f"Retrieved {len(results)} entries for session_id: {session_id}")
                for row in results:
                    session_data.append({
                        "prompt": str(row["prompt"]),
                        "sql_query": str(row["sql_query"]),
                        "chatbot_assistant": str(row["chatbot_assistant"]),
                    })
        return session_data

    def get_session_icon(self, session_id: str) -> Optional[str]:
        logger.info(f"Retrieving session_icon for session: {session_id}")
        with self.conn:
            result = self.conn.execute(
                '''SELECT session_icon
                FROM sessions
                WHERE session_id = ?''', (session_id,)
            ).fetchone()
            if result:
                session_icon = result["session_icon"]
                logger.info(f"Session icon retrieved for session_id {session_id}: {session_icon}")
                return session_icon
            logger.warning(f"No session icon found for session_id: {session_id}")
            return None

    def truncate_string(self, input_string: str, max_length: int = 19) -> str:
        return input_string[:max_length] + "..." if len(input_string) > max_length else input_string

    def get_session_meta_data(self) -> Dict[str, Dict[str, str]]:
        query = '''
        SELECT session_id, MIN(rowid) as first_rowid
        FROM sessions
        GROUP BY session_id
        '''
        cursor = self.conn.cursor()
        cursor.execute(query)
        session_first_rows = cursor.fetchall()
        result = {}
        for session_id, first_rowid in session_first_rows:
            cursor.execute(
                '''
                SELECT prompt, session_icon
                FROM sessions
                WHERE session_id = ? AND rowid = ?
                ''',
                (session_id, first_rowid)
            )
            row = cursor.fetchone()
            if row:
                result[session_id] = {
                    "prompt": str(row["prompt"]),
                    "session_icon": row["session_icon"],
                }
        return result

    def delete_all_sessions(self) -> Dict[str, str]:
        try:
            self.conn.execute("DELETE FROM sessions")
            self.conn.commit()
            logger.info("All sessions deleted successfully.")
            return {"message": "All sessions deleted successfully."}
        except Exception as e:
            logger.error(f"Error deleting all sessions: {e}")
            return {"error": "Failed to delete sessions."}

    def delete_session(self, session_id: str) -> Dict[str, str]:
        try:
            self.conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            self.conn.commit()
            logger.info(f"Session {session_id} deleted successfully.")
            return {"message": "Session deleted successfully."}
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return {"error": "Failed to delete session."}

    def close(self):
        logger.info("Closing database connection...")
        self.conn.close()
        logger.info("Database connection closed.")
