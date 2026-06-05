import sqlite3

db_path = "db/alpha_vault.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

vars_to_check = [
    "anl4_fs_basic_splt_v4_nd_eps_estimate",
    "anl4_fs_basic_splt_v4_nd_sales_estimate",
    "anl4_fs_detail_estimates_advanced_af_nd_ebitda_high",
    "anl4_fs_detail_estimates_advanced_af_nd_ebitda_low",
    "anl4_fs_detail_estimates_advanced_af_nd_ebitda_mean",
    "anl4_fs_detail_estimates_advanced_af_nd_ptp_high",
    "anl4_fs_detail_estimates_advanced_af_nd_ptp_low",
    "anl4_fs_detail_estimates_advanced_af_nd_ptp_mean",
    "anl4_fs_detail_estimates_advanced_af_nd_fcf_high",
    "anl4_fs_detail_estimates_advanced_af_nd_fcf_low",
    "anl14_mean_eps_fp1",
    "anl14_mean_sales_fp1",
    "anl16_actsurprise",
    "anl16_actsuescore",
    "anl16_actgrowth",
    "anl16_actstability",
    "anl16_actvalue",
    "anl44_analyst",
    "anl45_ad_rel_ret_per",
    "anl45_jensensalpha",
    "anl45_beta",
    "anl45_ad_ret_per"
]

print("Verifying prompt's whitelisted variables:")
for v in vars_to_check:
    row = cursor.execute("SELECT dataset, variable_id, description FROM whitelisted_variables WHERE variable_id = ?", (v,)).fetchone()
    if row:
        print(f"  [YES] {v} (Dataset: {row[0]}) - {row[2][:50]}")
    else:
        print(f"  [NO]  {v} is not in whitelisted_variables table!")

conn.close()
