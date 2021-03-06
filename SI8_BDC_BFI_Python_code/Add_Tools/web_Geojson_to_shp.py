# This script automates the downloading of catchment shapefiles from the Environment Agency website and converts to shp file format

import urllib.request
import os
import geopandas as gpd
import geojson
import pandas as pd
import json
import arcpy
import matplotlib.pyplot as plt

### ISSUES: crs for output is not in OSGB and I'm struggling to set up geopandas to allow it to change -  solved using arcpy
def main():
    # EA selected Catchments
    # catchment_list = [3549, 3367, 3336, 3359, 3045, 3334, 3155, 3123, 3493,
    #                   3498, 3261, 3423, 3282, 3243, 3251, 3157, 3111, 3029]

    # Kent and Leven Demo Areas for Toolboxes
    # catchment_list = [3251, 3029, 3111, 3243]

    # Management Catchments 
    catchment_list = [3536]

    #pick one of the following
    # catch_type = 'ManagementCatchment'
    catch_type = 'OperationalCatchment'

    gjf = os.path.abspath("C:/...") # output file location
    epsg_code = 27700
    outfold = os.path.join(gjf, "OC3536_shape")

    if os.path.isdir(outfold):
        print("output folder already exists")
    else:
        print("create output folder")
        os.makedirs(outfold)


    gpd_lis = []
    for catch in catchment_list:
        with urllib.request.urlopen("https://environment.data.gov.uk/"
                                    "catchment-planning/so/{0}/".format(catch_type) + str(catch) + "/polygon") as url:
            data = geojson.loads(url.read().decode())

            with urllib.request.urlopen("https://environment.data.gov.uk/"
                                        "catchment-planning/so/{0}/".format(catch_type) + str(catch) + ".json") as urlmet:
                metdata = json.loads(urlmet.read().decode())

                metpand = pd.DataFrame(metdata["items"])
                oc = metpand.label[0]
                print(oc)

            # print(data)

            out_file = os.path.join(outfold, "Op_catch_{0}.shp".format(catch))
            gp_df = gpd.read_file(str(data), driver="GeoJSON")
            gp_df['id'] = catch
            gp_df['opc_NAME'] = oc
            gpd_lis.append(gp_df)

            gp_df.to_file(out_file, driver="ESRI Shapefile")

    out_f = os.path.join(outfold, "Op_catchments_All.shp")
    print("merging all catchments")
    rdf = gpd.GeoDataFrame(pd.concat(gpd_lis, ignore_index=True),
                           crs=gpd_lis[0].crs)


    # print(rdf.crs)
    # print(rdf)

    rdf.to_file(out_f, driver="ESRI Shapefile")

    print("reprojecting features with arcpy")
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = outfold

    featureclasses = arcpy.ListFeatureClasses()

    sr = arcpy.SpatialReference(epsg_code)
    for fc in featureclasses:
        print("input crs = {0}".format(arcpy.Describe(fc).spatialReference.name))
        tempShp = os.path.join(outfold, "tempshp.shp")

        arcpy.Project_management(fc, tempShp, sr)

        arcpy.CopyFeatures_management(tempShp, fc)
        print("output crs = {0}".format(arcpy.Describe(fc).spatialReference.name))

    if arcpy.Exists(tempShp):
        arcpy.Delete_management(tempShp)

    check_gdf = gpd.read_file(out_f, driver="ESRI Shapefile")
    check_gdf.plot(column='id')
    plt.show()

if __name__ == '__main__':
    main()
