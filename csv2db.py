import csv
import psycopg2

# DB情報
path = 'localhost'
port = '5432'
dbname = 'postgres'
user = 'blackPorgy'
password = 'password'

# psycopg2にdb情報を渡してアクセス
conText = "host={} port={} dbname={} user={} password={}"
conText = conText.format(path,port,dbname,user,password)
connection = psycopg2.connect(conText)
connection.get_backend_pid()
cur = connection.cursor()

# csvを開き，中のデータをdbへ投入
with open('data.csv', newline='') as csvfile:
    read = csv.reader(csvfile)
    for row in read:
        sql = "INSERT INTO KIONDATA VALUES('{}',{})"
        sql = sql.format(str(row[0]).replace("/","-"),row[1])
        cur.execute(sql)
        connection.commit()

cur.close()
connection.close()
