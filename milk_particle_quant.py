"""
Python code to quantify the area of particulate features in micrographs of milk.
This wants to be a parallelised .py script to extract a list of features from a single file.  

Copyright (C) 2024  Christopher James Pook

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
Contact: drchrispook@gmail.com
Liggins Institute, 
The University of Auckland,
85 Park Road, Grafton,
Auckland 1023,
Aotearoa New Zealand
""""

import pandas as pd
import os
# from multiprocessing import Pool
from multiprocess import Pool
from datetime import datetime
from skimage.measure import find_contours
from skimage.io import imread
from skimage.filters import gaussian
from skimage.filters.rank import autolevel
from skimage.measure import find_contours
from skimage.morphology import disk
from shapely import Polygon, Point
import plotly.offline as offline
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# _input_tup needs to contain the following values:
    # the path to the input image
    # a list of values for _gauss_range
    # a list of values for _thresh_range
    # a Boolean for _live_plot
    # a Boolean for _save_figs
    # the file path of _output_folder
def analyse_image(_input_tup):
    ff = _input_tup[0] # input_image
    _gauss_range = _input_tup[1]
    _thresh_range  = _input_tup[2]
    _live_plot = _input_tup[3]
    _save_figs = _input_tup[4]
    _output_folder = _input_tup[5]
    
    contours_results = []
    first_pass = True

    tm = 'nf'
    if 'F+' in ff: tm = 'ff'
    tt = ff.split('_')[1]
    tt = tt.replace('T','')
    tt = int(tt)
#     print(tm, tt)
    pid = ff.split('\\')[0].split('-')[-1]
    frame = ff.split('\\')[-1].split('_')[-1].replace('.jpg','').replace('F+','').replace('F-','')
    frame = int(frame)
    
    raw = imread(ff)
    ydim = raw.shape[1]
    print('raw.shape:', raw.shape, ' ydim:', ydim)
    bpic = [] # blue channel data
    for ii in raw: bpic.append([x[2] for x in ii])        
    bpic = np.array(bpic, dtype=np.uint8) # back to numpy array

    for _gauss in _gauss_range:
        for _thresh in _thresh_range:
            blur = gaussian(bpic, sigma=_gauss) # Gaussian blur
            print('blue.shape 1:', blur.shape)
            blur = autolevel(blur,  disk(1000)) # autolevel to normalise greyscale range to 8-bit
            print('blue.shape 2:', blur.shape)
            
            # pad with white border
            pad = []
            pad.append([255] * (ydim +2)) # top row
            for ii in blur: 
                if len(ii) > ydim: print('LONG!!!!!', len(ii))
                pad.append([255, *ii, 255]) # edges
            pad.append([255] * (ydim +2)) # bottom row
            print('xlen set:', set([len(x) for x in pad]))
            pad = np.array(pad, dtype=np.uint8)
    
            contours = find_contours(pad, int(_thresh)) # FIND CONTOURS
            pollies = [Polygon(x) for x in contours]
            count = 0
            for ee in pad: count = count + len([x for x in ee if x < int(_thresh)]) # count is the number of pixels in this image that exceed the threshold
            for nn,ii in enumerate(contours):
                area = pollies[nn].area
                for n3, pp in enumerate([Point(x[0]) for x in contours]): # test a point in every contour to see if it's inside this contour
                    if pp.within(pollies[nn]): # if True it's a hole
                        area = area - pollies[n3].area # subtract the area of any holes
                out_dic = {'gauss':_gauss, 'thresh':_thresh, 'file':ff, 'pid':pid, 'frame':frame, 'tm':tm, 'time':tt, 'n':nn, 'contour':ii, 'area':area, 'count':count} 
                contours_results.append(out_dic)
            if _live_plot or _save_figs: 
                fig = px.imshow(blur.T) # plot the heatmap    
                for nn,ii in enumerate(contours):
                    il = list(zip(*ii))
                    fig.add_trace(go.Scatter(x = il[0], y = il[1], showlegend = False))
                    fig.update_layout(title = 'file: ' + ff + ', Gauss range: ' + str(_gauss) + ', thresh: ' + str(_thresh))
                if _live_plot: 
                    offline.plot(fig)
                if _save_figs:
                    fig.write_html(_save_figs + r'\\' + os.path.basename(ff).replace('.jpg','') + '_Gauss' + str(_gauss) + '_thresh' + str(_thresh) + '.html')


    contours = pd.DataFrame(contours_results) # df to collect contour results
    contours.to_pickle(_output_folder + r'\\' + os.path.basename(ff).replace('.jpg','.xz')) # pickle
    print('finished processing file ', ff)
    return contours



def parallel_milk_image_analysis(_input_tup_list):
    _output_df_list = []
    with Pool(os.cpu_count() -4) as pool: # Be nice and always leave a few cores free.
        _output_df_list = pool.map_async(analyse_image, _input_tup_list).get()
    return _output_df_list
