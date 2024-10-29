import sqlite3

MESSAGE_DB = "messages.db"
CHANNEL_DB = "channels.db"
TOKEN_DB = "tokens.db"

msg_conn = sqlite3.connect(MESSAGE_DB)
msg_cursor = msg_conn.cursor()

msg_cursor.execute('''
    CREATE TABLE IF NOT EXISTS messageHistory (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        message_type TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

msg_conn.commit()
msg_conn.close()

ch_conn = sqlite3.connect(CHANNEL_DB)
ch_cursor = ch_conn.cursor()

ch_cursor.execute('''
    CREATE TABLE IF NOT EXISTS channelOwnership (
        user_id TEXT PRIMARY KEY,
        channel_id TEXT NOT NULL
    );
''')

ch_conn.commit()
ch_conn.close()

tk_conn = sqlite3.connect(TOKEN_DB)
tk_cursor = tk_conn.cursor()

tk_cursor.execute('''
    CREATE TABLE IF NOT EXISTS token (
        user_id TEXT PRIMARY KEY,
        token TEXT NOT NULL
    );
''')

tk_conn.commit()
tk_conn.close()
