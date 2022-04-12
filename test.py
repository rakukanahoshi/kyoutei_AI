# %% [markdown]
# 選手のレース場、着順、日付をひたすらまとめていく

# %%
#!pip install tqdm

# %%
import pandas as pd
import os
from glob import glob
from tqdm import tqdm_notebook as tqdm

#格納したいカラムのデータフレームを作成する
Player_Data = ["PlayerID", "PlayerName", "Rank", "Day", "Race_No", "Place"]
Player_Data_Ghost = pd.DataFrame(index=[], columns=Player_Data)
df_player_data = pd.DataFrame(index=[], columns=Player_Data)

# %%
result_file_list = glob("test/*/result_html/*")
result_file = [x.replace("\\", "/") for x in result_file_list]
#print(result_file[1])

#途中から始める処理を書く
is_file = os.path.isfile("match_up.txt")

target_txts_list = [] #配列を空にする
match_up_list = [] #配列を空にする

if is_file:
    with open("match_up.txt", "r") as tf:
        match_up_list = tf.read().split(',')[:-1]
    #途中から始めるためのコード書く
    target_txts_list = set(result_file) - set(match_up_list)
else:
    target_txts_list = result_file

print(len(result_file))
print(len(target_txts_list))

#ディレクトリ探す
#jou_number = os.listdir(f"test/")


# %%
#result_htmlにアクセスして回す

for target_txt in tqdm(target_txts_list):
    #レース結果を保存したhtmlファイルとそのDF
    dfs = pd.read_html(target_txt, encoding="utf-8")

    tyakujun = dfs[2]
    Player_Data_Ghost["PlayerID"] = tyakujun["ボートレーサー"].str.extract(r"(\d+)").astype(int)
    Player_Data_Ghost["PlayerName"] = tyakujun["ボートレーサー"].str.extract(r"(\D+)")
    Player_Data_Ghost["Place"] = target_txt[-19:-17]
    Player_Data_Ghost["Day"] = target_txt[-16:-8]#Data型にしたい
    Player_Data_Ghost["Day"] = pd.to_datetime(Player_Data_Ghost["Day"])
    Player_Data_Ghost["Race_No"] = target_txt[-7:-5]
    Player_Data_Ghost["Rank"] = tyakujun["着"]

    #DFに情報を追加する
    df_player_data = df_player_data.append(Player_Data_Ghost)

    #取得済みリストを作る
    with open("match_up.txt", "a", encoding="utf-8") as file:
            file.write(target_txt + ",")

df_player_data.drop_duplicates(keep="last", inplace=True)


# %%
display(df_player_data)
df_player_data.describe()

# %%
df_player_data.isna().sum()

# %%
output_file = "PlayerRankData.csv"
df_player_data.to_csv(os.path.join("data/", output_file), mode="a", index=False)

# %% [markdown]
# # 目的は？四半期、半期毎のトータルの複勝率、三連率、開催地の複勝率、三連率をリターンする関数

# %%
PlayerRankData = pd.read_csv("data/PlayerRankData.csv", encoding="utf-8")

# %%
Player_Win = [ "RaceID", "PlayerID",
                "q_Total_2", "q_Total_3", "h_Total_2", "h_Total_3",
                "q_Venue_2", "q_Venue_3", "h_Venue_2", "h_Venue_3"]

Player_Win_Rate = pd.DataFrame(index=[], columns=Player_Win)

Player_Win_Rate.loc[0,"PlayerID"] = 4689
#x.loc[0, 'PlayerID'] = 999 みたいなだとどうです？
display(Player_Win_Rate)



# %%
import pandas as pd
import datetime

PlayerRankData = pd.read_csv("data/PlayerRankData.csv", encoding="utf-8")

def player_win_rate():
#NoAは出場数、_2は二連率、_3は3連率、Venueは開催地、qは3ヶ月、hは6ヶ月
Player_Win = [ "RaceID", "PlayerID",
                "q_Total_2", "q_Total_3", "h_Total_2", "h_Total_3",
                "q_Venue_2", "q_Venue_3", "h_Venue_2", "h_Venue_3"]

