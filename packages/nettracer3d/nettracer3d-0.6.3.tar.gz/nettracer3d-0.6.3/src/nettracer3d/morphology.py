from . import nettracer
from . import network_analysis
import numpy as np
from scipy.ndimage import zoom
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import tifffile
from functools import partial
import pandas as pd
from scipy import ndimage

def get_reslice_indices(slice_obj, dilate_xy, dilate_z, array_shape):
    """Convert slice object to padded indices accounting for dilation and boundaries"""
    if slice_obj is None:
        return None, None, None
        
    z_slice, y_slice, x_slice = slice_obj
    
    # Extract min/max from slices
    z_min, z_max = z_slice.start, z_slice.stop - 1
    y_min, y_max = y_slice.start, y_slice.stop - 1
    x_min, x_max = x_slice.start, x_slice.stop - 1

    # Add dilation padding
    y_max = y_max + ((dilate_xy-1)/2) + 1
    y_min = y_min - ((dilate_xy-1)/2) - 1
    x_max = x_max + ((dilate_xy-1)/2) + 1
    x_min = x_min - ((dilate_xy-1)/2) - 1
    z_max = z_max + ((dilate_z-1)/2) + 1
    z_min = z_min - ((dilate_z-1)/2) - 1

    # Boundary checks
    y_max = min(y_max, array_shape[1] - 1)
    x_max = min(x_max, array_shape[2] - 1)
    z_max = min(z_max, array_shape[0] - 1)
    y_min = max(y_min, 0)
    x_min = max(x_min, 0)
    z_min = max(z_min, 0)

    return [z_min, z_max], [y_min, y_max], [x_min, x_max]

def reslice_3d_array(args):
    """Internal method used for the secondary algorithm to reslice subarrays around nodes."""

    input_array, z_range, y_range, x_range = args
    z_start, z_end = z_range
    z_start, z_end = int(z_start), int(z_end)
    y_start, y_end = y_range
    y_start, y_end = int(y_start), int(y_end)
    x_start, x_end = x_range
    x_start, x_end = int(x_start), int(x_end)
    
    # Reslice the array
    resliced_array = input_array[z_start:z_end+1, y_start:y_end+1, x_start:x_end+1]
    
    return resliced_array



def _get_node_edge_dict(label_array, edge_array, label, dilate_xy, dilate_z, cores = 0):
    """Internal method used for the secondary algorithm to find pixel involvement of nodes around an edge."""
    
    # Create a boolean mask where elements with the specified label are True
    label_array = label_array == label
    dil_array = nettracer.dilate_3D_recursive(label_array, dilate_xy, dilate_xy, dilate_z) #Dilate the label to see where the dilated label overlaps

    if cores == 0: #For getting the volume of objects. Cores presumes you want the 'core' included in the interaction.
        edge_array = edge_array * dil_array  # Filter the edges by the label in question
        label_array = np.count_nonzero(dil_array)
        edge_array = np.count_nonzero(edge_array) # For getting the interacting skeleton

    elif cores == 1: #Cores being 1 presumes you do not want to 'core' included in the interaction
        label_array = dil_array - label_array
        edge_array = edge_array * label_array
        label_array = np.count_nonzero(label_array)
        edge_array = np.count_nonzero(edge_array) # For getting the interacting skeleton

    elif cores == 2: #Presumes you want skeleton within the core but to only 'count' the stuff around the core for volumes... because of imaging artifacts, perhaps
        edge_array = edge_array * dil_array
        label_array = dil_array - label_array
        label_array = np.count_nonzero(label_array)
        edge_array = np.count_nonzero(edge_array) # For getting the interacting skeleton


    
    args = [edge_array, label_array]

    return args

def process_label(args):
    """Modified to use pre-computed bounding boxes instead of argwhere"""
    nodes, edges, label, dilate_xy, dilate_z, array_shape, bounding_boxes = args
    print(f"Processing node {label}")
    
    # Get the pre-computed bounding box for this label
    slice_obj = bounding_boxes[label-1]  # -1 because label numbers start at 1
    if slice_obj is None:
        return None, None, None
        
    z_vals, y_vals, x_vals = get_reslice_indices(slice_obj, dilate_xy, dilate_z, array_shape)
    if z_vals is None:
        return None, None, None
        
    sub_nodes = reslice_3d_array((nodes, z_vals, y_vals, x_vals))
    sub_edges = reslice_3d_array((edges, z_vals, y_vals, x_vals))
    return label, sub_nodes, sub_edges



def create_node_dictionary(nodes, edges, num_nodes, dilate_xy, dilate_z, cores=0):
    """Modified to pre-compute all bounding boxes using find_objects"""
    node_dict = {}
    array_shape = nodes.shape
    
    # Get all bounding boxes at once
    bounding_boxes = ndimage.find_objects(nodes)
    
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
        # Create args list with bounding_boxes included
        args_list = [(nodes, edges, i, dilate_xy, dilate_z, array_shape, bounding_boxes) 
                    for i in range(1, num_nodes + 1)]

        # Execute parallel tasks to process labels
        results = executor.map(process_label, args_list)

        # Process results in parallel
        for label, sub_nodes, sub_edges in results:
            executor.submit(create_dict_entry, node_dict, label, sub_nodes, sub_edges, 
                          dilate_xy, dilate_z, cores)

    return node_dict

