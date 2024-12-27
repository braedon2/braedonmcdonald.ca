from abc import ABCMeta, abstractmethod

class AbstractConfig(metaclass=ABCMeta):
    @property
    @abstractmethod
    def api_secret_key(self):
        pass

    @property
    @abstractmethod
    def api_access_key(self):
        pass

    @property
    @abstractmethod
    def photo_albums_bucket(self):
        pass

    @property
    @abstractmethod
    def photo_albums_db_path(self):
        pass

    @property
    @abstractmethod
    def photo_albums_root(self):
        pass

    @property
    @abstractmethod
    def generated_site_root(self):
        pass

class Config(AbstractConfig):
    api_secret_key = 'yourverysecretkey'
    api_access_key = "youraccesskey"
    photo_albums_bucket = 'braedonmcdonaldphotoalbums'
    photo_album_db_path = '/absolute/path/to/db'
    photo_albums_root = '/absolute/path/to/photo/albums'
    generated_site_root = '/absolute/path/to/build'

class TestConfig(AbstractConfig):
    api_secret_key = 'yourverysecretkey'
    api_access_key = "youraccesskey"
    photo_albums_bucket = 'braedonmcdonaldphotoalbums'
    photo_album_db_path = '/absolute/path/to/test/db'
    photo_albums_root = '/absolute/path/to/test/photo/albums'
    generated_site_root = '/absolute/path/to/test/build'