
# -*- coding: utf-8 -*-
"""
This is ILEE_CSK main function .py file.
@author: Pai Li
"""


#read libraries
import numpy as np
from skimage import io
import os
import time
import copy
#import sys

from skimage.filters import gaussian
from skimage.filters import scharr
from skimage.filters import threshold_niblack
from skimage.morphology import skeletonize
from skimage.transform import resize
from skimage.measure import label
from skimage.morphology import binary_closing
from skimage.morphology import remove_small_holes
from skimage.morphology import remove_small_objects

from scipy.sparse import coo_matrix
from scipy.sparse.linalg import cg
from scipy.ndimage import distance_transform_edt
from scipy.ndimage import convolve
import scipy.io

import pandas as pd
import skan
import numba as nb
import seaborn as sns
from .fast_interp import interp3d
import scikit_posthocs as sp
import matplotlib.pyplot as plt

#define global varibles
global pL
global saved_img_shape
global saved_pL_type
global temp_directory

pL = 0
saved_img_shape = 0
saved_pL_type = 'blank'
temp_directory = 'D:/MATLAB_temp'


#import MATLAB module if available
from imp import find_module

matlab_check = True
try:
    import matlab.engine
except ModuleNotFoundError:
    matlab_check = False
    print('MATLAB engine not found, bypassing MATLAB module...')
if (matlab_check):
    print('MATLAB engine detect: importing MATLAB module...')
    global eng
    eng = matlab.engine.start_matlab()
    module_path = find_module('ILEE_CSK')[1]
    eng.cd(module_path)


##load functions
def rearrange_image_dimension(img, target_channel = None):
    '''
    transform your image array of any demension order (most likely x(height)-y(width)-z(stack)-channel or channel-x-y-z structure, depending on your confocal microscope) into z-x-y array with your object channel.This function depends on sorting, so your channel number must be lower than your stack number, and your stack number (z-resolution) must be lower than your x and y resolution.

    img, 3D or 4D array read from a tiff file by skimage.io; if img is 3D array (only one channel, which is your cytoskeleton), target_channel must be None.
    target_channel, int, your cytoskeleton fluorescence channel index
    '''
    img_size = np.array(img.shape)
    dimension = img_size.shape[0]
    df_dimension = pd.DataFrame(data = img_size, columns = ['dimension_size'])
    df_dimension['dimension_index'] = range(img_size.shape[0])
    df_dimension = df_dimension.sort_values(by = ['dimension_size', 'dimension_index'])
    if (dimension <= 2):
        print ('Error: image have less than 3 dimensions; please check data structure')
        return()
    elif (dimension == 3):
        if (target_channel != None):
            print ('Error: your image only have 3 dimensions, in which case your target_channel must be None and we assume the dimension with lowest size to be z')
            return()
        else:
            result = np.moveaxis(img, source = np.array(df_dimension['dimension_index']), destination = np.array([0,1,2]))
    elif (dimension >= 5):
        print('image has more than 4 dimension (x, y, z, and channel); please check data structure')
        return()
    else:
        result = np.moveaxis(img, source = np.array(df_dimension['dimension_index']), destination = np.array([0,1,2,3]))

    if (target_channel != None):
        return(result[target_channel])
    else :
        return(result)

#This function calculates brightness distribution parameters for downstream computation of coarse global threshold. Please beware that max is set to 4095 to fit other functions.
def call_BD_max (img, subpeak_fold = 0.8):
    BD = np.histogram(a = img.flatten(), bins = 4095, range = (0,4095))[0]
    kernal = np.array([0.2,0.2,0.2,0.2,0.2])
    BD_smoothed = np.convolve(a = BD, v = kernal, mode='same')
    freqs = BD_smoothed/img.flatten().shape[0]
    peak_brightness = np.argmax(BD_smoothed)
    peak_frequency = freqs.max()
    subpeak = peak_frequency*subpeak_fold
    for i in range(4095):
        if (freqs[i]>subpeak):
            left_boarder = i - 0.5
            break
    for i in range(peak_brightness, 4095):
        if (freqs[i]<subpeak):
            right_boarder = i - 0.5
            break
    return (peak_brightness, peak_frequency, left_boarder, right_boarder)


#This function FASTLY measures the global threshold (NE_peak) that gives maximum non-connected negative elements
def NE_peak (img, show_process=False):
    max_value = int(max(img.flatten()))
    NE_distribution=np.zeros(max_value) #to store count

    last_NE=0
    for i in range(0, max_value, 20):
        if (show_process):
            print('Analyzing at thresholding =', i)
        labeled_map = label((img<i), return_num=True, connectivity=1)
        NE_distribution[i]=labeled_map[1]
        if (NE_distribution[i]<last_NE):
            mark = i
            break
        last_NE=NE_distribution[i]

    for i in range (mark-40, mark):
        if (show_process):
            print('Analyzing at thresholding =', i)
        labeled_map = label((img<i), return_num=True, connectivity=1)
        NE_distribution[i]=labeled_map[1]
        flag1 = NE_distribution[i]<NE_distribution[i-1]
        flag2 = NE_distribution[i]<NE_distribution[i-2]
        flag3 = NE_distribution[i]<NE_distribution[i-3]
        if(flag1 & flag2 &flag3):
            break

    NE_peak = np.argmax(NE_distribution)
    return (NE_peak)


#This function calculate total cell area in certain cases.
def cell_2D_area(img, global_thres_fold = 3.5, hole_thres = 'default', objective_thres = 4, output_fig = False):
    '''
    Get estimated cell area for a 2D image. Required when the image contains true blank (I don't mean tissue area without fluorescence; I mean nothing-at-all blank) area that should not regarded as part of your biological sample. We do global thresholding of x fold of NE_peak, then closing, then fill holes, then delete small dots, then got the area.

    Parameters
    ----------
    img : 2D array.
        Your input image, must be 2D array.
    global_thres_fold : positive number.
        Fold of NE_peak to be used as global theshold. The default is 3.5.
    hole_thres : None or positive number.
        Size by pixel of maximum holes you want to close. If input is 'default', then will use 1/16 of x-resolution multiplied with 1/16 of y-resolution. The default is 'default'
    objective_thres : positive number.
        The minimum size by pixel of non-connected element regarded as cell component. The default is 4.
    output_fig = False: bool
        Whether output cell area image. Default is False 

    Returns
    -------
    Area of the cell by pixel.
    (selective) cell area image

    '''
    
    if (img.ndim==2):
        img = img-img.min()
        img = img.astype('float')
        thres = NE_peak(img)*global_thres_fold
        img_c = img>thres
        img_c = binary_closing(img_c)
        if(hole_thres == 'default'):
            hole_thres = (img.shape[0]/16)*(img.shape[1]/16)
        img_c = remove_small_holes(img_c, area_threshold = hole_thres)
        img_c = remove_small_objects(img_c, min_size = objective_thres)
        area = np.sum(img_c)
        print('argument setting:', global_thres_fold, hole_thres, objective_thres)
        if output_fig:
            return (area, img_c)
        else:
            return (area)
    else:
        print ('Error!!! Wrong input shape; only support 2D array.')
        
        
#This function test and calculate the image effective areas of all tif files in the document using global cell_2D_area parameters
def test_and_call_areas_of_folder (folder_path, obj_channel, global_thres_fold = 3.5, hole_thres = 'default', objective_thres = 4):
    file_name_array = os.listdir(folder_path)
    samples_path = []
    tif_name_array = []
    for i in file_name_array:
        if i.endswith(".tif"):
            tif_name_array.append(i)
            samples_path.append(folder_path+'/'+i)
            
    print ('Now printing effective area segmentation results:')
    df_areas = pd.DataFrame(columns = ['file_path', 'area'])
    for i in range(len(samples_path)):
        print ('current objective sample is:', samples_path[i])
        img = io.imread(samples_path[i])
        img = rearrange_image_dimension(img, target_channel = obj_channel)
        img = np.amax(img, axis=0)
        img = img.astype('float')
        img = img-img.min()
        img = (img/img.max())*4095
        area_test = cell_2D_area(img = img, 
                                 global_thres_fold = global_thres_fold,
                                 hole_thres = hole_thres,
                                 objective_thres = objective_thres,
                                 output_fig = True)
        plt.figure(figsize = (5, 5))
        plt.imshow(img, cmap = 'gray_r', alpha = 1)
        plt.imshow(area_test[1], cmap = 'Greens', alpha = 0.36)
        plt.axis('off')
        plt.show()
        new_row = pd.DataFrame(data = [[samples_path[i], area_test[0]]],columns = ['file_path', 'area'])
        df_areas = pd.concat([df_areas, new_row], ignore_index = True)
    
    return (df_areas)
        

#This function turns pixels "significantly" different from its surrounding to the mean of surrounding. The level of significance is determined by k.
def sig_dif_filter(img, k=2):
    #img_cxmean=np.zeros(img.shape)
    #img_cxstd=np.zeros(img.shape)
    result=copy.deepcopy(img)
    surrounding=np.zeros([8,img.shape[0],img.shape[1]])
    #saving surrounding pixels as a vector
    kernel=np.array([[0.7071,0,0],[0,0.2029,0],[0,0,0]])
    surrounding[0]=convolve(img, weights=kernel)
    kernel=np.array([[0,1,0],[0,0,0],[0,0,0]])
    surrounding[1]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0.7071],[0,0.2029,0],[0,0,0]])
    surrounding[2]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[1,0,0],[0,0,0]])
    surrounding[3]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[0,0,1],[0,0,0]])
    surrounding[4]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[0,0.2029,0],[0.7071,0,0]])
    surrounding[5]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[0,0,0],[0,1,0]])
    surrounding[6]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[0,0.2029,0],[0,0,0.7071]])
    surrounding[7]=convolve(img, weights=kernel)

    surrounding_mean = np.mean(surrounding, axis=0)
    abs_dif = abs(result-surrounding_mean)
    surrounding_std = np.std(surrounding, axis=0)
    swap_judge = abs_dif > k*surrounding_std
    result[swap_judge] = surrounding_mean[swap_judge]

    return(result, swap_judge)


