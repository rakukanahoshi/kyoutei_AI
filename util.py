from numpy import NaN
from urllib3 import Retry
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup




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
    #w = df['w'].str.split(expand=True)
    #lw = df['lw'].str.split(expand=True)
    m = df['m'].str.split(expand=True)
    #b = df['b'].str.split(expand=True)
    
    ret = pd.concat([rid, en, info, flst, m], axis=1)
    cols = ('rid en pid class name branch from age weight F L st '
            'mn mnww mnwww '.split())
    ret.columns = cols
    ret["idx"] = ret['rid'].astype(str) + "_" + ret['en'].map(lambda x: f'{x:>02}')
    #ret.index = idx
    #ret.index.name = 'rid_en'
    ret.drop(["name", "from", "age", "mn"], axis=1, inplace=True)
    ret["weight"] = ret["weight"].str.replace("kg", "")
    ret[['F', 'L']] = ret[['F', 'L']].applymap(lambda x:x[1:])
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

#開催中のレース成績をまとめる
def Open_Grades_sort(target_info):
    New_col = 'insert_1_1 insert_1_2 insert_2_1 insert_2_2 insert_3_1 insert_3_2 insert_4_1 insert_4_2 insert_5_1 insert_5_2 insert_6_1 insert_6_2 insert_7_1 insert_7_2 \
            start_timing_1_1 start_timing_1_2 start_timing_2_1 start_timing_2_2 start_timing_3_1 start_timing_3_2 start_timing_4_1 start_timing_4_2 start_timing_5_1 start_timing_5_2 start_timing_6_1 start_timing_6_2 start_timing_7_1 start_timing_7_2 \
            rank_1_1 rank_1_2 rank_2_1 rank_2_2 rank_3_1 rank_3_2 rank_4_1 rank_4_2 rank_5_1 rank_5_2 rank_6_1 rank_6_2 rank_7_1 rank_7_2'.split()

    dfs_dummy = pd.DataFrame(index=[])
    dfs = pd.read_html(target_info, encoding="utf-8")
    dfs_ = dfs[0]["レースNo（艇番色）進入コースSTタイミング成績", "レースNo（艇番色）進入コースSTタイミング成績"]

    for i in range(1, 25, 4):
        y = dfs_.iloc[i+2].map({chr(ord('０')+i): i for i in range(1,7)})
        x = pd.concat([dfs_.iloc[i], dfs_.iloc[i+1], y])
        x_ = pd.DataFrame(x)
        x_ = x_.reset_index()
        x_ = x_.transpose()
        x_ = x_.iloc[1]
        dfs_dummy = dfs_dummy.append(x_)

    dfs_dummy.columns = New_col
    dfs_dummy.reset_index(drop=True, inplace=True)    
    return dfs_dummy


