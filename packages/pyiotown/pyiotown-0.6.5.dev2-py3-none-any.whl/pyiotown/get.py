import requests
import aiohttp

def node_common(url, token, nid, group_id, include_lorawan_session):
    header = {'Accept':'application/json','token':token}

    # only for administrators
    if group_id is not None:
        header['grpid'] = group_id

    uri = url + "/api/v1.0/" + ("nodes" if nid is None else f"node/{nid}")

    if include_lorawan_session == False:
        uri += '/without-lorawan-session'

    return uri, header

def node(url, token, nid=None, group_id=None, verify=True, timeout=60, include_lorawan_session=True):
    uri, header = node_common(url, token, nid, group_id)
    
    try:
        r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
    except Exception as e:
        print(e)
        return False, None
    
    if r.status_code == 200:
        result = r.json()['nodes'] if nid is None else r.json()['node']
        return True, result
    else:
        return False, r.json()

async def async_node(url, token, nid=None, group_id=None, verify=True, timeout=60, include_lorawan_session=True):
    uri, header = node_common(url, token, nid, group_id, include_lorawan_session)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=True, verify_ssl=verify)) as session:
        async with session.get(uri, headers=header) as response:
            result = await response.json()
            
            if response.status == 200:
                return True, result['nodes'] if nid is None else result['node']
            else:
                return False, result

def storage_common(url, token, nid, date_from, date_to, count, sort, group_id):
    header = {'Accept':'application/json','token':token}

    # only for administrators
    if group_id is not None:
        header['grpid'] = group_id

    uri = url + "/api/v1.0/storage"

    params = []
    
    if nid is not None:
        params.append(f"nid={nid}")
        
    if date_from is not None:
        params.append(f"from={date_from}")

    if date_to is not None:
        params.append(f"to={date_to}")

    if count is not None:
        params.append(f"count={count}")

    if sort is not None:
        params.append(f"sort={sort}")

    if len(params) > 0:
        uri += '?' + '&'.join(params)

    return uri, header
        
def storage(url, token, nid=None, date_from=None, date_to=None, count=None, sort=None, lastKey=None, consolidate=True, group_id=None, verify=True, timeout=60):
    uri_prefix, header = storage_common(url, token, nid, date_from, date_to, count, sort, group_id)

    result = None
    
    while True:
        try:
            uri = uri_prefix
            if lastKey is not None:
                uri += "&lastKey=" + lastKey
            r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
        except Exception as e:
            print(e)
            return False, None
    
        if r.status_code == 200:
            data_obj = r.json()
            if result is None:
                # at first
                result = data_obj
                
                # if 'lastKey' in result.keys():
                #     del result['lastKey']
            else:
                result['data'] += data_obj['data']
                if 'lastKey' in data_obj.keys():
                    result['lastKey'] = data_obj['lastKey']
                elif 'lastKey' in result.keys():
                    del result['lastKey']

            if consolidate == True and 'lastKey' in result.keys():
                lastKey = result['lastKey']
            else:
                return True, result
        else:
            print(r)
            return False, r.json()

async def async_storage(url, token, nid=None, date_from=None, date_to=None, count=None, sort=None, lastKey=None, consolidate=True, group_id=None, verify=True, timeout=60):
    uri_prefix, header = storage_common(url, token, nid, date_from, date_to, count, sort, group_id)

    result = None

    while True:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=True, verify_ssl=verify)) as session:
            uri = uri_prefix
            if lastKey is not None:
                uri += "&lastKey=" + lastKey
            
            async with session.get(uri, headers=header) as response:
                if response.status == 200:
                    data = await response.json()
                    if result is None:
                        result = data
                    else:
                        result['data'] += data['data']
                        if 'lastKey' in data.keys():
                            result['lastKey'] = data['lastKey']
                        elif 'lastKey' in result.keys():
                            del result['lastKey']

                    if consolidate == True and 'lastKey' in result.keys():
                        lastKey = result['lastKey']
                    else:
                        return True, result
                else:
                    return False, await response.json()


def command_common(url, token, nid, group_id):
    uri = f"{url}/api/v1.0/command/{nid}"
    header = {
        'Accept': 'application/json',
        'token': token
    }

    if group_id is not None:
        header['grpid'] = group_id

    return uri, header

def command(url, token, nid, group_id=None, verify=True, timeout=60):
    uri, header = command_common(url, token, nid, group_id)

    try:
        r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, r.json()
    except Exception as e:
        print(e)
        return False, None

async def async_command(url, token, nid, group_id=None, verify=True, timeout=60):
    uri, header = command_common(url, token, nid, group_id)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=True, verify_ssl=verify)) as session:
        async with session.get(uri, headers=header) as response:
            if response.status == 200:
                return True, await response.json()
            else:
                return False, await response.json()

def file(url, token, file_id, group_id=None, verify=True, timeout=60):
    uri = url + "/api/v1.0/file/" + file_id
    header = {'token':token}
    if group_id is not None:
        header['grpid'] = group_id
        
    try:
        r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
        if r.status_code == 200:
            return True, r.content
        else:
            print(r)
            return False, r
    except Exception as e:
        print(e)
        return False, None

def downloadAnnotations(url, token, classname, verify=True, timeout=60):
    ''' 
    url : IoT.own Server Address
    token : IoT.own API Token
    classname : Image Class ex) car, person, airplain
    '''
    uri = url + "/api/v1.0/nn/images?labels=" + classname
    header = {'Accept':'application/json', 'token':token}
    try:
        r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        else:
            print(r)
            return None
    except Exception as e:
        print(e)
        return None
