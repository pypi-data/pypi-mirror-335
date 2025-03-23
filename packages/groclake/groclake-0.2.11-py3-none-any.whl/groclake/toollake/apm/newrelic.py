import requests
import json

class Newrelic:
    def __init__(self, api_key, account_id):
        self.api_key = api_key
        self.account_id = account_id
        self.nrql_url = "https://api.newrelic.com/graphql"
        self.headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def execute_nrql(self, nrql_query):
        """
        .

        Returns:
            dict: A dictionary containing the HTTP error metrics.
        """
        NRQL_QUERY = f"""
            {{
            actor {{
                account(id: {self.account_id}) {{
                nrql(query: "{nrql_query}") {{
                    results
                }}
                }}
            }}
            }}
            """
        payload = {
            "query": NRQL_QUERY
        }
        
        print(payload)
        response = requests.post(self.nrql_url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data: {response.status_code}")
            return None

        