Player_Win_Rate = pd.DataFrame(index=[], columns=Player_Win)

## 変数
#レースID
race_id = "012015060101"

#開催日、半期、四半期
open_day = datetime.datetime.strptime("2015-06-01", '%Y-%m-%d') #Dayの値を持ってきたい
bf_h_day = open_day - datetime.timedelta(days=180)
bf_q_day = open_day - datetime.timedelta(days=90)

open_day = str(open_day.date())
bf_h_day = str(bf_h_day.date())
bf_q_day = str(bf_q_day.date())

#開催地
open_place = "1"
#プレイヤー
player_id = 4045

## 期間と開催地を絞る

PRD_H_Period = PlayerRankData.query(f"'{bf_h_day}' <= Day <= '{open_day}'")#開催日から半期さかのぼる処理を書きたい
PRD_Q_Period = PlayerRankData.query(f'"{bf_q_day}" <= Day <= "{open_day}"')#開催日から4半期さかのぼる処理を書きたい

#開催地のデータ―
#Placeを変数にする
PRD_Loc_H_Period = PRD_H_Period.query(f"{open_place} == Place") #半期の開催地のデータ
PRD_Loc_Q_Period = PRD_Q_Period.query(f"{open_place} == Place") #四半期の開催地のデータ

#PlayerIDの選手の全出場数

Player_Turn_Sum = PRD_H_Period[PRD_H_Period["PlayerID"] == player_id]
Player_Loc_Turn_Sum = PRD_Loc_H_Period[PRD_Loc_H_Period["PlayerID"] == player_id]
#PlayerIDの選手の開催地の出場数
Player_Q_Turn_Sum = PRD_Q_Period[PRD_Q_Period["PlayerID"] == player_id]
Player_Q_Loc_Turn_Sum = PRD_Loc_Q_Period[PRD_Loc_Q_Period["PlayerID"] == player_id]

#出場回数によって決められた値を与える
#半期の全出場回数が200未満はnanをとりあえず入れる。
#後で平均値よりしたの値を代入

if len(Player_Turn_Sum) >= 0:
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

    Player_Win_Rate.loc[1,"h_Total_2"] = DW_H_Rate[player_id]
    Player_Win_Rate.loc[1,"h_Total_3"] = TW_H_Rate[player_id]

else:
    Player_Win_Rate.loc[1,"h_Total_2"] = None
    Player_Win_Rate.loc[1,"h_Total_3"] = None



if len(Player_Loc_Turn_Sum) > 0:
    ##開催地の勝率を計算
    PRD_Loc_H_1st = PRD_Loc_H_Period['PlayerID'][PRD_Loc_H_Period['Rank']=="１"].value_counts() / PRD_Loc_H_Period['PlayerID'].value_counts()
    PRD_Loc_H_2nd = PRD_Loc_H_Period['PlayerID'][PRD_Loc_H_Period['Rank']=="２"].value_counts() / PRD_Loc_H_Period['PlayerID'].value_counts()
    PRD_Loc_H_3rd = PRD_Loc_H_Period['PlayerID'][PRD_Loc_H_Period['Rank']=="３"].value_counts() / PRD_Loc_H_Period['PlayerID'].value_counts()

    DW_Loc_H_Rate = PRD_Loc_H_1st + PRD_Loc_H_2nd
    DW_Loc_H_Rate = DW_Loc_H_Rate.fillna(0)
    TW_Loc_H_Rate = DW_Loc_H_Rate + PRD_Loc_H_3rd
    TW_Loc_H_Rate = TW_Loc_H_Rate.fillna(0)

    Player_Win_Rate.loc[1,"q_Venue_2"] = DW_Loc_H_Rate[player_id]
    Player_Win_Rate.loc[1,"q_Venue_2"] = TW_Loc_H_Rate[player_id]


else:
    Player_Win_Rate.loc[1,"q_Venue_2"] = None
    Player_Win_Rate.loc[1,"q_Venue_2"] = None


