from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.translation import gettext as _
from .forms import UploadFileForm
from .models import Images
from osgeo import gdal, osr
import os
import uuid
import osgeo_utils.gdal_merge as gdal_merge
import math


def _bounds_to_wgs84(ds, x_min, y_min, x_max, y_max):
    src_wkt = ds.GetProjection()
    if not src_wkt:
        return x_min, y_min, x_max, y_max

    src = osr.SpatialReference()
    src.ImportFromWkt(src_wkt)
    dst = osr.SpatialReference()
    dst.ImportFromEPSG(4326)

    if hasattr(src, 'SetAxisMappingStrategy'):
        src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    if hasattr(dst, 'SetAxisMappingStrategy'):
        dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    ct = osr.CoordinateTransformation(src, dst)
    corners = [
        (x_min, y_min),
        (x_min, y_max),
        (x_max, y_min),
        (x_max, y_max),
    ]
    lons = []
    lats = []
    for x, y in corners:
        lon, lat, *_ = ct.TransformPoint(x, y)
        lons.append(lon)
        lats.append(lat)

    return min(lons), min(lats), max(lons), max(lats)


def landing(request):
    return render(request, 'landing.html')

def howto_view(request):
    return render(request, 'howto.html')



def geotiff_to_png(img_instance):
    """
    Convert a GeoTIFF to PNG for visualization and return its extent.
    """
    try:
        tif_path = img_instance.img.path
        print(f"Processing file: {tif_path}") 
        
        if not tif_path.lower().endswith('.tif') and not tif_path.lower().endswith('.tiff'):
            raise ValueError("File is not a TIFF file")
            
        tif_dir = os.path.dirname(tif_path)
        tif_base = os.path.basename(tif_path)
        tif_stem, _tif_ext = os.path.splitext(tif_base)

        # Always give the output PNG a new unique filename (avoid collisions and make it clear it's generated).
        unique_suffix = uuid.uuid4().hex[:8]
        png_filename = f"{tif_stem}_{unique_suffix}.png"
        png_path = os.path.join(tif_dir, png_filename)
        
        # open the dataset to get the georeferencing info
        ds = gdal.Open(tif_path)
        if ds is None:
            raise Exception(f"GDAL could not open {tif_path}. Is it a valid GeoTIFF?")
        
        try:
            # get the geotransform
            gt = ds.GetGeoTransform()
            if gt is None:
                raise Exception("Could not get geotransform from the image. Is it georeferenced?")
                
            x_min = gt[0]
            y_max = gt[3]
            x_max = x_min + gt[1] * ds.RasterXSize
            y_min = y_max + gt[5] * ds.RasterYSize

            x_min, y_min, x_max, y_max = _bounds_to_wgs84(ds, x_min, y_min, x_max, y_max)

            print(f"Image bounds: x_min={x_min}, y_min={y_min}, x_max={x_max}, y_max={y_max}")  

            # save the extent to the database
            img_instance.min_lon = x_min
            img_instance.max_lon = x_max
            img_instance.min_lat = y_min
            img_instance.max_lat = y_max
            img_instance.save()

            # convert to PNG
            print(f"Converting to PNG: {tif_path} -> {png_path}")  # Debug log
            gdal.Translate(
                png_path,
                tif_path,
                options='-scale -ot Byte'
            )
            
            # verify PNG was created
            if not os.path.exists(png_path):
                raise Exception(f"Failed to create PNG at {png_path}")

            try:
                rel_png = os.path.relpath(png_path, settings.MEDIA_ROOT)
                img_instance.png.name = rel_png
                img_instance.name = os.path.basename(rel_png)
                img_instance.save(update_fields=['png', 'name'])
            except Exception as e:
                raise Exception(f"PNG created but failed to update DB path: {str(e)}")
                
            print(f"Successfully processed {tif_path}") 
            return png_path
            
        finally:
            ds = None  # ensure dataset is closed
            
    except Exception as e:
        print(f"Error in geotiff_to_png: {str(e)}")  
        raise  

def merge_geotiffs(tif_paths, output_tif):
    """
    Merge multiple GeoTIFFs into one composite.
    """
    params = ['', '-o', output_tif] + tif_paths + ['-separate', '-co', 'COMPRESS=LZW']
    gdal_merge.main(params)



