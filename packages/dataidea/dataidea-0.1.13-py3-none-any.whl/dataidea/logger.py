import requests
import os

def login(username:str, password:str):
    url = 'https://loggerapi.dataidea.org/api/auth/token/'
    response = requests.post(url, json={'username': username, 'password': password})

    # save in the environment variable
    os.environ['DATAIDEA_ACCESS_TOKEN'] = response.json()['access']
    os.environ['DATAIDEA_REFRESH_TOKEN'] = response.json()['refresh']

    print(f"Login successful for {username}")
    return response.json()

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

# def get_event_logs():
#     '''
#     Get event logs from the DATAIDEA LOGGER API
#     '''
#     access_token = os.getenv('DATAIDEA_ACCESS_TOKEN')

#     url = 'https://loggerapi.dataidea.org/api/event-log/'
#     response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
#     return response.json()


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


# def get_llm_event_logs():
#     '''
#     Get LLM event logs from the DATAIDEA LOGGER API
#     '''
#     access_token = os.getenv('DATAIDEA_ACCESS_TOKEN')
#     url = 'https://loggerapi.dataidea.org/api/llm-log/'
#     response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
#     return response.json()


if __name__ == '__main__':
    api_key = os.getenv('DATAIDEA_API_KEY')

    login('jumashafara', 'Chappie@256')
    
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