import pandas as pd
import json
import time
import requests


def query_databricks_tables_api(query, endpoint, token, warehouse_id):
    ## REST API CONFIG ##
    api = "/api/2.0/sql/statements/"
    api_url = f"https://{endpoint}{api}"
    warehouse_state_api = f"https://{endpoint}/api/2.0/sql/warehouses/{warehouse_id}"

    # API REQUEST HEADER
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # STRING TYPE INPUT
    if not isinstance(query, str):
        raise Exception("Query needs to be a String Type!")

    # API BODY
    payload = {
        "warehouse_id": warehouse_id,
        "statement": query,
        "disposition": "EXTERNAL_LINKS",
        "format": "JSON_ARRAY"
    }

    ## API POST, RUN QUERY ##
    response = requests.post(
        api_url,
        headers=headers,
        json=payload
    )

    # CHECK RETURN
    if response.status_code == 200:
        statement_id = response.json()["statement_id"]
        print(f"SQL statement submitted successfully. Statement ID: {statement_id}")
        # print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.status_code} - {response.text}")
        # raise Exception(f"Error: {response.status_code} - {response.text}")

    # CHECK STATE OF STATEMENT
    wait = True
    while wait:
        print('Waiting api return!')
        statement_current_state = requests.get(
            f"{api_url}{statement_id}",
            headers=headers
        )

        # RAISE EXCEPTION IF SOME ISSUE OCCURED WITH THE STATEMENT
        if statement_current_state.json()["status"]["state"] in ('FAILED', 'CANCELED', 'CLOSED'):
            raise Exception(
                "Statement ended, reason: {exception} | Message: {message}!".format(
                    exception=statement_current_state.json()["status"]["state"],
                    message=statement_current_state.json()["status"]["error"]["message"]
                )
            )
        else:
            # CHECK IF CLUSTER IS RUNNING
            cluster_current_state = requests.get(
                warehouse_state_api,
                headers=headers
            )
            if cluster_current_state.json()["state"] != 'RUNNING':
                time.sleep(120)
            else:
                # CHECK CURRENT STATE OF THE STATEMENT
                # print( statement_current_state.json() )
                wait = statement_current_state.json()["status"]["state"] != 'SUCCEEDED'

    # GET COLUMN NAMES FROM API RETURN
    columns = [col["name"] for col in statement_current_state.json()["manifest"]["schema"]["columns"]]

    # GET DATA FROM EXTERNAL LINKS
    array_to_become_df = []
    # print(statement_current_state.json()["manifest"]["total_chunk_count"])
    for n in range(statement_current_state.json()["manifest"]["total_chunk_count"]):
        # print(f"Current chunk: {n}!")
        external_link = \
        requests.get(
            f'{api_url}{statement_id}/result/chunks/{n}',
            headers=headers
        ).json()["external_links"][0]["external_link"]
        for row in requests.get(external_link).json():
            array_to_become_df.append(row)
        # print(requests.get( external_link ).json())

    # RETURN PANDAS DATAFRAME
    # print(len(array_to_become_df))
    return pd.DataFrame(
        data=array_to_become_df,
        columns=columns
    )
