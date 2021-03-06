# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OA_WebMap_Updater
                                 A QGIS plugin
 Updater for OA Webmap
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-03-20
        git sha              : $Format:%H$
        copyright            : (C) 2021 by VP
        email                : pinnavalerio@yahoo.co.uk
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction 
from qgis.utils import iface
from qgis.core import QgsProject, QgsLayerTreeGroup, QgsLayerTreeLayer
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton  # Qt5
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .OA_WebMap_Updater_dialog import OA_WebMap_UpdaterDialog
import os.path


class OA_WebMap_Updater:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
                # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = iface.mapCanvas()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        """
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OA_WebMap_Updater_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
        """
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&OA WebMap Updater')
        self.toolbar = self.iface.digitizeToolBar()
        self.popupMenu = QMenu()
        self.toolButton = QToolButton()
        self.toolButtonAction = None
        
        # Setup map tools
        self.tool = None
        
        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('OA_WebMap_Updater', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/OA_WebMap_Updater/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'OA WebMap Updater'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&OA_WebMap_Updater'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        if QgsProject.instance().fileName() !=  QgsProject.instance().homePath() + '/' +'QGIS to WebGIS upload.qgs':
            QMessageBox.warning(None,
                'OA Webmap Uploader',
                'This is not a valid OA Webmap project')
        else:
            time1 = datetime.now()

            ###Chech names for local and add _local if missing
            root = QgsProject.instance().layerTreeRoot()

            group = root.findGroup('Local Survey Export Data (check path)')
            for child in group.children():
                if child.name().endswith('_local')== False:
                    child.setName(child.name()+'_local')

            #Delete all the features from the live layers
            
            layer = QgsProject.instance().mapLayersByName('oamap_point')[0]
            layer.startEditing()
            listOfIds = []
            for feat in layer.getFeatures():
                listOfIds.append(feat.id())
                layer.deleteFeatures( listOfIds )
            layer.commitChanges()
            listOfIds.clear()

            layer = QgsProject.instance().mapLayersByName('oamap_polyline')[0]
            layer.startEditing()
            listOfIds = []
            for feat in layer.getFeatures():
                listOfIds.append(feat.id())
                layer.deleteFeatures( listOfIds )
            layer.commitChanges()
            listOfIds.clear()

            layer = QgsProject.instance().mapLayersByName('oamap_polygon')[0]
            layer.startEditing()
            listOfIds = []
            for feat in layer.getFeatures():
                listOfIds.append(feat.id())
                layer.deleteFeatures( listOfIds )
            layer.commitChanges()
            listOfIds.clear()

            #Copy and paste features

            # polygons 
            local_polygon = QgsProject.instance().mapLayersByName('oamap_polygon_local')[0]
            live_external_polygon = QgsProject.instance().mapLayersByName('oamap_polygon')[0]
            iface.setActiveLayer( local_polygon ) 
            local_polygon.selectAll()
            iface.actionCopyFeatures().trigger()
            iface.setActiveLayer(live_external_polygon)
            live_external_polygon.startEditing()
            iface.actionPasteFeatures().trigger()
            live_external_polygon.commitChanges()
            local_polygon.removeSelection()
            live_external_polygon.removeSelection()

            #points
            local_point = QgsProject.instance().mapLayersByName('oamap_point_local')[0]
            live_external_point = QgsProject.instance().mapLayersByName('oamap_point')[0]

            iface.setActiveLayer( local_point ) 
            local_point.selectAll()
            iface.actionCopyFeatures().trigger()
            # Set destination layer active
            iface.setActiveLayer(live_external_point)
            # Turn on editing on destination layer
            live_external_point.startEditing()
            # Paste features
            iface.actionPasteFeatures().trigger()
            #Save changes
            live_external_point.commitChanges()
            #Remove selection from both layers
            local_point.removeSelection()
            live_external_point.removeSelection()

            #polylines
            local_polyline = QgsProject.instance().mapLayersByName('oamap_polyline_local')[0]
            live_external_polyline = QgsProject.instance().mapLayersByName('oamap_polyline')[0]

            iface.setActiveLayer( local_polyline ) 
            local_polyline.selectAll()
            iface.actionCopyFeatures().trigger()
            iface.setActiveLayer(live_external_polyline)
            live_external_polyline.startEditing()
            iface.actionPasteFeatures().trigger()
            live_external_polyline.commitChanges()
            local_polyline.removeSelection()
            live_external_polyline.removeSelection()

            ###Rename the layer as original
            root = QgsProject.instance().layerTreeRoot()

            group = root.findGroup('Local Survey Export Data (check path)')
            for child in group.children():
                if child.name().endswith('_local')== True:
                    child.setName(child.name()[:-6])

            time_end = datetime.now()
            ##duration
            delta = time_end-time1
            delta_b = (str(delta)[0:10])

            QMessageBox.about(
            None,
            'OAE Webmap',
            '''WebMap successfully updated
            in {} 
            '''.format(delta_b))