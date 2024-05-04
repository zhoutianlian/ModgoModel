import Main
import Config.Database

# time1 = datetime.datetime.now()
Config.Database.set_db('local_test')
# corproation.run_mini(1259)
Main.run_mini(1354, True)
# time2 = datetime.datetime.now()
# print(time2-time1)