#開催地毎の勝率
if len(Player_Q_Turn_Sum) >= 0:
    #四半期毎
    ##全開催地の勝率を計算
    PRD_Q_1st = PRD_Q_Period['PlayerID'][PRD_Q_Period['Rank']=="１"].value_counts() / PRD_Q_Period['PlayerID'].value_counts()
    PRD_Q_2nd = PRD_Q_Period['PlayerID'][PRD_Q_Period['Rank']=="２"].value_counts() / PRD_Q_Period['PlayerID'].value_counts()
    PRD_Q_3rd = PRD_Q_Period['PlayerID'][PRD_Q_Period['Rank']=="３"].value_counts() / PRD_Q_Period['PlayerID'].value_counts()

    DW_Q_Rate = PRD_Q_1st + PRD_Q_2nd
    DW_Q_Rate = DW_Q_Rate.fillna(0)
    TW_Q_Rate = DW_Q_Rate + PRD_Q_3rd
    TW_Q_Rate = TW_Q_Rate.fillna(0)

    Player_Win_Rate.loc[1,"q_Total_2"] = DW_Q_Rate[player_id]
    Player_Win_Rate.loc[1,"q_Total_3"] = TW_Q_Rate[player_id]

else:
    Player_Win_Rate.loc[1,"q_Total_2"] = None
    Player_Win_Rate.loc[1,"q_Total_3"] = None


if len(Player_Q_Loc_Turn_Sum) > 0:
    ##開催地の勝率を計算
    PRD_Loc_Q_1st = PRD_Loc_Q_Period['PlayerID'][PRD_Loc_Q_Period['Rank']=="１"].value_counts() / PRD_Loc_Q_Period['PlayerID'].value_counts()
    PRD_Loc_Q_2nd = PRD_Loc_Q_Period['PlayerID'][PRD_Loc_Q_Period['Rank']=="２"].value_counts() / PRD_Loc_Q_Period['PlayerID'].value_counts()
    PRD_Loc_Q_3rd = PRD_Loc_Q_Period['PlayerID'][PRD_Loc_Q_Period['Rank']=="３"].value_counts() / PRD_Loc_Q_Period['PlayerID'].value_counts()

    DW_Loc_Q_Rate = PRD_Loc_Q_1st + PRD_Loc_Q_2nd
    DW_Loc_Q_Rate = DW_Loc_Q_Rate.fillna(0)
    TW_Loc_Q_Rate = DW_Loc_Q_Rate + PRD_Loc_Q_3rd
    TW_Loc_Q_Rate = TW_Loc_Q_Rate.fillna(0)

    Player_Win_Rate.loc[1,"q_Venue_2"] = DW_Loc_Q_Rate[player_id]
    Player_Win_Rate.loc[1,"q_Venue_3"] = TW_Loc_Q_Rate[player_id]

else:
    Player_Win_Rate.loc[1,"q_Venue_2"] = None
    Player_Win_Rate.loc[1,"q_Venue_3"] = None


Player_Win_Rate.loc[1,"PlayerID"] = player_id #PlayerIDの変数
Player_Win_Rate.loc[1,"RaceID"] = race_id #PlayerIDの変数



# %%
display(PlayerRankData)
PlayerRankData.dtypes

# %%
#player_winrate()
{chr(ord('０')+i):i for i in range(1,7)} #こんな辞書を渡すとrankはintにできそう

# %%
import os
import pandas as pd

#NoAは出場数、_2は二連率、_3は3連率、Venueは開催地、qは3ヶ月、hは6ヶ月
Player_Win = [ "RaceID","PlayerID", "NoA",
                "q_Total_2", "q_Total_3", "h_Total_2", "h_Total_3",
                "q_Venue_2", "q_Venue_3", "h_Venue_2", "h_Venue_3"]

url = "test/01/result_html/01_20140102_01.html"
dfs = pd.read_html(url, encoding="utf-8")
dfs[2]

Player_Win_Rate = pd.DataFrame(index=[], columns=Player_Win)



