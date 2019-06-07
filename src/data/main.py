from builder import EnvironmentValues, DirectoryValues, LoggingValues
from builder import Writer, Reader
from ddi_ipam_pull import DdiCallTypes, IpamApiRequestGet, DdiCallFilenames
import logging


def main(ext_att=False, net_view=True):
    log_cls = LoggingValues()
    logging.basicConfig(filename=log_cls.log_filename(),
                        level=logging.DEBUG,
                        format=log_cls.log_format())

    logger = logging.getLogger(__file__.split("/")[-1:][0])

    logger.info('=========================')
    logger.info('Main Script Initializing.')
    logger.info('=========================')

    logger.info('Loading Project Environment Variables.')
    env_cls = EnvironmentValues()
    dir_cls = DirectoryValues()
    write_cls = Writer()
    logger.info('Project Environment Variables Loaded.')

    logger.info('===================')
    logger.info('Compiling DDI Data.')
    logger.info('===================')
    call_types = DdiCallTypes()
    filenames = DdiCallFilenames()
    ext_call_setup = IpamApiRequestGet()

    def extensible_attribute_call():
        logger.info('Pulling current Extensible Attribute data.')
        ext_attr_data = ext_call_setup.ddi_call(call_types.
                                                extensibles_attribute())
        # print(ext_attr_data)
        # print(type(ext_attr_data))
        write_cls.write_to_pkl(dir_cls.raw_dir(),
                               filenames.extensibles_attribute_filename(),
                               ext_attr_data)
        logger.info('Extensible Attribute data written to .pkl file.')

    if ext_att:
        extensible_attribute_call()
    else:
        logger.info('Extensible Attributes data was not set to True. Skipping')

    def network_view_call():
        logger.info('Pulling current Network View Data.')
        network_view_data = ext_call_setup.ddi_call(call_types.
                                                    network_views())
        print(network_view_data)
        print(type(network_view_data))
        write_cls.write_to_pkl(dir_cls.raw_dir(),
                               filenames.network_views_filename(),
                               network_view_data)
        logger.info('Network View data written to .pkl file.')

    if net_view:
        network_view_call()
    else:
        logger.info('Network View data was not set to True. Skipping.')
    exit()
    print(env_cls.payload_password())
    print(env_cls.header_row())
    print(type(dir_cls.reports_dir()))
    print(dir_cls.raw_dir())
    print(dir_cls.interim_dir())
    print(dir_cls.reports_dir())
    print(type(dir_cls.processed_dir()))


if __name__ == '__main__':
    main()
