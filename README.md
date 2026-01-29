# Satellite Data Processing Platform

A Django-based web application for processing and visualizing satellite imagery data with geospatial mapping capabilities.

## Features

- Upload and process TIFF satellite imagery files
- Interactive map visualization using OpenLayers and MapTiler
- Create composite images from multiple satellite files
- Multi-language support (English/Russian)
- Responsive web interface

## Prerequisites

- Python 3.11+
- GDAL library (>=3.4.0) with system dependencies
- Django 4.2+
- MapTiler API key (free tier available)

## Installation

### GDAL Installation (Required First)

**macOS:**
```bash
brew install gdal
export GDAL_DATA=$(gdal-config --datadir)
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install gdal-bin libgdal-dev
export GDAL_DATA=$(gdal-config --datadir)
```

**Windows:**
1. Download from [OSGeo4W](https://trac.osgeo.org/osgeo4w/)
2. Install GDAL package
3. Add GDAL to PATH

### Project Setup

1. Clone the repository:
```bash
git clone [https://github.com/ramyberrekiapro/VWebsite.git](https://github.com/ramyberrekiapro/Roscosmos-Satellite-Data-Processing-Web-Prototype/
cd Roscosmos-Satellite-Data-Processing-Web-Prototype
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Generate Django secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

6. Edit `.env` file with your values:
```env
SECRET_KEY=your-generated-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MAPTILER_KEY=your-maptiler-api-key-here
```

7. Get MapTiler API Key:
   - Sign up at [MapTiler](https://www.maptiler.com/)
   - Get free API key (100,000 requests/month)
   - Add key to `.env` file

8. Initialize database:
```bash
python manage.py migrate
```

9. Collect static files:
```bash
python manage.py collectstatic --noinput
```

10. Start development server:
```bash
python manage.py runserver
```

Access at: `http://localhost:8000`

## Usage

### Quick Start
1. Access the application at `http://localhost:8000`
2. Upload TIFF satellite imagery files using the file upload interface
3. View uploaded files on the interactive map
4. Select multiple images to create composite visualizations
5. Download processed results

### Sample Data for Testing

The project includes ready-to-use sample TIFF files in the `img/` directory:

**Sample Files Available:**
- `MM22_MSUMR_20220823T114027_13101300_N3828E04330_20220824_1D_TOAL1.tif` (~29MB)
- `MM22_MSUMR_20220823T114027_13101300_N3828E04330_20220824_1D_TOAL2.tif` (~29MB)
- `MM22_MSUMR_20220823T114027_13101300_N3828E04330_20220824_1D_TOAL3.tif` (~29MB)
- `MM22_MSUMR_20220823T114027_13101300_N3828E04330_20220824_1D_TOAL4.tif` (~29MB)
- `MM22_MSUMR_20220823T114027_13101300_N3828E04330_20220824_1D_TOAL5.tif` (~29MB)
- `MM22_MSUMR_20220823T114027_13101300_N3828E04330_20220824_1D_TOAL6.tif` (~29MB)

**How to Use Sample Data:**
1. Navigate to the `img/` directory in your project
2. Select and upload any of the `*_TOAL*.tif` files
3. These are multispectral satellite image bands from the same scene
4. Upload multiple bands (TOAL1, TOAL2, TOAL3, etc.) for best results

### Creating Composite Images

**What is a Composite Image?**
A composite image combines multiple satellite image bands into a single visualization. Each band represents different light wavelengths (e.g., red, green, blue, near-infrared), allowing for enhanced analysis and visualization.

**Step-by-Step Composite Creation:**
1. **Upload Multiple Bands**: Upload at least 2-3 TIFF files from the sample data
2. **View on Map**: Each uploaded image will appear as a checkbox in the image list
3. **Select Images**: Check the boxes next to images you want to combine
4. **Create Composite**: Click the "Create Composite" button
5. **Download Result**: The composite image will be generated and available for download

**Recommended Combinations:**
- **True Color**: TOAL1 (Red), TOAL2 (Green), TOAL3 (Blue)
- **False Color Vegetation**: TOAL3 (Red), TOAL4 (Green), TOAL5 (Blue)
- **All Bands**: Select all 6 TOAL files for comprehensive analysis

**Tips for Best Results:**
- Use images from the same satellite scene (same date/time)
- Select bands that complement each other
- Start with 2-3 bands for simpler composites
- Experiment with different combinations for various analyses

### Supported File Formats
- **Format**: GeoTIFF (.tif, .tiff)
- **Size**: Maximum 100MB per file
- **Coordinate Systems**: WGS84, UTM, and common projections
- **Bands**: Single and multi-band satellite imagery

### Features Explained
- **Upload**: Drag & drop or select multiple TIFF files
- **Map View**: Interactive OpenLayers map with satellite overlay
- **Composite Creation**: Merge multiple images into single visualization
- **Language Support**: Switch between English and Russian (top-right menu)

## Project Structure

```
VWebsite/
├── project/          # Django project settings
├── files/           # File upload and processing logic
├── templates/       # HTML templates
├── static/          # Static assets (CSS, JS)
├── media/           # User uploaded files
├── locale/          # Internationalization files
├── requirements.txt # Python dependencies
├── .env.example     # Environment variables template
└── README.md        # This file
```

## Environment Variables

| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `SECRET_KEY` | Django secret key | `django-insecure-abc123...` | Yes |
| `DEBUG` | Debug mode (True/False) | `True` | No (defaults: True) |
| `ALLOWED_HOSTS` | Allowed hostnames (comma-separated) | `localhost,127.0.0.1` | No |
| `MAPTILER_KEY` | MapTiler API key | `0yTWWeUHxuwcas4gxFET` | Yes |

### Getting Required Values

**Django SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**MapTiler API Key:**
1. Register at [MapTiler Cloud](https://cloud.maptiler.com/)
2. Verify email address
3. Navigate to Account → Keys
4. Copy default key or create new one
5. Free tier: 100,000 requests/month

## Troubleshooting

### Common Issues

**GDAL Installation Errors:**
```bash
# Error: Could not find the GDAL library
# Solution: Install system dependencies first
# macOS:
brew install gdal
# Ubuntu:
sudo apt-get install gdal-bin libgdal-dev
```

**Permission Errors:**
```bash
# Error: Permission denied for media directory
# Solution: Set proper permissions
chmod 755 media/
chmod 644 media/*
```

**Map Not Loading:**
- Verify MapTiler API key is valid
- Check browser console for API errors
- Ensure internet connection is active
- Verify API key hasn't exceeded quota

**Static Files Not Loading:**
```bash
python manage.py collectstatic --noinput --clear
```

**Database Issues:**
```bash
# Reset database if needed
rm db.sqlite3
python manage.py migrate
```

### Development vs Production

**Development (default):**
- DEBUG=True
- SQLite database
- Django development server
- Static files served by Django

**Production Setup:**
- DEBUG=False
- PostgreSQL/MySQL recommended
- Gunicorn + Nginx
- Static files served by Nginx
- Environment variables properly configured

### Performance Tips
- Use compressed TIFF files for faster uploads
- Limit concurrent uploads to 3-4 files
- Clear old images from media directory regularly
- Use CDN for static files in production

## Security Notes

- Never commit `.env` file to version control
- Always use strong, unique `SECRET_KEY` in production
- Set `DEBUG=False` in production environments
- Keep GDAL library and dependencies updated
- Use HTTPS in production
- Validate all uploaded file types and sizes
- Regular backup of database and media files

## License

MIT License - feel free to use this project for commercial and personal projects

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style
- Add comments for complex logic
- Test with different TIFF file formats
- Update documentation for new features