#This is a upgraded version of sig_dif_filter
def sig_dif_filter_v2(img, lv2_thres, k1=2, k2=1):
    result=copy.deepcopy(img)
    surrounding=np.zeros([8,img.shape[0],img.shape[1]])
    #saving surrounding pixels as a vector
    kernel=np.array([[0.7071,0,0],[0,0.2029,0],[0,0,0]])
    surrounding[0]=convolve(img, weights=kernel)
    kernel=np.array([[0,1,0],[0,0,0],[0,0,0]])
    surrounding[1]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0.7071],[0,0.2029,0],[0,0,0]])
    surrounding[2]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[1,0,0],[0,0,0]])
    surrounding[3]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[0,0,1],[0,0,0]])
    surrounding[4]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[0,0.2029,0],[0.7071,0,0]])
    surrounding[5]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[0,0,0],[0,1,0]])
    surrounding[6]=convolve(img, weights=kernel)
    kernel=np.array([[0,0,0],[0,0.2029,0],[0,0,0.7071]])
    surrounding[7]=convolve(img, weights=kernel)

    surrounding_mean = np.mean(surrounding, axis=0)
    surrounding_std = np.std(surrounding, axis=0)
    dif_map = result-surrounding_mean

    adjusted_threshold=k1*surrounding_std*(img>lv2_thres) + k2*surrounding_std*(img<=lv2_thres)
    swap_judge = (np.absolute(dif_map) > adjusted_threshold)*(img<=lv2_thres) + (dif_map > adjusted_threshold)*(img>lv2_thres)
    result[swap_judge] = surrounding_mean[swap_judge]
    return(result, swap_judge)


#This is the 3d version of significant difference filter - but the kernel is 2d, because unit of x,y and z are equal, and pixels at adjacent layer have very low relavence to target pixel.
def sig_dif_filter_3d(img, k=2):
    result = np.zeros(img.shape)
    swap_judge = np.zeros(img.shape)
    for i in range(img.shape[0]):
        result[i,:,:], swap_judge[i,:,:] = sig_dif_filter(img[i,:,:],k=k)
    return(result, swap_judge)


#This is upgraded version of 3D v2
def sig_dif_filter_3d_v2(img, lv2_thres, k1=2, k2=1):
    result = np.zeros(img.shape)
    swap_judge = np.zeros(img.shape, dtype = 'int8')
    for i in range(img.shape[0]):
        result[i,:,:], swap_judge[i,:,:] = sig_dif_filter_v2(img[i,:,:], lv2_thres=lv2_thres, k1=k1, k2=k2)
    return(result, swap_judge)


def kernel_scaler_3x3 (kernel, k):
    result=np.zeros(kernel.shape)
    result[0] = k*kernel[0]
    result[1] = (1-k)*kernel[0] + kernel[1] + (1-k)*kernel[2]
    result[2] = k*kernel[2]
    return (result)

def scharr_3d (img, xy_unit, z_unit):
    k = xy_unit/z_unit

    #Note: the default demension order of np.array is Z(depth), X(height), Y(width); this is different from Matlab(X, Y, Z)
    kernel_stack = np.array([[[9,30,9],[30,100,30],[9,30,9]],
                         [[0,0,0],[0,0,0],[0,0,0]],
                         [[-9,-30,-9],[-30,-100,-30],[-9,-30,-9]]])
    kernel_stack = kernel_scaler_3x3(kernel_stack, k=k)
    kernel_h = np.array([[[9,30,9],[0,0,0],[-9,-30,-9]],
                         [[30,100,30],[0,0,0],[-30,-100,-30]],
                         [[9,30,9],[0,0,0],[-9,-30,-9]]])
    kernel_h = kernel_scaler_3x3(kernel_h, k=k)
    kernel_w = np.array([[[9,0,-9],[30,0,-30],[9,0,-9]],
                         [[30,0,-30],[100,0,-100],[30,0,-30]],
                         [[9,0,-9],[30,0,-30],[9,0,-9]]])
    kernel_w = kernel_scaler_3x3(kernel_w, k=k)

    grad_h = convolve(img, weights = kernel_h)/256
    grad_w = convolve(img, weights = kernel_w)/256
    grad_stack = convolve(img, weights = kernel_stack)/256

    img_grad=((grad_h**2+grad_w**2+grad_stack**2)/3)**0.5
    return(img_grad)

def gaussian_scaled (img, xy_unit, z_unit, sigma=0.5, truncate=1):
    k = xy_unit/z_unit
    kernel = np.zeros([3,3,3])
    kernel[1,1,1]=1
    kernel = gaussian(kernel, sigma = sigma, truncate = truncate, channel_axis = None)
    kernel = kernel_scaler_3x3(kernel, k = k)
    return (convolve(img, weights = kernel))

def g_thres_para_3D (scaling_factor):
    if(scaling_factor<1):
        print('error: scaling_factor < 1')
    elif((scaling_factor>=1) & (scaling_factor<2)):
        k_miu = 0.0436*scaling_factor**4 - 0.3039*scaling_factor**3 + 0.7974*scaling_factor**2 - 0.9126*scaling_factor + 0.9838
        k_sigma = 0.0591*scaling_factor**4 - 0.4004*scaling_factor**3 + 1.0045*scaling_factor**2 - 1.0648*scaling_factor + 0.6601
    elif(scaling_factor>=2):
        k_miu = 0.0003*scaling_factor**3 - 0.0059*scaling_factor**2 + 0.0428*scaling_factor + 0.55
        k_sigma = 0.0008*scaling_factor**3 - 0.0122*scaling_factor**2 + 0.0711*scaling_factor + 0.1919
    return(k_miu, k_sigma)

def sgConv_3D (sigma_cbg, width20, scaling_factor, model = 'multilinear'):
    k_miu, k_sigma = g_thres_para_3D (scaling_factor = scaling_factor)
    miu_g = k_miu*sigma_cbg
    sigma_g = k_sigma*sigma_cbg
    if (model == 'multilinear'):
        a1 = -17.231
        a2 = 37.554
        a3 = 0.12504
        grad_thres = a1*miu_g + a2*sigma_g + a3*width20
    elif (model == 'interaction'):
        grad_thres = miu_g + 1.07629*(sigma_cbg**0.503)/(width20**0.625)*sigma_g
    else:
        print('error: model must be "multilinear" or "interaction"')
    return (grad_thres)

def sgConv_2D (sigma_cbg, mode = 'standard'):
    pred_grad_mean = sigma_cbg * 0.854234
    pred_grad_std = sigma_cbg * 0.446927
    if(mode == 'standard'):
        k = sigma_cbg * 0.034876
    elif(mode == 'conservative'):
        k = sigma_cbg * 0.040018
    else:
        print('mode should be either standard or conservative')
    grad_thres = pred_grad_mean + k*pred_grad_std
    return (grad_thres)

def pL_4 (img):
    global pL
    global saved_img_shape
    global saved_pL_type

    row=[]
    col=[]
    value=[]
    for n in range(len(img.flatten())):
        count=0
        i=int(n/img.shape[1])
        j=n%img.shape[1]
        if(j>=1):
            row.extend([n])
            col.extend([img.shape[1]*i+j-1])
            value.extend([-1])
            count+=1
        if(j<=(img.shape[1]-2)):
            row.extend([n])
            col.extend([img.shape[1]*i+j+1])
            value.extend([-1])
            count+=1
        if(i>=1):
            row.extend([n])
            col.extend([img.shape[1]*(i-1)+j])
            value.extend([-1])
            count+=1
        if(i<=(img.shape[0]-2)):
            row.extend([n])
            col.extend([img.shape[1]*(i+1)+j])
            value.extend([-1])
            count+=1
        row.extend([n])
        col.extend([img.shape[1]*i+j])
        value.extend([count])

    pL=coo_matrix((value, (row, col)), shape=(img.shape[0]*img.shape[1], img.shape[0]*img.shape[1]))
    saved_img_shape = img.shape
    saved_pL_type = 'pL_4'
    print('current image shape and type for laplacian matrix:', saved_img_shape, saved_pL_type)
    return(pL)

def pL_8 (img):
    global pL
    global saved_img_shape
    global saved_pL_type

    row=[]
    col=[]
    value=[]
    for n in range(len(img.flatten())):
        count=0
        i=int(n/img.shape[1])
        j=n%img.shape[1]
        up = (i>=1)
        down = (i<=(img.shape[0]-2))
        left = (j>=1)
        right = (j<=(img.shape[1]-2))

        if(left):
            row.extend([n])
            col.extend([img.shape[1]*i+j-1])
            value.extend([-1])
            count+=1
        if(right):
            row.extend([n])
            col.extend([img.shape[1]*i+j+1])
            value.extend([-1])
            count+=1
        if(up):
            row.extend([n])
            col.extend([img.shape[1]*(i-1)+j])
            value.extend([-1])
            count+=1
        if(down):
            row.extend([n])
            col.extend([img.shape[1]*(i+1)+j])
            value.extend([-1])
            count+=1
        if(up & left):
            row.extend([n])
            col.extend([img.shape[1]*(i-1)+j-1])
            value.extend([-0.7071])
            count+=(0.7071)
        if(up & right):
            row.extend([n])
            col.extend([img.shape[1]*(i-1)+j+1])
            value.extend([-0.7071])
            count+=(0.7071)
        if(down & left):
            row.extend([n])
            col.extend([img.shape[1]*(i+1)+j-1])
            value.extend([-0.7071])
            count+=(0.7071)
        if(down & right):
            row.extend([n])
            col.extend([img.shape[1]*(i+1)+j+1])
            value.extend([-0.7071])
            count+=(0.7071)

        row.extend([n])
        col.extend([img.shape[1]*i+j])
        value.extend([count])
    pL = coo_matrix((value, (row, col)), shape=(img.shape[0]*img.shape[1], img.shape[0]*img.shape[1]))
    pL = pL*4/6.8284 # this normalize pL to pL_4 to make effect of K identical
    saved_img_shape = img.shape
    saved_pL_type = 'pL_8'
    print('current image shape and type for laplacian matrix:', saved_img_shape, saved_pL_type)
    return(pL)


