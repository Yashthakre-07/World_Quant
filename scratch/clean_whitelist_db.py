import sqlite3

db_path = "db/alpha_vault.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get total count before cleaning
before_count = cursor.execute("SELECT COUNT(*) FROM whitelisted_variables").fetchone()[0]
print(f"Total whitelisted variables before cleaning: {before_count}")

# The verified whitelisted variables for Sai's profile
allowed_vars = [
    # analyst4
    "anl4_afv4_eps_mean",
    "anl4_afv4_eps_high",
    "anl4_afv4_eps_low",
    "anl4_ebitda_mean",
    "anl4_ebitda_high",
    "anl4_ebitda_low",
    
    # analyst14
    "anl14_actvalue_eps_fp0",
    "anl14_high_eps_fp1",
    "anl14_high_ebitda_fp1",
    
    # analyst45
    "anl45_jensensalpha",
    "average_daily_relative_return_percent",
    "relative_return_percent_today"
]

# We delete any variables not in this list
# Construct place holders
placeholders = ','.join(['?'] * len(allowed_vars))
query = f"DELETE FROM whitelisted_variables WHERE variable_id NOT IN ({placeholders})"

cursor.execute(query, allowed_vars)
conn.commit()

after_count = cursor.execute("SELECT COUNT(*) FROM whitelisted_variables").fetchone()[0]
print(f"Total whitelisted variables after cleaning: {after_count}")

# Print remaining variables
rows = cursor.execute("SELECT dataset, variable_id, description FROM whitelisted_variables").fetchall()
print("\nRemaining whitelisted variables in Database:")
for r in rows:
    print(f"  [{r[0]}] {r[1]} - {r[2][:70]}")

conn.close()
