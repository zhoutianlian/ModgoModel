# -*- coding: utf-8 -*-：
__all__ = ['Valuation']


class Valuation(object):

    def __init__(self, vid):
        self.vid = vid

    def run(self):
        from Data.Read import read_pattern, ready
        from Config.Type import valuation_types
        from Tool.Util import send_mq
        db_config, db, fd = ready(self.vid)

        data = read_pattern(self.vid, db, db_config)
        result = valuation_types[data[fd.type]](self.vid, eid=data[fd.eid])
        send_mq(data[fd.eid])
        return result

