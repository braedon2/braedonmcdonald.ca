from abc import ABCMeta, abstractmethod
from os import path

class AbstractConfig(metaclass=ABCMeta):
    project_root = '/absolute/path/to/project/root'

    api_secret_key = 'yourverysecretkey'
    api_access_key = 'youraccesskey'
    templates_path = 'relative/path/to/templates'
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

# always instantiate instead of using Config directly so you don't miss "not implemented" errors

class Config(AbstractConfig):
    #abstract class implementations
    photo_albums_bucket = 'braedonmcdonaldphotoalbums'
    photo_albums_db_path = path.join(AbstractConfig.project_root, 'photo-albums.db')
    photo_albums_root = path.join(AbstractConfig.project_root, 'photo-albums')
    generated_site_root = path.join(AbstractConfig.project_root, 'generated')

class TestConfig(AbstractConfig):
    # abstract class implementations
    photo_albums_bucket = 'braedonmcdonaldphotoalbumstest'
    photo_albums_db_path = path.join(AbstractConfig.project_root, 'photo-albums-test.db')
    photo_albums_root = path.join(AbstractConfig.project_root, 'test-data')
    generated_site_root = path.join(AbstractConfig.project_root, 'generated-test')

    # unique to TestConfig
    test_data_source = path.join(AbstractConfig.project_root, 'test-data-source')