#!/usr/bin/env python

# Copyright 2016 NeuroData (http://neurodata.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# qa_reg.py
# Created by Vikram Chandrashekhar.
# Edited by Greg Kiar and Eric Bridgeford.
# Email: Greg Kiar @ gkiar@jhu.edu

import os
import re
import sys
import numpy as np
import nibabel as nb
import ndmg.utils as mgu
from argparse import ArgumentParser
from scipy import ndimage
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl
mpl.use('Agg')  # very important above pyplot import

import matplotlib.pyplot as plt


def reg_mri_pngs(mri, atlas, outdir, loc=0, mean=False, minthr=2, maxthr=95):
    """
    outdir: directory where output png file is saved
    fname: name of output file WITHOUT FULL PATH. Path provided in outdir.
    """
    atlas_data = nb.load(atlas).get_data()
    mri_data = nb.load(mri).get_data()
    if mri_data.ndim==4:  # 4d data, so we need to reduce a dimension
        if mean:
            mr_data = mri_data.mean(axis=3)
        else:
            mr_data = mri_data[:,:,:,loc]
    else:  # dim=3
        mr_data = mri_data

    cmap1 = LinearSegmentedColormap.from_list('mycmap1', ['black', 'magenta'])
    cmap2 = LinearSegmentedColormap.from_list('mycmap2', ['black', 'green'])

    fig = plot_overlays(atlas_data, mr_data, (cmap1, cmap2), minthr, maxthr)

    # name and save the file
    fname = os.path.split(mri)[1].split(".")[0] + '.png'
    fig.savefig(outdir + '/' + fname, format='png')
    plt.close()

def plot_brain(brain, minthr=2, maxthr=95):
    cmap = LinearSegmentedColormap.from_list('mycmap2', ['black', 'magenta'])
    plt.rcParams.update({'axes.labelsize': 'x-large',
                         'axes.titlesize': 'x-large'})
    fbr = plt.figure()
    if brain.shape == (182, 218, 182):
        x = [78, 90, 100]
        y = [82, 107, 142]
        z = [88, 103, 107]
    else:
        shap = brain.shape
        x = [int(shap[0]*0.35), int(shap[0]*0.51), int(shap[0]*0.65)]
        y = [int(shap[1]*0.35), int(shap[1]*0.51), int(shap[1]*0.65)]
        z = [int(shap[2]*0.35), int(shap[2]*0.51), int(shap[2]*0.65)]
    coords = (x, y, z)

    labs = ['Sagittal Slice (YZ fixed)',
            'Coronal Slice (XZ fixed)',
            'Axial Slice (XY fixed)']
    var = ['X', 'Y', 'Z']
    # create subplot for first slice
    # and customize all labels
    idx = 0
    for i, coord in enumerate(coords):
        for pos in coord:
            idx += 1
            ax = fbr.add_subplot(3, 3, idx)
            ax.set_title(var[i] + " = " + str(pos))
            if i == 0:
                image = ndimage.rotate(brain[pos, :, :], 90)
            elif i == 1:
                image = ndimage.rotate(brain[:, pos, :], 90)
            else:
                image = brain[:, :, pos]

            if idx % 3 == 1:
                ax.set_ylabel(labs[i])
                ax.yaxis.set_ticks([0, image.shape[0]/2, image.shape[0] - 1])
                ax.xaxis.set_ticks([0, image.shape[1]/2, image.shape[1] - 1])

            min_val, max_val = get_min_max(image, minthr, maxthr)
            ax.imshow(image, interpolation='none', cmap=cmap, alpha=0.5,
                      vmin=min_val, vmax=max_val)

    fbr.set_size_inches(12.5, 10.5, forward=True)
    return fbr


def plot_overlays(atlas, b0, cmaps=None, minthr=2, maxthr=95):
    plt.rcParams.update({'axes.labelsize': 'x-large',
                         'axes.titlesize': 'x-large'})
    foverlay = plt.figure()

    if cmaps is None:
        cmap1 = LinearSegmentedColormap.from_list('mycmap1',
                                                  ['black', 'magenta'])
        cmap2 = LinearSegmentedColormap.from_list('mycmap2',
                                                  ['black', 'green'])
        cmaps = (cmap1, cmap2)

    if b0.shape == (182, 218, 182):
        x = [78, 90, 100]
        y = [82, 107, 142]
        z = [88, 103, 107]
    else:
        shap = b0.shape
        x = [int(shap[0]*0.35), int(shap[0]*0.51), int(shap[0]*0.65)]
        y = [int(shap[1]*0.35), int(shap[1]*0.51), int(shap[1]*0.65)]
        z = [int(shap[2]*0.35), int(shap[2]*0.51), int(shap[2]*0.65)]
    coords = (x, y, z)

    labs = ['Sagittal Slice (YZ fixed)',
            'Coronal Slice (XZ fixed)',
            'Axial Slice (XY fixed)']
    var = ['X', 'Y', 'Z']
    # create subplot for first slice
    # and customize all labels
    idx = 0
    for i, coord in enumerate(coords):
        for pos in coord:
            idx += 1
            ax = foverlay.add_subplot(3, 3, idx)
            ax.set_title(var[i] + " = " + str(pos))
            if i == 0:
                image = ndimage.rotate(b0[pos, :, :], 90)
                atl = ndimage.rotate(atlas[pos, :, :], 90)
            elif i == 1:
                image = ndimage.rotate(b0[:, pos, :], 90)
                atl = ndimage.rotate(atlas[:, pos, :], 90)
            else:
                image = b0[:, :, pos]
                atl = atlas[:, :, pos]

            if idx % 3 == 1:
                ax.set_ylabel(labs[i])
                ax.yaxis.set_ticks([0, image.shape[0]/2, image.shape[0] - 1])
                ax.xaxis.set_ticks([0, image.shape[1]/2, image.shape[1] - 1])

            min_val, max_val = get_min_max(image, minthr, maxthr)
            ax.imshow(atl, interpolation='none', cmap=cmaps[0], alpha=0.5)
            ax.imshow(image, interpolation='none', cmap=cmaps[1], alpha=0.5,
                     vmin=min_val, vmax=max_val)

    foverlay.set_size_inches(12.5, 10.5, forward=True)
    return foverlay


def get_min_max(data, minth=2, maxthr=95)
    '''
    data: regmri data to threshold.
    '''
    min_val = np.percentile(data, 2)
    max_val = np.percentile(data, 95)
    return (min_val, max_val)
