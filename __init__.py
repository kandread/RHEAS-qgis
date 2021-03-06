# -*- coding: utf-8 -*-
"""
/***************************************************************************
 rheas
                                 A QGIS plugin
 Processes RHEAS simulations.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-05-08
        copyright            : (C) 2018 by Kostas Andreadis
        email                : kandread@jpl.nasa.gov
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load rheas class from file rheas.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .rheas import rheas
    return rheas(iface)