#Create 6-connection laplacian matrix(3D). Note: pL is a GLOBAL variable!!!!!
@nb.njit
#pL_internal_calculate is used to generate sparse matrix data for pL_6 with accelerated speed using numba
def pL_internal_calculate (size_h, size_w, stack_num, xy_unit, z_unit):
    k = xy_unit/z_unit
    size_stack=size_h*size_w
    total_pixel = size_stack * stack_num
    row=np.zeros(size_stack*stack_num*7)
    col=np.zeros(size_stack*stack_num*7)
    value=np.zeros(size_stack*stack_num*7)
    mi=-1

    for n in range(total_pixel):
        count=0
        i=int(n/size_stack)
        ii=int((n%size_stack)/size_w)
        iii=n%size_w

        if(i>=1):
            mi+=1
            row[mi]=n
            col[mi]=(i-1)*size_stack + ii*size_w + iii
            value[mi]=-k
            count+=k
        if(i<=(stack_num-2)):
            mi+=1
            row[mi]=n
            col[mi]=(i+1)*size_stack + ii*size_w + iii
            value[mi]=-k
            count+=k
        if(ii>=1):
            mi+=1
            row[mi]=n
            col[mi]=i*size_stack + (ii-1)*size_w + iii
            value[mi]=-1
            count+=1
        if(ii<=(size_h-2)):
            mi+=1
            row[mi]=n
            col[mi]=i*size_stack + (ii+1)*size_w + iii
            value[mi]=-1
            count+=1
        if(iii>=1):
            mi+=1
            row[mi]=n
            col[mi]=i*size_stack + ii*size_w + iii-1
            value[mi]=-1
            count+=1
        if(iii<=(size_w-2)):
            mi+=1
            row[mi]=n
            col[mi]=i*size_stack + ii*size_w + iii+1
            value[mi]=-1
            count+=1
        mi+=1
        row[mi]=n
        col[mi]=i*size_stack + ii*size_w + iii
        value[mi]=count

    row=row[0:mi+1]
    col=col[0:mi+1]
    value=value[0:mi+1]
    return(row,col,value)


def pL_6 (img, xy_unit, z_unit):
    #building matrix pL
    global pL
    global saved_img_shape
    size_h=img.shape[1]
    size_w=img.shape[2]
    stack_num=img.shape[0]
    row,col,value = pL_internal_calculate (size_h=size_h, size_w=size_w, stack_num=stack_num, xy_unit=xy_unit, z_unit=z_unit)
    pL=coo_matrix((value, (row, col)), shape=(stack_num*size_h*size_w, stack_num*size_h*size_w))
    saved_img_shape = img.shape
    print('current image shape and type for laplacian matrix:', saved_img_shape, 'pL_6(3D)')
    return(pL)

#calculating global threshold by given k and grad_thres by ILEG using linear solver
def ILEG_py (img, k, grad_thres, pL_type, tol=1e-05, x0=None, M=None):
    global pL
    global saved_img_shape
    global saved_pL_type
    current_img_shape = img.shape
    if ((current_img_shape==saved_img_shape)&(pL_type==saved_pL_type)):
        print('Current sample does not need to regenerate laplacian matrix')
    else:
        print('Current image shape is', img.shape)
        print('saved image shape is', saved_img_shape)
        print('generating first laplacian matrix or regenerating laplacian matrix due to change of image size.')
        if(pL_type == 'pL_8'):
            pL = pL_8(img)
        elif(pL_type == 'pL_4'):
            pL = pL_4(img)
        else:
            print('error: please choose pL_8 or pL_4')

    #constructing selection matrix
    row=[]
    col=[]
    value=[]
    temp=scharr(img)
    temp=temp.flatten()
    flt_size=temp.shape[0]
    for i in range(flt_size):
        if (temp[i]>=grad_thres):
            row.extend([i])
            col.extend([i])
            value.extend([1])
    S_matrix=coo_matrix((value, (row, col)), shape=(flt_size, flt_size))
    A=k*pL+S_matrix
    A=coo_matrix(A)
    b=S_matrix*img.flatten()

    print('start solving')
    t0 = time.time()
    result = cg(A=A, b=b, rtol=tol, x0=x0, M=M)
    t1 = time.time()
    total_time = t1-t0
    print('ILEG linear solver parameters generated; solving time:', total_time)
    result = result[0]
    result = np.reshape(result, img.shape)
    return (result)


#calculating global threshold by given k and grad_thres by ILEG using linear solver
def ILEG_py_3d (img, xy_unit, z_unit, k, grad_thres, tol=1e-05, x0=None, M=None):
    global pL
    global saved_img_shape
    current_img_shape = img.shape
    if (current_img_shape==saved_img_shape):
        print('Current sample does not need to regenerate laplacian matrix')
    else:
        print('generating first laplacian matrix or regenerating laplacian matrix due to change of image size.')
        pL=pL_6(img, xy_unit=xy_unit, z_unit=z_unit)

    #constructing selection matrix
    row=[]
    col=[]
    value=[]
    img_grad = scharr_3d(img, xy_unit = xy_unit, z_unit = z_unit)
    img_grad=img_grad.flatten()
    flt_size=img_grad.shape[0]
    for i in range(flt_size):
        if (img_grad[i]>=grad_thres):
            row.extend([i])
            col.extend([i])
            value.extend([1])
    S_matrix=coo_matrix((value, (row, col)), shape=(flt_size, flt_size))

    A=k*pL+S_matrix
    A=coo_matrix(A)
    b=S_matrix*img.flatten()

    print('ILEG linear solver parameters generated; start solving by CPU; this may be very slow (~5min)')
    t0 = time.time()
    result = cg(A=A, b=b, rtol=tol, x0=x0, M=M)
    t1 = time.time()
    total_time = t1-t0
    print('solving time:', total_time)
    result = result[0]
    result = np.reshape(result, img.shape)
    return (result)

def ILEE_matlab_3D (img_pp, xy_unit, z_unit, k, grad_thres, temp_directory, tol = 1e-05, use_GPU = False):
    global eng
    img_grad = scharr_3d(img_pp, xy_unit=xy_unit, z_unit=z_unit)
    scipy.io.savemat(file_name = (temp_directory + 'temp_ILEE_input.mat'),
                     mdict = {'img_pp_flt' : img_pp.flatten(), 'img_grad_flt' : img_grad.flatten()})
    output_file = eng.ILEE_matlab_3D(temp_directory,
                                     img_pp.shape[0], img_pp.shape[1], img_pp.shape[2],
                                     xy_unit, z_unit, k, float(grad_thres),
                                     tol, use_GPU)
    local_thres_flt = scipy.io.loadmat(output_file)['result_flt']
    return (np.reshape(local_thres_flt, img_pp.shape))

def interpolation3d_blocking(img_dif, scale = 3, w_block = 66, output_binary = True):
    nz = img_dif.shape[0]
    nx = img_dif.shape[1]
    ny = img_dif.shape[2]
    interpolater = interp3d([0,0,0], [nz-1, nx-1, ny-1], [1,1,1], img_dif, k = 3)
    if(output_binary):
        result = np.zeros((img_dif.shape[0]*scale, img_dif.shape[1]*scale, img_dif.shape[2]*scale), dtype='uint8')
    else:
        result = np.zeros((img_dif.shape[0]*scale, img_dif.shape[1]*scale, img_dif.shape[2]*scale))
    extend = (1/scale)*(scale-1)/2
    indexes_z = np.linspace(-extend, nz-1+extend, num = nz*scale, endpoint = True)
    indexes_x = np.linspace(-extend, nx-1+extend, num = nx*scale, endpoint = True)

    i = -1
    not_end = True
    while(not_end):
        i+=1
        left = i*w_block
        right = (i+1)*w_block
        if(right>=ny):
            not_end = False
            right = ny
        indexes_y = np.linspace(left-extend, right-1+extend, num = (right-left)*scale, endpoint = True)
        crd_z, crd_x, crd_y = np.meshgrid(indexes_z, indexes_x, indexes_y, indexing='ij', copy = False) #copy = False, please remember that we directly use the original memory address of the linspace
        #block_result, block_result_f = interpolater(crd_z, crd_x, crd_y)
        if(output_binary):
            block_result = interpolater(crd_z, crd_x, crd_y)[0]
        else:
            block_result = interpolater(crd_z, crd_x, crd_y)[1]
        #print(left, right, 'done')
        result[:,:,(left*3):(right*3)] = block_result

    return(result)


#return element size map: each pixel equals to the size of the elment it belongs to
def element_size(binary_img):
    labeled_img = label(binary_img, connectivity=2)
    labeled_img_flt = labeled_img.flatten()
    result = np.zeros(labeled_img_flt.shape)
    size_list = np.unique(labeled_img_flt, return_counts=True)
    size_list[1][0]=0 #negative element will not have value
    for i in range(result.shape[0]):
        result[i] = size_list[1][labeled_img_flt[i]]
    result = np.reshape(result, (binary_img.shape))
    return(result)


