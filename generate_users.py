import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

NUM_USERS = 20
OUTPUT_FILE = "insert_users.sql"

# Current timestamp
now = datetime.now()
past_year = now - timedelta(days=365)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("-- Users\n")
    for i in range(NUM_USERS):
        first_name = fake.first_name().replace("'", "''")
        last_name = fake.last_name().replace("'", "''")
        email = fake.unique.email().replace("'", "''")
        password = fake.password(length=10).replace("'", "''")

        # Generate datetime objects first
        created_dt = fake.date_time_between_dates(
            datetime_start=past_year, datetime_end=now
        )
        updated_dt = fake.date_time_between_dates(
            datetime_start=created_dt, datetime_end=now
        )

        # Then convert to string for SQL
        created_at = created_dt.strftime("%Y-%m-%d %H:%M:%S")
        updated_at = updated_dt.strftime("%Y-%m-%d %H:%M:%S")

        sql_user = f"""INSERT INTO users
(email, first_name, last_name, password, created_at, updated_at)
VALUES('{email}', '{first_name}', '{last_name}', '{password}', '{created_at}', '{updated_at}');\n"""
        f.write(sql_user)

print(f"✅ Generated {NUM_USERS} users in {OUTPUT_FILE}")
