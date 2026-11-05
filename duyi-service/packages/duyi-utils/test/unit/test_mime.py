from duyi_utils.shared.mime import get_mime_type, IMAGE_MIME, DOC_MIME


class TestGetMimeType:
    def test_with_dot(self):
        assert get_mime_type(".png") == "image/png"

    def test_without_dot(self):
        assert get_mime_type("png") == "image/png"

    def test_uppercase(self):
        assert get_mime_type(".JPG") == "image/jpeg"

    def test_doc_type(self):
        assert get_mime_type(".pdf") == "application/pdf"

    def test_docx_type(self):
        assert get_mime_type(".docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def test_unknown_type(self):
        assert get_mime_type(".xyz") is None

    def test_empty_string(self):
        assert get_mime_type("") is None


class TestMimeConstants:
    def test_image_mime_not_empty(self):
        assert len(IMAGE_MIME) > 0

    def test_doc_mime_not_empty(self):
        assert len(DOC_MIME) > 0

    def test_all_keys_start_with_dot(self):
        for key in {**IMAGE_MIME, **DOC_MIME}:
            assert key.startswith(".")
