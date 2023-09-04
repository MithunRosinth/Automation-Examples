from unittest import result
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import yaml
from git import Repo
import os
from datetime import date
import subprocess
from pathlib import Path

################ AUTHENTICATION METHOD ################

def auth():
    creds={
        'username' : '',
        'password' : ''
    }
    r = requests.post(DD_URL+'/api/v2/api-token-auth/',
    data=json.dumps(creds),headers={'Content-Type': 'application/json'} )
    return r.content.decode('UTF-8').split('"')[3]

################ PRODUCT CREATION ################

def create_prod():
    tags=[]
    for i in config_data['tags']:
        tags.append(i)
    fields={
    'name': config_data['product_name'],
    'product_name': config_data['product_name'],
    'prod_type':'1',
    'tags': tags,
    'description': config_data['product_description']
    }
    r = requests.post(DD_URL+'/api/v2/products/',
    data=json.dumps(fields),headers={'Content-Type': 'application/json',
    'Authorization': 'Token '+DD_TOKEN} )
    return r.json()['id']

################ PRODUCT DELETION ################

def delete_prod(PROD_ID):
    r = requests.delete(DD_URL+'/api/v2/products/'+PROD_ID, headers={'Authorization': 'Token '+DD_TOKEN})

################ CREATE ENGAGEMENT ################

def create_eng(PROD_ID):
    fields={
    'name': config_data['engagement_name'],
    'product':str(PROD_ID),
    'engagement_type':'CI/CD',
    'target_start': str(t_date),
    'prod_type':'1',
    'target_end': str(t_date),
    'description': config_data['engagement_description']
    }
    r = requests.post(DD_URL+'/api/v2/engagements/',
    data=json.dumps(fields),headers={'Content-Type': 'application/json',
    'Authorization': 'Token '+DD_TOKEN} )
    print(r.content)

################ SCAN UPLOAD ################

def upload_scan(result_file,result_path):
    mp_encoder = MultipartEncoder(
    fields={
        'scan_type': result_file.split('.')[0].replace("/", ""),
        'product_name':'test',
        'engagement_name': config_data['engagement_name'],
        'name':'test_en',
        'engagement': str(get_eng_id()),
        'file':(result_file, open(result_path, 'rb'), 'application/json')
        }
    )
    r = requests.post(DD_URL+'/api/v2/import-scan/',
        data=mp_encoder,headers={'Content-Type': mp_encoder.content_type,
        'Authorization': 'Token '+DD_TOKEN} )
    print(r.content)

################ UPLOAD CONFIG ################

def result_publish(result_repo_dir):
    for filename in os.listdir(result_repo_dir):
        if(filename.startswith('.')):
            continue
        result_file='/'+filename
        result_path=result_repo_dir+'/'+filename
        upload_scan(result_file, result_path)

################ VALIDATIONS ################

def check_prod_exists():
    fields={
        'name': config_data['product_name']
    }
    r=requests.get(DD_URL+'/api/v2/products',data=json.dumps(fields),headers={'Authorization': 'Token '+DD_TOKEN})
    if(r.json()['count']==0):
        return 0
    else:
        return 1

def check_eng_exists():
    fields={
        'name': config_data['engagement_name']
    }
    r=requests.get(DD_URL+'/api/v2/engagements',data=json.dumps(fields),headers={'Authorization': 'Token '+DD_TOKEN})
    if(r.json()['count']==0):
        return 0
    else:
        return 1

################ DATA RETRIEVAL ################

def get_prod_id():
    fields={
        'name': config_data['product_name']
    }
    r=requests.get(DD_URL+'/api/v2/products',data=json.dumps(fields),headers={'Authorization': 'Token '+DD_TOKEN})
    return r.json()['results'][0]['id']

def get_eng_id():
    fields={
        'name': config_data['engagement_name']
    }
    r=requests.get(DD_URL+'/api/v2/engagements',data=json.dumps(fields),headers={'Authorization': 'Token '+DD_TOKEN})
    return r.json()['results'][0]['id']

################ TOOL CONFIG ################

def tool_config():
    fields_data={
        "name": "string",
        "description": "string",
        "url": "string",
        "authentication_type": "API",
        "api_key": "string",
        "tool_type": 1
    }
    r = requests.post(DD_URL+'/api/v2/tool_configurations/',
    data=json.dumps(fields_data),headers={'Content-Type': 'application/json',
    'Authorization': 'Token '+DD_TOKEN} )
    global config_id
    config_id=r.json()['result'][0]['id']

################ API SCAN CONFIG ################

def sonar_api_scan_config():
    fields_data={
        "service_key_1": "<Placeholder for sonar project key>",
        "product": get_prod_id(),
        "tool_configuration": config_id
    }
    r = requests.post(DD_URL+'/api/v2/product_api_scan_configurations/',
    data=json.dumps(fields_data),headers={'Content-Type': 'application/json',
    'Authorization': 'Token '+DD_TOKEN} )
    

################ PARAMETERS CONFIG ################

today=date.today()
t_date=today.strftime('%Y-%m-%d')

dd_ip=open(str(Path.home())+'/config/ip_vol/dd_ip.yaml','r')
dd_ip_data=yaml.load(dd_ip, Loader=yaml.SafeLoader)
DD_IP=dd_ip_data['DD_IP']
dd_ip.close()
DD_URL='http://'+DD_IP+':8000'

################ AUTHENTICATION ################

DD_TOKEN=auth()

################ CONFIG LOAD ################

config_file=open(str(Path.home())+'/config/defect_dojo/dd_conf.yaml','r')
config_data=yaml.load(config_file, Loader=yaml.SafeLoader)