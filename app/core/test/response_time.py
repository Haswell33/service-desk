import requests
import argparse
import json
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from requests.auth import HTTPBasicAuth
from getpass import getpass

APP_URL = '<url>'
LOGIN_URL = f'{APP_URL}/login/'


def make_request(endpoint, seconds, request, username, password, data):
    waiting = True
    start = datetime.now()
    start_timestamp = _get_datetime_object(datetime.now().strftime('%H:%M:%S'))
    end_timestamp = start_timestamp + relativedelta(seconds=+seconds)
    session = requests.session()
    session.get(LOGIN_URL)
    csrf_token = session.cookies['csrftoken']
    login_data = {'username': username, 'password': password, 'csrfmiddlewaretoken': csrf_token}
    login_response = session.post(f'{APP_URL}/login/', data=login_data)
    print(f'cookies: {login_response.cookies}')
    headers = {'User-Agent': 'Mozilla/5.0'}
    print(endpoint)
    i = 3
    while waiting:
        now = datetime.now().strftime("%H:%M:%S")
        start_request = datetime.now()
        response = session.request(
            request,
            APP_URL + endpoint
        )
        diff = datetime.now() - start_request
        print(f'({now}) {response.reason} {response.status_code}: {response.request} {response.url} [{int((diff.seconds * 1000) + (diff.microseconds / 1000))} ms]')
        print(response.elapsed.total_seconds())
        i = i + 1
        time.sleep(3)
        if datetime.now().strftime("%H:%M:%S") >= end_timestamp.strftime("%H:%M:%S"):
            session.close()
            waiting = False
            print(f'Test finished: {start.strftime("%H:%M:%S")} - {end_timestamp.strftime("%H:%M:%S")}')


def _get_datetime_object(date):
    return datetime.strptime(date, '%H:%M:%S')


def parse_args():
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('-e', '--endpoint', help='', type=str, required=True)
    arg_parser.add_argument('-s', '--seconds', help='', type=int, required=True)
    arg_parser.add_argument('-u', '--username', help='', type=str, required=True)
    arg_parser.add_argument('-r', '--request', help='', type=str, required=True)
    arg_parser.add_argument('-d', '--data', help='', type=str, required=False)
    return arg_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    password = getpass(prompt=f"Enter password for user '{args.username}': ")
    # auth = HTTPBasicAuth(args.username, password)
    make_request(args.endpoint, args.seconds, args.request, args.username, password, args.data)
'''''''''
data={
    'csrfmiddlewaretoken': login_response.cookies['csrftoken'],
    'title': f'testing_{now}',
    'type': 1,
    'priority': 1,
    'assignee': None,
    'attachments': None,
    'description': 'test'},
headers=headers
            
            
            data={
                'csrfmiddlewaretoken': login_response.cookies['csrftoken'],
                'transition': 28},
            headers=headers
            '''
