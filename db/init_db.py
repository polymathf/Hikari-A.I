import aiosqlite

async def init_db():
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'eng'
            )
        """)
        await db.commit()

    async with aiosqlite.connect("groups.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'eng',
                active BOOLEAN DEFAULT 1,
                topic TEXT DEFAULT NULL,
                description TEXT DEFAULT NULL,
                add_time REAL DEFAULT NULL,
                style TEXT DEFAULT 'default'
            )
        """)
        await db.commit()

    async with aiosqlite.connect("cooldowns.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cooldowns (
                chat_id INTEGER,
                command TEXT,
                end_time REAL,
                PRIMARY KEY (chat_id, command)
            )
        """)
        await db.commit()