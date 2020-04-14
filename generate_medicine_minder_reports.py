import os, sys
sys.dont_write_bytecode = True
import sqlite3

import data_handlers.sqlitemanager as sqlitemanager


class Medicine_Minder_Report_Manager():

    def __init__(self):
        self.dbname = 'MedicineMinder.db'
        self.mgr = sqlitemanager.sqlManager(self.dbname)

    def pull_all_flagged_person_medicines_for_today(self, sql_template='pull_all_flagged_person_medicines_for_today.sql'):
        sql = self.mgr.load_sql_from_csv( os.path.join('sql_templates',sql_template) )
        result = self.mgr.run_a_query(sql, return_header=True)
        return result


if __name__ == '__main__':
    minder = Medicine_Minder_Report_Manager()
    print minder.pull_all_flagged_person_medicines_for_today()
    print 'done'
