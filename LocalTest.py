import Main
import Config.Database

# time1 = datetime.datetime.now()
Config.Database.set_db('test')
from Config.mongodb import read_mongo_limit, update_data_demo
# corproation.run_mini(1259)
Main.Valuation(36480).run()
# time2 = datetime.datetime.now()
# print(time2-time1)