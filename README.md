# milk_particle_quant
Python code to quantify the area of particulate features in micrographs of milk.

This script uses the skimage and shapely libraries to convert a colour micrograph to an 8-bit image gresycale by extracting the blue channel. A Gaussian blur is applied and contours around features are detected. The area of contours are calculated and the area of any contours within contours are subtracted as holes. 

The code is written for incoropration into a parallel processing script which feeds it an input tuple containing:
    # the path to the input image
    # a list of values for _gauss_range
    # a list of values for _thresh_range
    # a Boolean for _live_plot
    # a Boolean for _save_figs
    # the file path of _output_folder

The various value for _gauss_range and _thresh_range are so you can optimise the results for your own images. 


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
