import mysql.connector
from datetime import datetime,timedelta
import time

import requests

debug = True
time_window_hours=168 # equivant a une semaine


use_option3=False

# pair_list = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF']
# pair_list = {'EURUSD': 5, 'USDCHF': 5, 'GBPUSD': 5, 'USDJPY': 3, 'AUDUSD': 5, 'USDCAD': 5
#     , 'EURCHF': 5, 'EURGBP': 5, 'EURJPY': 3, 'EURCAD': 5, 'EURAUD': 5, 'GBPCHF': 5, 'GBPJPY': 3,
#               'CHFJPY': 3,
#               }
pair_list={'AUDCAD':5,'AUDCHF':5,'AUDJPY':3,'AUDNZD':5,'AUDSGD':2,'AUDUSD':5,'CADCHF':5,'CADJPY':3,'CHFJPY':3,'EURAUD':5,'EURCAD':5,'EURCHF':5,'EURGBP':5,'EURJPY':3,'EURNZD':5,'EURSGD':5,'EURUSD':5,'GBPAUD':5,'GBPCAD':5,'GBPCHF':5,'GBPJPY':3,'GBPNZD':5,'GBPSGD':5,'GBPUSD':5,'NZDCAD':5,'NZDCHF':5,'NZDJPY':3,'NZDUSD':5,'USDCAD':5,'USDCHF':5,'USDJPY':3,'USDSGD':5,'SGDJPY':3}


try:

    # linux server
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
            database="bvnwurux_tick_values"
    )
    db2 = mysql.connector.connect(
        host="localhost",
        user="root2",
        password="root",
        database="bvnwurux_tick_values"
    )

    print("successfully connected to db")
   
    if use_option3:
        print("using base and quote calculation (slowing down)")
except Exception as e:
    if e.errno==2003:
        print("database could not be connected to")
        exit()
    else:
        print(e)


def print_(txt):
    if debug:
        print(txt)


def check_symbol(symbol):

    mycursor = db.cursor()
    mycursor.execute("SHOW TABLES")
    rows = mycursor.fetchall()

    # first check if symbol in table
    found=False
    for x in rows:
        if symbol==x[0].upper():
            print_("found : "+symbol+" in database already")
            found=True
            break
    # just a lil mod to add a unique key to the process
    if found:
        print("found !")
        try:
            print("h?")
            exec="""ALTER TABLE `{}` ADD UNIQUE INDEX `unique_id` (`datetime`);""".format(symbol)
            print(exec)

            print("2")
            # mycursor.execute(exec)
            print("3")
            print("{} was just altered to have a unique id".format(symbol))
        except Exception as e:
            print(e)
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

        print_("table created : "+symbol)
    # now check if the quote of the symbol is already created, if not create it as a table e.g. EUR-USD --> EUR and USD
    found_base=found_quote=False
    split = symbol.split("-")


    if len(split) > 1:
        base_c=split[0]
        quote_c=split[1]

        for x in rows:
            if base_c==x[0].upper():
                print_("found base "+base_c+" in database already")
                found_base=True
            if quote_c==x[0].upper():
                print_("found quote "+quote_c+" in database already")
                found_quote=True

                # to shorten the loop in case both found
                if found_base:
                    break

        if not found_base:
            mycursor.reset()

            mycursor.execute("""CREATE TABLE `{}` (
                                `val` INT(11) NULL DEFAULT NULL,
                                `datetime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                                `id` INT(11) NOT NULL AUTO_INCREMENT,
                                PRIMARY KEY (`id`) USING BTREE
                                )
                                COLLATE='latin1_swedish_ci'
                                ENGINE=MyISAM;
                                """.format(base_c))
            print_("table created : " + base_c)

        if not found_quote:
            mycursor.reset()

            mycursor.execute("""CREATE TABLE `{}` (
                                `val` INT(11) NULL DEFAULT NULL,
                                `datetime` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
                                `id` INT(11) NOT NULL AUTO_INCREMENT,
                                PRIMARY KEY (`id`) USING BTREE
                                )
                                COLLATE='latin1_swedish_ci'
                                ENGINE=MyISAM;
                                """.format(quote_c))
            print_("table created : " + quote_c)
    else:
        print_("symbol could not be splitted into base and quote")


    mycursor.reset()
    mycursor.close()
ask={}
bid={}
spread={}

first=[]

