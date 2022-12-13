import json

import rel
import websocket

pairs_dict={'AUDCAD':5,'AUDCHF':5,'AUDJPY':3,'AUDNZD':5,'AUDSGD':2,'AUDUSD':5,'CADCHF':5,'CADJPY':3,'CHFJPY':3,'EURAUD':5,'EURCAD':5,'EURCHF':5,'EURGBP':5,'EURJPY':3,'EURNZD':5,'EURSGD':5,'EURUSD':5,'GBPAUD':5,'GBPCAD':5,'GBPCHF':5,'GBPJPY':3,'GBPNZD':5,'GBPSGD':5,'GBPUSD':5,'NZDCAD':5,'NZDCHF':5,'NZDJPY':3,'NZDUSD':5,'USDCAD':5,'USDCHF':5,'USDJPY':3,'USDSGD':5,'SGDJPY':3}

polygon_api_key="<hidden>"

pairs=""
pairs_dict_new={}
for i,pair in enumerate(pairs_dict):

    pairs=pairs+"C."+pair[:3]+"-"+pair[3:]+","

    changed_symbol=pair[:3]+"-"+pair[3:]

    pairs_dict_new[changed_symbol]=pairs_dict[pair]
passe=False


def on_open(ws):
    print("Opened connection")
    ws.send('{"action":"auth","params":"'+polygon_api_key+'"}') #connecting with secret api key

def on_message(ws, message):
    print("msg",message)
    json_msg = json.loads(message)[0]

    global pairs_dict_new,passe
    if passe:
        return

    if json_msg['status'] == "auth_success":  # successfully authenticated
        r = ws.send('{"action":"subscribe","params":"C.*"}')  # subscribing to currencies
        print("should subscribe to " + pairs)
        passe = True


if __name__ == "__main__":
    # websocket.enableTrace(True) # just to show all the requests made (debug mode)
    ws = websocket.WebSocketApp("wss://socket.polygon.io/forex",
                              on_open=on_open,
                              on_message=on_message)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
