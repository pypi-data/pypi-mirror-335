import requests
import aiohttp

def data_common(url, token, _id, nid, date_from, date_to, group_id):
    uri = url + "/api/v1.0/data"

    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'token': token
    }

    # only for administrators
    if group_id is not None:
        header['grpid'] = group_id

    params = {}
    
    if nid is not None:
        params['nid'] = nid
    elif _id is not None:
        params['_id'] = _id
        
    if date_from is not None:
        params['from'] = date_from

    if date_to is not None:
        params['to'] = date_to

    return uri, header, params
    
def data(url, token, _id=None, nid=None, date_from=None, date_to=None, group_id=None, verify=True, timeout=60):
    uri, header, params = data_common(url, token, _id, nid, date_from, date_to, group_id)

    try:
        r = requests.delete(uri, json=params, headers=header, verify=verify, timeout=timeout)
    except Exception as e:
        print(e)
        return False, None
    
    if r.status_code == 200:
        return True, r.json()
    else:
        return False, r.json()

async def async_data(url, token, _id=None, nid=None, date_from=None, date_to=None, group_id=None, verify=True, timeout=60):
    uri, header, params = data_common(url, token, _id, nid, date_from, date_to, group_id)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=True, verify_ssl=verify)) as session:
        async with session.delete(uri, headers=header, json=params) as response:
            if response.status == 200:
                return True, await response.json()
            else:
                return False, await response.json()

