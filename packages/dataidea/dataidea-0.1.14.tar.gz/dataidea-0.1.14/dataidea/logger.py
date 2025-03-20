import requests
import os


def event_log(data:dict):
    '''
    Log an event to the DATAIDEA LOGGER API

    parameters:
    data: dict

    eg:
    data = {
        'api_key': '1234567890',
        'user_id': '1234567890',
        'message': 'This is a test message',
        'level': 'info',
        'metadata': {'test': 'test'}
    }
    '''
    url = 'https://loggerapi.dataidea.org/api/event-log/'
    response = requests.post(url, json=data)

    if response.status_code == 201:
        print('Event logged successfully')
    else:
        print('Failed to log event')

    return response.status_code


def llm_log(data:dict):
    '''
    Log an LLM event to the DATAIDEA LOGGER API

    parameters:
    data: dict

    eg:
    data = {
        'api_key': '1234567890',
        'user_id': '1234567890',
        'source': 'llm',
        'query': 'This is a test query',
        'response': 'This is a test response',
    }
    '''
    url = 'https://loggerapi.dataidea.org/api/llm-log/'
    response = requests.post(url, json=data)

    if response.status_code == 201:
        print('LLM event logged successfully')
    else:
        print('Failed to log LLM event')

    return response.status_code


if __name__ == '__main__':
    api_key = os.getenv('DATAIDEA_API_KEY')
    
    event_log({
        'api_key': api_key,
        'user_id': '1234567890',
        'message': 'This is a test message',
        'level': 'info',
        'metadata': {'test': 'test'}
    })

    llm_log({
        'api_key': api_key,
        'user_id': '1234567890',
        'source': 'llm',
        'query': 'This is a test query',
        'response': 'This is a test response',
    })