# tu_scraper

東京大学文学部・大学院人文社会系研究科( http://www.l.u-tokyo.ac.jp/ )の  
大学院生向けお知らせ一覧ページ( http://www.l.u-tokyo.ac.jp/student/student_news/news_pg.html )に  
新規掲載されたお知らせを抽出し、メールにて通知します。

# 機能

scraping.pyと同階層にoldNews.csvがない場合、初回起動モードとなり  
お知らせ一覧ページに掲載中のお知らせを全件抽出し、過去のお知らせとしてoldNews.csvに記録します。  
（初回起動モードでは、メールは送信されません）

scraping.pyと同階層にoldNews.csvがある場合は通常起動モードとなります。  
お知らせ一覧ページに掲載中のお知らせと、oldNews.csvに記録された過去のお知らせを比較し  
oldNews.csvにないお知らせを新着お知らせとみなし、oldNews.csvに追加した上で  
新着お知らせをメールにて配信します。

メールの配信元情報（メールアドレス・パスワード・ホスト名）はfromAddr.yamlに記載します。  
配信先はtoAddr.txtに列挙する形で記載します。  
上記2ファイルがscraping.pyと同階層にない場合、プログラムはエラーとなります。

プログラムの実行結果はapp.logの名前でログファイルとして出力されます。  
app.logは日毎でログローテートが行われます。

本プログラムはcron等により定期実行する運用を推奨しますが、  
その場合は出力されるログファイルによるディスクフルにご注意下さい。

# 動作環境

* Python 3系
* Pythonライブラリ Beautiful Soup( https://www.crummy.com/software/BeautifulSoup/bs4/doc/ )

# 使い方

上記の動作環境を満たしていることを前提とします。

```sh
# リポジトリからクローン
git clone https://github.com/herst5/tu_scraper
cd tu_scraper

# fromAddr.yamlを修正し、メールの配信元情報（メールアドレス・パスワード・ホスト名）を記載
vi fromAddr.yaml

# toAddr.txtを修正し、メールの配信先を記載
vi toAddr.txt

# プログラム実行。初回起動モード
python scraping.py
```

# その他

本プログラムは処理内にて東京大学文学部・大学院人文社会系研究科のウェブサイトに接続しています。  
過剰な頻度で実行することはDOS攻撃を行うことと同等のため、ご注意ください。

# 作者

herst5( https://github.com/herst5 )