#半期、四半期の勝率
def player_win_rate_cal(rid, player_ID):
    Player_Win = [ 
                "q_Total_2", "q_Total_3", "h_Total_2", "h_Total_3",
                "q_Venue_2", "q_Venue_3", "h_Venue_2", "h_Venue_3"]

    Player_Win_Rate = pd.DataFrame(index=[], columns=Player_Win)
    PlayerRankData = pd.read_csv("data/PlayerRankData.csv", encoding="utf-8")

    ## 変数
    #レースID 01_20140102_10
    day = rid[3:7] + "-" + rid[7:9] + "-" + rid[9:11]

    #開催日、半期、四半期
    open_day = datetime.datetime.strptime(day, '%Y-%m-%d') #Dayの値を持ってきたい
    bf_h_day = open_day - datetime.timedelta(days=180)
    bf_q_day = open_day - datetime.timedelta(days=90)

    open_day = str(open_day.date())
    bf_h_day = str(bf_h_day.date())
    bf_q_day = str(bf_q_day.date())

    #開催地
    open_place = int(rid[0:2])
    #プレイヤー
    player_ID

    ## 期間と開催地を絞る

    PRD_H_Period = PlayerRankData.query(f"'{bf_h_day}' <= Day <= '{open_day}'")#開催日から半期さかのぼる処理を書きたい
    PRD_Q_Period = PlayerRankData.query(f'"{bf_q_day}" <= Day <= "{open_day}"')#開催日から4半期さかのぼる処理を書きたい

    #開催地のデータ―
    PRD_Loc_H_Period = PRD_H_Period.query(f"{open_place} == Place") #半期の開催地のデータ
    PRD_Loc_Q_Period = PRD_Q_Period.query(f"{open_place} == Place") #四半期の開催地のデータ

    #PlayerIDの選手の全出場数

    Player_Turn_Sum = PRD_H_Period[PRD_H_Period["PlayerID"] == player_ID]
    Player_Loc_Turn_Sum = PRD_Loc_H_Period[PRD_Loc_H_Period["PlayerID"] == player_ID]
    #PlayerIDの選手の開催地の出場数
    Player_Q_Turn_Sum = PRD_Q_Period[PRD_Q_Period["PlayerID"] == player_ID]
    Player_Q_Loc_Turn_Sum = PRD_Loc_Q_Period[PRD_Loc_Q_Period["PlayerID"] == player_ID]

    #出場回数によって決められた値を与える
    #半期の全出場回数が200未満はnanをとりあえず入れる。
    #後で平均値よりしたの値を代入

    if len(Player_Turn_Sum) >= 100:
        # 半期毎
        ## 全開催地の勝率を計算
        PRD_H_1st = PRD_H_Period['PlayerID'][PRD_H_Period['Rank']=="１"].value_counts() / PRD_H_Period['PlayerID'].value_counts()
        PRD_H_2nd = PRD_H_Period['PlayerID'][PRD_H_Period['Rank']=="２"].value_counts() / PRD_H_Period['PlayerID'].value_counts()
        PRD_H_3rd = PRD_H_Period['PlayerID'][PRD_H_Period['Rank']=="３"].value_counts() / PRD_H_Period['PlayerID'].value_counts()

        #DW = 複勝率, TW = 三連率
        DW_H_Rate = PRD_H_1st + PRD_H_2nd
        DW_H_Rate = DW_H_Rate.fillna(0)
        TW_H_Rate = DW_H_Rate + PRD_H_3rd
        TW_H_Rate = TW_H_Rate.fillna(0)

        Player_Win_Rate.loc[1,"h_Total_2"] = DW_H_Rate[player_ID]
        Player_Win_Rate.loc[1,"h_Total_3"] = TW_H_Rate[player_ID]

    else:
        Player_Win_Rate.loc[1,"h_Total_2"] = NaN
        Player_Win_Rate.loc[1,"h_Total_3"] = NaN



    if len(Player_Loc_Turn_Sum) > 8:
        ##開催地の勝率を計算
        PRD_Loc_H_1st = PRD_Loc_H_Period['PlayerID'][PRD_Loc_H_Period['Rank']=="１"].value_counts() / PRD_Loc_H_Period['PlayerID'].value_counts()
        PRD_Loc_H_2nd = PRD_Loc_H_Period['PlayerID'][PRD_Loc_H_Period['Rank']=="２"].value_counts() / PRD_Loc_H_Period['PlayerID'].value_counts()
        PRD_Loc_H_3rd = PRD_Loc_H_Period['PlayerID'][PRD_Loc_H_Period['Rank']=="３"].value_counts() / PRD_Loc_H_Period['PlayerID'].value_counts()

        DW_Loc_H_Rate = PRD_Loc_H_1st + PRD_Loc_H_2nd
        DW_Loc_H_Rate = DW_Loc_H_Rate.fillna(0)
        TW_Loc_H_Rate = DW_Loc_H_Rate + PRD_Loc_H_3rd
        TW_Loc_H_Rate = TW_Loc_H_Rate.fillna(0)

        Player_Win_Rate.loc[1,"q_Venue_2"] = DW_Loc_H_Rate[player_ID]
        Player_Win_Rate.loc[1,"q_Venue_2"] = TW_Loc_H_Rate[player_ID]

    else:
        Player_Win_Rate.loc[1,"q_Venue_2"] = NaN
        Player_Win_Rate.loc[1,"q_Venue_2"] = NaN

    if len(Player_Q_Turn_Sum) >= 40:
        #四半期毎
        ##全開催地の勝率を計算
        PRD_Q_1st = PRD_Q_Period['PlayerID'][PRD_Q_Period['Rank']=="１"].value_counts() / PRD_Q_Period['PlayerID'].value_counts()
        PRD_Q_2nd = PRD_Q_Period['PlayerID'][PRD_Q_Period['Rank']=="２"].value_counts() / PRD_Q_Period['PlayerID'].value_counts()
        PRD_Q_3rd = PRD_Q_Period['PlayerID'][PRD_Q_Period['Rank']=="３"].value_counts() / PRD_Q_Period['PlayerID'].value_counts()

        DW_Q_Rate = PRD_Q_1st + PRD_Q_2nd
        DW_Q_Rate = DW_Q_Rate.fillna(0)
        TW_Q_Rate = DW_Q_Rate + PRD_Q_3rd
        TW_Q_Rate = TW_Q_Rate.fillna(0)

        Player_Win_Rate.loc[1,"q_Total_2"] = DW_Q_Rate[player_ID]
        Player_Win_Rate.loc[1,"q_Total_3"] = TW_Q_Rate[player_ID]

    else:
        Player_Win_Rate.loc[1,"q_Total_2"] = NaN
        Player_Win_Rate.loc[1,"q_Total_3"] = NaN


    if len(Player_Q_Loc_Turn_Sum) > 4:
        ##開催地の四半期の勝率を計算
        PRD_Loc_Q_1st = PRD_Loc_Q_Period['PlayerID'][PRD_Loc_Q_Period['Rank']=="１"].value_counts() / PRD_Loc_Q_Period['PlayerID'].value_counts()
        PRD_Loc_Q_2nd = PRD_Loc_Q_Period['PlayerID'][PRD_Loc_Q_Period['Rank']=="２"].value_counts() / PRD_Loc_Q_Period['PlayerID'].value_counts()
        PRD_Loc_Q_3rd = PRD_Loc_Q_Period['PlayerID'][PRD_Loc_Q_Period['Rank']=="３"].value_counts() / PRD_Loc_Q_Period['PlayerID'].value_counts()

        DW_Loc_Q_Rate = PRD_Loc_Q_1st + PRD_Loc_Q_2nd
        DW_Loc_Q_Rate = DW_Loc_Q_Rate.fillna(0)
        TW_Loc_Q_Rate = DW_Loc_Q_Rate + PRD_Loc_Q_3rd
        TW_Loc_Q_Rate = TW_Loc_Q_Rate.fillna(0)

        Player_Win_Rate.loc[1,"q_Venue_2"] = DW_Loc_Q_Rate[player_ID]
        Player_Win_Rate.loc[1,"q_Venue_3"] = TW_Loc_Q_Rate[player_ID]

    else:
        Player_Win_Rate.loc[1,"q_Venue_2"] = NaN
        Player_Win_Rate.loc[1,"q_Venue_3"] = NaN


    #Player_Win_Rate.loc[1,"PlayerID"] = player_ID #PlayerIDの変数
    #Player_Win_Rate.loc[1,"raceID"] = rid #PlayerIDの変数

    return Player_Win_Rate

