import json
import requests
import os
import pandas as pd
import numpy as np
import time
import lz4.frame
import lz4.frame as lz4f


from SharedData.IO.SyncTable import SyncTable
from SharedData.Logger import Logger
from SharedData.Database import *


class ClientAPI:
    
    @staticmethod
    def table_subscribe_thread(table, host, port,
            lookbacklines=1000, lookbackdate=None, snapshot=False,
            bandwidth=1e6, protocol='http'):

        apiurl = f"{protocol}://{host}:{port}"
        
        records = table.records
        
        params = {                    
            'token': os.environ['SHAREDDATA_TOKEN'],            
        }

        tablename = table.tablename
        tablesubfolder = None
        if '/' in table.tablename:
            tablename = table.tablename.split('/')[0]
            tablesubfolder = table.tablename.split('/')[1] 

        url = apiurl+f"/api/subscribe/{table.database}/{table.period}/{table.source}/{tablename}"
        
        lookbackid = records.count - lookbacklines
        if tablesubfolder:
            params['tablesubfolder'] = tablesubfolder        
        if lookbacklines:
            params['lookbacklines'] = lookbacklines
        if lookbackdate:
            params['lookbackdate'] = lookbackdate
            lookbackdate = pd.Timestamp(lookbackdate)
            lookbackid, _ = records.get_date_loc(lookbackdate)
        if bandwidth:
            params['bandwidth'] = bandwidth
                
        hasindex = records.table.hasindex           
        lastmtime = pd.Timestamp('1970-01-01')
        if hasindex:
            lastmtime = np.max(records[lookbackid:]['mtime'])
            lastmtime = pd.Timestamp(np.datetime64(lastmtime))
        while True:
            try:
                params['page'] = 1
                if hasindex:
                    params['mtime'] = lastmtime
                params['count'] = records.count
                params['snapshot'] = snapshot
                snapshot = False

                response = requests.get(url, params=params)
                if response.status_code != 200:
                    if response.status_code == 204:
                        time.sleep(1)
                        continue
                    else:
                        raise Exception(response.status_code, response.text)
                
                data = lz4.frame.decompress(response.content)
                buffer = bytearray()
                buffer.extend(data)
                if len(buffer) >= records.itemsize:
                    # Determine how many complete records are in the buffer
                    num_records = len(buffer) // records.itemsize
                    # Take the first num_records worth of bytes
                    record_data = buffer[:num_records *
                                                records.itemsize]
                    # And remove them from the buffer
                    del buffer[:num_records *
                                        records.itemsize]
                    # Convert the bytes to a NumPy array of records
                    rec = np.frombuffer(
                        record_data, dtype=records.dtype)
                    if hasindex:
                        recmtime = pd.Timestamp(np.max(rec['mtime']))
                        if recmtime > lastmtime:
                            lastmtime = recmtime
                        
                    if records.table.hasindex:
                        # Upsert all records at once
                        records.upsert(rec)
                    else:
                        # Extend all records at once
                        records.extend(rec)

                pages = int(response.headers['Content-Pages'])
                if pages > 1:
                    # paginated response
                    for i in range(2, pages+1):
                        params['page'] = i                        
                        response = requests.get(url, params=params)
                        if response.status_code != 200:
                            raise Exception(response.status_code, response.text)
                        data = lz4.frame.decompress(response.content)
                        buffer = bytearray()
                        buffer.extend(data)
                        if len(buffer) >= records.itemsize:
                            # Determine how many complete records are in the buffer
                            num_records = len(buffer) // records.itemsize
                            # Take the first num_records worth of bytes
                            record_data = buffer[:num_records *
                                                        records.itemsize]
                            # And remove them from the buffer
                            del buffer[:num_records *
                                                records.itemsize]
                            # Convert the bytes to a NumPy array of records
                            rec = np.frombuffer(
                                record_data, dtype=records.dtype)
                            if hasindex:
                                recmtime = pd.Timestamp(np.max(rec['mtime']))
                                if recmtime > lastmtime:
                                    lastmtime = recmtime
                                
                            if records.table.hasindex:
                                # Upsert all records at once
                                records.upsert(rec)
                            else:
                                # Extend all records at once
                                records.extend(rec)
                        time.sleep(0.5)

                time.sleep(1)

            except Exception as e:
                msg = 'Retrying API subscription %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                     table.source, table.tablename, str(e))
                Logger.log.warning(msg)
                time.sleep(15)


    @staticmethod
    def table_publish_thread(table, host, port, lookbacklines, 
        lookbackdate, snapshot,bandwidth, protocol='http'):

        if port is None:
            apiurl = f"{protocol}://{host}"
        else:
            apiurl = f"{protocol}://{host}:{port}"
        
        while True:
            try:
                records = table.records
                
                params = {                    
                    'token': os.environ['SHAREDDATA_TOKEN'],            
                }

                tablename = table.tablename
                tablesubfolder = None
                if '/' in table.tablename:
                    tablename = table.tablename.split('/')[0]
                    tablesubfolder = table.tablename.split('/')[1] 

                url = apiurl+f"/api/publish/{table.database}/{table.period}/{table.source}/{tablename}"
                                
                if tablesubfolder:
                    params['tablesubfolder'] = tablesubfolder        
                if lookbacklines:
                    params['lookbacklines'] = lookbacklines
                if lookbackdate:
                    params['lookbackdate'] = lookbackdate
                    lookbackdate = pd.Timestamp(lookbackdate)            
                if bandwidth:
                    params['bandwidth'] = bandwidth
                
                
                # ask for the remote table mtime and count

                response = requests.get(url, params=params)

                if response.status_code != 200:
                    raise Exception(response.status_code, response.text)

                response = response.json()
                remotemtime = None
                if 'mtime' in response:
                    remotemtime = pd.Timestamp(response['mtime']).replace(tzinfo=None)
                remotecount = response['count']

                client = {}
                client.update(params)
                if 'mtime' in response:
                    client['mtime'] = remotemtime.timestamp()
                client['count'] = remotecount
                client = SyncTable.init_client(client,table)

                while True:
                    try:
                        client, ids2send = SyncTable.get_ids2send(client)
                        if len(ids2send) == 0:
                            time.sleep(0.001)                            
                        else:
                            rows2send = len(ids2send)
                            sentrows = 0
                            msgsize = min(client['maxrows'], rows2send)
                            bandwidth = client['bandwidth']
                            tini = time.time_ns()
                            bytessent = 0
                            while sentrows < rows2send:
                                t = time.time_ns()
                                message = records[ids2send[sentrows:sentrows +
                                                        msgsize]].tobytes()
                                compressed = lz4f.compress(message)
                                msgbytes = len(compressed)
                                bytessent+=msgbytes                        
                                msgmintime = msgbytes/bandwidth                        
                                
                                # create a post request
                                response = requests.post(url, params=params, data=compressed)
                                if response.status_code != 200:
                                    raise Exception('Failed to publish data remote!=200 !')

                                sentrows += msgsize
                                msgtime = (time.time_ns()-t)*1e-9
                                ratelimtime = max(msgmintime-msgtime, 0)
                                if ratelimtime > 0:
                                    time.sleep(ratelimtime)

                            totalsize = (sentrows*records.itemsize)/1e6
                            totaltime = (time.time_ns()-tini)*1e-9
                            if totaltime > 0:
                                transfer_rate = totalsize/totaltime
                            else:
                                transfer_rate = 0
                            client['transfer_rate'] = transfer_rate
                            client['upload'] += msgbytes
                        
                    except:
                        break

            except Exception as e:
                msg = 'Retrying API publish %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                        table.source, table.tablename, str(e))
                Logger.log.warning(msg)
                time.sleep(15)

    @staticmethod
    def get_table(database, period, source, tablename, 
            host, port=None,
            startdate=None, enddate=None, 
            symbols=None, portfolios=None, page=None, per_page=None,
            output_format=None, token=None, user=None):
            
        url = host
        if port:
            url = f"{url}:{port}"

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/table/{database}/{period}/{source}/{tablename}'
        url += route

        
        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if startdate:
            params['startdate'] = startdate
        if enddate:
            params['enddate'] = enddate
        if symbols:
            params['symbols'] = symbols
        if portfolios:
            params['portfolios'] = portfolios
        if user:
            params['user'] = user

        # Make the GET request
        response = requests.get(url, params=params)
        response.raise_for_status()
        rjson = json.loads(response.content)
        if 'data' in rjson:
            df = pd.DataFrame(rjson['data'])
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            pkey = DATABASE_PKEYS[database]
            df = df.set_index(pkey).sort_index()
        else:
            df = pd.DataFrame([])

        return df