import datetime #現在の年までをリストに収容するため
import os
import time                            # スリープを使うために必要
from selenium import webdriver         # Webブラウザを自動操作する（python -m pip install selenium)
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup

currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
year = date.strftime("%Y")
next_year = int(year) + 1
now_ym_data = int((f"{currentDateTime.year}{currentDateTime.month:02}"))#現在のyyyymm
#print(type(now_ym_data))

month_list = []
#年のfor
for i in range(2014, next_year):
    for k in range(1, 13): #月の表示
        k1 = f"{k:02}"
        nengetu = int(f"{i}{k1}")
        #print(type(nengetu))
        if nengetu <= now_ym_data:
        #現在の年月 >= 回してる年月のときにリストに入れる
            month_list.append(f"{i}{k1}")

#↓↓↓↓↓ターゲットURLを取得するための処理↓↓↓↓↓
is_file = os.path.isfile("target_urls.txt") #target_urls.txtの取得

#URLを書いたテキストをリスト化したい
target_txt_list = [] #配列を空にする
if is_file:#txtファイルがある場合はリストに格納する
    with open("target_urls.txt", "r") as tf:
        target_txt_list = tf.read().split(',')

driver = webdriver.Chrome()            # Chromeを準備
driver.get('http://www1.mbrace.or.jp/od2/K/pindex.html')  # URLを開く
time.sleep(1)                          # 1秒間待機

driver.switch_to.frame("menu") #フレーム切り替え

select_jyou = driver.find_element_by_name("JYOU") 
select_loc = Select(select_jyou)
select_month = driver.find_element_by_name("MONTH")
select_date = Select(select_month)

#for i in range(1, 25): #場の数
for j in range(len(month_list)):
    #for j in range(len(month_list)):
    for i in range(1, 25):
        driver.switch_to.default_content()
        driver.switch_to.frame("menu")
        #for k in range(): #type="radio" name="MDAY"の数で回す
        i1 = f"{i:02}" #場の表記を二桁にする
        select_loc.select_by_value(i1)
        select_date.select_by_value(month_list[j])
        time.sleep(15)

        driver.switch_to.default_content() #一度デフォルトのフレームに戻る
        driver.switch_to.frame(driver.find_element_by_name("DAY"))   #フレームdayに切り替え

        html = driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, "lxml")

        for element in soup.select("input"):
            open_day = element.get("value")
            #print(open_day)
            #i1,mohth_list[j],open_dayを合成してtarget_urlを作ってテキストを作成
            for k in range(1,13):
                k1 = f"{k:02}"
                target_url = f"rno={k1}&jcd={i1}&hd={month_list[j]}{open_day}"
                
                if target_url in target_txt_list:
                    pass
                else:
                    with open("target_urls.txt", "a", encoding="utf-8") as file:
                        file.write(target_url + ",")
            time.sleep(1)