from urllib3 import Retry
import pandas as pd

New_col = 'insert_1_1 insert_1_2 insert_2_1 insert_2_2 insert_3_1 insert_3_2 insert_4_1 insert_4_2 insert_5_1 insert_5_2 insert_6_1 insert_6_2 insert_7_1 insert_7_2 \
            start_timing_1_1 start_timing_1_2 start_timing_2_1 start_timing_2_2 start_timing_3_1 start_timing_3_2 start_timing_4_1 start_timing_4_2 start_timing_5_1 start_timing_5_2 start_timing_6_1 start_timing_6_2 start_timing_7_1 start_timing_7_2 \
            rank_1_1 rank_1_2 rank_2_1 rank_2_2 rank_3_1 rank_3_2 rank_4_1 rank_4_2 rank_5_1 rank_5_2 rank_6_1 rank_6_2 rank_7_1 rank_7_2'.split()

def parse(df):
    """変なインデックスと重複を除去"""
    df = df.copy()
    df = df.iloc[:, :8] # ボートNo, 2連率, 3連率 のとこまでにする
    new_col = 'en _ info flst _ _ m _'.split()
    """
    en  : 艇番
    _   : 除去する写真列
    info: 登録番号 級別 支部 出身 年齢 体重
    w   : 勝率 2連率 3連率
    lw  : 当地勝率 当地2連率 当地3連率
    m   : No. 2連率 3連率
    _   : No. 2連率 3連率
    """
    df.columns = new_col  # 新しい列名設定
    df.drop('_', axis=1, inplace=True)  # 写真列除去
    df = df[~df['en'].duplicated()]  # 重複除去
    df.reset_index(drop=True, inplace=True)  # インデックスをリセット
    return df

def split_inner_data(df, race_id):
    """文字列データ分割とレースID追加
    
    + rid_en(index),
    + rid,
    en,
    info:-> pid, class_, name br, from, age, weight
    flst:-> F, L, st
    w:-> w, ww, www
    lw:-> lw, lww, lwww
    m:-> mn, mnww, mnwww
    b:-> bn, bnww, bnwww
    """
    df = df.copy()
    df['rid'] = race_id
    rid = df['rid']
    en = df['en'].map({chr(ord('０')+i): i for i in range(1,7)})
    info = df['info'].str.replace('/', ' ').str.split(expand=True)
    info[2] = (info[2]+info[3]) # 姓+名
    info.drop(3, axis=1, inplace=True)
    flst = df['flst'].str.split(expand=True)
    w = df['w'].str.split(expand=True)
    lw = df['lw'].str.split(expand=True)
    m = df['m'].str.split(expand=True)
    b = df['b'].str.split(expand=True)
    
    ret = pd.concat([rid, en, info, flst, w, lw, m, b], axis=1)
    cols = ('rid en pid class name branch from age weight F L st '
            'w ww www lw lww lwww mn mnww mnwww bn bnww bnwww'.split())
    ret.columns = cols
    idx = ret['rid'].astype(str) + ret['en'].map(lambda x: f'{x:>02}')
    ret.index = idx
    ret.index.name = 'rid_en'
    return ret
 
def url2raceid(url):
    # urlからレースID作成
    rno, jcd, hd = url.split('?')[-1].split('&')
    f = lambda x: x[x.index('=')+1:]
    return int(f'{f(hd)}{f(jcd):>02}{f(rno):>02}')

"""
url = 'https://www.boatrace.jp/owpc/pc/race/racelist?rno=2&jcd=02&hd=20220413'
race_id = url2raceid(url)
split_inner_data(df, race_id)
"""
def open_Grades_sort(target_info):
    dfs_dummy = pd.DataFrame(index=[])
    dfs = pd.read_html(target_info, encoding="utf-8")
    dfs_ = dfs[0]["レースNo（艇番色）進入コースSTタイミング成績", "レースNo（艇番色）進入コースSTタイミング成績"]

    for i in range(1, 25, 4):
        x = pd.concat([dfs_.iloc[i], dfs_.iloc[i+1], dfs_.iloc[i+2]])
        x_ = pd.DataFrame(x)
        x_ = x_.reset_index()
        x_ = x_.transpose()
        x_ = x_.iloc[1]
        dfs_dummy = dfs_dummy.append(x_)

    dfs_dummy.columns = New_col
    dfs_dummy.reset_index(drop=True, inplace=True)    
    return dfs_dummy