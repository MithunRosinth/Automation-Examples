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

######################################


def create_upload(dd_engagement_id):
    return MultipartEncoder(
        {
            "scan_type": "ZAP Scan",
            "product_name": dd_product_name,
            "engagement_name": dd_engagement_name,
            "name": dd_engagement_name,
            "engagement": str(dd_engagement_id),
            "file": (
                result_path[0],
                open("/results/" + result_path[0], "rb"),
                "application/json",
            ),
        }
    )


################################################################################

def upload_scan(dd_engagement_id):
    print("uploading results to defectdojo")
    encoder = create_upload(dd_engagement_id)


    results_upload_request = requests.post(
        f"{dd_url}/api/v2/import-scan/",
        data=encoder,
        headers={
            "Content-Type": encoder.content_type,
            "Authorization": "Token " + dd_token,
        },
    )
    print(f"\n\nResults Uploaded to Defectdojo {results_upload_request}")


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
    
    result_path = os.listdir("/results")

    dd_product_id = get_prod_id()
    dd_engagement_id = get_engagement_id()

    print("Uploading results now!")
    upload_scan(dd_engagement_id)