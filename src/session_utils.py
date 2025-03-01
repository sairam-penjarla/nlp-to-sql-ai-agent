import sqlite3
import json
from typing import List, Dict, Optional, Tuple
from custom_logger import logger
import sqlite3
import logging

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
                    session_id TEXT,
                    conversation_id TEXT PRIMARY KEY,
                    prompt TEXT,
                    sql_query TEXT,
                    sql_data TEXT,
                    chatbot_assistant TEXT,
                    session_icon TEXT
                )
            ''')
        logger.info("Tables created or already exist.")

    def add_data_query_only(self, session_id, prompt, sql_query, session_icon, conversation_id):
        """
        Inserts a new row into the sessions table.
        """
        try:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO sessions (session_id, conversation_id, prompt, sql_query, session_icon) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, conversation_id, prompt, sql_query, session_icon))
            logger.info(f"Inserted new session data for session_id: {session_id}")
        except sqlite3.IntegrityError:
            logger.error(f"Failed to insert session {session_id}: conversation_id already exists.")

    def add_data_chatbot_response(self, session_id, sql_query, sql_data, chatbot_assistant, conversation_id):
        """
        Updates an existing record in the sessions table based on conversation_id.
        """
        try:
            with self.conn:
                updated_rows = self.conn.execute('''
                    UPDATE sessions 
                    SET sql_query = ?, sql_data = ?, chatbot_assistant = ? 
                    WHERE conversation_id = ?
                ''', (sql_query, sql_data, chatbot_assistant, conversation_id)).rowcount
            if updated_rows == 0:
                logger.warning(f"No record found for conversation_id: {conversation_id}")
            else:
                logger.info(f"Updated session data for conversation_id: {conversation_id}")
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")


    def get_session_data(self, session_id: str) -> List[Dict[str, str]]:
        logger.info(f"Retrieving session data for session: {session_id}")
        session_data = []
        with self.conn:
            results = self.conn.execute(
                '''SELECT prompt, sql_query, sql_data, chatbot_assistant, conversation_id
                FROM sessions
                WHERE session_id = ?''', (session_id,)
            ).fetchall()
            if results:
                logger.info(f"Retrieved {len(results)} entries for session_id: {session_id}")
                for row in results:
                    session_data.append({
                        "prompt": str(row["prompt"]),
                        "sql_query": str(row["sql_query"]),
                        "sql_data": str(row["sql_data"]),
                        "chatbot_assistant": str(row["chatbot_assistant"]),
                        "conversation_id": str(row["conversation_id"])
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

    def delete_session(self, session_id: str) -> Tuple[Dict[str, str], int]:
        try:
            self.conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            self.conn.commit()
            logger.info(f"Session {session_id} deleted successfully.")
            return {"message": "Session deleted successfully."}, 200  # Return 200 for success
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return {"error": "Failed to delete session."}, 500  # Return 500 for failure


    def delete_all_sessions(self) -> Tuple[Dict[str, str], int]:
        try:
            self.conn.execute("DELETE FROM sessions")
            self.conn.commit()
            logger.info("All sessions deleted successfully.")
            return {"message": "All sessions deleted successfully."}, 200  # Return 200 for success
        except Exception as e:
            logger.error(f"Error deleting all sessions: {e}")
            return {"error": "Failed to delete sessions."}, 500  # Return 500 for failure


    def close(self):
        logger.info("Closing database connection...")
        self.conn.close()
        logger.info("Database connection closed.")
