""" Miscallaneous functions in the utility module
"""


def imageblocks(im, width, format = 'flat'):
    """Extract all blocks of specified size from an image or list of images
    Automatically pads image to ensure num_blocks = num_pixels
    """

    # See
    # http://stackoverflow.com/questions/16774148/fast-way-to-slice-image-into-overlapping-patches-and-merge-patches-to-image
    if len(im.shape) == 2:
        im = im[:,:,np.newaxis]
    im = np.pad(im,[[width,width],[width,width],[0,0]] ,mode = 'symmetric' )
    Nr, Nc, n_channels = im.shape
    blksz = 2*width+1
    shape = (Nr-2*width, Nc-2*width, blksz, blksz, n_channels)
    strides = im.itemsize*np.array([Nc*n_channels, n_channels, Nc*n_channels, n_channels, 1])
    sb = np.lib.stride_tricks.as_strided(im, shape=shape, strides=strides)
    sb = np.ascontiguousarray(sb)
    sb = sb[:(Nr-2*width),:Nc-2*width,:,:,:]
    sb = np.ascontiguousarray(sb)
    sb.shape = (-1, blksz, blksz, n_channels)
    n_samples = sb.shape[0]
    if format == 'flat':
        return sb.transpose([0,3,1,2]).reshape(n_samples,n_channels,blksz*blksz).transpose([0,2,1])
    else:
        return sb



def generate_random_fidelity(ind, perc):
    """  generate perc percent random fidelity out of index set ind

    Parameters
    -----------
    ind : ndarray, (n_sample_in_class, )
    perc : float, percent to sample

    """
    ind = np.array(ind)
    num_sample = int(np.ceil(len(ind)*perc))
    ind2 = np.random.permutation(len(ind))
    return ind[ind2[:num_sample]]


def to_standard_labels(labels):
    """  convert any numeric labeling, i.e., labels that are numbers, to
    standard form, 0,1,2,...

    Parameters
    -----------
    labels : ndarray, (n_labels, )

    Return 
    -----------
    out_labels : ndarray, (n_labels, )
    """    
    tags = np.unique(labels)
    out_labels = np.zeros(labels.shape)
    for i, tag in enumerate(tags):
        out_labels[labels == tag] = i
    return out_labels

def vector_to_labels(V):
    """  convert a multiclass assignment vector (n_samples, n_class) 
    to a standard label 0,1,2... (n_samples,) by projecting onto largest component

    Parameters
    -----------
    V : ndarray, shape(n_samples,n_class)
        class assignment vector for multiclass

    """
    return np.argmax(V, axis = 1)


def labels_to_vector(labels):
    """  convert a standard label 0,1,2... (n_samples,)
    to a multiclass assignment vector (n_samples, n_class) by assigning to e_k

    Parameters
    -----------
    labels : ndarray, shape(n_samples,)

    """
    labels = labels.astype(int)
    n_class = max(labels)+1
    vec = np.zeros([labels.shape[0], n_class])
    for i in range(n_class):
        vec[labels == i,i] = 1.
    return vec

def standard_to_binary_labels(labels):
	""" convert standard labeling 0,1 to binary labeling -1, 1
	"""
    out_labels = np.zeros(labels.shape)
    out_labels[labels == 0] = -1
    out_labels[labels == 1] = 1 
    return out_labels


def generate_initial_value_multiclass(opt , n_samples = None, n_class = None): 
    """  generate initial value for multiclass classification. 
    an assignment matrix is returned 

    Parameters
    -----------
    opt: string :{'rd_equal','rd'}
        options for generating values
    n_samples : int
        number of nodes in the graph

    Return
    -------
    u_init : ndarray, shape(n_samples, n_class)

    """   
    
    if opt == 'rd_equal':
        ind = permutation(n_samples)
        u_init = np.zeros([n_samples, n_class]) 
        sample_per_class = n_samples/n_class
        for i in range(n_class):
            u_init[ind[i*sample_per_class:(i+1)*sample_per_class], i] = 1.
        return u_init
    elif opt == 'rd':
        u_init = np.random.uniform(low = -1, high = 1, size = [n_samples,n_class])
        u_init = labels_to_vector(vector_to_labels(u_init))
        return u_init

def compute_error_rate(labels, ground_truth):
    """ compute the error rate of a classification given ground_truth and the labels 
    since for clustering the order of the labels are relative, we will automatically 
    match ground_truth with labels according to the highest percentage of population 
    in ground truth 

    Parameters
    -----------
    labels : ndarray, shape(n_samples, )
    ground_truth : ndarray, shape(n_samples, )
    """
    # format the labels
    labels = to_standard_labels(labels).astype(int)
    ground_truth = to_standard_labels(ground_truth).astype(int)
    format_labels = np.zeros(labels.shape).astype(int)
    n_class = max(labels)
    for tag in range(n_class+1):
       format_labels[labels == tag] = np.argmax(np.bincount(ground_truth[labels == tag].astype(int)))
    return float(len(ground_truth[format_labels!= ground_truth]))/float(len(ground_truth))