from datetime import datetime
from unittest.mock import patch

from duyi_utils.upload.dir_strategy import date_uuid_strategy, flat_uuid_strategy


class TestDateUuidStrategy:
    def test_returns_upload_path_with_date(self):
        with patch("duyi_utils.upload.dir_strategy.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 6, 26, 10, 30, 0)
            result = date_uuid_strategy()
        assert result == "uploads/2025/06/26/"

    def test_single_digit_month_day_padded(self):
        with patch("duyi_utils.upload.dir_strategy.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 5, 10, 30, 0)
            result = date_uuid_strategy()
        assert result == "uploads/2025/01/05/"

    def test_ends_with_slash(self):
        with patch("duyi_utils.upload.dir_strategy.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 6, 26, 10, 30, 0)
            result = date_uuid_strategy()
        assert result.endswith("/")


class TestFlatUuidStrategy:
    def test_returns_flat_path(self):
        result = flat_uuid_strategy()
        assert result == "uploads/"

    def test_ends_with_slash(self):
        result = flat_uuid_strategy()
        assert result.endswith("/")
