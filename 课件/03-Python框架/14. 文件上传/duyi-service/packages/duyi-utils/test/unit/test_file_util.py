from duyi_utils.shared.file_util import get_suffix


class TestGetSuffix:
    def test_bare_filename(self):
        assert get_suffix("photo.png") == "png"

    def test_path_with_dirs(self):
        assert get_suffix("/a/b/c/report.PDF") == "pdf"

    def test_multiple_dots(self):
        assert get_suffix("archive.tar.gz") == "gz"

    def test_no_extension(self):
        assert get_suffix("noext") is None

    def test_dotfile_hidden_no_extension(self):
        assert get_suffix(".hidden") is None

    def test_empty_string(self):
        assert get_suffix("") is None
