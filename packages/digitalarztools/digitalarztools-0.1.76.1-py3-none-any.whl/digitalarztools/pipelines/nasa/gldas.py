import ee

from digitalarztools.pipelines.gee.core.image_collection import GEEImageCollection
from digitalarztools.pipelines.gee.core.region import GEERegion
from digitalarztools.pipelines.gee.tags.modis_daily_data import MODISDailyData


class GLDASData:
    """
    https://developers.google.com/earth-engine/datasets/catalog/NASA_GLDAS_V021_NOAH_G025_T3H
    """

    def __init__(self):
        self.gee_dataset_tag = "NASA/GLDAS/V021/NOAH/G025/T3H"
        self.gee_scale = 27830  # Corrected to 11 km resolution
        self.start_date_str = None
        self.end_date_str = None

    def get_gee_dataset_collection(self, region: GEERegion) -> ee.ImageCollection:
        img_coll = ee.ImageCollection(self.gee_dataset_tag).filterBounds(region.aoi)
        # print("image collection count ", GEEImageCollection.get_image_count(img_coll))
        return img_coll

    def aggregate_daily(self, gldas_datasets: ee.ImageCollection, mean_bands=(), sum_bands=(),
                        max_bands=()) -> ee.ImageCollection:
        def aggregation(date):
            date = ee.Date(date)
            next_day = date.advance(1, 'day')

            daily_collection = gldas_datasets.filterDate(date, next_day)

            mean_reduced = daily_collection.select(mean_bands).reduce(ee.Reducer.mean())
            sum_reduced = daily_collection.select(sum_bands).reduce(ee.Reducer.sum())
            max_reduced = daily_collection.select(max_bands).reduce(ee.Reducer.max())

            # Merge the results
            daily_image = mean_reduced.addBands(max_reduced).addBands(sum_reduced)

            # Rename summed bands to indicate summation
            # renamed_image = daily_image.rename(["snow_depth", "snow_depth_water_equivalent",
            #                                     "snowfall_sum", "snowmelt_sum"])

            return daily_image.set('system:time_start', date.millis())

        # Generate date range
        start_date = ee.Date(self.start_date_str)
        end_date = ee.Date(self.end_date_str)
        date_diff = end_date.difference(start_date, 'day').int()

        date_range = ee.List.sequence(0, date_diff).map(lambda i: start_date.advance(i, 'day'))

        daily_gldas = ee.ImageCollection(date_range.map(aggregation))
        return daily_gldas

    def convert_snow_metrics(self, img: ee.Image) -> ee.Image:
        img = img.addBands(img.select("SnowDepth_inst"))  # Already in meters
        img = img.addBands(
            img.select("SWE_inst").divide(1000))  # Convert kg/m² → meters of water equivalent (m.w.e)
        img = img.addBands(
            img.select("Snowf_tavg").multiply(10800).divide(1000))  # Convert kg/m²/s → m w.e./3 hours
        img = img.addBands(img.select("Qsm_acc").divide(1000))  # Convert kg/m² → meters

        return img

    def get_snow_metric_collection(self, gee_region: GEERegion, delta_in_days=10) -> ee.ImageCollection:
        """
        Retrieves snow-related metrics by combining GLDAS (SnowDepth, SWE, Snowfall, Snowmelt)
        and MODIS (Snow Cover). Converts GLDAS bands to meters.

        Conversions:
            - SnowDepth_inst (snow depth) (m) → **m** (no change)
            - SWE_inst (water stored in snow) (kg/m²) → **m of water equivalent** (÷ 1000)
            - Snowf_tavg (snowfall) (kg/m²/s) → **m of water equivalent per day** (× 86400 ÷ 1000)
            - Qsm_acc (snow melt) (kg/m²) → **m of water equivalent** (÷ 1000)
        """
        # Fetch dataset once and filter by date
        img_collection = self.get_gee_dataset_collection(gee_region)
        self.start_date_str, self.end_date_str = GEEImageCollection.get_latest_dates(img_collection, delta_in_days)

        # --- Fetch GLDAS Snow Metrics ---
        dataset = self.get_gee_dataset_collection(gee_region).filter(
            ee.Filter.date(self.start_date_str, self.end_date_str))
        dataset = dataset.map(lambda img: self.convert_snow_metrics(img))
        # Apply reducers selectively
        max_bands = ["SnowDepth_inst", "SWE_inst"]  # Use mean for these bands
        sum_bands = ["Snowf_tavg", "Qsm_acc"]  # Use sum for these bands

        dataset = self.aggregate_daily(dataset, max_bands=max_bands, sum_bands=sum_bands)

        # band_count = GEEImageCollection.get_image_count(dataset)
        # print(band_count)
        # band_names = GEEImageCollection.get_band_names(dataset)
        # print(band_names)

        def rename_bands(image):
            return image.select(["SnowDepth_inst_max", "SWE_inst_max", "Snowf_tavg_sum", "Qsm_acc_sum"]) \
                .rename(["snow_depth", "snow_depth_water_equivalent", "snowfall_sum", "snowmelt_sum"])

        gldas_snow_metrics = dataset.map(rename_bands)

        # --- Convert GLDAS Band Units to meters ---

        # gldas_snow_metrics = gldas_snow_metrics.map(convert_snow_metrics)

        return gldas_snow_metrics
