import aiosqlite
import time

async def init_cooldown_db():
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

async def set_cooldown(chat_id: int, command: str, duration: int):
    async with aiosqlite.connect("cooldowns.db") as db:
        end_time = time.time() + duration
        await db.execute("""
            INSERT OR REPLACE INTO cooldowns (chat_id, command, end_time)
            VALUES (?, ?, ?)
        """, (chat_id, command, end_time))
        await db.commit()

async def check_cooldown(chat_id: int, command: str) -> int:
    async with aiosqlite.connect("cooldowns.db") as db:
        async with db.execute("""
            SELECT end_time FROM cooldowns 
            WHERE chat_id = ? AND command = ?
        """, (chat_id, command)) as cursor:
            row = await cursor.fetchone()
            if row:
                remaining = row[0] - time.time()
                return int(remaining) if remaining > 0 else 0
            return 0