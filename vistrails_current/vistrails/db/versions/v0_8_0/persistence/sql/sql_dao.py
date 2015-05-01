###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from datetime import date, datetime
from time import strptime

class SQLDAO:
    def __init__(self):
        pass

    def convertFromDB(self, value, type, db_type):
        if value is not None:
            if type == 'str':
                return str(value)
            elif type == 'long':
                return long(value)
            elif type == 'float':
                return float(value)
            elif type == 'int':
                return int(value)
            elif type == 'date':
                if db_type == 'date':
                    return value
                else:
                    return date(*strptime(str(value), '%Y-%m-%d')[0:3])
            elif type == 'datetime':
                if db_type == 'datetime':
                    return value
                else:
                    return datetime(*strptime(str(value), 
                                              '%Y-%m-%d %H:%M:%S')[0:6])
        return None

    def convertToDB(self, value, type, db_type):
        if value is not None:
            if type == 'str':
                return "'" + str(value).replace("'", "''") + "'"
            elif type == 'long':
                return str(value)
            elif type == 'float':
                return str(value)
            elif type == 'int':
                return str(value)
            elif type == 'date':
                return "'" + value.isoformat() + "'"
            elif type == 'datetime':
                return "'" + value.strftime('%Y-%m-%d %H:%M:%S') + "'"
            else:
                return str(value)

        return "''"

    def createSQLSelect(self, table, columns, whereMap, orderBy=None, 
                        forUpdate=False):
        columnStr = ', '.join(columns)
        whereStr = ''
        whereClause = ''
        for column, value in whereMap.iteritems():
            whereStr += '%s %s = %s' % \
                        (whereClause, column, value)
            whereClause = ' AND'
        dbCommand = """SELECT %s FROM %s WHERE %s""" % \
                    (columnStr, table, whereStr)
        if orderBy is not None:
            dbCommand += " ORDER BY " + orderBy
        if forUpdate:
            dbCommand += " FOR UPDATE"
        dbCommand += ";"
        return dbCommand

    def createSQLInsert(self, table, columnMap):
        columns = []
        values = []
        for column, value in columnMap.iteritems():
            if value is None:
                value = 'NULL'
            columns.append(column)
            values.append(value)
        columnStr = ', '.join(columns)
        valueStr = ', '.join(values)
        dbCommand = """INSERT INTO %s(%s) VALUES (%s);""" % \
                    (table, columnStr, valueStr)
        return dbCommand

    def createSQLUpdate(self, table, columnMap, whereMap):
        setStr = ''
        comma = ''
        for column, value in columnMap.iteritems():
            if value is None:
                value = 'NULL'
            setStr += '%s %s = %s' % (comma, column, value)
            comma = ','
        whereStr = ''
        whereClause = ''
        for column, value in whereMap.iteritems():
            whereStr += '%s %s = %s' % \
                        (whereClause, column, value)
            whereClause = ' AND'
        dbCommand = """UPDATE %s SET %s WHERE %s;""" % \
                    (table, setStr, whereStr)
        return dbCommand

    def createSQLDelete(self, table, whereMap):
        whereStr = ''
        whereClause = ''
        for column, value in whereMap.iteritems():
            whereStr += '%s%s = %s' % \
                (whereClause, column, value)
            whereClause = ' AND '
        dbCommand = """DELETE FROM %s WHERE %s;""" % \
            (table, whereStr)
        return dbCommand

    def executeSQL(self, db, dbCommand, isFetch):
        # print 'db: %s' % dbCommand
        data = None
        cursor = db.cursor()
        cursor.execute(dbCommand)
        if isFetch:
            data = cursor.fetchall()
        else:
            data = cursor.lastrowid
        cursor.close()
        return data

    def start_transaction(self, db):
        db.begin()

    def commit_transaction(self, db):
        db.commit()

    def rollback_transaction(self, db):
        db.rollback()
