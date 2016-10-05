import datetime
import expa_wrapper
from credentials_store import credentials
import logging
import sys
import re
from expa_hubspot_converter import EXPAHubspotConverter
from hubspot_wrapper import HubspotWrapper


class StreamToLogger(object):
    """
   Fake file-like stream object that redirects writes to a logger instance.
   """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def get_hubspot_id(opportunity):
    description = opportunity['description']
    if description is None:
        return None
    regex_match = re.search('(?<=HID: )\d+$', description)
    if regex_match is None:
        return None
    return regex_match.group(0)


def synchronize_deals(expa, hubspot, date_to_sync):
    opportunities = expa.get_opportunities(date_to_sync)
    for current_opportunity in opportunities:
        logging.info('Processing opportunity {0}...'.format(current_opportunity['id']))
        hubspot_id = get_hubspot_id(current_opportunity)
        if hubspot_id is not None:
            set_in_reception_pipeline = False
            should_deal_be_in_reception_pipeline = EXPAHubspotConverter.should_deal_be_in_reception_pipeline(
                current_opportunity)
            if should_deal_be_in_reception_pipeline:
                is_deal_in_reception_pipeline = hubspot.is_deal_in_reception_pipeline(hubspot_id)
                if not is_deal_in_reception_pipeline:
                    set_in_reception_pipeline = True
            hubspot_properties = EXPAHubspotConverter.convert_opp_to_hubspot_properties(current_opportunity,
                                                                                        set_in_reception_pipeline)
            hubspot.update_deal(hubspot_id, hubspot_properties)


def synchronize_contacts(expa, hubspot):
    contacts = hubspot.get_contacts()
    logging.debug('Sync {0} Contacts'.format(len(contacts)))
    for hubspot_id, expa_id in contacts.iteritems():
        person = expa.get_person(expa_id)
        hubspot_properties = EXPAHubspotConverter.convert_person_to_hubspot_properties(person)
        hubspot.update_contact(hubspot_id, hubspot_properties)


def main():
    logging.basicConfig(filename='sync.log'.format(str(datetime.datetime.today().date())),
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s')
    stdout_logger = logging.getLogger('')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl
    stderr_logger = logging.getLogger('')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl
    logging.info("Generating an EXPA access token...")
    try:
        expa = expa_wrapper.EXPAWrapper(credentials["expa"]["user"], credentials["expa"]["password"])
        hubspot = HubspotWrapper(credentials['hubspot']['api_key'])
        if len(sys.argv) > 1 and sys.argv[1] == 'contacts':
            logging.info("Starting daily contacts sync...")
            synchronize_contacts(expa, hubspot)
        else:
            if len(sys.argv) > 1 and sys.argv[1] == 'daily':
                date_to_sync = datetime.datetime.today() - datetime.timedelta(hours=26)
                logging.info("Starting daily deals sync...")
            else:
                date_to_sync = datetime.datetime.today() - datetime.timedelta(minutes=180)
                logging.info("Starting continuous deals sync...")
            synchronize_deals(expa, hubspot, date_to_sync)
        logging.info("Sync has finished successfully!")
    except Exception:
        logging.exception("An error has occured while generating an EXPA access token!")


if __name__ == "__main__":
    main()
