import sqlite3

db_path = "db/alpha_vault.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

row = cursor.execute("SELECT dataset, variable_id, description FROM whitelisted_variables WHERE variable_id = 'anl4_fs_basic_splt_v4_nd_eps_estimate'").fetchone()
print("Result for anl4_fs_basic_splt_v4_nd_eps_estimate:")
print(row)

rows_containing_basic_splt = cursor.execute("SELECT variable_id FROM whitelisted_variables WHERE variable_id LIKE '%basic_splt%'").fetchall()
print("Variables containing 'basic_splt':")
for r in rows_containing_basic_splt[:10]:
    print(f"  {r[0]}")

conn.close()
