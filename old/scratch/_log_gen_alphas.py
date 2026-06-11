import sys, json
sys.stdout.reconfigure(encoding='utf-8')
with open('scratch/groupa_generation_9.json', encoding='utf-8') as f:
    alphas = json.load(f)
lines = ['\n[GENERATED ALPHAS] - Generation 9 Group A (16 alphas):']
for i, a in enumerate(alphas):
    fam = a.get('family', '')
    ds  = a.get('dataset', '')
    frm = a.get('formula', '')[:120]
    ano = a.get('anomaly_basis', '')
    lines.append(f'  #{i+1} [{fam}] [{ds}]')
    lines.append(f'       Formula: {frm}...')
    lines.append(f'       Anomaly: {ano}')
lines.append('')
lines.append('[STEP 5 GENERATOR DONE] - 16 alphas generated and saved to groupa_generation_9.json')
lines.append('')
with open('live_run.txt', 'a', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('live_run.txt updated with GENERATED ALPHAS')
