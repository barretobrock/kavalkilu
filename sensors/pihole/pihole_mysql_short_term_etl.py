"""A script to load a short-term snapshot of pihole data into a sql table for faster loading"""

from kavalkilu.tools.log import Log
from kavalkilu.tools.databases import MySQLLocal


# Initiate Log, including a suffix to the log name to denote which instance of log is running
log = Log('pihole_db_shortterm', 'pihole_db', log_lvl='DEBUG')
log.debug('Logging initiated')

# Number of days to go back
INT_DAYS = 14

# Log into piholedb
db = MySQLLocal('piholedb')
mysqlconn = db.engine.connect()


delete_query = """
    TRUNCATE TABLE short_term_queries
"""

insert_query = """
    INSERT short_term_queries
    SELECT *
    FROM pihole_queries 
    WHERE record_date >= DATE_SUB(CURDATE(), INTERVAL {} day) 
    ORDER BY record_date ASC
""".format(INT_DAYS)
del_res = mysqlconn.execute(delete_query)
log.debug('Deletion query sent to database.')
res = mysqlconn.execute(insert_query)

log.debug('Query sent to database. Result shows {} rows affected.'.format(res.rowcount))

log.debug('Closing connections.')
mysqlconn.close()

log.close()
