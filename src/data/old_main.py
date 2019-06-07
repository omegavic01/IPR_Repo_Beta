from builder import EnvironmentValues, DirectoryValues, LoggingValues
from builder import Writer, Reader
from ddi_ipam_pull import DdiCallTypes, IpamApiRequestGet, DdiCallFilenames
import logging
import time


def main(ext_att=False, net_view=False, get_networks=True):
    log_cls = LoggingValues()
    logging.basicConfig(filename=log_cls.log_filename(),
                        level=logging.DEBUG,
                        filemode='a',
                        format=log_cls.log_format())

    logger = logging.getLogger(__file__.split("/")[-1:][0])

    logger.info('=========================')
    logger.info('Main Script Initializing.')
    logger.info('=========================')

    logger.info('Loading Project Environment Variables.')
    env_cls = EnvironmentValues()
    dir_cls = DirectoryValues()
    write_cls = Writer()
    reader_cls = Reader()
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
        logger.info('Extensible Attr data written to .pkl file in Raw Dir.')

    if ext_att:
        extensible_attribute_call()
    else:
        logger.info('Extensible Attributes data was not set to True. Skipping')

    def network_view_call():
        logger.info('Pulling current Network View Data.')
        network_view_data = ext_call_setup.ddi_call(call_types.
                                                    network_views())
        # print(network_view_data)
        # print(type(network_view_data))
        write_cls.write_to_pkl(dir_cls.raw_dir(),
                               filenames.network_views_filename(),
                               network_view_data)
        logger.info('Network View data written to .pkl file in raw Dir.')

    if net_view:
        network_view_call()
    else:
        logger.info('Network View data was not set to True. Skipping.')

    def get_network():
        logger.info('Pulling current IPAM Data.')
        network_views = reader_cls.read_from_pkl(dir_cls.raw_dir(),
                                                 filenames.
                                                 network_views_filename())
        network_data = []
        start = time.perf_counter()
        for _ref in network_views:
            # if _ref == network_views[1]:
            #     break
            network_data += ext_call_setup.ddi_call(call_types.
                                                    networks(_ref['name']))
        end = time.perf_counter()
        logging.info("Downloaded {} Networks in {} seconds".
                     format(len(network_data), end - start))
        write_cls.write_to_pkl(dir_cls.raw_dir(),
                               filenames.networks_filename(),
                               network_data)
        logger.info('Network Data written to .pkl file in raw Dir.')

    if get_networks:
        get_network()
    else:
        logger.info('Network data was not set to True.  Skipping.')
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