#calculate the total length of a skeleton image (binary).
def total_length (img_sk):
    kernel=np.array([[0.7071,0.5,0.7071],[0.5,0,0.5],[0.7071,0.5,0.7071]])
    length_by_pix = convolve(img_sk.astype('float'), weights=kernel, mode='constant', cval=0)
    length_by_pix = length_by_pix*img_sk
    return (np.sum(length_by_pix))

#calculate the total length of a skeleton image (binary).

def total_length_3d (img_sk):
    kernel = np.array([[[0.866,0.7071,0.866],[0.7071,0.5,0.7071],[0.866,0.7071,0.866]],
                         [[0.7071,0.5,0.7071],[0.5,0,0.5],[0.7071,0.5,0.7071]],
                         [[0.866,0.7071,0.866],[0.7071,0.5,0.7071],[0.866,0.7071,0.866]]])

    length_by_pix = convolve(img_sk.astype('float'), weights=kernel, mode='constant', cval=0)
    length_by_pix = length_by_pix*img_sk
    return(np.sum(length_by_pix))


@nb.njit
def compute_point_DT_on_plane (img, sn, h, w, target_plane):
    r = 0
    r_max = 10000
    current_DT = 10000
    while(r < r_max):
        kh_start = h-r
        if (kh_start<0): kh_start=0
        kh_end = h+r+1
        if (kh_end>img.shape[1]): kh_end=img.shape[1]
        kw_start = w-r
        if (kw_start<0): kw_start=0
        kw_end = w+r+1
        if (kw_end>img.shape[2]): kw_end=img.shape[2]
        kh_end_idx=kh_end-1
        kw_end_idx=kw_end-1
        #DT on current plane
        #fix h
        for kw in range (kw_start, kw_end):
            if (img[target_plane, kh_start, kw]==0):
                temp_DT = ((kh_start-h)**2 + (kw-w)**2 + (target_plane-sn)**2)**0.5
                if (temp_DT<current_DT): current_DT = temp_DT
            if (img[target_plane, kh_end_idx, kw]==0):
                temp_DT = ((kh_end_idx-h)**2 + (kw-w)**2 + (target_plane-sn)**2)**0.5
                if (temp_DT<current_DT): current_DT = temp_DT
                #fix w
        for kh in range (kh_start+1, kh_end-1):
            if (img[target_plane, kh, kw_start]==0):
                temp_DT = ((kh-h)**2 + (kw_start-w)**2 + (target_plane-sn)**2)**0.5
                if (temp_DT<current_DT): current_DT = temp_DT
            if (img[target_plane, kh, kw_end_idx]==0):
                temp_DT = ((kh-h)**2 + (kw_end_idx-w)**2 + (target_plane-sn)**2)**0.5
                if (temp_DT<current_DT): current_DT = temp_DT
        r_max = current_DT
        r+=1
    return(current_DT)

@nb.njit
def compute_point_DT_in_space (img, sn, h, w, sn_size):
    current_DT = compute_point_DT_on_plane (img=img, sn=sn, h=h, w=w, target_plane=sn)
    sn_ext=1
    while(sn_ext < current_DT):
        top = sn-sn_ext
        if(top>=0):
            temp_DT = compute_point_DT_on_plane(img=img, sn=sn, h=h, w=w, target_plane = top)
            if (temp_DT<current_DT): current_DT = temp_DT
        bot = sn+sn_ext
        if(bot<sn_size):
            temp_DT = compute_point_DT_on_plane (img=img, sn=sn, h=h, w=w, target_plane = bot)
            if (temp_DT<current_DT): current_DT = temp_DT
        sn_ext+=1
    return (current_DT)


@nb.njit (parallel=True)
def average_DT_low_memory(img_binary, img_sk):
    sn_size, h_size, w_size = img_binary.shape
    n = int(np.sum(img_binary))
    data = np.zeros((5, n)) #0 means sn, 1 means h, 2 means w, 3 means whether on skeleton, and 4 means DT value
    i = -1
    for sn in range(sn_size):
        for h in range(h_size):
            for w in range(w_size):
                if(img_binary[sn,h,w]>0):
                    i+=1
                    data[0,i] = sn
                    data[1,i] = h
                    data[2,i] = w
                    #print(sn,h,w,i)
                    if(img_sk[sn,h,w]>0):
                        data[3,i] = 1
    for i in nb.prange(n):
        data[4,i] = compute_point_DT_in_space(img = img_binary, sn = int(data[0,i]), h = int(data[1,i]), w = int(data[2,i]), sn_size = sn_size)

    ave_all = np.mean(data[4,:])
    std_all = np.std(data[4,:])
    data_sk = data[4,:][data[3]>0]
    ave_sk = np.mean(data_sk)
    std_sk = np.std(data_sk)
    return(ave_all, std_all, ave_sk, std_sk)

@nb.njit
def anisotropy_2d_internal(shape,adj,point_list,radius,box_size):
    '''
    INPUT:
    -shape: size of the sample
    -adj: adjancy matrix of the graph
    -point_list:all the points on the skeleton
    -radius: search radius
    -box_size: sampling density

    OUTPUT
    -eigvec_list: eigenvectors of the tangent tensor at each sample point
    -eigval_list: eigenvalues of the tangent tensor at each sample point
    '''
    size_r = int(shape[0]/box_size) + 1
    size_c = int(shape[1]/box_size) + 1

    total_length_list = np.zeros((size_r,size_c))
    coor_list = np.zeros((size_r,size_c,2))
    eigval_list = np.zeros((size_r,size_c,2))
    eigvec_list = np.zeros((size_r,size_c,2,2))

    threshold = radius * radius

    for i in range(size_r):
            for j in range(size_c):
                sample_point = np.array([i*box_size,j*box_size])
                neighbor = []

                for point_index in range(len(point_list)):
                    point = point_list[point_index]
                    distance = (sample_point[0] - point[0])**2 + (sample_point[1] - point[1])**2

                    if distance < threshold:
                        neighbor.append(point_index)

                total_length = 0
                total_tensor = np.zeros((2,2))
                for neighbor_point in neighbor:
                    #csr adj matrix, replaced by nbgraph
                    #edge_point_list = adj.getrow(neighbor_point)
                    #idx_list = edge_point_list.indices
                    #data = edge_point_list.data

                    idx_list = adj.neighbors(neighbor_point)
                    for k in range(len(idx_list)):
                        idx = idx_list[k]
                        if idx > neighbor_point:
                            #upper triangular matrix, avoid to count edges twice
                            #get the tangent tensor for each edge
                            gradient = point_list[idx] - point_list[neighbor_point]
                            gradient = gradient.astype('float')

                            #2d gradient
                            '''
                            gradient[0] = 0
                            if gradient[1] == 0 and gradient[2] == 0:
                                continue
                            '''
                            #L2 norm
                            gradient = gradient/np.linalg.norm(gradient)
                            gradient1 = gradient.reshape(-1,1)
                            tensor = np.outer(gradient,gradient1)
                            #weighted average
                            edge_length = adj.edge(neighbor_point,idx)
                            tensor = tensor * edge_length
                            total_length = total_length + edge_length
                            total_tensor = total_tensor + tensor

                if(total_length == 0):
                    eigvals = np.zeros(2)
                    eigvecs = np.zeros((2,2))
                else:
                    #ave_tensor = total_tensor/total_length
                    eigvals, eigvecs = np.linalg.eig(total_tensor)
                    idx = eigvals.argsort()[::-1]
                    eigvals = eigvals[idx]
                    eigvecs = eigvecs[:, idx]

                total_length_list[i,j] = total_length
                coor_list[i,j] = sample_point
                eigval_list[i,j] = eigvals
                eigvec_list[i,j] = eigvecs

    return (eigval_list, eigvec_list, total_length_list, coor_list)

def analyze_anisotropy_2d (img_sk, radius = 90, box_size = 45, weighting_method = 'by_length', return_box_data = False):
    sk_data = skan.Skeleton(img_sk)
    adj = sk_data.nbgraph
    point_list = sk_data.coordinates
    shape_tuple = img_sk.shape
    eigval, eigvec, box_total_length, coor_list = anisotropy_2d_internal(shape = shape_tuple, adj = adj, point_list = point_list, radius = radius, box_size = box_size)
    box_anisotropy = np.abs(eigval[:,:,0] - eigval[:,:,1])

    if (weighting_method == 'by_length'):
        total_length = np.sum(box_total_length)
        anisotropy = np.sum(box_anisotropy) / total_length
    elif(weighting_method == 'equal_box'):
        box_anisotropy_flt = box_anisotropy[box_total_length!=0]
        box_total_length_flt = box_total_length[box_total_length!=0]
        box_anisotropy_flt = box_anisotropy_flt / box_total_length_flt
        anisotropy = np.mean(box_anisotropy_flt)
    else:
        print ('Warining: wrong input of weighting_method; cannot calculate')

    if (return_box_data):
        return(anisotropy, coor_list, eigval, eigvec, box_total_length, box_anisotropy)
    else:
        return(anisotropy)

