
from osgeo import gdal

in_path = "C:\\Users\\Sirius\\Desktop\\VWebsite\\img\\"
out_path = "C:\\Users\\Sirius\\Desktop\\VWebsite\\imgpng\\"

import os
for filename in os.listdir(in_path):
    if filename.endswith('.tif'): 
        in_file = in_path+filename
        out_file = out_path + os.path.splitext(os.path.basename(filename))[0] + ".png"
        print(out_file)
        print(in_file)
        ds = gdal.Translate(out_file, in_file, options = "-scale -ot Byte") 