# #!/usr/bin/env python3
import datetime

import signal
import websocket
import rel
import json
import database
from threading import Thread
import mysql.connector
import sys


use_argv=False

pairs_dict={'EURUSD':5,
              'GBPUSD':5,
              'USDJPY':3,
              'USDCHF':5}
# pairs_dict={'EURUSD':5,'USDCHF':5,'GBPUSD':5,'USDJPY':3,'AUDUSD':5,'USDCAD':5
#     ,'EURCHF':5,'EURGBP':5,'EURJPY':3,'EURCAD':5,'EURAUD':5,'GBPCHF':5,'GBPJPY':3,'CHFJPY':3,
#             }

# pairs_dict={'AUDCAD':5,'AUDCHF':5,'AUDJPY':3,'AUDNZD':5,'AUDSGD':2,'AUDUSD':5,'CADCHF':5,'CADJPY':3,'CHFJPY':3,'EURAUD':5,'EURCAD':5,'EURCHF':5,'EURGBP':5,'EURJPY':3,'EURNZD':5,'EURSGD':5,'EURUSD':5,'GBPAUD':5,'GBPCAD':5,'GBPCHF':5,'GBPJPY':3,'GBPNZD':5,'GBPSGD':5,'GBPUSD':5,'NZDCAD':5,'NZDCHF':5,'NZDJPY':3,'NZDUSD':5,'USDCAD':5,'USDCHF':5,'USDJPY':3,'USDSGD':5,'SGDJPY':3}


out_dict={}

if use_argv:
    if len(sys.argv)>0:
        sys.argv.pop(0)
        for i in sys.argv:
            s = i.split(":")
            out_dict[s[0]] = s[1]
    else:
        print("no arguments passed, cannot start robot")
        exit()
    pairs_dict=out_dict

pairs_dict_new={}

# just a simple function to put a "-" in the middle
pairs=""

for i,pair in enumerate(pairs_dict):

    pairs=pairs+"C."+pair[:3]+"-"+pair[3:]+","

    changed_symbol=pair[:3]+"-"+pair[3:]

    pairs_dict_new[changed_symbol]=pairs_dict[pair]
    database.check_symbol(changed_symbol)

pairs = pairs[:-1]

print(pairs_dict_new)
# thread to insert into database


datas=[]
def add_queue(symbol,t,a,b,r_n):
    global datas
    datas.append([symbol,t,a,b,r_n])
    # print(datas)

def add_db():
    global datas
    try:
        # db = mysql.connector.connect(
        #     host="104.168.157.164",
        #     user="bvnwurux_noe_dev",
        #     password="Tickprofile333",
        #     database="bvnwurux_tick_values"
        # )
        while True:
            for x in datas:
                database.add_db(x[0],x[1],x[2],x[3],x[4])
                if x in datas:
                    datas.remove(x)
    except KeyboardInterrupt:
        print("program ending..")


threads=[]
t2 = Thread(target=add_db)
t2.start()
# for x in range(0,10):
#
#     t2 = Thread(target=add_db)
#     t2.start()
#     threads.append(t2)


polygon_api_key="CHPTP31pFymL7FDLC0yH4elSBRXTL0eT"





def on_message(ws, message):
    # print("msg",message)


    global pairs_dict_new
    try:
        json_msg=json.loads(message)[0]

        if 'message' in json_msg:
            print(json_msg['message'])

        if 'status' in json_msg:
            if json_msg['status']=="auth_success": # successfully authenticated
                r=ws.send('{"action":"subscribe","params":"'+pairs+'"}')  # subscribing to currencies
                print("should subscribe to "+pairs)
        #get the data feed from the currencies
        if 'ev' in json_msg:
            if json_msg['ev']=="C":
                symbol=json_msg['p'].replace("/","-")
                round_number=pairs_dict_new[symbol]
                t = Thread(target=add_queue, args=(symbol,json_msg['t'],json_msg['a'],json_msg['b'],round_number,))
                t.start()
                # print(message)

                # t.join(1)

    except Exception as e:
        print("error : ",e)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    database.db.close()
    print("### closed ###")
    exit()


def on_open(ws):
    print("Opened connection")
    ws.send('{"action":"auth","params":"'+polygon_api_key+'"}') #connecting with secret api key


if __name__ == "__main__":
    # websocket.enableTrace(True) # just to show all the requests made (debug mode)
    ws = websocket.WebSocketApp("wss://socket.polygon.io/forex",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close,)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()