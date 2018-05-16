# -*- coding: utf-8 -*-
"""
/***************************************************************************
 rheasDialog
                                 A QGIS plugin
 Processes RHEAS simulations.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-05-08
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Kostas Andreadis
        email                : kandread@jpl.nasa.gov
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import psycopg2 as pg

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import pyqtSlot

from qgis.core import QgsRasterLayer, QgsProject, QgsContrastEnhancement, QgsLayerTreeLayer

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'rheas_dialog_base.ui'))


class rheasDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(rheasDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.schema.currentIndexChanged.connect(self.refreshTables)
        self.database.currentIndexChanged.connect(self.refreshSchemas)
        self.render.clicked.connect(self.loadRaster)
        self.addDatabases()
        self.addSchemas()
        self.addTables()

    def addDatabases(self):
        """Add available database connections."""
        self.settings = QSettings()
        self.settings.beginGroup('/PostgreSQL/connections/')
        connections = self.settings.childGroups()
        self.settings.endGroup()
        for conn in connections:
            self.database.addItem(conn)
            
    def getConnectionParameters(self):
        """Get database connection information."""
        conn = self.database.itemText(self.database.currentIndex())
        self.settings.beginGroup('PostgreSQL/connections')
        dbname = self.settings.value("{0}/database".format(conn))
        host = self.settings.value("{0}/host".format(conn))
        port = self.settings.value("{0}/port".format(conn))
        username = self.settings.value("{0}/username".format(conn))
        password = self.settings.value("{0}/password".format(conn))
        self.settings.endGroup()
        return dbname, host, port, username, password

    def addSchemas(self):
        """Add available schemas from database."""
        dbname, host, port, username, password = self.getConnectionParameters()
        db = pg.connect(dbname=dbname, host=host, port=port, user=username, password=password)
        cur = db.cursor()
        sql = "select schema_name from information_schema.schemata"
        cur.execute(sql)
        results = cur.fetchall()
        for r in results:
            name = r[0]
            if not name.startswith("pg_"):
                self.schema.addItem(name)
        cur.close()
        db.close()

    @pyqtSlot()
    def refreshSchemas(self):
        """Refresh list of schemas when database changes."""
        self.schema.clear()
        self.addSchemas()
        
    @pyqtSlot()
    def refreshTables(self):
        """Refresh list of tables when selected schema changes."""
        self.table.clear()
        self.addTables()

    @pyqtSlot()
    def loadRaster(self):
        """Load rasters when button is clicked."""
        dbname, host, port, username, password = self.getConnectionParameters()
        schema = self.schema.itemText(self.schema.currentIndex())
        table = self.table.itemText(self.table.currentIndex())
        startdate = self.startdate.date()
        enddate = self.enddate.date()
        dates = [startdate]
        while dates[-1] < enddate:
            dates.append(dates[-1].addDays(1))
        for dt in dates:
            connString = "PG: dbname={3} host={4} user={5} password={6} port={7} mode=2 schema={0} column=rast table={1} where='fdate=date\\'{2}\\''".format(schema, table, dt.toString("yyyy-M-d"), dbname, host, username, password, port)
            layer = QgsRasterLayer(connString, "{0}".format(dt.toString("yyyy-M-d")))
            if layer.isValid():
                layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum)
            root = QgsProject.instance().layerTreeRoot()
            group = root.findGroup(schema)
            if group is None:
                group = root.addGroup(schema)
            QgsProject.instance().addMapLayer(layer, False)
            group.insertChildNode(0, QgsLayerTreeLayer(layer))

    def addTables(self):
        """Add available tables contained in selected schema."""
        dbname, host, port, username, password = self.getConnectionParameters()
        db = pg.connect(dbname=dbname, host=host, port=port, user=username, password=password)
        cur = db.cursor()
        idx = self.schema.currentIndex()
        schema = self.schema.itemText(idx)
        sql = "select table_name from information_schema.tables where table_schema='{0}'".format(schema)
        cur.execute(sql)
        results = cur.fetchall()
        for r in results:
            name = r[0]
            self.table.addItem(name)
        cur.close()
        db.close()