def strange_round(val,r_n):
    # cc=val/pow(10,-r_n)
    c=round(val/pow(10,-r_n),2)
    return c

buffer=datetime.fromtimestamp(0)

def delete_old():
    t0=time.time()

    try:
        # then delete all the data older than X hours (input by user)
        global buffer,pair_list
        now = datetime.utcnow()

        if buffer < now:
            buffer = now + timedelta(hours=1)

            delta = timedelta(hours=time_window_hours)
            time_delete = now - delta
            del_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time_delete.timestamp()))

            for pair in pair_list:
                pair = pair[:3] + "-" + pair[3:]
                del_req = "DELETE FROM `{}` where datetime<'{}'".format(pair, del_time)
                mycursor = db.cursor()

                mycursor.reset()
                mycursor.execute(del_req)


            print("smash")
            dt = time.time() - t0
            print("dt delete db : ", dt)
    except Exception as e:
        print(e)


send_once=False
def add_db(symbol,t,a,b,r_n):
    global ask,bid,spread,first,db,send_once
    delete_old()
    t0 = time.time()

    a=round(a,r_n)
    b=round(b,r_n)

    try:
        # check there is no data for that second already in the database
        timestamp = t/1000
        sql_t = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))

        now_timestamp = time.time()

        delta_t = round(now_timestamp - timestamp,2)

        if delta_t>10 and not send_once:
            send_once=True
            requests.get("https://api.telegram.org/bot<hidden>/sendMessage?chat_id=<hidden>&text=10 secs delta passed")

        mycursor=db.cursor()


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

            #@TODO : increase spead of this call to make it more efficient (thread is shit)

            # handle the base and quote system
            if delta_spread!=0 and use_option3:
                add_base_quote(symbol,delta_spread,delta_ask,delta_bid,r_n)


        t_now=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

        # print("last t: [",sql_t,"]",symbol," [",t_now,"]")
        print(symbol,"  dt [",delta_t,"]")
        # updating current values to be the old one of the next round
        spread[symbol]=new_spread
        ask[symbol]=a
        bid[symbol]=b



        # close the cursor to be able to use it again next request
        mycursor.close()

        dt = time.time()-t0

        # print("[add_db] ",dt)

    except Exception as e:
        print("error : ",e)


def add_base_quote(symbol,delta_spread,delta_ask,delta_bid,r_n):
    global db2
    split = symbol.split("-")
    t0 = time.time()

    delta_spread=strange_round(delta_spread, r_n)
    delta_ask=strange_round(delta_ask, r_n)
    delta_bid=strange_round(delta_bid, r_n)

    # according to formula, change the value of delta spread
    if delta_bid > delta_ask or delta_bid < delta_ask:
        delta_spread = -delta_spread
    if delta_spread==0:
        return

    if len(split) > 1:
        base_c=split[0]
        quote_c=split[1]

        # starting values should be 0, since at the beginning the tables are empty
        b_curr_val=0
        q_curr_val=0

        try:
            search="SELECT val FROM {} ORDER BY id DESC LIMIT 1;".format(base_c)

            mycursor2=db2.cursor()
            mycursor2.execute(search)
            row=mycursor2.fetchall()

            # get the latest value of the base currency
            if len(row)>0:
                b_curr_val=row[0][0]

            search="SELECT val FROM {} ORDER BY id DESC LIMIT 1;".format(quote_c)
            mycursor2.reset()
            mycursor2.execute(search)
            row=mycursor2.fetchall()

            # get the latest value of the base/quote currency
            if len(row)>0:
                q_curr_val=row[0][0]
            dt = time.time() - t0
            # print("dt in base currency : ",dt)

            #if the spread is positive, add it to the base currency, and substract from the quote currency
            # if the spread is negative, substract from base and add to quote
            if delta_spread!=0:
                insert_base="INSERT INTO {base}(val) VALUES({val})".format(base=base_c,val=b_curr_val+delta_spread)
                mycursor2.reset()
                mycursor2.execute(insert_base)

                insert_quote = "INSERT INTO {quote}(val) VALUES({val})".format(quote=quote_c, val=q_curr_val - delta_spread)
                mycursor2.reset()
                mycursor2.execute(insert_quote)
                # print(symbol," ",delta_spread)
            mycursor2.close()
        except Exception as e:
            print("[add_base_quote]",e)

    else:
        print_("symbol could not be splitted into base and quote")
