from dqsegdb_web.core import Constants
from flask import session
import imp
import logging
import time
import pymysql

log = logging.getLogger()
log.setLevel(logging.DEBUG)

class DAO:
    '''
    Data-Access-Object module.
    All connections to the database are made via this class.
    '''
    ######################
    # CONNECTION METHODS #
    ######################
    def __init__(self):
        '''
        Establish DB connection.
        '''
        # Instantiate objects.
        constant = Constants.Constants()
        # Attempt connection.
        try:
            # Attempt DB connection.
            self.cnxn = pymysql.connect(host=constant.db_host,
                                        user=constant.db_user,
                                        passwd=constant.db_pass,
                                        db=constant.db,
                                        cursorclass=pymysql.cursors.DictCursor,
                                        charset='utf8')
        except pymysql.OperationalError as e:
            # Log event.
            full_err_msg = '** Problem establishing database connection: ' + str(e)
            log.error(full_err_msg)
            raise Exception(full_err_msg)
        else:
            self.ensure_utf8()

    def ensure_utf8(self):
        """
        Ensure that the UTF-8 character set is used when interrogating the
        database.
        """
        err_msg = 'ensuring UTF-8 character set used'
        try:
            # Set DB cursor.
            cur = self.cnxn.cursor()
        except pymysql.OperationalError as e:
            # Log event.
            full_err_msg = '**** Problem ' + err_msg + '. Unable to create \
cursor on database connection: ' + str(e)
            log.error(full_err_msg)
            raise Exception(full_err_msg)
        else:
            try:
                # Get.
                cur.execute("SET NAMES UTF8")
                r = cur.fetchall()
            except pymysql.OperationalError as e:
                # Log event.
                full_err_msg = '**** Problem ' + err_msg + '. Unable to \
execute SQL statement: ' + str(e)
                log.error(full_err_msg)
                raise Exception(full_err_msg)

    def __del__(self):
        '''
        Close DB connection.
        '''
        # If connection exists.
        try:
            self.cnxn
        except:
            # Log event.
            log.warning('** Database connection has already closed.')
        else:
            # Close
            try:
                self.cnxn.close()
            except:
                # Log event.
                full_err_msg = '** Problem closing database connection.'
                log.error(full_err_msg)
                raise Exception(full_err_msg)
