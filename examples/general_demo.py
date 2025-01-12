#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This example script shows the process of using the toolbox with dicom data and processing them to output an unwrapped
phase plot. More precisely, it will:

* Download unsorted dicoms
* Run dcm2bids to convert to nifti with bids structure
* Unwrap phase
* Save wrapped and unwrapped plot of first X, Y volume as unwrap_phase_plot.png in the output directory

To use the script, simply provide an output directory where the processing and output figure will be generated, if no
directory is provided, a directory *output_dir* will be created in the current directory.

::

    from examples.general_demo import general_demo
    general_demo()

"""

import os
import numpy as np
from matplotlib.figure import Figure
import glob
import logging

import nibabel as nib

from shimmingtoolbox.unwrap.unwrap_phase import unwrap_phase
from shimmingtoolbox.utils import run_subprocess
from shimmingtoolbox import dicom_to_nifti
from shimmingtoolbox.load_nifti import read_nii


def general_demo(path_output=os.path.join(os.path.curdir, 'output_dir')):
    """
    Args:
        path_output (str): Output directory to store data and results.

    Returns:
        str: File name and path of output figure
    """

    logging.basicConfig(level='INFO')

    # Download example data
    path_testing_data = os.path.join(path_output, 'testing_data')
    run_subprocess(['st_download_data', 'testing_data', '--output', path_testing_data])

    # Transfer from dicom to nifti
    path_dicom_unsorted = os.path.join(path_testing_data, 'dicom_unsorted')
    path_nifti = os.path.join(path_output, 'niftis')
    dicom_to_nifti(path_dicom_unsorted, path_nifti, subject_id='sub-01')

    # Open phase data
    fname_phases = glob.glob(os.path.join(path_nifti, 'sub-01', 'fmap', '*phase*.nii.gz'))

    nii_phase_e1, _, _ = read_nii(fname_phases[0])
    nii_phase_e2, _, _ = read_nii(fname_phases[1])

    # Open mag data
    fname_mags = glob.glob(os.path.join(path_nifti, 'sub-01', 'fmap', '*magnitude*.nii.gz'))

    nii_mag_e1 = nib.load(fname_mags[0])
    nii_mag_e2 = nib.load(fname_mags[1])

    # Call prelude to unwrap the phase
    unwrapped_phase_e1 = unwrap_phase(nii_phase_e1, 'prelude', mag=nii_mag_e1.get_fdata())
    unwrapped_phase_e2 = unwrap_phase(nii_phase_e2, 'prelude', mag=nii_mag_e2.get_fdata(), threshold=200)

    # Plot results
    fig = Figure(figsize=(10, 10))
    # FigureCanvas(fig)
    ax = fig.add_subplot(3, 2, 1)
    im = ax.imshow(nii_mag_e1.get_fdata()[:-1, :-1, 0])
    fig.colorbar(im)
    ax.set_title("Mag e1")
    ax = fig.add_subplot(3, 2, 2)
    im = ax.imshow(nii_mag_e2.get_fdata()[:-1, :-1, 0])
    fig.colorbar(im)
    ax.set_title("Mag e2")
    ax = fig.add_subplot(3, 2, 3)
    im = ax.imshow(nii_phase_e1.get_fdata()[:-1, :-1, 0])
    fig.colorbar(im)
    ax.set_title("Wrapped e1")
    ax = fig.add_subplot(3, 2, 4)
    im = ax.imshow(nii_phase_e2.get_fdata()[:-1, :-1, 0])
    fig.colorbar(im)
    ax.set_title("Wrapped e2")
    ax = fig.add_subplot(3, 2, 5)
    im = ax.imshow(unwrapped_phase_e1[:-1, :-1, 0])
    fig.colorbar(im)
    ax.set_title("Unwrapped e1")
    ax = fig.add_subplot(3, 2, 6)
    im = ax.imshow(unwrapped_phase_e2[:-1, :-1, 0])
    fig.colorbar(im)
    ax.set_title("Unwrapped e2")

    fname_figure = os.path.join(path_output, 'unwrap_phase_plot.png')
    fig.savefig(fname_figure)

    return fname_figure


if __name__ == '__main__':
    general_demo()
