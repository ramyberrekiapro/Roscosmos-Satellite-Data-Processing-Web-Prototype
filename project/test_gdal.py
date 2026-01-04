from osgeo import gdal
def test_gdal():
    print("GDAL version:", gdal.VersionInfo())
    print("GDAL data path:", gdal.GetConfigOption('GDAL_DATA', 'Not set'))
if __name__ == '__main__':
    test_gdal()