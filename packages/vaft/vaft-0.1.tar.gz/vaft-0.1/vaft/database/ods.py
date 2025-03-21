import requests
import urllib3
import h5pyd, h5py
import omas
import subprocess
import numpy
from uncertainties import ufloat
from uncertainties.unumpy import uarray


def is_connect():
    """
    Check if the user is connected to the server.
    
    input: None
    output: True if the user is connected to the server, False otherwise.

    """
    try:
        if h5pyd.getServerInfo()['state']=='READY':
            username = h5pyd.getServerInfo()['username']
            return True 
        else:
            return False
    except requests.exceptions.ConnectTimeout:
        return False
    

def exist_file(username=h5pyd.getServerInfo()['username'], shot=None):
    """
    Check if the file exists.

    If the 'username' or 'shot' parameter is provided, the function will check if a file with a matching prefix exists.
    If 'username' or 'shot' is not provided, the function will list all files in the user's folder.
    
    Parameters:
        username (str): The username to access the corresponding folder.
        shot (int, optional): The shot number to search for (default is None).
    
    Returns:
        bool: True if the file or folder exists, False if it does not or if a connection error occurs.
    """
    try:
        Folder = list(h5pyd.Folder("/" + username + "/"))
        if shot is not None:
            file_list = list(Folder)
            file_exist = False  

            for file in file_list:
                if file.split("_")[0] == str(shot):
                    file_exist = True
                    print(file)
                    return True
            
            if not file_exist:
                print("File does not exist")
                return False
        else:
            print(list(Folder))
    except urllib3.exceptions.MaxRetryError:
        return False
    return True

def save(ods, shot, filename=None, env='server'):
    """
    Function to save an ODS (Open Data Structure) file either locally or to an HDF5 server.

    This function handles saving the ODS data to an HDF5 file, either on the local file system or
    remotely to an HDF5 server using the `hsload` command. If no filename is provided, the function 
    defaults to using the shot number with an `.h5` extension.

    Parameters:
    ods (object): The Open Data Structure (ODS) object that needs to be saved.
    shot (int): The shot number associated with the ODS data, used to generate the filename if not provided.
    filename (str, optional): The name of the file to save the ODS data. Defaults to `None`, which generates a name based on the shot number.
    env (str, optional): The environment where the file will be saved. It can be either 'server' for server upload or 'local' for local storage. Defaults to 'server'.

    Returns:
    None: The function doesn't return any specific value but prints information about the saving process.
    """

    # If no filename is provided, use the shot number to create a default file name
    if filename is None:
        filename = str(shot) + '.h5'

    # If the environment is 'local', save the file locally using OMAS
    if env == 'local':
        omas.save_omas_h5(ods, filename)

    # Test the connection to the server, and exit if the connection fails
    if is_connect() != True:
        print('Error: Connection to the server failed')
        return
    
    # Get the current username from the HDF5 server and construct the file path
    username = 'public' if h5pyd.getServerInfo()['username'] == 'admin' else h5pyd.getServerInfo()['username']
    file_path = "hdf5://{}/{}".format(username, filename)
    omas.save_omas_h5(ods, filename)

    command = ['hsload', '--h5image', filename, file_path]
    result = subprocess.run(command, capture_output=True, text=True)

    subprocess.run(['rm', filename], capture_output=True, text=True)

def convertDataset(ods, data):
    """
    Recursive utility function to map HDF5 structure to ODS

    :param ods: input ODS to be populated

    :param data: HDF5 dataset of group
    """
    import h5py

    keys = data.keys()
    try:
        keys = sorted(list(map(int, keys)))
    except ValueError:
        pass
    for oitem in keys:
        item = str(oitem)
        if item.endswith('_error_upper'):
            continue
        if isinstance(data[item], h5py.Dataset):
            if item + '_error_upper' in data:
                if isinstance(data[item][()], (float, numpy.floating)):
                    ods.setraw(item, ufloat(data[item][()], data[item + '_error_upper'][()]))
                else:
                    ods.setraw(item, uarray(data[item][()], data[item + '_error_upper'][()]))
            else:
                ods.setraw(item, data[item][()])
        elif isinstance(data[item], h5py.Group):
            convertDataset(ods.setraw(oitem, ods.same_init_ods()), data[item])

def load(shot, directory=None):

    if isinstance(shot, list):
        shot_list = shot
        ods_list = []
        for shot in shot_list:
            ods = omas.ODS()
            if directory is None:
                filename = f'hdf5://public/{shot}.h5'
            else:
                filename = f'hdf5://{directory}/{shot}.h5'
            with h5py.File(h5pyd.H5Image(filename)) as data:
                convertDataset(ods, data)
            ods_list.append(ods)
        return ods_list

    else:
        ods = omas.ODS()
        shot_list = [int(shot)]
        if directory is None:
            filename = f'hdf5://public/{shot}.h5'
        else:
            filename = f'hdf5://{directory}/{shot}.h5'
        with h5py.File(h5pyd.H5Image(filename)) as data:
            convertDataset(ods, data)
        return ods