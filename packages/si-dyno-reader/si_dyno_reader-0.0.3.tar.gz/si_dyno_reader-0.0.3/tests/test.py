import os
import unittest
from siDynoReader import DynoDataSet, MetricType
from siDynoReader.exceptions import ChannelNotFoundError

class TestDynoDataSet(unittest.TestCase):
    def setUp(self):
        """Initialize the dataset before each test."""
        base_path = os.path.dirname(__file__)
        test_file = os.path.join(base_path, "data/demoData-00001.001")
        self.data_set = DynoDataSet(test_file)

    def test_metadata(self):
        """Test if the project, dyno and test id value is correctly extracted."""
        self.assertEqual(self.data_set.project, "001")
        self.assertEqual(self.data_set.dyno, "demoData")
        self.assertEqual(self.data_set.test_id, "00001")

    def test_channel_case_insensitive(self):
        """Test if channel name as parameter is case insensitive"""
        self.assertEqual(self.data_set.get_description("BSFC"), "BSFC [g/kWh]")
        self.assertEqual(self.data_set.get_description("bsfc"), "BSFC [g/kWh]")
        self.assertEqual(self.data_set.get_description("bSFc"), "BSFC [g/kWh]")

    def test_exception_wrong_channel_name(self):
        """Test if the correct exception is raised if a channel name is used that doesn't exists"""
        with self.assertRaises(ChannelNotFoundError):
            self.data_set.get_description("BliBlaBlup")
        with self.assertRaises(ChannelNotFoundError):
            self.data_set.get_data("BliBlaBlup")
        with self.assertRaises(ChannelNotFoundError):
            self.data_set.get_measure_point("BliBlaBlup")
        with self.assertRaises(ChannelNotFoundError):
            self.data_set.get_measure_point_data("BliBlaBlup")

    def test_channel_list(self):
        """Test if the channel list is correct"""
        self.assertEqual(self.data_set.get_channels(), ["Time", "Throttle", "Power", "BSFC", "WaterTemperature", "Test_State", "text"])

    def test_data_of_channel(self):
        """Test if the first five values of the channel name is correct"""
        self.assertEqual(self.data_set.get_data("Throttle")[:5], [0.0, 0.5, 1.0, 1.5, 2.0])
        self.assertEqual(self.data_set.get_data("Throttle", MetricType.MEAN), 50)
        self.assertEqual(self.data_set.get_data("Throttle", time_range=[44, 46.5]), [44.0, 44.5, 45.0, 45.5, 46.0])
        self.assertEqual(self.data_set.get_data("Throttle", time_range=[44, 46.5], metric=MetricType.MEAN), 45)

    def test_measure_points(self):
        """Test whether the measuring points have been extracted correctly"""
        self.assertEqual(self.data_set.get_measure_point("Throttle"), [13.5, 39.5, 65.5, 91.5])
        self.assertEqual(self.data_set.get_measure_point("Throttle", MetricType.MIN), [7.0, 33.0, 59.0, 85.0])

    def test_metric(self):
        """Test if all metrics are correct calculated"""
        self.assertEqual(round(self.data_set.get_data("BSFC", MetricType.MEAN),3), 11.893)
        self.assertEqual(round(self.data_set.get_data("BSFC", MetricType.MEDIAN),3), 13.023)
        self.assertEqual(round(self.data_set.get_data("BSFC", MetricType.MIN),3), 0.002)
        self.assertEqual(round(self.data_set.get_data("BSFC", MetricType.MAX),3), 19.999)
        self.assertEqual(round(self.data_set.get_data("BSFC", MetricType.RANGE),3), 19.997)
        self.assertEqual(round(self.data_set.get_data("BSFC", MetricType.VARIANCE),3), 43.505)
        self.assertEqual(round(self.data_set.get_data("BSFC", MetricType.STD_DEV),3), 6.596)

if __name__ == '__main__':
    unittest.main()
