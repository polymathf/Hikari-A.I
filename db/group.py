import aiosqlite
import time

async def add_group(
        chat_id: int,
        lang: str = "eng",
        active: bool = True,
        topic: str = None,
        description: str = None,
        add_time: float = None,
        style: str = "default"
    ):
    if add_time is None:
        add_time = time.time()

    async with aiosqlite.connect("groups.db") as db:
        await db.execute("""
            INSERT OR REPLACE INTO groups 
            (chat_id, lang, active, topic, description, add_time, style)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, lang, active, topic, description, add_time, style))
        await db.commit()

async def deactivate_group(chat_id: int):
    async with aiosqlite.connect("groups.db") as db:
        await db.execute("""
            UPDATE groups SET active = 0 WHERE chat_id = ?
        """, (chat_id,))
        await db.commit()

async def count_groups():
    async with aiosqlite.connect("groups.db") as db:
        async with db.execute("SELECT COUNT(*) FROM groups") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def count_active_groups():
    async with aiosqlite.connect("groups.db") as db:
        async with db.execute("SELECT COUNT(*) FROM groups WHERE active = 1") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
        
async def get_active_groups() -> list[int]:
    async with aiosqlite.connect("groups.db") as db:
        cursor = await db.execute("SELECT chat_id FROM groups WHERE active = 1")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def get_group_lang(chat_id: int) -> str | None:
    async with aiosqlite.connect("groups.db") as db:
        async with db.execute("SELECT lang FROM groups WHERE chat_id = ?", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
        
async def get_group_add_time(chat_id: int) -> float | None:
    async with aiosqlite.connect("groups.db") as db:
        await db.execute("""
            ALTER TABLE groups ADD COLUMN add_time REAL DEFAULT NULL
        """)
        await db.commit()
        
        async with db.execute("SELECT add_time FROM groups WHERE chat_id = ?", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
        
async def get_group_style(chat_id: int) -> str | None:
    async with aiosqlite.connect("groups.db") as db:
        async with db.execute("SELECT style FROM groups WHERE chat_id = ?", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_group_style(chat_id: int, style: str):
    async with aiosqlite.connect("groups.db") as db:
        cursor = await db.execute("PRAGMA table_info(groups)")
        columns = await cursor.fetchall()
        has_style_column = any(col[1] == 'style' for col in columns)
        
        if not has_style_column:
            await db.execute("ALTER TABLE groups ADD COLUMN style TEXT DEFAULT 'default'")
            await db.commit()
        
        await db.execute("""
            UPDATE groups SET style = ? WHERE chat_id = ?
        """, (style, chat_id))
        await db.commit()