import os
import json
from tf_core import tf_command

@tf_command("create")
def create(**kwargs):
    if kwargs["flowtype"] == "airflow":
        db = json.load(open("db.json", mode="r"))
        db['flows'].append({
            "name": kwargs["name"],
            "address": kwargs["address"],
            "flowtype": kwargs["flowtype"],
            "host":  kwargs["host"],
            "username":  kwargs["username"],
            "password":  kwargs["password"],
        })
        json.dump(db, open("db.json", mode="w"), indent=4)
    else:
        raise NotImplementedError()

@tf_command("test")
def test(**kwargs):
    from tf_core.io import OnpremIO
    db = json.load(open("db.json", mode="r"))
    for flow in db['flows']:
        if flow['name'] == kwargs['name']:
            with OnpremIO(flow['host'], username=flow['username'], password=flow['password']) as io:
                print(io.isdir(flow['address']))

@tf_command("download")
def download_dags(**kwargs):
    from tf_core.io import OnpremIO, GoogleCloudIO
    db = json.load(open("db.json", mode="r"))
    for flow in db['flows']:
        if flow['name'] == kwargs['name']:
            if flow['flowtype'] == 'airflow':
                with OnpremIO(flow['host'], username=flow['username'], password=flow['password']) as io:
                    io.download_folder(
                        io.join(flow['address'], "dags"), 
                        os.path.abspath("dags")
                    )
            elif flow['flowtype'] == 'composer':
                with GoogleCloudIO(flow['service_account'], bucket_name=flow['bucket_name']) as io:
                    io.download_folder(
                        io.join("dags"), 
                        os.path.abspath("dags")
                    )

# def upload_dags(**kwargs):
#     from tf_core.io import OnpremIO
#     db = json.load(open("db.json", mode="r"))
#     for flow in db['flows']:
#         if flow['name'] == kwargs['name']:
#             with OnpremIO(flow['host'], username=flow['username'], password=flow['password']) as io:
#                 io.upload_folder(
#                     os.path.abspath("dags"),
#                     flow['address'] + "/dags"
#                 )