@nb.njit
def anisotropy_3d_internal(shape, adj,point_list, radius, box_size):
    depth_num = shape[0]
    row_num = shape[1]
    col_num = shape[2]
    size_r = int(row_num / box_size) + 1
    size_c = int(col_num / box_size) + 1
    size_d = int(depth_num / box_size) + 1
    threshold = radius * radius

    total_length_list = np.zeros((size_d, size_r, size_c))
    coor_list = np.zeros((size_d, size_r, size_c, 3))
    eigval_list = np.zeros((size_d, size_r, size_c, 3))
    eigvec_list = np.zeros((size_d, size_r, size_c, 3, 3))

    for d in range(size_d):
        for i in range(size_r):
            for j in range(size_c):

                sample_point = np.array([d * box_size, i * box_size, j * box_size])
                neighbor = []

                for point_index in range(len(point_list)):

                    point = point_list[point_index]
                    # searching region is a cylinder
                    distance = (sample_point[0] - point[0]) ** 2 + (sample_point[1] - point[1]) ** 2 + (
                                sample_point[2] - point[2]) ** 2

                    if distance < threshold:
                        neighbor.append(point_index)

                total_length = 0
                total_tensor = np.zeros((3, 3))
                for neighbor_point in neighbor:
                    # csr adj matrix, replaced by nbgraph
                    # edge_point_list = adj.getrow(neighbor_point)
                    # idx_list = edge_point_list.indices
                    # data = edge_point_list.data

                    idx_list = adj.neighbors(neighbor_point)

                    for k in range(len(idx_list)):
                        idx = idx_list[k]
                        if idx > neighbor_point:
                            # upper triangular matrix, avoid to count edges twice
                            # get the tangent tensor for each edge
                            gradient = point_list[idx] - point_list[neighbor_point]
                            gradient = gradient.astype('float')

                            # 2d gradient
                            '''
                            gradient[0] = 0
                            if gradient[1] == 0 and gradient[2] == 0:
                                continue
                            '''
                            # L2 norm
                            gradient = gradient/np.linalg.norm(gradient)
                            gradient1 = gradient.reshape(-1, 1)
                            tensor = np.outer(gradient, gradient1)
                            # weighted average
                            edge_length = adj.edge(neighbor_point, idx)
                            tensor = tensor * edge_length
                            total_length = total_length + edge_length
                            total_tensor = total_tensor + tensor

                if (total_length == 0):
                    eigvals = np.zeros(3)
                    eigvecs = np.zeros((3, 3))
                else:
                    #ave_tensor = total_tensor / total_length
                    eigvals, eigvecs = np.linalg.eig(total_tensor)
                    idx = eigvals.argsort()[::-1]
                    eigvals = eigvals[idx]
                    eigvecs = eigvecs[:, idx]

                total_length_list[d, i, j] = total_length
                eigval_list[d, i, j] = eigvals
                eigvec_list[d, i, j] = eigvecs
                coor_list[d,i,j] = sample_point

    return  eigval_list, eigvec_list, total_length_list, coor_list


def analyze_anisotropy_3d(img_sk, radius = 30, box_size = 15, weighting_method = 'by_length', return_box_data = False):
    sk_data = skan.Skeleton(img_sk)
    adj = sk_data.nbgraph
    point_list = sk_data.coordinates
    shape_tuple = img_sk.shape
    eigval, eigvec, box_total_length, coor_list = anisotropy_3d_internal(shape=shape_tuple, adj=adj, point_list=point_list,
                                                              radius=radius, box_size=box_size)
    a = eigval[:, :, : , 0] - eigval[:, :, :, 1]
    b = eigval[:, :, : , 0] - eigval[:, :, :, 2]
    c = eigval[:, :, : , 1] - eigval[:, :, :, 2]
    box_anisotropy = (a**2 + b**2 + c**2)**0.5

    if (weighting_method == 'by_length'):
        total_length = np.sum(box_total_length)
        anisotropy = np.sum(box_anisotropy) / total_length
    elif(weighting_method == 'equal_box'):
        box_anisotropy_flt = box_anisotropy[box_total_length!=0]
        box_total_length_flt = box_total_length[box_total_length!=0]
        box_anisotropy_flt = box_anisotropy_flt / box_total_length_flt
        anisotropy = np.mean(box_anisotropy_flt)
    else:
        print ('Warining: wrong input of weighting_method; cannot calculate')

    if (return_box_data):
        return(anisotropy, coor_list, eigval, eigvec, box_total_length, box_anisotropy)
    else:
        return(anisotropy)



## estimating K2--------------------------------------------------------------
def opt_k2(folder_path, target_channel = None):
    '''
    This functions calculates the optimal K2 for a batch of samples (raw TIFF files) to be analyzed. Please include all samples from different groups to be compared into the same document.

    Parameters
    ----------
    folder_path : string,
        a local path of your image samples. The final document name should contain an "/" in the end, for example, folder_path = 'D:/experiment/all my samples/'
    target_channel : int, optional
        It should be an given int for most of the situations. If your raw TIFF file does not have the channel demension (which is a rare case, please use default)
    Returns K2
    ----------
    '''
    print ('starting estimating K2...')
    estimated_max_DT = []
    files_name_array = os.listdir(folder_path)
    samples_path=[]
    for i in files_name_array:
        if i.endswith(".tif"):
            samples_path.append(folder_path+'/'+i)
    for current_path in samples_path:
        print (current_path)
        img = io.imread(current_path)
        img = rearrange_image_dimension(img, target_channel = target_channel)
        img = np.amax(img, axis=0)
        img = img-img.min()
        img = img.astype('float')

        l = (img.shape[0]**2+img.shape[1]**2)**0.5
        window_size = int(l/(32*1.414))*2+1
        coarse_local_thres = threshold_niblack(img, window_size = window_size, k=-0.36)
        coarse_distance_map = distance_transform_edt(img>coarse_local_thres)
        values = coarse_distance_map[coarse_distance_map>0].flatten()
        values = np.sort(values)
        values = values[::-1]
        n = values.shape[0]
        ave_DT = np.mean(values[0:int(n/50)])

        estimated_max_DT.append(ave_DT)
        print('current sample done, next...')

    DT = np.mean(estimated_max_DT)
    k2 = 10**(1.8686*np.log(DT) + 0.0681)
    print('K2 estimation finished')
    return(k2)


##calculation-----------------------------------------------------------------
def ILEE_2d (img, k2, k1 = 2.5, pL_type = 'pL_8', gauss_dif = True):
    '''

    In 2D mode, generate a difference image (raw_image - threshold_image) as ILEE output for downstream analysis or visualization.

    Parameters
    ----------
    img :
    2D array, an image of z-axis maximum projection of your target channel or the 2D "raw" image. If it is not float, may have processing error.
    k2 :
    a number; should be your pre-determined optimal K2 for comparison purpose.
    k1 :
    The default is 2.5, which can identify one-pixel-size filament.
    pL_type :
    string. The default is 'pL_8'.
    gauss_dif :
    Bool, default is True; whether the difference image is gaussian-blurred slightly for smoother render

    Returns
    -------
    float 2D array, the rendered 2D difference image.

    '''
    print('starting pre-processing the sample...')
    img_pp, marks = sig_dif_filter(img, k=2) #need to provide data
    img_pp = gaussian(img_pp, sigma = 0.5, truncate = 1, channel_axis = None)
    NE_peak_value = NE_peak(img)
    coarse_bg_data = img_pp[img < (1.163*NE_peak_value+101.68)]
    sigma_cbg = np.std(coarse_bg_data)
    grad_thres = sgConv_2D(sigma_cbg = sigma_cbg, mode = 'conservative')
    print('Start generating local threshold using ILEE...')
    local_thres1 = ILEG_py(img_pp, grad_thres = grad_thres, pL_type = 'pL_8', k = k1) # optimized value to distinguish thinnest actin
    local_thres2 = ILEG_py(img_pp, grad_thres = grad_thres, pL_type = 'pL_8', k = k2)
    local_thres = local_thres1*(local_thres1<local_thres2) + local_thres2*(local_thres1>=local_thres2)
    print('starting post-processing the sample...')
    dif_map = img_pp-local_thres
    element_size_map = element_size(dif_map>0)
    default_negative = np.mean(dif_map[dif_map<0])
    dif_map[(element_size_map>0)&(element_size_map<=3)] = default_negative
    if(gauss_dif):
        dif_map = gaussian(dif_map, sigma=0.5, truncate=1, channel_axis = None)
    return(dif_map)


