#!/usr/bin/env python
# This is a prototype and nearly all of the code here was taken from other sources
# See http://trustedsignal.blogspot.com/2012/02/plotting-photo-location-data-with-bing.html

def print_header():
    print '''<?xml version="1.0"?>
<rss xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#" version="2.0">
  <channel>
    <title>GPS Metadata Plotted</title>
    <description>GPS Metadata from images plotted</description>'''

def print_item(filename, description, lat, lon):
    print '''    <item><title>%s</title><description>%s</description><geo:lat>%.4f</geo:lat><geo:long>%.4f</geo:long></item>''' % (filename, filename, lat, lon)

def print_footer():
    print '''</channel>
</rss>'''

def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
        print tag, ret[decoded]
    return ret

def processFiles(args):
    input_filemask = "JPG"
    directory = args[1]
    if os.path.isdir(directory):
        list_of_files = glob.glob('%s/*.%s' % (directory, input_filemask))
    else:
        list_of_files = sys.argv[1:]
    for file_name in list_of_files:
        lat, lon = get_lat_lon(get_exif_data(file_name))
        print_item(file_name, "static", lat, lon)

def get_exif_data(fn):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    i = Image.open(fn)
    info = i._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                    exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def _get_if_exist(data, key):
    if key in data:
        return data[key]
    return None

def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)
    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)
    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)
    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None
    if "GPSInfo" in exif_data:      
        gps_info = exif_data["GPSInfo"]
        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":                     
                lat = 0 - lat
            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
    return lat, lon

if __name__ == '__main__':
    import glob
    import sys
    import os.path
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
     
    print_header()
    processFiles(sys.argv)
    print_footer()
