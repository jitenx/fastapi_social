import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

NUM_POSTS = 1000
NUM_USERS = 20  # Make sure this matches your actual users
OUTPUT_FILE = "insert_posts.sql"

# Current timestamp
now = datetime.now()
past_year = now - timedelta(days=365)

# List of valid owner IDs
user_ids = list(range(1, NUM_USERS + 1))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("-- Posts\n")
    for _ in range(NUM_POSTS):
        title = fake.sentence(nb_words=random.randint(3, 7)).replace("'", "''")
        content = fake.paragraph(nb_sentences=random.randint(3, 50)).replace("'", "''")
        published = "true" if random.choice([True, False]) else "false"

        # Generate datetime objects first
        created_dt = fake.date_time_between_dates(
            datetime_start=past_year, datetime_end=now
        )
        updated_dt = fake.date_time_between_dates(
            datetime_start=created_dt, datetime_end=now
        )

        # Convert to string for SQL
        created_at = created_dt.strftime("%Y-%m-%d %H:%M:%S")
        updated_at = updated_dt.strftime("%Y-%m-%d %H:%M:%S")

        owner_id = random.choice(user_ids)

        sql_post = f"""INSERT INTO posts
(title, content, published, created_at, updated_at, owner_id)
VALUES('{title}', '{content}', {published}, '{created_at}', '{updated_at}', {owner_id});\n"""
        f.write(sql_post)

print(f"✅ Generated {NUM_POSTS} posts in {OUTPUT_FILE}")
