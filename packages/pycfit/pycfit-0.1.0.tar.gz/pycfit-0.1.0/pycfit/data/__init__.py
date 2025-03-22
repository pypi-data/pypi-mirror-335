import numpy as np
from pathlib import Path

def load_average_data():
    """
    Example data from SPICE mission
    Average spectra from window 'O III 703 / Mg IX 706 (Merged)'

    Returns a tuple: (wavelength, intensity, uncertainty)

    Source file: solo_L2_spice-n-ras_20240425T121922_V22_251658647-000.fits
    """

    LOCAL_DIR = Path(__file__).parent
    avg = np.load(LOCAL_DIR.joinpath('avg_data.npz'))

    return avg['wavelength'], avg['intensity'], avg['uncertainty']


def load_grid_data(patch=False):
    """
    Example data from SPICE mission
    Raster spectra from window 'O III 703 / Mg IX 706 (Merged)'

    Returns a tuple: (wavelength, intensity, uncertainty, mask)

    Optional keyword "patch=True" will return only a 20x20 subset.
    Otherwise, full raster is returned

    Source file: solo_L2_spice-n-ras_20240425T121922_V22_251658647-000.fits
    """

    LOCAL_DIR = Path(__file__).parent

    if patch:
        data = np.load(LOCAL_DIR.joinpath('patch_data.npz'))
    else:
        data = np.load(LOCAL_DIR.joinpath('grid_data.npz'))

    return data['wavelength'], data['intensity'], data['uncertainty'], data['mask']