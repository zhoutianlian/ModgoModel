import json
import datetime
#############将日期格式的数据转为json#########
class DateEncoder(json.JSONEncoder):
      def default(self, obj):
            if isinstance(obj, datetime.datetime):
                  return obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, datetime.date):
                  return obj.strftime("%Y-%m-%d")
            else:
                  return json.JSONEncoder.default(self, obj)