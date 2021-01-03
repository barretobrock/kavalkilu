import unittest
from kavalkilu import InfluxDBLocal, InfluxDBHomeAuto


class TestInflux(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.influx = InfluxDBLocal(InfluxDBHomeAuto.TEMPS)

    def setUp(self) -> None:
        pass

    def test_read_query_to_df(self):
        """Test reading in a query to a pandas dataframe"""
        query = '''
            SELECT 
                last("temp")
            FROM "temps" 
            WHERE 
                location =~ /mushroom|r6du|elutuba|wc|v2lis|freezer|fridge/
                AND time > now() - 30m
            GROUP BY 
                "location" 
            fill(null)
            ORDER BY ASC
        '''
        df = self.influx.read_query(query, time_col='time')


if __name__ == '__main__':
    unittest.main()
