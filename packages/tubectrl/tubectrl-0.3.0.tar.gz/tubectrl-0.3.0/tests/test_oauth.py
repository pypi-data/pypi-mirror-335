from . import YouTube, MissingClientSecretsFile, InvalidSecretsFileError
import pytest
from pathlib import Path
from unittest.mock import patch


def test_secrets_file_not_provided():
    youtube = YouTube()
    with pytest.raises(MissingClientSecretsFile):
        youtube.authenticate()


def test_secrets_file_not_found():
    youtube = YouTube()
    with pytest.raises(FileNotFoundError):
        youtube.authenticate('client_secret.json')


def test_empty_secrets_file_provided():
    youtube = YouTube()
    with pytest.raises(InvalidSecretsFileError):
        youtube.authenticate('secret.json')


def test_youtube_authenticated():
    with patch.object(YouTube, 'authenticate', return_value=None) as authenticate:
        youtube = YouTube()
        assert youtube.authenticate('secret.json') is None
    authenticate.assert_called_once_with('secret.json')
    