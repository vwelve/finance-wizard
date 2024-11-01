import sqlite3
import uuid
import logging

from typing import Tuple, List

Message = Tuple[str, str, str, str, str]


class Database:
    MESSAGE_DATABASE = "messages.db"
    TOKEN_DATABASE = "tokens.db"
    CHANNEL_DATABASE = "channels.db"
    TOOL_DATABASE = "tools.db"

    @staticmethod
    def get_user_messages(user_id: str) -> List[Message]:
        conn = sqlite3.connect(Database.MESSAGE_DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM messageHistory
            WHERE user_id = ?
            ORDER BY timestamp ASC;
        """, (str(user_id),))

        messages: List[Message] = cursor.fetchall()

        conn.close()
        logging.info(f"get_user_messages(user_id={user_id}): {messages}")
        return messages

    @staticmethod
    def update_user_messages(user_id: str, message_type: str, content: str, row_id: str = "", *args,
                             has_tool: bool = False):
        logging.info(f"update_user_messages(user_id={user_id}, message_type={message_type}, content={content}, "
                     f"row_id={row_id}, has_tool={has_tool})")
        if not row_id:
            row_id = str(uuid.uuid4())

        conn = sqlite3.connect(Database.MESSAGE_DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messageHistory (id, user_id, message_type, content, has_tool)
            VALUES (?, ?, ?, ?, ?);
        """, (row_id, user_id, message_type, content, int(has_tool)))

        conn.commit()
        conn.close()

    @staticmethod
    def clear_message_history(user_id: str):
        conn = sqlite3.connect(Database.MESSAGE_DATABASE)
        cursor = conn.cursor()
        
        # Execute the SQL query to delete all non-system messages for a specific user
        cursor.execute("""
            DELETE FROM messageHistory
            WHERE message_type != 'system' AND user_id = ?;
        """, (str(user_id),))
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_channel(user_id: str) -> str:
        conn = sqlite3.connect(Database.CHANNEL_DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM channelOwnership
            WHERE user_id = ?
        """, (user_id,))

        result = cursor.fetchone()
        channel: str = result[1] if result is not None else ""

        conn.commit()
        conn.close()
        logging.info(f"get_user_channel(user_id={user_id}): {channel}")

        return channel

    @staticmethod
    def update_user_channel(user_id: str, channel_id: str):
        logging.info(f"update_user_channel(user_id={user_id}, channel_id={channel_id})")
        conn = sqlite3.connect(Database.CHANNEL_DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO channelOwnership (user_id, channel_id)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET channel_id = excluded.channel_id
        """, (str(user_id), channel_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_user_token(user_id: str) -> str:
        conn = sqlite3.connect(Database.TOKEN_DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM token
            WHERE user_id = ?
        """, (str(user_id),))

        result = cursor.fetchone()
        token: str = result[1] if result is not None else ""

        conn.commit()
        conn.close()
        logging.info(f"get_user_token(user_id={user_id}): {token}")
        return token

    @staticmethod
    def set_user_token(user_id: str, token: str):
        conn = sqlite3.connect(Database.TOKEN_DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO token (user_id, token)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET token = excluded.token
        """, (str(user_id), token))

        conn.commit()
        conn.close()

    @staticmethod
    def update_tools(message_id: str, tool_id: str, tool_type: str, name: str, arguments: str):
        conn = sqlite3.connect(Database.TOOL_DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tools (message_id, tool_id, type, name, arguments)
            VALUES (?, ?, ?, ?, ?)
        """, (message_id, tool_id, tool_type, name, arguments))

        conn.commit()
        conn.close()

    @staticmethod
    def get_tools(message_id: str):
        conn = sqlite3.connect(Database.TOOL_DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM tools 
            WHERE message_id = ?
        """, (message_id,))
        tool_calls = cursor.fetchall()

        conn.commit()
        conn.close()

        return tool_calls