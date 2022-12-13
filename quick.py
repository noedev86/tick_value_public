import mysql.connector

# import sys

# print( 'Number of arguments:', len(sys.argv), 'arguments.')
# print ('Argument List:', str(sys.argv))

# pairs_dict={'AUDCAD':5,'AUDCHF':5,'AUDJPY':3,'AUDNZD':5,'AUDSGD':2,'AUDUSD':5,'CADCHF':5,'CADJPY':3,'CHFJPY':3,'EURAUD':5,'EURCAD':5,'EURCHF':5,'EURGBP':5,'EURJPY':3,'EURNZD':5,'EURSGD':5,'EURUSD':5,'GBPAUD':5,'GBPCAD':5,'GBPCHF':5,'GBPJPY':3,'GBPNZD':5,'GBPSGD':5,'GBPUSD':5,'NZDCAD':5,'NZDCHF':5,'NZDJPY':3,'NZDUSD':5,'USDCAD':5,'USDCHF':5,'USDJPY':3,'USDSGD':5,'SGDJPY':3}

try:

    # linux server
    # db = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="<hidden>",
    #     database="bvnwurux_tick_values"
    # )
    db = mysql.connector.connect(
        host="<hidden>",
        user="<hidden>",
        password="<hidden>",
        database="<hidden>"
    )
    try:
        search = "SELECT * FROM EUR ORDER BY id DESC LIMIT 1;"
        mycursor = db.cursor()

        mycursor.reset()
        res = mycursor.execute(search)
        rows = mycursor.fetchall()

    except Exception as e:
        print(e)
    print(res)

except Exception as e:
    print(e)

