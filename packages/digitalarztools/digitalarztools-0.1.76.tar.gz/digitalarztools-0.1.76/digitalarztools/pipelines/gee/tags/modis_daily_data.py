import enum
from datetime import datetime, timedelta

import ee

from digitalarztools.pipelines.gee.core.image_collection import GEEImageCollection
from digitalarztools.pipelines.gee.core.region import GEERegion
from digitalarztools.pipelines.usgs.fews_net import FEWSNetData


class MODISDatasetTags(enum.Enum):
    Water = {"tag": 'MODIS/061/MOD09A1'}
    Temperature = {"tag": 'MODIS/061/MOD11A1'}
    SnowCover = {"tag": 'MODIS/061/MOD10A1'} #MODIS/061/MOD10A1


class MODISDailyData:

    @staticmethod
    def get_dataset_collection(dataset_tag: MODISDatasetTags, region: GEERegion) -> ee.ImageCollection:
        return (ee.ImageCollection(dataset_tag.value["tag"])
                .filterBounds(region.bounds))

    @classmethod
    def get_latest_dates(cls, delta_in_days=10, dataset_tag: MODISDatasetTags = None, region: GEERegion = None) -> (
            str, str):
        # Calculate the date range for the latest 10 days
        if dataset_tag is None:
            end_date = datetime.now()
        else:
            ee_img_coll = cls.get_dataset_collection(dataset_tag, region=region)
            end_date = GEEImageCollection.get_collection_max_date(ee_img_coll)
        start_date = end_date - timedelta(days=delta_in_days)

        # Convert dates to strings formatted as required by the Earth Engine API
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    @staticmethod
    def get_temperature_vis_param():
        # Define visualization parameters
        return {
            'min': 13000.0,
            'max': 16500.0,
            'palette': [
                '040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
                '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
                '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
                'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
                'ff0000', 'de0101', 'c21301', 'a71001', '911003'
            ],
        }

    @staticmethod
    def convert_modis_lst_to_celsius(dn_value):
        """
        Converts a MODIS LST digital number (DN) to degrees Celsius.

        Parameters:
        - dn_value: The MODIS LST DN value to convert.

        Returns:
        - The temperature in degrees Celsius.
        """
        # Constants
        scale_factor = 0.02
        kelvin_to_celsius_offset = 273.15

        # Convert DN to Kelvin
        kelvin_value = dn_value * scale_factor

        # Convert Kelvin to Celsius
        celsius_value = kelvin_value - kelvin_to_celsius_offset

        return celsius_value

    @classmethod
    def get_temperature_image_collection(cls, delta_in_days=10, region: GEERegion = None) -> ee.ImageCollection:
        start_date_str, end_date_str = cls.get_latest_dates(delta_in_days)
        # Define the dataset with the updated date range
        dataset = ee.ImageCollection('MODIS/061/MOD11A1') \
            .filter(ee.Filter.date(start_date_str, end_date_str))
        if region is not None:
            dataset = dataset.filterBounds(region.bounds)

        # Select the Land Surface Temperature band
        landSurfaceTemperature = dataset.select('LST_Day_1km')
        return landSurfaceTemperature

    @classmethod
    def get_temperature_data_url(cls, delta_in_days=10, region: GEERegion = None) -> str:
        landSurfaceTemperature = cls.get_temperature_image_collection(delta_in_days, region)
        # Generate a URL for visualization
        landSurfaceTemperatureVis = cls.get_temperature_vis_param()
        url = landSurfaceTemperature.getMapId(landSurfaceTemperatureVis)
        return url['tile_fetcher'].url_format

    @classmethod
    def get_snow_cover_vis_paramters(cls):
        return {
            'min': 0.0,
            'max': 100.0,
            'palette': ['0dffff', '0524ff', '001b7f'],
        }

    @classmethod
    def get_snow_cover_image_collection(cls, delta_in_days=30, region: GEERegion = None, start_date_str =None, end_date_str=None):
        """
        Retrieves MODIS Snow Cover Image Collection with improved date filtering.
        - Uses the MODIS 061 MOD10A1 dataset.
        - Selects the 'NDSI_Snow_Cover' band and masks no-snow areas.

        Args:
            delta_in_days (int): Number of past days to include in the dataset.
            region (GEERegion): Region to filter by bounds.

        Returns:
            ee.ImageCollection: Processed MODIS Snow Cover Collection.
        """
        # Get date range
        if start_date_str is None and end_date_str is None:
            start_date_str, end_date_str = cls.get_latest_dates(delta_in_days)
        # print("MODIS Start Date:", start_date_str, "End Date:", end_date_str)  # Debugging

        # Load MODIS dataset
        tag = MODISDatasetTags.SnowCover.value["tag"]
        dataset = ee.ImageCollection(tag).filter(ee.Filter.date(start_date_str, end_date_str))

        # Debugging: Check the number of images before region filtering
        # print("Number of MODIS Images before region filter:", dataset.size().getInfo())

        # Apply region filter if provided
        if region is not None:
            # print("Filtering MODIS dataset to region bounds:", region.bounds.getInfo())  # Debugging
            dataset = dataset.filterBounds(region.aoi)

        # Select and mask snow cover band
        snow_cover = dataset.select('NDSI_Snow_Cover')

        # Mask out areas where no snow cover is detected
        masked_snow_cover = snow_cover.map(lambda image: image.updateMask(image.gt(0)))

        # Debugging: Check final dataset size
        # print("Number of MODIS Images after processing:", masked_snow_cover.size().getInfo())

        return masked_snow_cover

    @classmethod
    def get_snow_cover_url(cls, delta_in_days=30, region: GEERegion = None):
        masked_snow_cover = cls.get_snow_cover_image_collection(delta_in_days, region)
        image = masked_snow_cover.mean()
        # image = masked_snow_cover.sort('system:time_start', False).first()
        # Define visualization parameters.
        snow_cover_vis = cls.get_snow_cover_vis_paramters()

        # Generate the map ID and token.
        url = image.getMapId(snow_cover_vis)

        return url['tile_fetcher'].url_format

    @staticmethod
    def get_water_masked(region: GEERegion, date_range: tuple, water_threshold: float = 0.1) -> ee.Image:
        # 'MODIS/061/MOD09A1'
        modis = ee.ImageCollection(MODISDatasetTags.Water.value["tag"]) \
            .filterDate(date_range[0], date_range[1]) \
            .select(['sur_refl_b02', 'sur_refl_b04']) \
            .filterBounds(region.bounds)  # Filter by region of interest

        # Calculate NDWI for MODIS
        def calculate_ndwi_modis(image):
            ndwi = image.normalizedDifference(['sur_refl_b04', 'sur_refl_b02']).rename('NDWI_MODIS')
            return image.addBands(ndwi)

        # Apply NDWI calculation to each image
        modis_ndwi = modis.map(calculate_ndwi_modis)

        # Reduce the image collection to a single image using the max function
        ndwi_max = modis_ndwi.select('NDWI_MODIS').max()

        # Create a water mask where NDWI is greater than the threshold
        water_mask = ndwi_max.gt(water_threshold)

        # Mask the water layer to only include the AOI and apply the water mask
        water_masked = ndwi_max.updateMask(water_mask).clip(region.aoi)

        return water_masked
