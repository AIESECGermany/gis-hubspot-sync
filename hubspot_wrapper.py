import requests
import json
import logging
import re


class HubspotWrapper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.hubapi.com/'

    def fire_get_request(self, url, filters=None):
        url += '?'
        if filters is not None:
            for key, value in filters.iteritems():
                url += '{0}={1}&'.format(key, value)

        url += 'hapikey={0}'.format(self.api_key)
        result = requests.get(url)
        return result

    @staticmethod
    def convert_deal_properties_to_array_to_send(deal_properties):
        array_to_send = {'properties': []}
        for key, value in deal_properties.iteritems():
            array_to_send['properties'].append({'name': key, 'value': value})
        return array_to_send

    @staticmethod
    def convert_contact_properties_to_array_to_send(contact_properties):
        array_to_send = {'properties': []}
        for key, value in contact_properties.iteritems():
            array_to_send['properties'].append({'property': key, 'value': value})
        return array_to_send

    def fire_put_request(self, url, array_to_send):
        url += '?hapikey={0}'.format(self.api_key)
        print array_to_send
        headers = {'content-type': 'application/json'}
        result = requests.put(url, data=json.dumps(array_to_send), headers=headers)
        print result.content
        return result

    def fire_post_request(self, url, array_to_send):
        url += '?hapikey={0}'.format(self.api_key)
        print array_to_send
        headers = {'content-type': 'application/json'}
        result = requests.post(url, data=json.dumps(array_to_send), headers=headers)
        print result.content
        return result

    def is_deal_in_reception_pipeline(self, deal_id):
        url = self.base_url + 'deals/v1/deal/{0}'.format(deal_id)
        result = self.fire_get_request(url)
        if result.status_code != 200:
            logging.error(result.content)
            raise Exception
        pipeline_id = result.json()['properties']['pipeline']['value']
        return pipeline_id == '5467c9aa-d815-4855-90dd-725f4702a7f1'

    def update_deal(self, deal_id, deal_properties):
        url = self.base_url + 'deals/v1/deal/{0}'.format(deal_id)
        array_to_send = HubspotWrapper.convert_deal_properties_to_array_to_send(deal_properties)
        result = self.fire_put_request(url, array_to_send)
        if result.status_code != 200:
            logging.error(result.content)

    def update_contact(self, contact_id, contact_properties):
        url = self.base_url + 'contacts/v1/contact/vid/{0}/profile'.format(contact_id)
        array_to_send = HubspotWrapper.convert_contact_properties_to_array_to_send(contact_properties)
        result = self.fire_post_request(url, array_to_send)
        if result.status_code != 204:
            message = result.json()
            logging.error(message)
            if(message['error'] != 'CONTACT_EXISTS'):

    def get_contact(self, contact_id):
        url = self.base_url + 'contacts/v1/contact/vid/{0}/profile'.format(contact_id)
        result = self.fire_get_request(url, {'property': 'contact_type'})
        if result.status_code != 200:
            logging.error(result.content)
            raise Exception
        return result.json()

    def is_contact_a_trainee(self, contact_id):
        contact = self.get_contact(contact_id)
        return 'contact_type' in contact['properties'] and contact['properties']['contact_type']['value'] == 'Trainee'

    def get_contacts(self):
        contacts = {}
        url = self.base_url + 'contacts/v1/lists/all/contacts/all'
        filters = {'property': 'expa_id', 'property': 'expa_url'}
        result = self.fire_get_request(url, filters).json()
        while True:
            for contact in result['contacts']:
                expa_id = None
                if 'expa_id' in contact['properties']:
                    expa_id = contact['properties']['expa_id']['value']
                elif 'expa_url' in contact['properties']:
                    re_result = re.search('(?<=/)\d+$', contact['properties']['expa_url']['value'])
                    if re_result is not None:
                        expa_id = re_result.group(0)
                if expa_id is not None:
                    contact_id = contact['vid']
                    if self.is_contact_a_trainee(contact_id):
                        logging.info('Adding contact {0} to the process queue...'.format(contact_id))
                        contacts[contact_id] = expa_id
                    else:
                        logging.info('Skipping contact {0} because he/she is not a trainee...'.format(contact_id))
            if result['has-more']:
                filters['vidOffset'] = result['vid-offset']
                result = self.fire_get_request(url, filters).json()
            else:
                break
        return contacts