#開催期間中の出場レースの艇番
def bort_color(load_url):
    #load_url = target_info
    target_col = "0 1 2 3 4 5 6 7 8 9 10 11 12 13".split()
    New_col = "bort_color_1_1 bort_color_1_2 bort_color_2_1 bort_color_2_2 bort_color_3_1 bort_color_3_2 bort_color_4_1 bort_color_4_2 bort_color_5_1 bort_color_5_2 bort_color_6_1 bort_color_6_2 bort_color_7_1 bort_color_7_2".split()

    df_boat_color = pd.DataFrame(index=[], columns=target_col)
    #html = requests.get(load_url)

    soup = BeautifulSoup(open(load_url, encoding="utf-8"), "lxml")

    for i in range(6):
        is_fs = soup.find_all("tbody",attrs={"class":"is-fs12"})[i]
        table = is_fs.find_all("td")

        for x in range(9,23):#9,23
            if table[x].string:
                target_tag = str(is_fs.find_all("td")[x])
                col_name = str(x-9)
                #print("is-boatColor" in target_tag)
                #文字列にis-boatColorがあるかどうか
                #あればis-boatColorXのXをPandasに格納する
                if "is-boatColor" in target_tag:
                    df_boat_color.loc[i, col_name] = int(target_tag[23:24])
                else:
                    df_boat_color.loc[i, col_name] = "NaN"

    df_boat_color.columns = New_col            
    return df_boat_color

def weather_condition(load_url):
    weather_columns = "temp whether win_s win_a temp_w wave_h".split()
    df_weather_conditions = pd.DataFrame(index=[], columns=weather_columns)

    soup = BeautifulSoup(open(load_url, encoding="utf-8"), "lxml")

    weather_bodys = soup.find_all("div", attrs={"class":"weather1_body"})[0]
    weather_body = weather_bodys.find_all("div", attrs={"class":"weather1_bodyUnitLabel"})

    weather_list = []

    for i in range(len(weather_body)):
        weather_text = weather_body[i].text
        weather_text = weather_text.split("\n")
        del weather_text[0]
        del weather_text[-1]

        weather_list.append(weather_text)

    #weather_wind_a = 
    weather_wind_a = weather_bodys.select('[class^=weather1_bodyUnitImage]')[2]

    weather_wind_a = str(weather_wind_a)

    target = 'is-wind'
    idx = weather_wind_a.find(target)
    r = weather_wind_a[idx+len(target):]
    r = r.replace('"></p>', "")

    df_weather_conditions.loc[0, "temp"] = weather_list[0][1].replace("℃", "")
    df_weather_conditions.loc[0, "whether"] = weather_list[1][0]
    df_weather_conditions.loc[0, "win_s"] = weather_list[2][1].replace("m", "")
    df_weather_conditions.loc[0, "win_a"] = r
    df_weather_conditions.loc[0, "temp_w"] = weather_list[3][1].replace("℃", "")
    df_weather_conditions.loc[0, "wave_h"] = weather_list[4][1].replace("cm", "")

    return df_weather_conditions.loc[0]