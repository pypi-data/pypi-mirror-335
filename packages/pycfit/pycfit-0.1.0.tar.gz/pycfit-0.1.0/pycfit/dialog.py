"""
Interactive (GUI) dialogs and views
"""
import ast
import pickle
import numpy as np
import pyqtgraph as pg
from astropy.modeling.models import Moffat1D
from astropy.modeling.fitting import TRFLSQFitter
from pathlib import Path
from copy import deepcopy
from qtpy.uic import loadUi
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt, QVariant
from qtpy.QtWidgets import QDialog, QMessageBox, QDialogButtonBox, QFileDialog
from .function import FunctionFitter, Component
from .util import ConvertFloat, TiedFunction

class FitDialog(QDialog):
    """ Dialog box to edit function and fit to data """
    def __init__(self, fitter, parent=None, limited_adjustment=False):
        assert isinstance(fitter, FunctionFitter), 'Bad FunctionFitter argument'

        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/Fit.ui'), self)
        self.setFixedSize(self.size())

        self.fitter = fitter
        self._fit_clicked = False
        self.limited_adjustment = limited_adjustment

        ## Models
        self.functionTreeModel = FunctionTreeModel(self)
        self.componentGraphItems = []
        self.sumGraph = SumGraph(self)
        self.resGraph = ResGraph(self)
        self.initializeComponentGraphItems()

        ## Views
        self.treeView.setModel(self.functionTreeModel)

        # Show grid lines and data points on graph - Sum Graph
        self.graph.showGrid(x=True, y=True)
        self.graph.plot(self.fitter.x, self.fitter.y, symbol='o', pen=None)
        if self.fitter.uncertainty is None:
            temp_uncert = np.zeros_like(self.fitter.x)
            self.error_bars = pg.ErrorBarItem(x=self.fitter.x, y=self.fitter.y, height=temp_uncert)
            self.res_error_bars = pg.ErrorBarItem(x=self.fitter.x, y=np.zeros_like(self.fitter.x), height=temp_uncert)
        else:
            self.error_bars = pg.ErrorBarItem(x=self.fitter.x, y=self.fitter.y, height=self.fitter.uncertainty)
            self.res_error_bars = pg.ErrorBarItem(x=self.fitter.x, y=np.zeros_like(self.fitter.x), height=self.fitter.uncertainty)
        self.graph.addItem(self.sumGraph)
        self.graph.addItem(self.error_bars)
        self.graph.addItem(self.sumGraph)

        # Show grid lines and data points on graph - Residuals Graph
        self.graph_residuals.showGrid(x=True, y=True)
        self.graph_residuals.plot(self.fitter.x, np.zeros(len(self.fitter.y)), symbol=None, pen='r')
        self.graph_residuals.addItem(self.resGraph)
        self.graph_residuals.addItem(self.res_error_bars)
        self.graph_residuals.setXLink(self.graph)
        self.graph_residuals.enableAutoRange()

        self.checkBoxShowRes.setEnabled(False) # Checkbox currently does nothing. Disable for now

        if self.limited_adjustment:
            self.addComponentButton.setEnabled(False)
            self.exportButton.setEnabled(False)

        ## Controllers
        # Tree actions
        self.treeView.doubleClicked.connect(self.functionTreeDoubleClicked)
        self.treeView.keyPressEvent = self.functionTreeModel.keyPress
        self.treeView.selectionModel().selectionChanged.connect(self.selectionChange)
        # Connect and initialize buttons
        self.addComponentButton.clicked.connect(self.addComponent)
        self.fitButton.clicked.connect(self.fit)
        self.exportButton.clicked.connect(self.export)
        self.updateDisplay()

        return

    def get_model(self):
        return deepcopy(self.fitter.function.model)
    
    def addComponent(self):
        ID = self.functionTreeModel.rootItem.childCount()
        newComponentDialog = NewComponentDialog(self)
        if newComponentDialog.exec():
            if newComponentDialog.constraint_type == 'Voigt':
                QMessageBox.critical(self, None, 'Voigt components are not yet supported')
            else:
                self.fitter.add_component(newComponentDialog.component)
                self.addGraphComponent(newComponentDialog.component) #This will adjust the internal component parameter values
                self.functionTreeModel.addComponent(self.fitter.function.components[ID]) #Reference from the Function to make sure it's using the right pointer
                self.updateDisplay()
        return

    def fit(self):
        self.fitter.fit()
        self.functionTreeModel.reload()
        self.updateGraph()
        self.updateDisplay()

    def export(self):
        """
        Pickle and store the currently fitted astropy model to a file
        or store the function creator in a Python script
        """
        filename, filetype = QFileDialog.getSaveFileName(self, 'Save function', None, 'Python Code (*.py);;Pickle File (*.pkl)')
        if not filename : return # Canceled

        #Write the astropy function creator to a Python script
        if filetype == 'Python Code (*.py)' : 
            with open(filename, 'w') as code :
                print('from astropy.modeling.models import Const1D', file=code)
                print('from astropy.modeling.models import Linear1D', file=code)
                print('from astropy.modeling.models import Polynomial1D', file=code) # For Quadradic
                print('from astropy.modeling.models import Gaussian1D', file=code)
                print('from astropy.modeling.models import Moffat1D', file=code)
                
                print('\nfrom pycfit.util import sum_components, TiedFunction', file=code)
                print('\nmodel = sum_components(' + ', '.join(cmp.codeName for cmp in self.fitter.function.components.values()) + ')', file=code)
                
                for component in self.fitter.function.components.values() :
                    print('\n#', component.name, file=code)                
                    plist = component.getParamsLists()
                    for p in plist:
                        pbase = '_'.join(p[0].split('_')[:-1])
                        print(f'model.{p[0]}.value = {p[2]}', file=code)
                        print(f'model.{p[0]}.fixed = {component.model.fixed[pbase]}', file=code)
                        print(f'model.{p[0]}.bounds = {component.model.bounds[pbase]}', file=code)

                        if component.model.tied[pbase] is False:
                            print(f'model.{p[0]}.tied = False', file=code)    
                        else:                        
                            print(f'model.{p[0]}.tied = TiedFunction("{component.model.tied[pbase]}")', file=code)

        #Pickle and store the currently fitted astropy model to a file
        elif filetype == 'Pickle File (*.pkl)': 
            with open(filename, 'wb') as f:
                pickle.dump(self.fitter.function.model, f)
        
        return
                                        
               
    def updateDisplay(self):
        """Enable/disable buttons"""
        buttonsOn = False if self.fitter.function.model is None else True
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(buttonsOn)
        self.fitButton.setEnabled(buttonsOn)
        if not self.limited_adjustment:
            self.exportButton.setEnabled(buttonsOn)
        return

    def functionTreeDoubleClicked(self, index) :
        '''
        Edit a parameter when double-clicked
        '''
        tree_item = index.internalPointer()
        if tree_item.parentItem == self.functionTreeModel.rootItem:
            if AdjustComponentDialog(tree_item, self).exec():
                if self.fitter.function.model.n_submodels == 1:
                    self.fitter.function.model.name = tree_item.itemData[1]
                else:
                    thisID = int(tree_item.itemData[0].split('_')[-1])
                    self.fitter.function.model[thisID].name = tree_item.itemData[1]
            return  # Limited action if it's a Component type objects

        if ParameterDialog(tree_item, self).exec():
            self.fitter.function.compute_components()
            self.functionTreeModel.reload()
            self.updateDisplay()
        return

    def selectionChange(self, selected, deselected) :
        '''
        When the selected component changes...
        '''
        tags = []
        for index in selected.indexes():
            tags.append(int(index.internalPointer().itemData[0].split('_')[1]))
        selectedTags = set(tags)

        if len(selectedTags) > 0:
            self.fitter.function.selected_comp = selectedTags.pop()
        else:
            self.fitter.function.selected_comp = -1

        self.updateGraph()
        return
        
    def initializeComponentGraphItems(self):
        if self.fitter.function.model is not None:
            for comp in self.fitter.function.components.values():
                self.addGraphComponent(comp, set_defaults=False) # To skip adjusting the model parameters
        return

    def addGraphComponent(self, comp, set_defaults=True):
        if 'Constant' in comp.name:
            graph = ConstGraph(comp, self, set_defaults=set_defaults)
        elif 'Linear' in comp.name:
            graph = LinearGraph(comp, self, set_defaults=set_defaults)
        elif 'Quadratic' in comp.name:
            graph = QuadraticGraph(comp, self, set_defaults=set_defaults)
        elif 'Gaussian' in comp.name:
            graph = GaussianGraph(comp, self, set_defaults=set_defaults)
        elif 'Moffat' in comp.name:
            graph = MoffatGraph(comp, self, set_defaults=set_defaults)
        else:
            graph = None

        if graph is not None:
            self.componentGraphItems.append(graph)
            self.graph.addItem(graph)
            self.sumGraph.updateGraph()
            self.resGraph.updateGraph()
        
        return

    def updateGraph(self):
        """ To handle parameter updates after a fit """
        for graphItem in self.componentGraphItems:
            graphItem.updateGraph()
        return

    def reject(self):
        '''If the user cancels the fit'''
        if self._fit_clicked :
            if QMessageBox.question(self, None, 'Are you sure you want to cancel without saving?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes :
                super().reject()
        else :
            super().reject()


class NewComponentDialog(QDialog):
    '''
    Dialog box to create a new component
    '''
    def __init__(self, parent=None) :
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/NewComponent.ui'), self)
        self.setFixedSize(self.size())
        
        self.constraint_type = self.typeComboBox.currentText()
        self.description = ''
        self.component = None
        self.ID = parent.functionTreeModel.rootItem.childCount()
    
    def accept(self) :
        self.constraint_type = self.typeComboBox.currentText()
        self.description = self.descLineEdit.text()
        self.component = Component(self.constraint_type, description=self.description, ID=self.ID)     
        super().accept()


class AdjustComponentDialog(QDialog):
    '''
    Dialog box to adjust Component model description
    '''
    def __init__(self, comp, parent=None):
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/AdjustComponent.ui'), self)
        self.setFixedSize(self.size())
        self.componentItem = comp
        self.modelTypeName.setText('_'.join(comp.itemData[0].split('_')[:-1]))
        self.descLineEdit.setText(comp.itemData[1])

    def accept(self) :
        self.componentItem.itemData[1] = self.descLineEdit.text()
        super().accept()

class ParameterDialog(QDialog):
    '''
    Dialog to edit a parameter
    '''
    def __init__(self, parameter, parent=None) :
        super().__init__(parent)
        loadUi(Path(__file__).parent.joinpath('ui/Parameter.ui'), self)
        self.setFixedSize(self.size())
        self.combomodel = parent.fitter.function.model
        if self.combomodel.n_submodels == 1:
            self.param_name = '_'.join(parameter.itemData[0].split('_')[:-1])
        else:
            self.param_name = parameter.itemData[0]
        self.parameter = parent.fitter.function.model.__getattribute__(self.param_name)

        self.freeRadioButton.clicked.connect(self.freeRadioButtonClicked)
        self.fixedRadioButton.clicked.connect(self.fixedRadioButtonClicked)
        self.tiedRadioButton.clicked.connect(self.tiedRadioButtonClicked)
        self.lowerCheckBox.clicked.connect(self.lowerCheckBoxClicked)
        self.upperCheckBox.clicked.connect(self.upperCheckBoxClicked)
        
        self.display_val = round(self.parameter.value, 3)
        self.valueLineEdit.setText(str(self.display_val))
        
        self.fixedRadioButton.setChecked(self.parameter.fixed)
        self.freeRadioButton.setChecked(not self.parameter.fixed)
        if self.parameter.tied:
            self.tiedRadioButton.setChecked(True)
            self.exprLineEdit.setText(str(self.parameter.tied))
        else:
            self.tiedRadioButton.setChecked(False)
            self.exprLineEdit.setText('')

        self.lowerCheckBox.setChecked(self.parameter.bounds[0] != None)
        self.lowerLineEdit.setText(str(self.parameter.bounds[0]))
        self.upperCheckBox.setChecked(self.parameter.bounds[1] != None)
        self.upperLineEdit.setText(str(self.parameter.bounds[1]))
        
        self.updateEnabled()
    
    def freeRadioButtonClicked(self, checked) :
        self.updateEnabled()
    
    def fixedRadioButtonClicked(self, checked) :
        self.updateEnabled()
    
    def tiedRadioButtonClicked(self, checked) :
        self.updateEnabled()
    
    def lowerCheckBoxClicked(self, checked) :
        self.updateEnabled()
    
    def upperCheckBoxClicked(self, checked) :
        self.updateEnabled()
    
    # Change the widgets that are enabled based on constraint type
    def updateEnabled(self) :
        if self.freeRadioButton.isChecked() :
            self.lowerCheckBox.setEnabled(True)
            
            self.lowerLineEdit.setEnabled(self.lowerCheckBox.isChecked())
            
            self.upperCheckBox.setEnabled(True)
            self.upperLineEdit.setEnabled(self.upperCheckBox.isChecked())
            
            self.exprLabel.setEnabled(False)
            self.exprLineEdit.setEnabled(False)
        elif self.fixedRadioButton.isChecked() :
            self.lowerCheckBox.setEnabled(False)
            self.lowerLineEdit.setEnabled(False)
            
            self.upperCheckBox.setEnabled(False)
            self.upperLineEdit.setEnabled(False)
            
            self.exprLabel.setEnabled(False)
            self.exprLineEdit.setEnabled(False)
        elif self.tiedRadioButton.isChecked() :
            self.lowerCheckBox.setEnabled(False)
            self.lowerLineEdit.setEnabled(False)
            
            self.upperCheckBox.setEnabled(False)
            self.upperLineEdit.setEnabled(False)
            
            self.exprLabel.setEnabled(True)
            self.exprLineEdit.setEnabled(True)
    
    # When the user clicks OK
    def accept(self) :		
        value = ConvertFloat(self.valueLineEdit.text())
        if value is None  :
            QMessageBox.critical(self, None, 'Value is not a valid floating point')
            return
        
        # Clear old info from model
        self.combomodel.fixed[self.param_name] = self.fixedRadioButton.isChecked()
        if not self.tiedRadioButton.isChecked():
            self.combomodel.tied[self.param_name] = False

        if self.freeRadioButton.isChecked() :
            if self.lowerCheckBox.isChecked() :
                lower_bound = ConvertFloat(self.lowerLineEdit.text())
                if lower_bound is None :
                    QMessageBox.critical(self, None, 'Lower Bound is not a valid floating point')
                    return
                elif value < lower_bound:
                    value = lower_bound
            else:
                lower_bound = None
            
            if self.upperCheckBox.isChecked() :
                upper_bound = ConvertFloat(self.upperLineEdit.text())
                if upper_bound is None :
                    QMessageBox.critical(self, None, 'Upper Bound is not a valid floating point')
                    return
                elif value > upper_bound:
                    value = upper_bound
            else:
                upper_bound = None            

            self.combomodel.bounds[self.param_name] = (lower_bound, upper_bound)

        elif self.tiedRadioButton.isChecked() :
            if not self.exprLineEdit.text() :
                QMessageBox.critical(self, 'Need Expression', 'An expression must be entered')
                return
            
            try :
                ast.parse('(' + self.exprLineEdit.text() + ')') # Check that the expression is valid. This does not validate that the variables exist.
            except SyntaxError :
                QMessageBox.critical(self, None, 'Expression must be valid')
                return
            
            self.combomodel.tied[self.param_name] = TiedFunction(self.exprLineEdit.text()) 
        
        # Check if value is the same as the initial rounded value
        if value != self.display_val: # Value has been changed
            self.parameter.value = value
        
        super().accept()


class FunctionTreeModel(QAbstractItemModel):
    def __init__(self, fitDialog, parent=None):
        super().__init__(parent)
        self.rootItem = self.createTree(fitDialog.fitter.function)
        self.function = fitDialog.fitter.function
        self.fitDialog = fitDialog

    def createTree(self, function):
        rootItem = TreeItem(None)
        data = function.asDict()
        for key, values in data.items():
            parentItem = TreeItem([key, values['desc'], "", ""], rootItem)
            for sublist in values['params']:
                childItem = TreeItem(sublist, parentItem)
        return rootItem

    def addComponent(self, comp):
        self.layoutAboutToBeChanged.emit()
        parentItem = TreeItem([comp.name, comp.description, "", ""], self.rootItem)
        params = comp.getParamsLists()
        for plist in params:
            childItem = TreeItem(plist, parent=parentItem)
        self.layoutChanged.emit()
        return

    def removeComponent(self, row):
        self.layoutAboutToBeChanged.emit()
        self.rootItem.removeChild(row)
        self.layoutChanged.emit()
        return

    def reload(self):
        """For updating parameter values and selected components """
        self.layoutAboutToBeChanged.emit()
        if self.function.selected_comp >= 0:
            currIdx = self.index(self.function.selected_comp, 0, QModelIndex())
            self.fitDialog.treeView.setCurrentIndex(currIdx)
        data = self.function.asDict()
        treeComp = self.rootItem.childItems
        for i, (name, info) in enumerate(data.items()):
            treeComp[i].itemData[0] = name
            treeParam = treeComp[i].childItems
            for j, plist in enumerate(info['params']):
                treeParam[j].updateData(plist)
        self.layoutChanged.emit()
        return

    def columnCount(self, parent):
        return 4

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            return ['Name', 'Description', 'Value', 'Constraint'][section]
    
    def rowCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().childCount()
        return self.rootItem.childCount()

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(index.column())

        return QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def keyPress(self, event) :
        '''
        Handle deleting a component
        '''
        if event.key() == Qt.Key_Delete and not self.fitDialog.limited_adjustment: # Handle deleting a component
            componentIndex = self.fitDialog.treeView.currentIndex()
            if componentIndex is None : return # Nothing selected
            
            # Work with ID so we can get all parts of a Component
            tree_item = componentIndex.internalPointer()
            ID = int(tree_item.itemData[0].split('_')[-1])

            self.function.delete(ID) # Remove from Function

            # Remove from Tree
            self.removeComponent(ID)
            self.fitDialog.treeView.reset()
            self.reload()             

            # Remove from Graph
            componentGraphItem = self.fitDialog.componentGraphItems[ID]
            self.fitDialog.componentGraphItems.remove(componentGraphItem)
            self.fitDialog.graph.removeItem(componentGraphItem)
            for i, graph in enumerate(self.fitDialog.componentGraphItems):
                graph.ID = i
            self.fitDialog.sumGraph.updateGraph()
            self.fitDialog.resGraph.updateGraph()

            self.fitDialog.updateDisplay()    #Disable buttons if the function is now empty


class TreeItem:
    def __init__(self, data, parent=None):
        self.itemData = data
        self.parentItem = parent
        self.childItems = []

        if parent is not None:
            parent.appendChild(self)

    def updateData(self, data):
        self.itemData = data

    def appendChild(self, item):
        self.childItems.append(item)

    def removeChild(self, row):
        self.childItems.remove(self.child(row))

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def data(self, column):
        return self.itemData[column]

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        return 0


class SumGraph(pg.GraphItem):
    ''' Show the sum of all components '''
    def __init__(self, fitDialog):
        self.function = fitDialog.fitter.function
        self.x = fitDialog.fitter.x
        super().__init__()
    
    def setData(self):
        if self.function.model is not None:
            pos = np.array([[x, self.function.model(x)] for x in self.x], dtype=float) # curve points
        else:
            pos = np.array([[x, np.nan] for x in self.x], dtype=float)

        self.display_data = {'pos' : pos, # curve points
                            'adj' : np.array([[i, i+1] for i in range(len(self.x)-1)]), # connect them all
                            'pen' : pg.mkPen(color='w', alpha=1.0, width=3.5), # Thick white line
                            'size' : [0 for x in self.x],
                            'symbol' : [None for x in self.x],
                            'pxMode' : True}
    
        self.updateGraph()
    
    def updateGraph(self):
        if self.function.model is not None:
            for i, x in enumerate(self.x) :
                self.display_data['pos'][i] = (x, self.function.model(x))
            
            super().setData(**self.display_data)


class ResGraph(pg.GraphItem):
    ''' Show the residual of the fit '''
    def __init__(self, fitDialog):
        self.function = fitDialog.fitter.function
        self.x = fitDialog.fitter.x
        self.y = fitDialog.fitter.y
        super().__init__()
    
    def setData(self):
        if self.function.model is not None:
            pos = np.array([[x, self.y[i] - self.function.model(x)] for i, x in enumerate(self.x)], dtype=float) # residual points
        else:
            pos = np.array([[x, np.nan] for x in self.x], dtype=float)

        self.display_data = {'pos' : pos, # curve points
                            'adj' : np.array([[i, i+1] for i in range(len(self.x)-1)]), # connect them all
                            'pen' : pg.mkPen(color='w', alpha=1.0, width=3.5), # Thick white line
                            'size' : [0 for x in self.x],
                            'symbol' : [None for x in self.x],
                            'pxMode' : True}
    
        self.updateGraph()
    
    def updateGraph(self):
        if self.function.model is not None:
            for i, x in enumerate(self.x) :
                self.display_data['pos'][i] = (x, self.y[i] - self.function.model(x))
            
            super().setData(**self.display_data)


class ConstGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a constant component"""
    def __init__(self, constComponent, fitDialog, set_defaults=True):
        self.ID = constComponent.ID
        self.fitDialog = fitDialog

        # Set default model values based on to-be-fit data
        if set_defaults:
            fitDialog.fitter.function.components[self.ID].model.amplitude.value = np.nanmin(fitDialog.fitter.y)
            self.fitDialog.fitter.compute_model()        
        
        # Extremis points for the display
        self.x_min = np.nanmin(fitDialog.fitter.x)
        self.x_max = np.nanmax(fitDialog.fitter.x)        
        
        self.dragPoint = None # Used when dragging points with mouse
        self.dragOffset = None
        super().__init__()
    
    def setData(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data = {'pos' : np.array([[self.x_min, component.model(self.x_min)], # position of grab points at ends of line segment
                                               [self.x_max, component.model(self.x_max)]], dtype=float),
                             'adj' : np.array([[0, 1]]), # Conect the two points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # Thin line (white or red depending on selection status)
                             'size' : [15, 15],
                             'symbol' : ['+', '+'],
                             'pxMode' : True,
                             'data' : ['left', 'right']} # Names of the points
        
        self.updateGraph()
    
    def updateGraph(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data['pos'][0] = [self.x_min, component.model(self.x_min)]
        self.display_data['pos'][1] = [self.x_max, component.model(self.x_max)]
        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)
        
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    # Used to move end-points
    def mouseDragEvent(self, ev) :
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            self.dragPoint = pts[0]
            ind = self.dragPoint.data()
            
            if   ind == 'left'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'right' : self.dragOffset = self.display_data['pos'][1] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        # Update component
        component = self.fitDialog.fitter.function.components[self.ID]
        if   ind == 'left'  : component.model.amplitude.value = (ev.pos() + self.dragOffset).y()
        elif ind == 'right' : component.model.amplitude.value = (ev.pos() + self.dragOffset).y()
        self.fitDialog.fitter.compute_model()     

        self.fitDialog.updateGraph()  #To update all elements for selection
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()


class LinearGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a linear component"""
    def __init__(self, linearComponent, fitDialog, set_defaults=True) :
        self.ID = linearComponent.ID
        self.fitDialog = fitDialog

        if set_defaults:
            fitDialog.fitter.function.components[self.ID].model.slope.value = 0
            fitDialog.fitter.function.components[self.ID].model.intercept.value = np.nanmin(fitDialog.fitter.y)
            self.fitDialog.fitter.compute_model()

        # Extremis points for the display
        self.x_min = np.nanmin(fitDialog.fitter.x)
        self.x_max = np.nanmax(fitDialog.fitter.x)        
        
        self.dragPoint = None # Used when dragging points with mouse
        self.dragOffset = None
        super().__init__()

    def setData(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data = {'pos' : np.array([[self.x_min, component.model(self.x_min)], # position of grab points at ends of line segment
                                               [self.x_max, component.model(self.x_max)]], dtype=float),
                             'adj' : np.array([[0, 1]]), # Conect the two points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # Thin line (white or red depending on selection status)
                             'size' : [15, 15],
                             'symbol' : ['+', '+'],
                             'pxMode' : True,
                             'data' : ['left', 'right']} # Names of the points

        self.updateGraph()
    
    def updateGraph(self) :
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data['pos'][0] = [self.x_min, component.model(self.x_min)]
        self.display_data['pos'][1] = [self.x_max, component.model(self.x_max)]
        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)

        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    # Used to move end-points
    def mouseDragEvent(self, ev) :
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            self.dragPoint = pts[0]
            ind = self.dragPoint.data()
            
            if   ind == 'left'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'right' : self.dragOffset = self.display_data['pos'][1] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        x0, y0 = self.display_data['pos'][0]
        x1, y1 = self.display_data['pos'][1]
        
        # Update component
        if   ind == 'left'  : y0 = (ev.pos() + self.dragOffset).y()
        elif ind == 'right' : y1 = (ev.pos() + self.dragOffset).y()
        
        component = self.fitDialog.fitter.function.components[self.ID]
        component.model.slope.value, component.model.intercept.value = np.polyfit([x0, x1], [y0, y1], deg=1)
        self.fitDialog.fitter.compute_model()

        self.fitDialog.updateGraph()  #To update all elements for selection
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()


class QuadraticGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a quadratic component"""
    def __init__(self, quadraticComponent, fitDialog, set_defaults=True) :
        self.ID = quadraticComponent.ID
        self.x = fitDialog.fitter.x
        self.fitDialog = fitDialog
        
        # extremis and middle points
        self.x_min = np.nanmin(self.x)
        self.x_max = np.nanmax(self.x)
        self.x_mid = (self.x_min + self.x_max) / 2

        # Set default model values based on to-be-fit data
        if set_defaults:
            xfit = [self.x_min, self.x_mid, self.x_max]
            yfit = [np.nanmin(fitDialog.fitter.y), np.nanmax(fitDialog.fitter.y), np.nanmin(fitDialog.fitter.y)]
            component = self.fitDialog.fitter.function.components[self.ID]
            component.model.c2.value, component.model.c1.value, component.model.c0.value = np.polyfit(xfit, yfit, deg=2)
            self.fitDialog.fitter.compute_model()

        self.dragPoint = None # Used when dragging points with mouse
        self.dragOffset = None
        super().__init__()
    
    def setData(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data = {'pos' : np.array([[self.x_min, component.model(self.x_min)], # position of grab points
                                               [self.x_mid, component.model(self.x_mid)],
                                               [self.x_max, component.model(self.x_max)]] +
                                               [[x, component.model(x)] for x in self.x], dtype=float), # Draw the curve
                             'adj' : np.array([[i, i+1] for i in range(3, len(self.x)+2)]), # connect the curve points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # thin white or red line
                             'size' : [15, 15, 15] + [0 for x in self.x], # only show the grab points
                             'symbol' : ['+', '+', '+'] + [None for x in self.x],
                             'pxMode' : True,
                             'data' : ['left', 'mid', 'right'] + [None for x in self.x]}
        
        self.updateGraph()
    
    def updateGraph(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        self.display_data['pos'][0] = [self.x_min, component.model(self.x_min)]
        self.display_data['pos'][1] = [self.x_mid, component.model(self.x_mid)]
        self.display_data['pos'][2] = [self.x_max, component.model(self.x_max)]
        
        for i, x in enumerate(self.x, start=3) :
            self.display_data['pos'][i] = (x, component.model(x))
        
        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)
        
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    def mouseDragEvent(self, ev):
        """ Used to move drag points"""
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            self.dragPoint = pts[0]
            ind = self.dragPoint.data()
            
            if   ind == 'left'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'mid'   : self.dragOffset = self.display_data['pos'][1] - pos
            elif ind == 'right' : self.dragOffset = self.display_data['pos'][2] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        x0, y0 = self.display_data['pos'][0]
        x1, y1 = self.display_data['pos'][1]
        x2, y2 = self.display_data['pos'][2]
        
        # Update component
        if   ind == 'left'  : y0 = (ev.pos() + self.dragOffset).y()
        elif ind == 'mid'   : y1 = (ev.pos() + self.dragOffset).y()
        elif ind == 'right' : y2 = (ev.pos() + self.dragOffset).y()
        component = self.fitDialog.fitter.function.components[self.ID]
        component.model.c2.value, component.model.c1.value, component.model.c0.value = np.polyfit([x0, x1, x2], [y0, y1, y2], deg=2)
        self.fitDialog.fitter.compute_model()

        self.fitDialog.updateGraph()
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()


class GaussianGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a gaussian component"""

    def __init__(self, gaussianComponent, fitDialog, set_defaults=True) :
        self.ID = gaussianComponent.ID
        self.x = fitDialog.fitter.x
        self.fitDialog = fitDialog

        # Set default model values based on to-be-fit data
        if set_defaults:
            component = fitDialog.fitter.function.components[self.ID]
            component.model.mean.value = np.nanmean(self.x)
            component.model.amplitude.value = np.nanmax(fitDialog.fitter.y) 
            self.fitDialog.fitter.compute_model()          

        # for grab points
        x_min = np.nanmin(self.x)
        x_max = np.nanmax(self.x)
        self.stddev_min = (x_max - x_min) / (len(self.x)-1) # Don't let the width go to zero
        
        self.dragPoint = None
        self.dragOffset = None
        super().__init__()
    
    def setData(self):
        # 'pos' is the position of grab points and the curve
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        
        mean = component.model.mean.value
        stddev = component.model.stddev.value
        self.display_data = {'pos' : np.array([[mean - stddev, component.model(mean - stddev)],
                                               [mean, component.model(mean)],
                                               [mean + stddev, component.model(mean + stddev)]] +
                                               [[x, component.model(x)] for x in self.x], dtype=float),
                             'adj' : np.array([[i, i+1] for i in range(3, len(self.x)+2)]), # connect the curve points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # thin white or red line
                             'size' : [15, 15, 15] + [0 for x in self.x], # only show the grad points
                             'symbol' : ['+', '+', '+'] + [None for x in self.x],
                             'pxMode' : True,
                             'data' : ['left', 'peak', 'right'] + [None for x in self.x]}

        self.updateGraph()
    
    # Used to move drag points
    def updateGraph(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'

        mean = component.model.mean.value
        stddev = component.model.stddev.value        
        self.display_data['pos'][0] = (mean - stddev, component.model(mean - stddev))
        self.display_data['pos'][1] = (mean, component.model(mean))
        self.display_data['pos'][2] = (mean + stddev, component.model(mean + stddev))
                        
        for i, x in enumerate(self.x, start=3) :
            self.display_data['pos'][i] = (x, component.model(x))

        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)
        
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    def mouseDragEvent(self, ev) :
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected 
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            ind = None
            for pt in pts :
                self.dragPoint = pt
                ind = pt.data()
                if ind is not None : break
            else :
                ev.ignore()
                return
            
            if   ind == 'left'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'peak'  : self.dragOffset = self.display_data['pos'][1] - pos
            elif ind == 'right' : self.dragOffset = self.display_data['pos'][2] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        # Update component
        component = self.fitDialog.fitter.function.components[self.ID]
        if   ind == 'left' :
            component.model.stddev.value = max(self.stddev_min, component.model.mean.value - (ev.pos() + self.dragOffset).x())
        elif ind == 'peak' :
            component.model.mean.value, component.model.amplitude.value = ev.pos() + self.dragOffset
        elif ind == 'right' :
            component.model.stddev.value = max(self.stddev_min, (ev.pos() + self.dragOffset).x() - component.model.mean.value)
        self.fitDialog.fitter.compute_model()

        self.fitDialog.updateGraph()
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()


class MoffatGraph(pg.GraphItem):
    """Graph object that can be added to the pgGraph that reprents a Moffat component"""

    def __init__(self, moffatComponent, fitDialog, set_defaults=True) :
        self.ID = moffatComponent.ID
        self.x = fitDialog.fitter.x
        self.fitDialog = fitDialog

        # Set default model values based on to-be-fit data
        if set_defaults:
            component = fitDialog.fitter.function.components[self.ID]
            amplitude_index = np.nanargmax(fitDialog.fitter.y)
            component.model.amplitude.value = fitDialog.fitter.y[amplitude_index]
            component.model.x_0.value = self.x[amplitude_index]
            component.model.alpha.value = 1 # When alpha=1, gamma=fwhm/2. Easier to calculate for initialization        
            try:
                half_max_left_index = np.argwhere(fitDialog.fitter.y[:amplitude_index] > component.model.amplitude.value / 2)[0][0] # Index of first y value that exceeds half the maximum
            except IndexError:
                half_max_left_index = None
            self.fwhm_min = 2 * (component.model.x_0.value - self.x[amplitude_index - 1])
            if half_max_left_index is not None:
                component.model.gamma.value = component.model.x_0.value - self.x[half_max_left_index]
            else:
                component.model.gamma.value = self.fwhm_min / 2 # Not accurate, but gives an initial value  
            self.fitDialog.fitter.compute_model()

        # for grab points
        self.dragPoint = None
        self.dragOffset = None
        super().__init__()
    
    def setData(self):
        # 'pos' is the position of grab points and the curve
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'
        
        x_0 = component.model.x_0.value
        hwhm = component.model.fwhm / 2 # half width half max
        hwqm = self.calc_full_width_quarter_max() / 2 # half width quarter max
        self.display_data = {'pos' : np.array([[x_0 - hwqm, component.model(x_0 - hwqm)],
                                               [x_0 - hwhm, component.model(x_0 - hwhm)],
                                               [x_0, component.model(x_0)],
                                               [x_0 + hwhm, component.model(x_0 + hwhm)],
                                               [x_0 + hwqm, component.model(x_0 + hwqm)]] +
                                               [[x, component.model(x)] for x in self.x], dtype=float),
                             'adj' : np.array([[i, i+1] for i in range(5, len(self.x)+4)]), # connect the curve points
                             'pen' : pg.mkPen(color=color, alpha=1.0), # thin white or red line
                             'size' : [15, 15, 15, 15, 15] + [0 for x in self.x], # only show the grad points
                             'symbol' : ['+', '+', '+', '+', '+'] + [None for x in self.x],
                             'pxMode' : True,
                             'data' : ['left quarter max', 'left half max', 'peak', 'right half max', 'right quarter max'] + [None for x in self.x]}
        self.updateGraph()
    
    def calc_full_width_quarter_max(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        return 2 * component.model.gamma.value * np.sqrt((2 ** (2 / component.model.alpha.value) - 1))

    def calc_alpha_gamma(self, component, fwqm, fwhm):
        component.model.alpha.value = 1 / np.log2(fwqm ** 2 / fwhm ** 2 - 1)
        component.model.gamma.value = fwhm / (2 * np.sqrt(2 ** (1 / component.model.alpha.value) - 1))

    def check_full_width_bounds(self, fwhm, fwqm, fwhm_fixed=False, fwqm_fixed=False, epsilon=1e-10):
        """
        checks bounds according to sqrt(2) < fwqm / fwhm <= sqrt(3) and fwhm >= fwhm_min
        Exactly one of fwhm_fixed and fwqm_fixed must be set to True. The other parameter will be calculated such that the ratio falls within the valid range
        Note: the lower bound is a '<' NOT '<='. Epsilon is a small number that is used when relevant to ensure the ratio of interest is never equivalent to sqrt(2)
        """
        assert fwhm_fixed + fwqm_fixed == 1, 'Exactly one of fwhm_fixed and fwqm_fixed must be set to True'
        if fwqm / fwhm <= np.sqrt(2):
            if fwhm_fixed:
                fwqm = fwhm * np.sqrt(2) + epsilon
            elif fwqm_fixed:
                fwhm = (fwqm - epsilon) / np.sqrt(2)
        if fwqm / fwhm > np.sqrt(3):
            if fwhm_fixed:
                fwqm = fwhm * np.sqrt(3)
            elif fwqm_fixed:
                fwhm = fwqm / np.sqrt(3)
        if fwhm < self.fwhm_min:
            return self.check_full_width_bounds(self.fwhm_min, fwqm, fwhm_fixed=True)
        return fwhm, fwqm

    # Used to move drag points
    def updateGraph(self):
        component = self.fitDialog.fitter.function.components[self.ID]
        color = 'r' if self.fitDialog.fitter.function.selected_comp == self.ID else 'w'

        x_0 = component.model.x_0.value
        hwhm = component.model.fwhm / 2 # half width half max
        hwqm = self.calc_full_width_quarter_max() / 2 # half width quarter max
        self.display_data['pos'][0] = (x_0 - hwqm, component.model(x_0 - hwqm))
        self.display_data['pos'][1] = (x_0 - hwhm, component.model(x_0 - hwhm))
        self.display_data['pos'][2] = (x_0, component.model(x_0))
        self.display_data['pos'][3] = (x_0 + hwhm, component.model(x_0 + hwhm))
        self.display_data['pos'][4] = (x_0 + hwqm, component.model(x_0 + hwqm))
                        
        for i, x in enumerate(self.x, start=5) :
            self.display_data['pos'][i] = (x, component.model(x))

        self.display_data['pen'] = pg.mkPen(color=color, alpha=1.0)
        
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        super().setData(**self.display_data)

    def mouseDragEvent(self, ev) :
        if ev.button() != Qt.MouseButton.LeftButton :
            ev.ignore()
            return
        
        self.fitDialog.fitter.function.selected_comp = self.ID # Mark this element as selected 
        if ev.isStart() :
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0 :
                ev.ignore()
                return
            
            ind = None
            for pt in pts :
                self.dragPoint = pt
                ind = pt.data()
                if ind is not None : break
            else :
                ev.ignore()
                return
            
            if   ind == 'left quarter max'  : self.dragOffset = self.display_data['pos'][0] - pos
            elif ind == 'left half max'     : self.dragOffset = self.display_data['pos'][1] - pos
            elif ind == 'peak'              : self.dragOffset = self.display_data['pos'][2] - pos
            elif ind == 'right half max'    : self.dragOffset = self.display_data['pos'][3] - pos
            elif ind == 'right quarter max' : self.dragOffset = self.display_data['pos'][4] - pos
        elif ev.isFinish() :
            self.dragPoint = None
            return
        elif self.dragPoint is None :
            ev.ignore()
            return
        
        ind = self.dragPoint.data()
        
        # Update component
        component = self.fitDialog.fitter.function.components[self.ID]
        if   ind == 'left quarter max':
            fwhm, fwqm = self.check_full_width_bounds(component.model.fwhm, 2 * (component.model.x_0.value - (ev.pos() + self.dragOffset).x()), fwqm_fixed=True)
            self.calc_alpha_gamma(component, fwqm, fwhm)
        elif ind == 'left half max' :
            fwhm, fwqm = self.check_full_width_bounds(2 * (component.model.x_0.value - (ev.pos() + self.dragOffset).x()), self.calc_full_width_quarter_max(), fwhm_fixed=True)
            self.calc_alpha_gamma(component, fwqm, fwhm)
        elif ind == 'peak' :
            component.model.x_0.value, component.model.amplitude.value = ev.pos() + self.dragOffset
        elif ind == 'right half max' :
            fwhm, fwqm = self.check_full_width_bounds(2 * ((ev.pos() + self.dragOffset).x() - component.model.x_0.value), self.calc_full_width_quarter_max(), fwhm_fixed=True)
            self.calc_alpha_gamma(component, fwqm, fwhm)
        elif ind == 'right quarter max':
            fwhm, fwqm = self.check_full_width_bounds(component.model.fwhm, 2 * ((ev.pos() + self.dragOffset).x() - component.model.x_0.value), fwqm_fixed=True)
            self.calc_alpha_gamma(component, fwqm, fwhm)
        self.fitDialog.fitter.compute_model()

        self.fitDialog.updateGraph()
        self.fitDialog.sumGraph.updateGraph()
        self.fitDialog.resGraph.updateGraph()
        self.fitDialog.functionTreeModel.reload()
        ev.accept()