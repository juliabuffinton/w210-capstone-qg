import pandas as pd
import glob
import os
import numpy as np
import concurrent.futures
import time

#https://forums.fast.ai/t/python-parallel-processing-tips-and-applications/2092
path = "/Users/sdatta/json_out"
allFiles = glob.glob(os.path.join(path,"*/*"))
np_array_list = []

start = time.time()

def read_json(in_file):
    file_substr = "/".join(in_file.split(sep="/")[-2:])
    print("Started ", file_substr," at ",time.time())
    l_df = pd.read_json(in_file, lines=True)
    l_df['filename'] = file_substr
    
    return l_df.as_matrix()


with concurrent.futures.ProcessPoolExecutor() as executor:
    for file in allFiles:
        np_array_list.append(read_json(file))
done = time.time()

elapsed = done - start
print("Time taken ",elapsed)

with concurrent.futures.ProcessPoolExecutor() as executor:
    comb_np_array = np.vstack(np_array_list)
    big_frame = pd.DataFrame(comb_np_array, columns=['id', 'text', 'title', 'url','filename'])
    
    print(big_frame.head(2)['filename'])
