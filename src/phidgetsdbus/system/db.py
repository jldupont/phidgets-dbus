"""
    Couchdb access 
    
    @author: jldupont
    Created on Jun 26, 2010
"""
import couchdb
from couchdb.http import PreconditionFailed, ResourceConflict

__all__=["db", "dbError", "dbSaveError", "dbEntryExist"]

server=couchdb.Server()

class dbEntry(couchdb.Document):
    """
    A database entry
    """
        
class dbError(Exception):
    """
    Error accessing the database
    """

class dbSaveError(Exception):
    """
    Error whilst saving an entry in the database
    """

class dbEntryExist(Exception):
    """
    Entry already exists in database
    """

class db(object):
    
    server=couchdb.Server()
    db=None

    @classmethod
    def create(cls):
        """
        Creates *if not exists* the database
        
        @return: True on successful creation OR already exists
        @return: False on error
        """
        try:
            cls.db=cls.server.create("sensors")
            return True
        except PreconditionFailed:
            cls.db=cls.server["sensors"]
            return True
        except:
            return False

    @classmethod
    def save(cls, ts, deviceId, sensorId, value):
        """
        Saves an entry in the database
        
        @param ts: timestamp
        @param deviceId: device identifier
        @param sensorId: sensor identifier
        @param value: sensor value
        
        @return: string, doc_id   
        """
        if cls.db is None:
            raise dbError
        
        ## ensure idempotence
        doc_id="%s:%s:%s" % (deviceId, sensorId, ts)
        entry=dbEntry(ts=ts, deviceId=deviceId, sensorId=sensorId, value=value)
        try:
            cls.db[doc_id]=entry
        except ResourceConflict:
            raise dbEntryExist
        except Exception,_e:
            raise dbSaveError
        
        return doc_id

        
        
if __name__=="__main__":
    print db.create()
    db.save(0, "80860", "pin1", 666)
