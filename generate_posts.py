import random
import asyncio
from datetime import datetime, timedelta
from faker import Faker
import aiosqlite

fake = Faker()

NUM_POSTS = 1000
NUM_USERS = 20  # must match your actual users
DB_FILE = "sql_app.db"

# Current timestamp
now = datetime.now()
past_year = now - timedelta(days=365)

# List of valid owner IDs
user_ids = list(range(1, NUM_USERS + 1))

# -------------------- GENERATE POSTS --------------------
posts_to_insert = []

for _ in range(NUM_POSTS):
    title = fake.sentence(nb_words=random.randint(3, 20)).replace("'", "''")
    content = "\n\n".join(fake.paragraphs(nb=random.randint(5, 20))).replace("'", "''")
    published = 1 if random.choice([True, False]) else 0

    created_dt = fake.date_time_between_dates(
        datetime_start=past_year, datetime_end=now
    )
    updated_dt = fake.date_time_between_dates(
        datetime_start=created_dt, datetime_end=now
    )

    created_at = created_dt.strftime("%Y-%m-%d %H:%M:%S")
    updated_at = updated_dt.strftime("%Y-%m-%d %H:%M:%S")

    owner_id = random.choice(user_ids)

    posts_to_insert.append(
        (title, content, published, created_at, updated_at, owner_id)
    )

print(f"✅ Generated {NUM_POSTS} posts in memory")


# -------------------- ASYNC INSERT --------------------
async def insert_posts():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        insert_sql = """
        INSERT INTO posts (title, content, published, created_at, updated_at, owner_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        await db.executemany(insert_sql, posts_to_insert)
        await db.commit()
        print(f"✅ Inserted {NUM_POSTS} posts into the database!")


# Run the async insertion
asyncio.run(insert_posts())
