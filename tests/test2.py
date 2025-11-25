
import pandas as pd
from cfg import project_path, data_path
import os
from utilities.utils import discrete


df1 = pd.read_excel(
    os.path.join(project_path, 'result.xlsx'),
    index_col=0,
    parse_dates=[0]
)
df2 = pd.read_excel(
    os.path.join(data_path, 'test.xlsx'),
    index_col=0,
    parse_dates=[0]
)
df3 = pd.read_excel(
    os.path.join(data_path, 'test2.xlsx'),
    index_col=0,
    parse_dates=[0]
)
df4 = pd.read_excel(
    os.path.join(data_path, 'test3.xlsx'),
    index_col=0,
    parse_dates=[0]
)
df5 = pd.read_excel(
    os.path.join(data_path, 'data_process.xlsx'),
    index_col=0,
    parse_dates=[0]
)
df5 = df5[['cds_cop']]
df1 = df1.rename(columns={
    'chr_12_num': 'AI_chr_12_num',
    'chr_3_num': 'AI_chr_3_num'
})
df = pd.concat([df1, df2, df3, df4, df5], axis=1, join='inner')
df['负荷区间'] = df.apply(lambda x: discrete(x['cds_cooling'], 100, 0, 3900), axis=1)
df['AI'] = df.apply(lambda x: str(int(x['AI_chr_12_num'])) + str(int(x['AI_chr_3_num'])), axis=1)
df['Actual'] = df.apply(lambda x: str(x['chr_12_num']) + str(x['chr_3_num']), axis=1)


def test(x):
    if x == '01':
        return 1
    if x == '10':
        return 2
    if x == '11':
        return 3
    return 0


df['AI推荐'] = df['AI'].apply(test)
df['实际工况'] = df['Actual'].apply(test)
df['match'] = df['AI推荐'] == df['实际工况']
df = df[['cds_cop', 'cds_cooling', 'AI_chr_12_num', 'AI_chr_3_num', 'chr_12_num', 'chr_3_num', '负荷区间', 'AI', 'Actual', 'AI推荐', '实际工况', 'match']]
df.to_excel(os.path.join(data_path, 'sq_chr_num.xlsx'))
