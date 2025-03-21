import unittest
from unittest.mock import patch
import urllib3

from aihub.api.files_api import FilesApi


class TestFilesApi(unittest.TestCase):
  """FilesApi unit test stubs"""

  def setUp(self) -> None:
    self.api = FilesApi()

  def tearDown(self) -> None:
    pass

  @patch.object(urllib3.PoolManager, 'request')
  def test_read_file(self, mock_request) -> None:
    """Test case for read_file

        Read file.
        """
    path = 'john.aihub-internal_instabase.com/my-repo/fs/Instabase Drive/files/foo.txt'

    # Mock the HTTP PUT request response
    file_contents = b'test'
    mock_response = urllib3.HTTPResponse(body=file_contents, status=200)
    mock_request.return_value = mock_response

    # Act
    response = self.api.read_file(path, expect_node_type='file')
    mock_request.assert_called_once()
    assert response == file_contents

  @patch.object(urllib3.PoolManager, 'request')
  def test_read_file_partial(self, mock_request) -> None:
    """Test case for read_file

        Read file.
        """
    path = 'john.aihub-internal_instabase.com/my-repo/fs/Instabase Drive/files/foo.txt'

    # Mock the HTTP PUT request response
    file_contents = b'test'
    mock_response = urllib3.HTTPResponse(body=file_contents[0:3], status=206)
    mock_request.return_value = mock_response

    # Act
    response = self.api.read_file(
        path, expect_node_type='file', range='bytes=0-2')
    mock_request.assert_called_once()
    assert response == file_contents[0:3]