def create_dict_entry(node_dict, label, sub_nodes, sub_edges, dilate_xy, dilate_z, cores = 0):
    """Internal method used for the secondary algorithm to pass around args in parallel."""

    if label is None:
        pass
    else:
        node_dict[label] = _get_node_edge_dict(sub_nodes, sub_edges, label, dilate_xy, dilate_z, cores = cores)


def quantify_edge_node(nodes, edges, search = 0, xy_scale = 1, z_scale = 1, cores = 0, resize = None, save = True, skele = False):

    def save_dubval_dict(dict, index_name, val1name, val2name, filename):

        #index name goes on the left, valname on the right
        df = pd.DataFrame.from_dict(dict, orient='index', columns=[val1name, val2name])

        # Rename the index to 'Node ID'
        df.index.name = index_name

        # Save DataFrame to Excel file
        df.to_excel(filename, engine='openpyxl')

    if type(nodes) is str:
        nodes = tifffile.imread(nodes)

    if type(edges) is str:
        edges = tifffile.imread(edges)

    if skele:
        edges = nettracer.skeletonize(edges)
    else:
        edges = nettracer.binarize(edges)

    if len(np.unique(nodes)) == 2:
        nodes, num_nodes = nettracer.label_objects(nodes)
    else:
        num_nodes = np.max(nodes)

    if resize is not None:
        edges = zoom(edges, resize)
        nodes = zoom(nodes, resize)
        edges = nettracer.skeletonize(edges)

    if search > 0:
        dilate_xy, dilate_z = nettracer.dilation_length_to_pixels(xy_scale, z_scale, search, search)
    else:
        dilate_xy, dilate_z = 0, 0


    edge_quants = create_node_dictionary(nodes, edges, num_nodes, dilate_xy, dilate_z, cores = cores) #Find which edges connect which nodes and put them in a dictionary.

    if save:
    
        save_dubval_dict(edge_quants, 'NodeID', 'Edge Skele Quantity', 'Search Region Volume', 'edge_node_quantity.xlsx')

    else:

        return edge_quants



def calculate_voxel_volumes(array, xy_scale=1, z_scale=1):
    """
    Calculate voxel volumes for each uniquely labelled object in a 3D numpy array.
    
    Args:
        array: 3D numpy array where different objects are marked with different integer labels
        xy_scale: Scale factor for x and y dimensions
        z_scale: Scale factor for z dimension
        
    Returns:
        Dictionary mapping object labels to their voxel volumes
    """

    labels = np.unique(array)
    if len(labels) == 2:
        array, _ = nettracer.label_objects(array)

    del labels
    
    # Get volumes using bincount
    if 0 in array:
        volumes = np.bincount(array.ravel())[1:]
    else:
        volumes = np.bincount(array.ravel())

    
    # Apply scaling
    volumes = volumes * (xy_scale**2) * z_scale
    
    # Create dictionary with label:volume pairs
    return {label: volume for label, volume in enumerate(volumes, start=1) if volume > 0}



def search_neighbor_ids(nodes, targets, id_dict, neighborhood_dict, totals, search, xy_scale, z_scale, root):

    if 0 in targets:
        targets.remove(0)
    targets = np.isin(nodes, targets)
    targets = nettracer.binarize(targets)
    
    dilate_xy, dilate_z = nettracer.dilation_length_to_pixels(xy_scale, z_scale, search, search)
    
    dilated = nettracer.dilate_3D_recursive(targets, dilate_xy, dilate_xy, dilate_z)
    dilated = dilated - targets #technically we dont need the cores
    search_vol = np.count_nonzero(dilated) * xy_scale * xy_scale * z_scale #need this for density
    targets = dilated != 0
    del dilated

    
    targets = targets * nodes
    
    unique, counts = np.unique(targets, return_counts=True)
    count_dict = dict(zip(unique, counts))
    print(count_dict)
    
    del count_dict[0]
    
    unique, counts = np.unique(nodes, return_counts=True)
    total_dict = dict(zip(unique, counts))
    print(total_dict)

    del total_dict[0]
    
    
    for label in total_dict:
        if label in id_dict:
            if label in count_dict:
                neighborhood_dict[id_dict[label]] += count_dict[label]
            totals[id_dict[label]] += total_dict[label]


    try:
        del neighborhood_dict[root]  #no good way to get this
        del totals[root] #no good way to get this
    except:
        pass
    
    volume = nodes.shape[0] * nodes.shape[1] * nodes.shape[2] * xy_scale * xy_scale * z_scale
    densities = {}
    for nodeid, amount in totals.items():
        densities[nodeid] = (neighborhood_dict[nodeid]/search_vol)/(amount/volume)

    return neighborhood_dict, totals, densities






def get_search_space_dilate(target, centroids, id_dict, search, scaling = 1):

    ymax = np.max(centroids[:, 0])
    xmax = np.max(centroids[:, 1])


    array = np.zeros((ymax + 1, xmax + 1))

    for i, row in enumerate(centroids): 
        if i + 1 in id_dict and target in id_dict[i+1]:
            y = row[0]  # get y coordinate
            x = row[1]  # get x coordinate
            array[y, x] = 1  # set value at that coordinate


    #array = downsample(array, 3)
    array = dilate_2D(array, search, search)

    search_space = np.count_nonzero(array) * scaling * scaling

    tifffile.imwrite('search_regions.tif', array)

    print(f"Search space is {search_space}")



    return array