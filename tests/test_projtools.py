"""
Test projtools
"""
import numpy as np
import pytest

import geoutils as gu
import geoutils.projtools as pt
from geoutils import examples


class TestProjTools:

    landsat_b4_path = examples.get_path("everest_landsat_b4")
    landsat_b4_crop_path = examples.get_path("everest_landsat_b4_cropped")
    landsat_rgb_path = examples.get_path("everest_landsat_rgb")
    aster_dem_path = examples.get_path("exploradores_aster_dem")

    @pytest.mark.parametrize("example", [landsat_b4_path, aster_dem_path])  # type: ignore
    def test_latlon_reproject(self, example: str) -> None:
        """
        Check that to and from latlon projections are self consistent within tolerated rounding errors
        """

        img = gu.Raster(example)

        # Test on random points
        nsample = 100
        randx = np.random.randint(low=img.bounds.left, high=img.bounds.right, size=(nsample,))
        randy = np.random.randint(low=img.bounds.bottom, high=img.bounds.top, size=(nsample,))

        lat, lon = pt.reproject_to_latlon([randx, randy], img.crs)
        x, y = pt.reproject_from_latlon([lat, lon], img.crs)

        assert np.all(x == randx)
        assert np.all(y == randy)

    def test_merge_bounds(self) -> None:
        """
        Check that merge_bounds and bounds2poly work as expected for all kinds of bounds objects.
        """
        img1 = gu.Raster(self.landsat_b4_path)
        img2 = gu.Raster(self.landsat_b4_crop_path)

        # Check union (default) - with Raster objects
        out_bounds = pt.merge_bounds((img1, img2))
        assert out_bounds[0] == min(img1.bounds.left, img2.bounds.left)
        assert out_bounds[1] == min(img1.bounds.bottom, img2.bounds.bottom)
        assert out_bounds[2] == max(img1.bounds.right, img2.bounds.right)
        assert out_bounds[3] == max(img1.bounds.top, img2.bounds.top)

        # Check intersection - with Raster objects
        out_bounds = pt.merge_bounds((img1, img2), merging_algorithm="intersection")
        assert out_bounds[0] == max(img1.bounds.left, img2.bounds.left)
        assert out_bounds[1] == max(img1.bounds.bottom, img2.bounds.bottom)
        assert out_bounds[2] == min(img1.bounds.right, img2.bounds.right)
        assert out_bounds[3] == min(img1.bounds.top, img2.bounds.top)

        # Check that the results is the same with rio.BoundingBoxes
        out_bounds2 = pt.merge_bounds((img1.bounds, img2.bounds), merging_algorithm="intersection")
        assert out_bounds2 == out_bounds

        # Check that the results is the same with a list
        out_bounds2 = pt.merge_bounds((list(img1.bounds), list(img2.bounds)), merging_algorithm="intersection")
        assert out_bounds2 == out_bounds

        # Check with gpd.GeoDataFrame
        outlines = gu.Vector(gu.examples.get_path("everest_rgi_outlines"))
        outlines = gu.Vector(outlines.ds.to_crs(img1.crs))  # reproject to img1's CRS
        out_bounds = pt.merge_bounds((img1, outlines.ds))

        assert out_bounds[0] == min(img1.bounds.left, outlines.ds.total_bounds[0])
        assert out_bounds[1] == min(img1.bounds.bottom, outlines.ds.total_bounds[1])
        assert out_bounds[2] == max(img1.bounds.right, outlines.ds.total_bounds[2])
        assert out_bounds[3] == max(img1.bounds.top, outlines.ds.total_bounds[3])
