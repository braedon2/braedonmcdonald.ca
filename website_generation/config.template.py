from abc import ABCMeta, abstractmethod

# ensure there are no trailing slashes when changing path strings

class AbstractConfig(metaclass=ABCMeta):
    api_secret_key = 'yourverysecretkey'
    api_access_key = 'youraccesskey'
    templates_path = 'absolute/path/to/templates'
    db_backup_bucket = 'braedonmcdonaldphotoalbumsdbbackup'

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
    photo_albums_bucket = 'braedonmcdonaldphotoalbums'
    photo_albums_db_path = '/absolute/path/to/db'
    photo_albums_root = '/absolute/path/to/photo/albums'
    generated_site_root = '/absolute/path/to/build'

class TestConfig(AbstractConfig):
    photo_albums_bucket = 'braedonmcdonaldphotoalbumstest'
    photo_albums_db_path = '/absolute/path/to/test/db'
    photo_albums_root = '/absolute/path/to/test/photo/albums'
    generated_site_root = '/absolute/path/to/test/build'