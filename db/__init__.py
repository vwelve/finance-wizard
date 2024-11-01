import sqlite3

MESSAGE_DB = "messages.db"
CHANNEL_DB = "channels.db"
TOKEN_DB = "tokens.db"
TOOLS_DB = "tools.db"

msg_conn = sqlite3.connect(MESSAGE_DB)
msg_cursor = msg_conn.cursor()

msg_cursor.execute('''
    CREATE TABLE IF NOT EXISTS messageHistory (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        message_type TEXT NOT NULL,
        content TEXT,
        has_tool INTEGER DEFAULT 0,
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

tools_conn = sqlite3.connect(TOOLS_DB)
tools_cursor = tools_conn.cursor()

tools_cursor.execute("""
    CREATE TABLE IF NOT EXISTS tools (
        message_id TEXT,
        tool_id TEXT,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        arguments TEXT NOT NULL,
        PRIMARY KEY (message_id, tool_id)
    )
""")

tools_conn.commit()
tools_conn.close()
