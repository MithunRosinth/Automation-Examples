from datetime import date
import json, os, requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

#######################################

def get_prod_id():
    print(f"Requesting Product ID for: {dd_product_name}")
    products = requests.get(
        f"{dd_url}/api/v2/products", headers={"Authorization": f"Token {dd_token}"}
    )
    for product in products.json()["results"]:
        if product["name"] == dd_product_name:
            dd_product_id = product["id"]
            print(f"Product ID for: {dd_product_name} is {dd_product_id}")
            return dd_product_id
    print("Product does not exists on defect dojo")
    return -1

########################################

def get_engagement_id():
    print(f"Requesting Engagement ID for: {dd_engagement_name}")
    engagements = requests.get(
        f"{dd_url}/api/v2/engagements", headers={"Authorization": f"Token {dd_token}"}
    )
    for engagement in engagements.json()["results"]:
        if engagement["name"] == dd_engagement_name:
            id = engagement["id"]
            print(f"Engagement ID for: {dd_engagement_name} is {id}")
            return id
    return -1

########################################

def create_prod():
    print(f"Creating new product on defectdojo with name {dd_product_name}")
    fields = {
        "name": dd_product_name,
        "product_name": dd_product_name,
        "prod_type": "1",
        "description": dd_product_desc,
    }
    product_creation_request = requests.post(
        f"{dd_url}/api/v2/products/",
        data=json.dumps(fields),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {dd_token}",
        },
    )
    product_id = product_creation_request.json()["id"]
    print(
        f"Created new product on defectdojo with name {dd_product_name} with id {product_id}"
    )
    return product_id

######################################

def create_eng():
    print(f"Creating new engagement on defectdojo with name {dd_engagement_name}")
    today = date.today()
    t_date = today.strftime("%Y-%m-%d")
    fields = {
        "name": dd_engagement_name,
        "product": str(get_prod_id()),
        "engagement_type": "CI/CD",
        "target_start": str(t_date),
        "prod_type": "1",
        "target_end": str(t_date),
        "description": f"Pipeline no: {dd_engagement_name} Scans",
    }
    engagement_creation_request = requests.post(
        f"{dd_url}/api/v2/engagements/",
        data=json.dumps(fields),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Token " + dd_token,
        },
    )
    dd_engagement_id = engagement_creation_request.json()["id"]
    print(
        f"Created new engagement on defectdojo with name {dd_product_name} with id {dd_engagement_id}"
    )
    return dd_engagement_id


if __name__ == "__main__":

    dd_url = os.environ["dd_url"]
    dd_username = os.environ["dd_username"]
    dd_password = os.environ["dd_password"]
    dd_product_name = os.environ["dd_product_name"]
    dd_product_desc = os.environ["dd_product_desc"]
    dd_engagement_name = f'Pipeline No {os.environ["pno"]}'

    print("Environment Variables Loaded")

    #######################################

    auth_request = requests.post(
        f"{dd_url}/api/v2/api-token-auth/",
        data=json.dumps({"username": dd_username, "password": dd_password}),
        headers={"Content-Type": "application/json"},
    )
    dd_token = auth_request.content.decode("UTF-8").split('"')[3]
    print("Authentication Token Generated")

    #######################################

    dd_product_id = get_prod_id()
    if dd_product_id == -1:
        dd_product_id = create_prod()
        dd_engagement_id = create_eng()
    else:
        dd_engagement_id = get_engagement_id()
        if dd_engagement_id == -1:
            dd_engagement_id = create_eng()
