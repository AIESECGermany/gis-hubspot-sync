import requests
import logging
import gis_token_generator
import json


class EXPAWrapper:
    def __init__(self, email, password):
        self.token_generator = gis_token_generator.GISTokenGenerator(email, password)
        self.access_token = ''
        self.base_url = 'https://gis-api.aiesec.org:443/v2/'
        self.opportunity_url = self.base_url + 'opportunities/'
        self.application_url = self.base_url + 'applications/'

    @staticmethod
    def format_date_time(date_time):
        return date_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    def log_request_error(result):
        try: 
            logging.error('Error: {0}'.format(result.json()))
        except Exception:
            logging.error('Error: {0}'.format(result))

    def fire_get_request(self, url):
        if self.access_token == '':
            self.access_token = self.token_generator.generate_token()
        while True:
            logging.debug("expa get request")
            result = requests.get(url.format(self.access_token), verify=False)
            if result.status_code != 200:
                log_request_error(result)
            if result.status_code == 401:
                self.access_token = self.token_generator.generate_token()
            if result.status_code == 200:
                break
        return result.json()

    def fire_post_request(self, url, body):
        if self.access_token == '':
            self.access_token = self.token_generator.generate_token()
        payload = json.dumps(body)
        headers = {'content-type': 'application/json'}
        url += '?access_token={0}'
        while True:
            logging.debug("expa post request")
            result = requests.post(url.format(self.access_token), data=payload, headers=headers,
                                   verify=False)
            if result.status_code != 200:
                log_request_error(result)
            if result.status_code == 403:
                self.access_token = self.token_generator.generate_token()
            break
        return result

    def get_page_number(self, last_interaction=None):
        url = self.base_url + 'people.json?access_token={0}&per_page=200'
        if last_interaction is not None:
            url += '&filters%5Blast_interaction%5D%5Bfrom%5D=' + EXPAWrapper.format_date_time(last_interaction)
        current_page = self.fire_get_request(url)
        return current_page['paging']['total_pages']

    def get_opportunities(self, last_interaction=None, page=None):
        url = self.base_url + 'opportunities.json?access_token={0}&per_page=200'
        if last_interaction is not None:
            url += '&filters%5Blast_interaction%5D%5Bfrom%5D=' + EXPAWrapper.format_date_time(last_interaction)
        url += '&filters%5Bcountries%5B%5D=1596'
        url += '&filters%5Bprogrammes%5B%5D=1&filters%5Bprogrammes%5B%5D=2'
        current_page = self.fire_get_request(url)
        logging.debug('Current page from EXPA: {0}'.format(current_page))
        total_items = current_page['paging']['total_items']
        logging.info('Loading %d opportunities from EXPA...', total_items)
        total_pages = current_page['paging']['total_pages']
        result = []
        if page is None:
            start_page = 1
            end_page = total_pages + 1
        else:
            start_page = page
            end_page = start_page + 1
        for c in range(start_page, end_page):
            current_page = self.fire_get_request(url + '&page=%d' % c)
            for i in current_page['data']:
                opportunity = self.get_opportunity_detail(i['id'])
                matched_applications = self.get_opportunity_matched_applications(i['id']);
                for a in matched_applications['data']:
                    if 'matched_applications' not in opportunity:
                        opportunity['matched_applications'] = []
                    application = self.get_application_detail(a['id'])
                    opportunity['matched_applications'].append(application)
                result.append(opportunity)
        return result

    def get_opportunity_detail(self, opportunity_id):
        url = self.opportunity_url + str(opportunity_id) + '.json?access_token={0}'
        return self.fire_get_request(url)

    def get_opportunity_matched_applications(self, opportunity_id):
        url = self.opportunity_url + str(opportunity_id) + '/applications.json?access_token={0}'
        url += '&filters%5Bstatuses%5D%5B%5D=matched&filters%5Bstatuses%5D%5B%5D=accepted&filters%5Bstatuses%5D%5B%5D=approved'
        return self.fire_get_request(url)

    def get_application_detail(self, application_id):
        url = self.application_url + str(application_id) + '.json?access_token={0}'
        return self.fire_get_request(url)

    def get_person(self, person_id):
        url = self.base_url + 'people/' + str(person_id) + '.json?access_token={0}'
        return self.fire_get_request(url)