def analyze_actin_2d_standard (img, img_dif, pixel_size = 1, exclude_true_blank = False, effective_area = 'calculate_in_this_channel'):
    '''

    Compute all cytoskeleton indices using 2d raw and difference image as input.

    Parameters
    ----------
    img : float 2D array.
        An image of z-axis maximum projection of your target channel or the 2D "raw" image. Values should be transformed into float type with 0-4095 dynamic range. For example, if you have a 12 bit int-type image, as a variable img, then it should be used as img.astype('float'); if you have a 16 bit int-type image, then you should transform img into img2 = img.astype('float')/65535*4095.
    img_dif : float 2D array.
        The difference image (raw_image - threshold_image) generated by ILEE_2d.
    pixel_size : number, optional
        The physical lenghth unit of your pixel, by micrometer (μm). The default is 1. If you set it into the real pixel size, the unit "PU" in your output table should be considered as μm.
    exclude_true_blank : bool, optional
        Whether to activate "exclude_true_blank" mode. This means we will detect regions that are purely blank: no non-fluoresence tissue, just pure blank, and cut off these region when calculating area. This is necessary when you are processing animal cell sample whose image field is not fully covered by the cell. The default is False.
    effective_area : string or , optional
        The effective area used to calculate area-related indices. It can be a string 'calculate_in_this_channel' or a forced number for area of current sample.
    Returns
    -------
    pandas.DataFrame, all cytoskeleton indices of input sample: occupancy, linear_density, skewness, cv, Diameter_tdt, Diameter_sdt, sev_act, branching_act, anisotropy

    '''
    print('start analyzing actin binary image...')
    if(exclude_true_blank):
        if(effective_area == 'calculate_in_this_channel'):
            print('Using exclude_true_blank mode to define cell area...')
            img_area = cell_2D_area(img)
        else:
            print('For current sample, you manually forced the effective area to be', effective_area, '. This value must be a number or the program will fail.')
            img_area = effective_area
    else:
        print ('Using total image as effective area...')
        img_area = img.shape[0]*img.shape[1]
    img_binary_ori_scale = img_dif>0
    occupancy = np.sum(img_binary_ori_scale)/img_area
    onMF_pixs = img[img_binary_ori_scale]
    std_onMF = np.std(onMF_pixs)
    mean_onMF = np.mean(onMF_pixs)
    pixs_skewness = ((onMF_pixs-mean_onMF)/std_onMF)**3
    skewness = np.mean(pixs_skewness)
    cv = std_onMF/mean_onMF

    img_dif_ovsp = resize(img_dif, (img_dif.shape[0]*3, img_dif.shape[1]*3), order = 3)
    img_binary = img_dif_ovsp>0

    DT_map = distance_transform_edt (img_binary)
    mean_DT = np.mean(DT_map[DT_map>0])
    diameter_tdt = 4*(mean_DT-0.5)*pixel_size/3 #"-0.5" aims to correct the boarder error where edge to the neagtive pixel center is 0.5 pix

    img_sk = skeletonize(img_binary).astype('bool')
    mean_DT_sk = np.mean(DT_map[img_sk>0])
    diameter_sdt = 2*(mean_DT_sk-0.5)*pixel_size/3 #"-0.5" aims to correct the boarder error where edge to the neagtive pixel center is 0.5 pix

    MF_full_length = total_length(img_sk.astype('float'))*pixel_size/3 # /3 because interpolated 3 fold
    element_count = label(img_binary, return_num=True, connectivity=2)[1]
    linear_density = MF_full_length / (img_area*pixel_size**2)
    sev_act = element_count / MF_full_length

    branch_data = skan.summarize(skan.Skeleton(img_sk))
    gt_branch_count = branch_data.shape[0]
    all_node_id = np.concatenate((branch_data['node-id-src'], branch_data['node-id-dst']))
    node_branching_list = np.unique(all_node_id, return_counts=True)[1]
    node_count = node_branching_list.shape[0]
    node_branching_list = node_branching_list-2
    branching_act = np.sum(node_branching_list[node_branching_list>0]) / MF_full_length

    anisotropy = analyze_anisotropy_2d (img_sk, radius = 150, box_size = 75, weighting_method = 'by_length', return_box_data = False)

    print('Note: output length unit: pixel unit (PU)')
    df = pd.DataFrame(data = [[occupancy, linear_density, skewness, cv, diameter_tdt, diameter_sdt, sev_act, branching_act, anisotropy]],
                      columns = ['occupancy', 'linear_density (PU/PU^2)', 'skewness', 'cv', 'diameter_tdt (PU)', 'diameter_sdt (PU)', 'segment_density (/PU of filament)', 'branching_act(/PU of filament)', 'anisotropy'])
    df_nsi = pd.DataFrame(data = [[MF_full_length, element_count, node_count, gt_branch_count]],
                      columns = ['total_length', 'total_element', 'total_node', 'total_graph_theoretic_branch'])

    return(df, df_nsi)


def ILEE_3d (img, xy_unit, z_unit, k1, k2, single_k1 = False, use_matlab = False, use_matlabGPU = False, gauss_dif = True, g_thres_model = 'multilinear'):
    '''
    In 3D mode, generate a difference image (raw_image - threshold_image) as ILEE output for downstream analysis or visualization.

    Parameters
    ----------
    img : 3D array
        The input image. Values should be transformed into float type with 0-4095 dynamic range. For example, if you have a 12 bit int-type image, as a variable img, then it should be used as img.astype('float'); if you have a 16 bit int-type image, then you should transform img into img2 = img.astype('float')/65535*4095.
    xy_unit : number
        The unit size of voxel on x- and y-axis by μm. Please check using ImageJ.
    z_unit : number
        The unit size of voxel on z-axis by μm, which is also your step size of stack imaging. Please check using ImageJ.
    k1 : number
        ILEE K1
    k2 : number
        ILEE K2
    single_k1 : bool, optional
        Whether to use single-K mode (use only K1) to save time. The default is False.
    use_matlab : bool, optional
        whether to use MATLAB for ILEE. The default is False.
    use_matlabGPU : bool, optional
        Whether to activate GPU_acceleration in MATLAB. The default is False. If use_matlab is False, this makes no difference.
    gauss_dif : Bool, optional;
        Whether the difference image is gaussian-blurred slightly for smoother render. Default is True.
    g_thres_model: string, choice of either 'multilinear' or 'interaction', default 'multilinear'.
        The model to estimate gradient threshold in 3D mode. Please check our paper [https://doi.org/10.1083/jcb.202203024](https://doi.org/10.1083/jcb.202203024) Fig. S9.

    Returns
    -------
    float 3D array, the rendered 3D difference image, the same shape as input.

    '''
    global temp_directory
    print('starting pre-processing the sample...')

    img_temp_continuous = img + np.random.random(size = img.shape) - 0.5
    NE_peak_value = NE_peak(img = img_temp_continuous)
    pb, pf, lb, rb = call_BD_max (img = img_temp_continuous, subpeak_fold = 0.8)
    width20 = rb - lb
    cbg_thres = 22.1408*(NE_peak_value**1.004)/(width20**0.481)

    img_pp, marks = sig_dif_filter_3d_v2(img, lv2_thres = cbg_thres, k1=3, k2=2)
    img_pp = gaussian_scaled(img_pp, xy_unit=xy_unit, z_unit=z_unit, sigma=0.5, truncate=1)
    coarse_bg_data = img_pp[img < cbg_thres]
    sigma_cbg = np.std(coarse_bg_data)
    grad_thres = sgConv_3D(sigma_cbg = sigma_cbg, width20 = width20, scaling_factor = z_unit/xy_unit, model = g_thres_model)

    if (use_matlab):
        print('starting 3D ILEE using matlab...')
        if (use_matlabGPU):
            print('use GPU acceleration')
        if(single_k1):
            local_thres = ILEE_matlab_3D(img_pp = img_pp, xy_unit = xy_unit, z_unit = z_unit, k = k1, grad_thres = grad_thres, temp_directory = temp_directory, use_GPU = use_matlabGPU)
        else:
            local_thres1 = ILEE_matlab_3D(img_pp = img_pp, xy_unit = xy_unit, z_unit = z_unit, k = k1, grad_thres = grad_thres, temp_directory = temp_directory, use_GPU = use_matlabGPU)
            local_thres2 = ILEE_matlab_3D(img_pp = img_pp, xy_unit = xy_unit, z_unit = z_unit, k = k2, grad_thres = grad_thres, temp_directory = temp_directory, use_GPU = use_matlabGPU)
            local_thres = local_thres1*(local_thres1<local_thres2) + local_thres2*(local_thres1>=local_thres2)
    else:
        print('starting 3D ILEE using Scipy linear solver...; this may take as much as 5 min for single k mode and double for standard mode')
        if(single_k1):
            local_thres = ILEG_py_3d(img_pp, xy_unit = xy_unit, z_unit = z_unit, k = k1, grad_thres = grad_thres)
        else:
            local_thres1 = ILEG_py_3d(img_pp, xy_unit = xy_unit, z_unit = z_unit, k = k1, grad_thres = grad_thres)
            local_thres2 = ILEG_py_3d(img_pp, xy_unit = xy_unit, z_unit = z_unit, k = k2, grad_thres = grad_thres)
            local_thres = local_thres1*(local_thres1<local_thres2) + local_thres2*(local_thres1>=local_thres2)

    dif_map = img_pp-local_thres
    element_size_map = element_size(dif_map>0)
    default_negative = np.mean(dif_map[dif_map<0])
    dif_map[(element_size_map>0)&(element_size_map<=3)] = default_negative
    if(gauss_dif):
        dif_map = gaussian_scaled(dif_map, xy_unit=xy_unit, z_unit=z_unit, sigma=0.5, truncate=1)
    return(dif_map)


