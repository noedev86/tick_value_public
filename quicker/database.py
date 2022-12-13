import mysql.connector
from datetime import datetime,timedelta
import time
import logging

debug = True
time_window_hours=168 # equivant a une semaine


try:

    # linux server

    # db = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="<hidden>",
    #     database="<hidden>"
    # )
    # real server
    db = mysql.connector.connect(
        host="<hidden>",
        user="bvnwurux_noe_dev",
        password="<hidden>",
        database="bvnwurux_tick_values"
    )
    # db.autocommit()

    # linux own localhost
    # db = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="root",
    #     database="<hidden>"
    # )
    # db = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="",
    #     database="shahin_tick_values"
    # )
    print("successfully connected to db")

except Exception as e:
    if e.errno==2003:
        print("database could not be connected to")
        exit()
    else:
        print(e)


def print_(*args):
    if debug:
        print(*args)


def check_symbol(symbol):

    mycursor = db.cursor()
    mycursor.execute("SHOW TABLES")
    rows = mycursor.fetchall()

    # first check if symbol in table
    found=False
    for x in rows:
        if symbol==x[0].upper():
            print_("found : ",symbol," in database already")
            found=True
            break

    # if is not found, create table
    if not found:
        mycursor.execute("""CREATE TABLE `{}` (
                            `Ask` DOUBLE NULL DEFAULT NULL,
                            `Bid` DOUBLE NULL DEFAULT NULL,
                            `spread` DOUBLE NULL DEFAULT NULL,
                            `delta_ask` DOUBLE NULL DEFAULT NULL,
                            `delta_bid` DOUBLE NULL DEFAULT NULL,
                            `delta_spread` DOUBLE NULL DEFAULT NULL,
                            `datetime` DATETIME NULL DEFAULT NULL)
                            COLLATE='latin1_swedish_ci'
                            ENGINE=MyISAM;

                            """.format(symbol))

        print_("table created : ",symbol)
    mycursor.reset()


ask={}
bid={}
spread={}

first=[]

def strange_round(val,r_n):
    # cc=val/pow(10,-r_n)
    c=round(val/pow(10,-r_n),2)
    return c


def delete_old(dict_delete):
    try:
        # then delete all the data older than X hours (input by user)

        #run until never, and wait 1 hour everytime
        while True:
            print("deleting old..")
            now = datetime.utcnow()
            delta = timedelta(hours=time_window_hours)
            time_delete = now - delta
            del_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time_delete.timestamp()))
            # pair_list = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF']


            for pair in dict_delete:
                del_req = "DELETE FROM `{}` where datetime<'{}'".format(pair, del_time)
                mycursor = db.cursor()

                mycursor.reset()
                mycursor.execute(del_req)

                print("smash "+pair)
            time.sleep(10)
    except KeyboardInterrupt:
        print_("delete old datas was stopped by keyboard")
    except Exception as e:
        print_("[delete_func]",e)
def add_db(symbol,t,a,b,r_n):
    global ask,bid,spread,first,db

    a=round(a,r_n)
    b=round(b,r_n)

    try:
        # check there is no data for that second already in the database
        timestamp = t/1000
        sql_t = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))
        search="SELECT * FROM `{}` where datetime='{}'".format(symbol,sql_t)
        mycursor=db.cursor()
        res=mycursor.execute(search)
        rows=mycursor.fetchall()


        if len(rows)>0:
            return

        new_spread=a-b
        # in case first round and current rows were not found
        if symbol not in first:
            # insert without deltas
            first.append(symbol)
            mycursor.reset()
            req = "INSERT INTO `{}`(Ask,Bid,datetime,spread) VALUES({},{},'{}',{})".format(
                symbol, a, b, sql_t, strange_round(new_spread,r_n))
            res=mycursor.execute(req)
        # case not first round
        else:
            delta_ask = a - ask[symbol]
            delta_bid = b - bid[symbol]
            delta_spread = new_spread - spread[symbol]
            req = "INSERT INTO `{}`(Ask,Bid,datetime,spread,delta_ask,delta_bid,delta_spread) VALUES({},{},'{}',{},{},{},{})".format(
                symbol, a, b, sql_t, strange_round(new_spread,r_n), strange_round(delta_ask,r_n), strange_round(delta_bid,r_n), strange_round(delta_spread,r_n))
            mycursor.reset()
            mycursor.execute(req)

        print_("time last inserted : [",sql_t,"]")

        # updating current values to be the old one of the next round
        spread[symbol]=new_spread
        ask[symbol]=a
        bid[symbol]=b

    except Exception as e:
        print_("error : ",e)
