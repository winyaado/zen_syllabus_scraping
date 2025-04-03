from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
import time
import csv

#環境変数
chromedriverpath = r"F:\hogehoge\chromedriver.exe"
url_syllabus = r"https://syllabus.zen.ac.jp/search/result?sort=name-asc&page=ページ番号"
content_name = r"textStyle_heading.3xl sm:fs_32px"
content_main = r"d_flex items_center text_base.body textStyle_body.md p_12px_12px_16px_12px md:p_16px_18px"
csv_heder = ["科目名","履修想定年次","単位数","開講Q","科目区分","授業の方法","評価方法","前提推奨科目",
             "前提必須科目","後継推奨科目","科目コード","到達目標","教科書・参考書","授業時間外の学修","特記事項"]

def chromedriver():
    # ChromeDriverの設定
    options = Options()
    options.add_argument("--headless")  # ヘッドレスモード（画面を表示しない）
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(chromedriverpath)  
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# By.CSS_SELECTOR用エスケープ
def css(selector):
    selector = re.sub(r'([.#\[\]$^*+()=|{}:<>?])', r'\\\1', selector)
    selector = r"." + selector.replace(" ", ".")
    return selector

def get_subjects(driver,pageno=1):
    try:
        links=[]
        # URLを開く
        url = url_syllabus.replace("ページ番号", str(pageno))
        driver.get(url)
        # JavaScriptの実行を待機
        time.sleep(1)
        pattern = re.compile(r"subjects")
        # aタグの中にhrefが在り"subjects"を含んでいるなら
        for a in driver.find_elements(By.TAG_NAME, "a"):
            href = a.get_attribute("href")
            if href:
                match = pattern.search(href)
                if match:
                    links.append(href)
        # 正常に取得できた場合次のページを再帰的に呼び出す
        if links:
            links = links + get_subjects(driver,pageno+1)
        return links
    except Exception as e:
        print(e)
    
def get_subjects_len(driver):
    try:
        # URLを開く
        url = url_syllabus.replace("ページ番号", "1")
        driver.get(url)
        # JavaScriptの実行を待機
        time.sleep(1)
        # ページ内のすべての要素を取得
        h2_tags = driver.find_elements(By.TAG_NAME, 'h2')
        for tag in h2_tags:
            if re.match(r"対象科目\(全\d+件\)", tag.text):
                return re.search(r'\d+', tag.text).group(0)
    except Exception as e:
        print(e)

def get_subjects_content(driver,url):
    try:
        # URLを開く
        driver.get(url)
        # JavaScriptの実行を待機
        time.sleep(1)
        # 各種情報取得
        科目情報 = []
        # 科目名
        print(driver.find_element(By.CSS_SELECTOR,css(content_name)).text)
        科目情報.append(driver.find_element(By.CSS_SELECTOR,css(content_name)).text)
        # 科目情報
        content = driver.find_elements(By.CSS_SELECTOR,css(content_main))
        for info in content:
            科目情報.append(info.text)
        return 科目情報
    except Exception as e:
        print(e)

driver = chromedriver()

# 対象科目数取得
subjects_len = get_subjects_len(driver)
print(f"対象科目数:{subjects_len}")
# 科目リンク取得
syllabus_links = get_subjects(driver)
print(f"取得科目数:{len(syllabus_links)}")
# 科目詳細取得
if str(len(syllabus_links)) == subjects_len:
    print("すべての科目リンクの取得に成功('ω')ノ")
    科目情報_list = []
    科目情報_list.append(csv_heder)
    for link in syllabus_links:
        科目情報_list.append(get_subjects_content(driver,link))
    # csv吐き出し
    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(科目情報_list)