from build import EnvironmentVariables, DirectoryValues
import logging


if __name__ == '__main__':
    LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=LOG_FMT)
    logger = logging.getLogger('main.py')
    logger.info('Loading Environment Variables.')
    env_cls = EnvironmentVariables()
    dir_cls = DirectoryValues()
    print(env_cls.payload_url())
    print(env_cls.payload_username())
    print(env_cls.payload_password())
    print(env_cls.header_row())
    print(type(dir_cls.report_dir()))
    print(dir_cls.raw_dir())
    print(dir_cls.interim_dir())
    print(type(dir_cls.processed_dir()))
    logger.info('Environment Variables Loaded.')