def analyze_actin_3d_standard (img, img_dif_ori, xy_unit, z_unit, oversampling_for_bundle = True, pixel_size = 1):
    '''
    Compute all cytoskeleton indices using 3d raw and difference image as input.

    Parameters
    ----------
    img : 3D array.
        The raw image of your object channel as input.
    img_dif_ori : 3D array.
        The difference image as input to define the cytoskeleton components.
    xy_unit : number
        The unit size of voxel on x- and y-axis by μm. Please check using ImageJ.
    z_unit : number
        The unit size of voxel on z-axis by μm, which is also your step size of stack imaging. Please check using ImageJ.
    oversampling_for_bundle : bool, optional
        Whether to use oversampled image to calculated diameter indices. Recommend to turn on for accuracy. The default is True.
    pixel_size : number, optional
        The physical lenghth unit (on x- and y-axis) of your voxel, by micrometer (μm). The default is 1. If you set it into the real pixel size, it should be equal to the parameter xy_unit, and the unit "PU" in your output table should be considered as μm.

    Returns
    -------
    None.

    '''
    print('start analyzing binary image')
    #occupancy, skewness, CV use z-axis-non-corrected img_dif; it is called img_binary_ori_scale in 3d mode.
    img_volume = img_dif_ori.shape[0]*img_dif_ori.shape[1]*img_dif_ori.shape[2]*(pixel_size**3)
    img_binary_ori = img_dif_ori>0
    occupancy = np.sum(img_binary_ori)/(img_dif_ori.shape[0]*img_dif_ori.shape[1]*img_dif_ori.shape[2])
    onMF_pixs = img[img_binary_ori]
    std_onMF = np.std(onMF_pixs)
    mean_onMF = np.mean(onMF_pixs)
    pixs_skewness = ((onMF_pixs-mean_onMF)/std_onMF)**3
    skewness = np.mean(pixs_skewness)
    cv = std_onMF/mean_onMF
    #correct img_dif to unified length unit on xyz
    img_dif_corrected = resize(img_dif_ori, (int(z_unit/xy_unit*img_dif_ori.shape[0]), img_dif_ori.shape[1], img_dif_ori.shape[2]), order=3, mode='symmetric')
    element_size_map = element_size(img_dif_corrected>0)
    default_negative = np.mean(img_dif_corrected[img_dif_corrected<0])
    img_dif_corrected[(element_size_map>0)&(element_size_map<=3)] = default_negative
    img_binary = img_dif_corrected>0
    img_sk = skeletonize(img_binary).astype('bool')

    branch_data = skan.summarize(skan.Skeleton(img_sk))
    gt_branch_count = branch_data.shape[0]
    MF_full_length = np.sum(branch_data['branch-distance']) #in 3D mode, cavities are approximated into the centroids. We have to use skan to count total length because convolution has strong overestimation for cavity.
    element_count = np.max(branch_data['skeleton-id'])
    linear_density = MF_full_length / img_volume
    sev_act = element_count / MF_full_length

    all_node_id = np.concatenate((branch_data['node-id-src'], branch_data['node-id-dst']))
    node_branching_list = np.unique(all_node_id, return_counts=True)[1] #[1] returns only count
    node_count = node_branching_list.shape[0]
    node_branching_list = node_branching_list-2
    branching_act = np.sum(node_branching_list[node_branching_list>0]) / MF_full_length

    anisotropy = analyze_anisotropy_3d(img_sk, radius=50, box_size=25, weighting_method = 'by_length', return_box_data=False)

    if (oversampling_for_bundle):
        print('start oversampling for calculation of physical indexes of bundling class; this may take some time (~1min)')
        img_binary = interpolation3d_blocking(img_dif_corrected, scale = 3, w_block = 66, output_binary = True) # DO NOT make output_binary False unless you have HUUUUUGE memory (32G???) or using a HPC.
        print('start calculating oversampled skeleton; this may take some time (3~5min)')
        img_sk = skeletonize(img_binary).astype('bool')
        print('Done; continue indexes calculation')

    DT_all, DT_all_std, DT_sk, DT_sk_std = average_DT_low_memory(img_binary = img_binary, img_sk = img_sk)
    diameter_tdt =  4 * (DT_all-0.5) * pixel_size # diameter = 2*radius; radius = DT_onSK; "-0.5" aims to correct the boarder error where edge to the neagtive pixel center is 0.5 pix, actually it varies from 0.5 to 0.5*sqrt2; Unit: pixel, or micron if pixel_size != 1
    if (oversampling_for_bundle):
        diameter_tdt = diameter_tdt/3
    diameter_tdt_std = 4 * DT_all_std * pixel_size #no need to -0.5 because it does not change std
    if (oversampling_for_bundle):
        diameter_tdt_std = diameter_tdt_std/3
    diameter_sdt =  2 * (DT_sk-0.5) * pixel_size # diameter = 2*radius; radius = DT_onSK; "-0.5" aims to correct the boarder error where edge to the neagtive pixel center is 0.5 pix, actually it varies from 0.5 to 0.5*sqrt2; Unit: pixel, or micron if pixel_size != 1
    if (oversampling_for_bundle):
        diameter_sdt = diameter_sdt/3
    diameter_sdt_std = 2 * DT_sk_std * pixel_size #no need to -0.5 because it does not change std
    if (oversampling_for_bundle):
        diameter_sdt_std = diameter_sdt_std/3

    df = pd.DataFrame(data = [[occupancy, linear_density, skewness, cv, diameter_tdt, diameter_sdt, sev_act, branching_act, anisotropy]],
                      columns = ['occupancy', 'linear_density (PU/PU^2)', 'skewness', 'cv', 'diameter_tdt (PU)', 'diameter_sdt (PU)', 'segment_density (/PU)', 'branching_act(/PU)', 'local anisotropy'])
    df_nsi = pd.DataFrame(data = [[MF_full_length, element_count, node_count, gt_branch_count]],
                      columns = ['total_length', 'total_element', 'total_node', 'total_graph_theoretic_branch'])

    return(df, df_nsi)


##batch processing------------------------------------------------------------
def analyze_document_2D (folder_path, obj_channel, k2, k1 = 2.5, pixel_size = 1, exclude_true_blank = False, effective_area_data = 'calculate_in_this_channel', include_nonstandarized_index = False):
    '''
    Process and analyze all the raw tiff samples in your document by 2D mode and output the result as a table (dataframe).

    Parameters
    ----------
    folder_path : string, a local path of your image samples.
        The final document name should contain an "/" in the end, for example, folder_path = 'D:/experiment/all my samples/'
    obj_channel : int.
        The channel index of cytoskeleton fluoresence in the 4D array read from raw TIFF
    k2 : number.
        The universal K2. Recommend use the optimal K2 calculated by the function opt_k2
    k1 = number, optional (default 2.5).
        The universal K1. Recommended and default is 2.5.
    pixel_size : number, optional (default 1).
        The physical lenghth unit of your pixel, by micrometer (μm). The default is 1. If you set it into the real pixel size, the unit "PU" in the output table should be regarded as μm.
    exclude_true_blank: bool, optional (default False).
        Whether large blank area will be excluded as "true void". This should only be True if you are using photos of single cells (e.g., single layer animal cell) whose background has nothing, rather than tissues. The performance of this parameter is not tested over massive single cell samples.
    include_nonstandarized_index: bool, optional (default False).
        Whether including output of non-standarized indices which may not be directly used for biological comparison.

    Returns
    -------
    df_result : pandas dataframe, the result
    df_nsi (if include_nonstandarized_index = True) : pandas dataframe, the result of non-standarized indices
        You can process it inside python IDE or export it as excel file.
    '''
    print ('starting analyzing samples in the document...')
    df_result = pd.DataFrame()
    df_nsi = pd.DataFrame()
    file_name_array = os.listdir(folder_path)
    samples_path = []
    tif_name_array = []
    for i in file_name_array:
        if i.endswith(".tif"):
            tif_name_array.append(i)
            samples_path.append(folder_path+'/'+i)

    for i in range(len(samples_path)):
        print ('current objective sample is:', samples_path[i])
        img = io.imread(samples_path[i])
        img = rearrange_image_dimension(img, target_channel = obj_channel)
        img = np.amax(img, axis=0)
        img = img.astype('float')
        img = img-img.min()
        img = (img/img.max())*4095

        img_dif = ILEE_2d(img = img,
                          k1 = k1,
                          k2 = k2)
        if (effective_area_data == 'calculate_in_this_channel'):
            current_effective_area = 'calculate_in_this_channel'
        else:
            current_effective_area = effective_area_data[i]
        new_data = analyze_actin_2d_standard (img = img,
                                             img_dif = img_dif,
                                             pixel_size = pixel_size,
                                             exclude_true_blank = exclude_true_blank,
                                             effective_area = current_effective_area)
        new_row = new_data[0]
        new_row['file_path'] = samples_path[i]
        new_row['file_name'] = tif_name_array[i]
        df_result = pd.concat([df_result, new_row], ignore_index = True)
        new_row_nsi = new_data[1]
        new_row_nsi['file_path'] = samples_path[i]
        new_row_nsi['file_name'] = tif_name_array[i]
        df_nsi = pd.concat([df_nsi, new_row_nsi], ignore_index = True)
        print('current sample done.\n')

    if include_nonstandarized_index:
        return (df_result, df_nsi)
    else:
        return (df_result)


