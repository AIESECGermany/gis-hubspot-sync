import dateutil.parser
import calendar
from datetime import datetime


class EXPAHubspotConverter:
    def __init__(self):
        pass

    @staticmethod
    def is_value_set(array, key):
        return array is not None and key in array and array[key] is not None and array[key] != ""

    @staticmethod
    def should_deal_be_in_reception_pipeline(opportunity):
        unmatched_status = ['unmatched', 'in progress', 'draft']
        return opportunity['current_status'] not in unmatched_status

    @staticmethod
    def convert_expa_birthdate_to_hubspot_timestamp(expa_birthdate):
        parsed_date = datetime.strptime(expa_birthdate, '%Y-%m-%d')
        timestamp = calendar.timegm(parsed_date.timetuple())
        return timestamp * 1000

    @staticmethod
    def convert_expa_matched_date_to_hubspot_timestamp(expa_matched_date):
        parsed_date = dateutil.parser.parse(expa_matched_date)
        parsed_date = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp = calendar.timegm(parsed_date.timetuple())
        return timestamp * 1000

    @staticmethod
    def convert_expa_date_to_hubspot_timestamp(expa_date):
        parsed_date = dateutil.parser.parse(expa_date)
        timestamp = calendar.timegm(parsed_date.timetuple())
        return timestamp * 1000

    @staticmethod
    def convert_opp_to_hubspot_properties(opportunity, set_in_reception_pipeline):
        properties = {'expa_id': opportunity['id'],
                      'expa_url': 'https://experience.aiesec.org/#/opportunities/{0}'.format(opportunity['id']),
                      'internship_type': 'i{0}'.format(opportunity['programmes']['short_name']),
                      'lc': opportunity['home_lc']['name'].title(), 'opportunity_name': opportunity['title']}
        if EXPAHubspotConverter.is_value_set(opportunity, 'applications_close_date'):
            properties['application_close_date'] = EXPAHubspotConverter.convert_expa_date_to_hubspot_timestamp(
                opportunity['applications_close_date'])
        if EXPAHubspotConverter.is_value_set(opportunity, 'duration_min'):
            properties['duration'] = opportunity['duration_min']
        if EXPAHubspotConverter.is_value_set(opportunity, 'current_status'):
            properties['expa_status'] = opportunity['current_status']
        # look for first matched for now and take the date
        if (EXPAHubspotConverter.is_value_set(opportunity, 'matched_applications')
            and EXPAHubspotConverter.is_value_set(opportunity['matched_applications'][0]['meta'], 'date_matched')):
            properties['matched_date'] = EXPAHubspotConverter.convert_expa_matched_date_to_hubspot_timestamp(
                opportunity['matched_applications'][0]['meta']['date_matched'])
        if set_in_reception_pipeline:
            reception_pipeline_id = '5467c9aa-d815-4855-90dd-725f4702a7f1'
            properties['pipeline'] = reception_pipeline_id
            properties['dealstage'] = '15b406a8-dfc8-464b-8ecd-f0b5090a3433'
        if EXPAHubspotConverter.is_value_set(opportunity['specifics_info'], 'salary'):
            properties['salary'] = opportunity['specifics_info']['salary']
        return properties

    @staticmethod
    def convert_person_to_hubspot_properties(person):
        properties = {'expa_id': person['id'], 'email': person['email'],
                      'expa_url': 'https://experience.aiesec.org/#/people/{0}'.format(person['id'])}
        if EXPAHubspotConverter.is_value_set(person, 'dob'):
            properties['birthday'] = EXPAHubspotConverter.convert_expa_birthdate_to_hubspot_timestamp(person['dob'])
        if EXPAHubspotConverter.is_value_set(person['current_office'], 'name'):
            properties['aiesec_entity'] = person['current_office']['name']
        if EXPAHubspotConverter.is_value_set(person, 'gender') and person['gender'] != 'Prefer not to answer':
            properties['gender'] = person['gender'].title()
        if EXPAHubspotConverter.is_value_set(person['contact_info'], 'phone'):
            properties['telephone'] = person['contact_info']['phone']
        return properties
