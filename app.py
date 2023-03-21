import psycopg2
from time import sleep, localtime, strftime

file = "data.log"

hostname = 'localhost'
database = 'data'
username = 'user'
password = 'password'
port = 5433
conn = None
cur = None
realtimeMode = True


def read(file):
    with open(file, 'r') as f:
        lines = f.readlines()
    return lines


def makeTimestamp(date, ts):
    if realtimeMode:
        timestamp = strftime("%Y-%m-%d %H:%M:%S+11", localtime())
    else:
        timezone = "+11"
        dateArr = date.split('-')[::-1]
        dateArr[0] = "20" + dateArr[0]
        timestamp = "-".join(dateArr) + " " + ts + timezone
    return timestamp


def enrich(readLine):
    readLine[0] = makeTimestamp(readLine[0], readLine[1])
    del readLine[1]
    readLine[1] = readLine[1].replace('\n', '')
    # converting from scientific form to decimal (14 point precision)
    readLine[1] = f"{float(readLine[1]):.14f}"
    return readLine


def insertDB(enrichedData):
    try:
        conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = username,
            password = password,
            port = port
        )

        cur = conn.cursor()
        insert_script = 'INSERT INTO my_table (ts, val) VALUES (%s, %s)'
        cur.execute(insert_script, (enrichedData[0], enrichedData[1]))
        conn.commit()

        print("INSERTED INTO DB: (" + enrichedData[0] + ", " + enrichedData[1] + ")", end='\n', flush=True)

    except Exception as err:
        print(err)

    finally:
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()


if __name__ == "__main__":
    print("READ FILE")
    print("STARTING...")
    for i in read(file):
        insertDB(enrich(i.split(',')))
        # print(enrich(i.split(',')), end='\n', flush=True)
        sleep(10)