def upload_files(request):
    imgs = Images.objects.exclude(img__contains='composites/').order_by('-id')
    errors = []
    successes = []

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print("Form data:", request.POST) 
        print("Files:", request.FILES) 

        if form.is_valid():
            files = form.cleaned_data.get('file') or request.FILES.getlist('file')
            if not files:
                errors.append(_("No files were uploaded."))
            else:
                for f in files:
                    try:
                        print(f"Processing uploaded file: {f.name}")  
                        img = Images(img=f)
                        img.save()  # save first to get a path

                        try:
                            png_path = geotiff_to_png(img)
                            print(f"Successfully processed {f.name} -> {png_path}")  
                            successes.append(_("%(filename)s processed to PNG and saved successfully.") % {'filename': f.name})
                        except Exception as e:
                            error_msg = _("Error processing %(filename)s: %(error)s") % {'filename': f.name, 'error': str(e)}
                            print(error_msg)  
                            errors.append(error_msg)
                            img.delete()  # Clean up if conversion fails
                    except Exception as e:
                        error_msg = _("Error saving %(filename)s: %(error)s") % {'filename': getattr(f, 'name', 'file'), 'error': str(e)}
                        print(error_msg)  
                        errors.append(error_msg)
        else:
            print("Form errors:", form.errors)  # Debug log
            for field, error_list in form.errors.items():
                for error in error_list:
                    errors.append(f"{field}: {error}")

        imgs = Images.objects.exclude(img__contains='composites/').order_by('-id')
    else:
        form = UploadFileForm()

    return render(request, 'index.html', {
        'form': form,
        'imgs': imgs,
        'errors': errors,
        'successes': successes,
        'maptiler_key': settings.MAPTILER_KEY
    })
def convert(request):
    """
    Merge selected images and create a composite PNG.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    ids = request.POST.get('pics', '')
    ids = [i for i in ids.split(',') if i.isdigit()]

    images = Images.objects.filter(id__in=ids)

    if not images:
        return JsonResponse({'error': 'No images selected'}, status=400)

    tif_paths = []
    for img in images:
        p = img.img.path
        pl = (p or '').lower()
        if not (pl.endswith('.tif') or pl.endswith('.tiff')):
            return JsonResponse({'error': f'Invalid input (not a GeoTIFF): {os.path.basename(p)}'}, status=400)
        if not os.path.exists(p):
            return JsonResponse({'error': f'Input file missing on disk: {os.path.basename(p)}'}, status=400)
        tif_paths.append(p)

    composite_dir = os.path.join(settings.MEDIA_ROOT, 'composites')
    os.makedirs(composite_dir, exist_ok=True)

    composite_tif = os.path.join(composite_dir, 'Composite.tif')
    composite_png = os.path.join(composite_dir, 'Composite.png')

    # Ensure clean merge: delete existing outputs first
    for path in (composite_tif, composite_png):
        if os.path.exists(path):
            os.remove(path)

    merge_geotiffs(tif_paths, composite_tif)
    ds = gdal.Open(composite_tif)
    if ds is None:
        return JsonResponse({'error': 'Failed to open composite GeoTIFF'}, status=500)

    try:
        gt = ds.GetGeoTransform()
        if gt is None:
            return JsonResponse({'error': 'Composite has no geotransform'}, status=500)

        x_min = gt[0]
        y_max = gt[3]
        x_max = x_min + gt[1] * ds.RasterXSize
        y_min = y_max + gt[5] * ds.RasterYSize

        x_min, y_min, x_max, y_max = _bounds_to_wgs84(ds, x_min, y_min, x_max, y_max)
    finally:
        ds = None

    if not all(math.isfinite(v) for v in [x_min, y_min, x_max, y_max]):
        return JsonResponse({'error': 'Composite extent is invalid (non-finite). Check input rasters CRS/georeferencing.'}, status=500)

    ds = gdal.Open(composite_tif)
    if ds:
        band_count = ds.RasterCount
        data_type = gdal.GetDataTypeName(ds.GetRasterBand(1).DataType)
        band1 = ds.GetRasterBand(1)
        min_val, max_val = band1.GetMinimum(), band1.GetMaximum()
        if min_val is None or max_val is None:
            min_val, max_val = band1.ComputeStatistics(False)[:2]
        print(f'Composite raster: bands={band_count}, type={data_type}, band1 range=({min_val}, {max_val})')
        ds = None
    else:
        print('Failed to reopen composite raster for logging')
        band_count, min_val, max_val = 1, 0, 65535

    if band_count >= 3:
        opts = ['-b', '1', '-b', '2', '-b', '3', '-scale', str(min_val), str(max_val), '0', '255', '-ot', 'Byte']
    else:
        opts = ['-scale', str(min_val), str(max_val), '0', '255', '-ot', 'Byte']

    print(f'gdal.Translate options: {opts}')
    gdal.Translate(composite_png, composite_tif, options=' '.join(opts))

    rel_tif = os.path.relpath(composite_tif, settings.MEDIA_ROOT)
    rel_png = os.path.relpath(composite_png, settings.MEDIA_ROOT)

    composite_img, _created = Images.objects.update_or_create(
        img=rel_tif,
        defaults={
            'png': rel_png,
            'name': 'Composite.png',
        }
    )

    composite_img.min_lon = x_min
    composite_img.max_lon = x_max
    composite_img.min_lat = y_min
    composite_img.max_lat = y_max
    composite_img.save(update_fields=['min_lon', 'max_lon', 'min_lat', 'max_lat'])

    # Ensure we always return a usable PNG URL (fallback to img if png field is empty)
    png_url = composite_img.png.url if composite_img.png else composite_img.img.url
    print(f'Composite png_url returned: {png_url}')

    return JsonResponse({
        'success': True,
        'png_url': png_url,
        'extent': [x_min, y_min, x_max, y_max]
    })
