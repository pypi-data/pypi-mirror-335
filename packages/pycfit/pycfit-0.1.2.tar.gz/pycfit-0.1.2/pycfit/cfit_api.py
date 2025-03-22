"""
Main API Functions
"""
import pickle
from astropy.modeling import Model
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication
from .function import FunctionFitter
from .dialog import FitDialog
from .grid import Grid
from .dialog_grid import GridDialog



## For Single Spectra ##
def cfit(wavelength, intensity, uncertainty=None, function=None):
    fitter = FunctionFitter(wavelength, intensity, uncertainty, function=function)
    return fitter



def cfit_gui(wavelength, intensity, uncertainty=None, function=None):
    """
    Single spectra fit GUI
    Will return the astropy model that is stored at the time of GUI exit.
    Meaning -- if you have done a "fit", and then adjusted your graphs, the
    adjusted model is returned.

    wavelength:  (1D array)
    intensity:   (1D array)
    uncertainty: (optional 1D array) Measurement uncertainty
    function:  (opional.  astropy model or path to .pkl) 
                Expects an astropy model object, plain or pickled 
                If passed, loads this as the initial model state.
                Otherwise, loads with no model at start
    """
    # create FunctionFitter object
    if function:
        try:
            if isinstance(function, Model):
                astroModel = function
            else:
                with open(function, 'rb') as pkl:
                    astroModel = pickle.load(pkl)
            fitter = FunctionFitter(wavelength, intensity, uncertainty, function=astroModel)
            model_init = astroModel.copy()
        except:
            print(f'Bad function argument: {function}')
            return
    else:
        fitter = FunctionFitter(wavelength, intensity, uncertainty)
        model_init = None

    # Create interactive fit dialog object
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(['cfit_gui'])
    fd = FitDialog(fitter=fitter)
    if fd.exec_():
        return fd.get_model()
    else:
        print('Canceled!')
        return model_init


def cfit_load(modelFile):
    """Utility to load astropy Model from pickle"""
    try:
        with open(modelFile, 'rb') as pkl:
            astroModel = pickle.load(pkl)
        if isinstance(astroModel, Model):
            return astroModel
        else:
            raise Exception()
    except:
        print(f'Bad pickle file path: {modelFile}')



## For Grid of Spectras ##
def cfit_grid(function, wavelength, intensity, uncertainty=None, mask=None, auto_fit=False, parallel=True):
    GM = Grid(function, wavelength, intensity, uncertainty=uncertainty, mask=mask)
    if auto_fit:
        print("Fitting across the grid. This may take a few minutes . . . ")
        GM.fit(parallel=parallel)

    return GM


def cfit_grid_gui(function, wavelength, intensity, uncertainty=None, mask=None, parallel=True):
    GM = cfit_grid(function, wavelength, intensity, uncertainty=uncertainty, mask=mask, auto_fit=True, parallel=parallel)

    # Create interactive fit dialog object
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(['cfit_grid_gui'])
    gd = GridDialog(GM)
    if gd.exec_():
        return gd.get_results()
    else:
        print('Canceled!')
        return function
        

