from pathlib import Path
import json, sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent
OUT = P / 'results'
OUT.mkdir(exist_ok=True)
df = pd.read_csv(P / 'bank-full.csv', sep=';')
df['subscribed'] = df['y'].eq('yes').astype(int)
df['age_group'] = pd.cut(df['age'], bins=[0, 24, 34, 44, 54, 64, 120], labels=['18–24', '25–34', '35–44', '45–54', '55–64', '65+'], include_lowest=True)

def summary(column):
    return (df.groupby(column, observed=True, dropna=False)['subscribed'].agg(contacts='size', subscriptions='sum').assign(conversion_pct=lambda x: 100*x.subscriptions/x.contacts).sort_values('contacts', ascending=False).round(2))

for col in ['job', 'age_group', 'poutcome']:
    table = summary(col)
    table.to_csv(OUT / f'{col}.csv', encoding='utf-8-sig')
    plot = table.sort_values('conversion_pct').plot.barh(y='conversion_pct', legend=False, color='#3266a8', figsize=(8, 4.5))
    plot.set_xlabel('Conversion to deposit, %'); plot.set_ylabel(col); plot.set_title('Bank marketing: conversion by ' + col)
    plot.grid(axis='x', alpha=.2); plt.tight_layout(); plt.savefig(OUT / f'{col}.png', dpi=150); plt.close()

with sqlite3.connect(':memory:') as db:
    df.drop(columns=['age_group']).to_sql('bank', db, index=False)
    sql = (P / 'queries.sql').read_text(encoding='utf-8')
    for i, statement in enumerate(sql.split(';')):
        if statement.strip():
            pd.read_sql_query(statement, db).to_csv(OUT / f'sql_{i+1}.csv', index=False, encoding='utf-8-sig')
    assert abs(pd.read_sql_query('SELECT AVG(subscribed)*100 AS rate FROM bank', db).iloc[0,0] - df.subscribed.mean()*100) < 1e-9

stats = {'rows':len(df), 'duplicates':int(df.duplicated(subset=[c for c in df if c not in ['subscribed','age_group']]).sum()), 'null_cells':int(df.isna().sum().sum()), 'unknown_counts':{c:int(df[c].eq('unknown').sum()) for c in df.select_dtypes('object') if df[c].eq('unknown').any()}, 'subscriptions':int(df.subscribed.sum()), 'conversion_pct':round(df.subscribed.mean()*100,2)}
(OUT/'summary.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2),encoding='utf-8')
print(json.dumps(stats, ensure_ascii=False, indent=2))
print('\nPREVIOUS CAMPAIGN\n',summary('poutcome').to_string())
print('\nAGE\n',summary('age_group').to_string())
