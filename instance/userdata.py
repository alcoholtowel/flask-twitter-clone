import sqlite3

# データベースファイルへのパス
db_path = 'site.db'

# SQLiteデータベースに接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# userテーブル作成用のSQLコマンド
create_table_sql = '''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER NOT NULL, 
    username TEXT NOT NULL, 
    profile TEXT, 
    icon_url VARCHAR(100), 
    header_url VARCHAR(100), 
    PRIMARY KEY (id)
)
'''

# userテーブルの作成
cursor.execute(create_table_sql)

# ユーザーデータの挿入
users = [
    (1, 'Amane', '一年周（ヒトトセアマネ）。夢ツイートしかしない。', 'icon1.png', 'header1'),
    (2, '周の夢日記', '周が見た夢について記録するよ。それしかないよ。', 'icon2.png', 'header2'),
    (3, '腐ってる周', 'BLについて語るときのアカウントらしい。使うのかなほんとに', 'icon3.png', 'header3')
]

for user in users:
    cursor.execute('''
        INSERT INTO user (id, username, profile, icon_url, header_url) VALUES (?, ?, ?, ?, ?)
    ''', user)

# 変更をコミットして接続を閉じる
conn.commit()
conn.close()

print('userテーブルの作成とデータ挿入が完了したよ。')