def analyze_document_3D (folder_path, obj_channel, k1, k2, xy_unit, z_unit, pixel_size = 1, single_k1 = True, oversampling_for_bundle = False, use_GPU = False, g_thres_model = 'multilinear', include_nonstandarized_index = False):
    '''

    Process and analyze all the raw tiff samples in your document in 3D mode and output the result as a table (dataframe). Please note that it can be slow if the MATLAB-based GPU acceleration is not available. In 3D mode, K1 = 10^((log10(2.5)+log10(K2))/2).

    Parameters
    ----------
    folder_path : string
        A local path of your image samples. The final document name should contain an "/" in the end, for example, folder_path = 'D:/experiment/all my samples/'
    obj_channel : int
        Your channel index of cytoskeleton fluoresence in the 4D array read from raw TIFF
    k1 : number
        The universal K1 you set. Recommend use optimal_K1 = 10**((np.log10(2.5) + np.log10(optimal_K2))/2)
    k2 : number
        The universal K2 you set. Recommend use the optimal K2 calculated by the function opt_k2
    xy_unit : number
        The unit size of voxel on x- and y-axis by μm. Please check using ImageJ.
    z_unit : number
        The unit size of voxel on z-axis by μm, which is also your step size of stack imaging. Please check using ImageJ.
    pixel_size : number, optional
        The physical lenghth unit (on x- and y-axis) of your voxel, by micrometer (μm). The default is 1. If you set it into the real pixel size, it should be equal to the parameter xy_unit, and the unit "PU" in your output table should be considered as μm.
    single_k1 : bool, optional
        Whether to use single-K mode (use only K1) to save time. The default is True.
    oversampling_for_bundle : Bool, optional
        Whether oversampling when calculating some bundling features. It has VERY high memory consumption.
    use_GPU : bool, optional
        Whether to activate GPU acceleration. We highly recommend you turn it on if you have MATLAB and compatible GPU. The default is False.
    g_thres_model : string, optional. Choose the model of gradient threshold calculation. Must be "multilinear" or "interaction". Please refer to our publication. The default is multilinear.

    Returns
    -------
    df_result : pandas dataframe
        You can process it inside python IDE or export it as excel file.

    '''
    print ('starting analyzing samples in the document...')
    df_result = pd.DataFrame()
    df_nsi = pd.DataFrame()
    file_name_array = os.listdir(folder_path)
    samples_path = []
    tif_name_array = []
    for i in file_name_array:
        if i.endswith(".tif"):
            tif_name_array.append(i)
            samples_path.append(folder_path+'/'+i)

    for i in range(len(samples_path)):
        print ('current objective sample is:', samples_path[i])
        img = io.imread(samples_path[i])
        img = rearrange_image_dimension(img, target_channel = obj_channel)
        img = img.astype('float')
        img = img-img.min()
        img = (img/img.max())*4095

        img_dif = ILEE_3d (img,
                           xy_unit = xy_unit,
                           z_unit = z_unit,
                           k1 = k1,
                           k2 = k2,
                           single_k1 = single_k1,
                           use_matlab = use_GPU,
                           use_matlabGPU = use_GPU,
                           gauss_dif = True,
                           g_thres_model = g_thres_model)
        new_data = analyze_actin_3d_standard (img = img,
                                             img_dif_ori = img_dif,
                                             xy_unit = xy_unit,
                                             z_unit = z_unit,
                                             oversampling_for_bundle = oversampling_for_bundle,
                                             pixel_size = pixel_size)

        new_row = new_data[0]
        new_row['file_path'] = samples_path[i]
        new_row['file_name'] = file_name_array[i]
        df_result = pd.concat([df_result, new_row], ignore_index = True)
        new_row_nsi = new_data[1]
        new_row_nsi['file_path'] = samples_path[i]
        new_row_nsi['file_name'] = file_name_array[i]
        df_nsi = pd.concat([df_nsi, new_row_nsi], ignore_index = True)
        print('current sample done.\n')

    if include_nonstandarized_index:
        return (df_result, df_nsi)
    else:
        return (df_result)


#Data visualization and statistic analysis functions

def visualize_2D_segment_of_tif (file_path, obj_channel, k2, k1 = 2.5, show_oversampled = True, curving_raw = 0.5):
    '''
    Show how ILEE segments a tif image in 2D mode.

    Parameters
    ----------
    folder_path : string
        A local path of your image samples. The final document name should contain an "/" in the end, for example, folder_path = 'D:/experiment/all my samples/'
    obj_channel : int
        Your channel index of cytoskeleton fluoresence in the 4D array read from raw TIFF
    k2 : number
        The universal K2 you set. Recommend use the optimal K2 calculated by the function opt_k2
    k1 : number
        The universal K1 you set. Default is 2.5
    show_oversampled: bool
        Whether show oversampled(in-used) image
    curving_raw: positive number, default 0.5
        For better visualization, convert raw to 0-1 float and powered by this value. If set to 1, show literal raw image, which can be very faint

    Returns
    -------
    Directly show image by plt.
    '''

    img = io.imread(file_path)
    img = rearrange_image_dimension(img, target_channel = obj_channel)
    img = np.amax(img, axis=0)
    img = img.astype('float')
    img = img-img.min()
    img = (img/img.max())*4095
    img_dif = ILEE_2d(img = img,
                      k1 = k1,
                      k2 = k2)
    img_binary = img_dif>0
    img_ovsp = resize(img, (img.shape[0]*3, img.shape[1]*3), order = 3)
    img_dif_ovsp = resize(img_dif, (img_dif.shape[0]*3, img_dif.shape[1]*3), order = 3)
    img_binary_ovsp = img_dif_ovsp>0

    if show_oversampled:
        i1 = img_ovsp/img_ovsp.max()
        i1 = i1**curving_raw
        i2 = np.zeros((img_ovsp.shape[0],img_ovsp.shape[1],4))
        i2[:,:,0] = img_binary_ovsp*1
        i2[:,:,3] = img_binary_ovsp*0.6
    else:
        i1 = img/img.max()
        i1 = i1**curving_raw
        i2 = np.zeros((img.shape[0],img.shape[1],4))
        i2[:,:,0] = img_binary*1
        i2[:,:,3] = img_binary*0.6

    fig, axs = plt.subplots(ncols = 3, figsize=(15, 5), dpi = 300)
    axs[0].set_title('Raw')
    axs[0].imshow(i1, cmap = 'gray_r')
    axs[0].axis('off')
    axs[1].set_title('ILEE')
    axs[1].imshow(i2)
    axs[1].axis('off')
    axs[2].set_title('Merge')
    axs[2].imshow(i1, cmap = 'gray_r')
    axs[2].imshow(i2)
    axs[2].axis('off')

    plt.show()


def visualize_results(df_result):
    #must use the format generated by function analyze_document_2D/3D
    #visualize columns in df_result whose data type is 'float'.
    df_result['group'] = [i.split('-')[0] for i in df_result['file_name']]
    df_result['repeat'] = [(i.split('-')[1]).split('.')[0] for i in df_result['file_name']]

    indices = []
    for col in df_result.columns:
      if (df_result[col].dtype in ['float']):
        indices.append(col)

    sns.set(font_scale = 1.6)
    sns.set_style("ticks")
    n_indices = len(indices)
    n_rows = int(n_indices/3)+((n_indices%3)>0)

    fig, axes = plt.subplots(n_rows, 3, figsize = (5*n_rows, 15))

    for i in range(n_indices):
      g1 = sns.barplot(data = df_result,
                       x = 'group',
                       y = indices[i],
                       ci = 'sd',
                       errwidth = 4,
                       capsize= 0.3,
                       errcolor = 'black',
                       palette = 'deep',
                       ax = axes[int(i/3),i%3])
      g2 = sns.stripplot(data = df_result,
                        x = 'group',
                        y = indices[i],
                        size = 16,
                        edgecolor = 'gray',
                        linewidth = 3,
                        alpha = 0.86,
                        palette = 'dark',
                        ax = axes[int(i/3),i%3])
    fig.tight_layout()
    i+=1
    while(i<n_rows*3):
        axes[int(i/3),i%3].axis('off')
        i+=1
    plt.show()


def multiple_comparison (df, cat_var_column, value_column, p_thres, p_adjust):
    #cat_vars: list of names of columns for categorical variables
    #value: name of (dependent) the numeric variable you want to compare
    result = pd.DataFrame()
    cat_vars = np.unique(df[cat_var_column])
    n = cat_vars.shape[0]

    data = []
    for i in range(n):
        data.append(df[df[cat_var_column] == cat_vars[i]][value_column])
        new_row = pd.DataFrame(columns = ['group','index','n','mean','std'],
                               data = [[cat_vars[i], i, data[i].shape[0], np.mean(data[i]), np.std(data[i])]])
        result = pd.concat([result, new_row], ignore_index = True)
    p_matrix = sp.posthoc_ttest(data, p_adjust = p_adjust)
    p_matrix = np.array(p_matrix)

    result = result.sort_values(by = ['mean'], ascending = False, ignore_index = True)
    result['mark'] = ''

    start=0
    mark=0
    result.at[0, 'mark'] = chr(97+mark)

    while(1):
        for i in range(start + 1, n):
            #print ('forward comparing', start, i, chr(97+mark))
            start_id = result.loc[start]['index']
            i_id = result.loc[i]['index']
            #print(p_matrix[start_id,i_id])
            if (p_matrix[start_id,i_id] > p_thres):
                if (result.at[i, 'mark'] == ''):
                  result.at[i, 'mark'] = result.at[i, 'mark'] + (chr(97+mark))
                elif (result.at[i, 'mark'][-1] != chr(97+mark)):
                  result.at[i, 'mark'] = result.at[i, 'mark'] + (chr(97+mark))
            else:
                mark+=1
                result.at[i, 'mark'] = result.at[i, 'mark'] + (chr(97+mark))
                start = i*1
                #print (i, 'extend', chr(97+mark))
                break
        for ii in range (i-1, 0, -1):
            #print ('backward comparing', i, ii, chr(97+mark))
            ii_id = result.loc[ii]['index']
            i_id = result.loc[i]['index']
            if (p_matrix[ii_id, i_id] > p_thres):
                if (result.at[ii, 'mark'] == ''):
                  result.at[ii, 'mark'] = result.at[ii, 'mark'] + (chr(97+mark))
                elif (result.at[ii, 'mark'][-1] != chr(97+mark)):
                  result.at[ii, 'mark'] = result.at[ii, 'mark'] + (chr(97+mark))
        if (i==n-1):
            break

    return (result)


def total_df_multiple_comparison (df, cat_var_column, p_thres = 0.05, column_types = ['float'], p_adjust = 'holm'):
    sd_table = pd.DataFrame(columns = ['group'], data = np.unique(df[cat_var_column]))
    value_cols = []
    for col in df.columns:
      if (df[col].dtype in column_types):
        value_cols.append(col)
    for col in value_cols:
      result = multiple_comparison(df = df, cat_var_column = cat_var_column, value_column = col, p_thres = p_thres, p_adjust = p_adjust)
      print('Cytoskeleton index:', col)
      print(result, '\n')
      add_on_table = result[['group', 'mark']]
      add_on_table = add_on_table.rename(columns={'mark': col})
      sd_table = sd_table.merge(add_on_table, on = 'group')
    return (sd_table)
