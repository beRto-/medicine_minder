import sqlite3
import csv
import sys
import os


class sqlManager():

    def __init__(self, dbName):
        self.sql_template_path = 'sql_templates'

        self.conn = sqlite3.connect(dbName)
        self.conn.text_factory = str  #non UTF-8 (remove "u" character in front)
        #self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def substitute_variables_into_query(self, sql, variables={}):
        for key, value in variables.iteritems():
            sql = sql.replace(key,value)
        return sql

    def load_sql_from_csv(self, csv_path):
        with open(csv_path, 'rb') as f:
            sql = f.read() # read (text) SQL file into string variable
            f.close()
        return sql

    def run_a_query(self, sql, return_header=True):
        self.cursor.execute(sql)
        #print sql
        query_result = self.cursor.fetchall()
        #print query_result
        if len(query_result)>0:
            if return_header:
                query_result = self.get_column_names_from_query_result() + query_result
            return query_result
        else:
            return None

    def update_key_value_in_parameter_table(self, table_name, key_name, new_record_value):
        sql = "UPDATE %s SET key_value = '%s' WHERE key_name = '%s'" % (table_name, new_record_value, key_name)
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            print 'successfully updated %s to %s' % ( key_name, str(new_record_value) )
        except:
            print 'query failed: %s' % sql

    def get_column_names_from_query_result(self):
        # http://stackoverflow.com/questions/9752372/how-do-i-get-the-column-names-from-a-row-returned-from-an-adodbapi-query
        col_names = [i[0] for i in self.cursor.description]
        return [tuple(col_names)]

    def insert_values_into_database(self, table_name, to_db):
        # to_db is a list of tuples
        placeholders = ', '.join('?' * len(to_db[0]))
        sql = 'INSERT OR IGNORE INTO %s VALUES (%s);' % (table_name, placeholders)
        #print sql
        try:
            self.cursor.executemany(sql, to_db)
            self.conn.commit()
            print 'successfully inserted %i records to %s' % ( len(to_db), table_name )
        except Exception as e:
            print 'failed to insert records'
            print e

    def upload_csv_file_to_database(self, table_name, csv_path, business_date, append_business_date = True, skip_header = True):
        # http://stackoverflow.com/questions/2887878/importing-a-csv-file-into-a-sqlite3-database-table-using-python
        # https://www.tutorialspoint.com/sqlite/sqlite_insert_query.htm
        # INSERT INTO TABLE_NAME VALUES (value1,value2,value3,...valueN);
        if not os.path.isfile(csv_path):
            print 'ERROR cannot upload csv to database. File does not exist: %s' % csv_path
            return
        record_count = 0
        with open(csv_path,'rb') as infile:
            reader = csv.reader(infile)
            to_db = []
            if skip_header:
                next(reader, None)  # skip the headers
            for row in reader:
                if append_business_date:
                    to_db.append( tuple([business_date] + row) )
                else:
                    to_db.append( tuple(row) )
                record_count += 1
        insert_values_into_database(table_name, to_db)
        print '%s file uploaded (%d records)' % ( os.path.basename(csv_path), record_count )

    def __del__(self):
        self.conn.close()


if __name__ == '__main__':
    print 'nothing going on here'
