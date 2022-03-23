import os
from glob import escape
from azure.storage.blob import BlobServiceClient
import xarray as xr
import re
import sys

# Helper functions

local_path = "./data"

if not os.path.exists(local_path):
    os.makedirs(local_path)


def parse_coords(coords):
    lat, lat_dec, lon, lon_dec = coords.split('_')
    lat = re.sub('^[A-Z]*0*', '', lat)
    lon = re.sub('^[A-Z]*0*', '', lon)
    return eval(f"(-{lon}.{lon_dec}, {lat}.{lat_dec}, -{lon}.{lon_dec}+0.25, {lat}.{lat_dec}+0.25)")


def bbox_intersects(box1, box2):
    left1, bottom1, right1, top1 = box1
    left2, bottom2, right2, top2 = box2
    return not(left2 >= right1 or right2 <= left1 or top2 <= bottom1 or bottom2 >= top1)


def get_scenes(blobs, bbox):
    target_scenes = []
    for country, scenes in blobs.items():
        for blob, box in scenes:
            if bbox_intersects(box, bbox):
                print(box)
                target_scenes.append(blob)
    return target_scenes


def get_mosaic(bbox):
    # Retrieve the blobs
    cred = 'sv=2020-10-02&st=2022-03-21T10%3A09%3A29Z&se=2022-06-30T09%3A09%3A00Z&sr=c&sp=rl&sig=VdoMJdqis89RWVSYRscPFwNujKoXXQx6dteC%2FUVlV6Y%3D'  # Shared Access Signature
    url = "https://euwpbww002sta01.blob.core.windows.net"
    container = 'mosaicdatachallenge2022'
    blob_service_client = BlobServiceClient(account_url=url, credential=cred)
    container_client = blob_service_client.get_container_client(
        container=container)
    blobs = {}
    for blob in container_client.list_blobs():
        try:
            region, coords, _ = blob.name.split('/')
            if region not in blobs.keys():
                blobs[region] = {(f'{region}/{coords}', parse_coords(coords))}
            else:
                blobs[region].add((f'{region}/{coords}', parse_coords(coords)))
        except Exception as e:
            print(e)

    # Get scenes
    scenes = get_scenes(blobs, bbox)
    print(f"{len(scenes)} scenes intersect")
    if len(scenes) == 0:
        print('No scenes found')
        return

    # download scenes
    all_data = None
    for scene in scenes:
        data = None
        for tif in ['red_median', 'green_median', 'blue_median', 'nir_median']:
            scene_path = os.path.join(local_path, scene)
            if not os.path.exists(scene_path):
                os.makedirs(scene_path)
            blob_client = blob_service_client.get_blob_client(
                container=container, blob=f'{scene}/{tif}.tif')
            download_file_path = os.path.join(scene_path, f'{tif}.tif')
            print("\nDownloading blob to \n\t" + download_file_path)
            with open(download_file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            tif_data = xr.open_rasterio(download_file_path).assign_coords(
                band=[tif.split('_')[0]])
            if data is None:
                data = tif_data
            else:
                data = xr.concat((data, tif_data), dim='band')

        if all_data is None:
            all_data = data.rename('var')
        else:
            all_data = all_data.combine_first(data)

    # Crop to bounding box
    all_data = all_data.where((all_data.x >= bbox[0]) &
                              (all_data.x <= bbox[2]) &
                              (all_data.y >= bbox[1]) &
                              (all_data.y <= bbox[3]), drop=True)

    return all_data
