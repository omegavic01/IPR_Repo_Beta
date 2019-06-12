import unittest
from builder import EnvironmentValues, DirectoryValues, LoggingValues
from builder import Writer, Reader


class TestProjEnvVariables(unittest.TestCase):

    def setUp(self):
        self.env_cls = EnvironmentValues()

    def test_type_of_env_cls_payload_url(self):
        self.assertIsInstance(self.env_cls.payload_url(), str)

    def test_type_of_env_cls_payload_username(self):
        self.assertIsInstance(self.env_cls.payload_username(), str)

    def test_type_of_env_cls_payload_password(self):
        self.assertIsInstance(self.env_cls.payload_password(), str)

    def test_type_of_env_cls_header_row(self):
        self.assertIsInstance(self.env_cls.header_row(), list)


class TestProjDirVariables(unittest.TestCase):

    def setUp(self):
        self.dir_cls = DirectoryValues()

    def test_type_of_dir_cls_interim_dir(self):
        self.assertIsInstance(self.dir_cls.interim_dir(), str)

    def test_type_of_dir_cls_processed_dir(self):
        self.assertIsInstance(self.dir_cls.processed_dir(), str)

    def test_type_of_dir_cls_raw_dri(self):
        self.assertIsInstance(self.dir_cls.raw_dir(), str)

    def test_type_of_dir_cls_reports_dir(self):
        self.assertIsInstance(self.dir_cls.reports_dir(), str)


if __name__ == '__main__':
    unittest.main()
