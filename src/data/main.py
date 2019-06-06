from builder import EnvironmentVariables, DirectoryValues
import logging

FORMAT = "[%(asctime)s, %(name)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format=FORMAT)


def main():
    logger = logging.getLogger(__file__.split('/')[-1:][0])
    logger.info('Loading Environment Variables.')
    env_cls = EnvironmentVariables()
    dir_cls = DirectoryValues()
    print(env_cls.payload_url())
    print(env_cls.payload_username())
    print(env_cls.payload_password())
    print(env_cls.header_row())
    print(type(dir_cls.reports_dir()))
    print(dir_cls.raw_dir())
    print(dir_cls.interim_dir())
    print(dir_cls.reports_dir())
    print(type(dir_cls.processed_dir()))
    logger.info('Environment Variables Loaded.')



if __name__ == '__main__':
#    print(__file__.split('/')[-1:][0])
#    logger = logging.getLogger(__name__)
#    logger.info('Loading Environment Variables.')
#    env_cls = EnvironmentVariables()
#    dir_cls = DirectoryValues()
#    print(env_cls.payload_url())
#    print(env_cls.payload_username())
#    print(env_cls.payload_password())
#    print(env_cls.header_row())
#    print(type(dir_cls.reports_dir()))
#    print(dir_cls.raw_dir())
#    print(dir_cls.interim_dir())
#    print(dir_cls.reports_dir())
#    print(type(dir_cls.processed_dir()))
#    logger.info('Environment Variables Loaded.')
    main()
