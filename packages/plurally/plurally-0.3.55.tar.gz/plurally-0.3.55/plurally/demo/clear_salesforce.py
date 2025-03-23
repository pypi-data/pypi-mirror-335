from simple_salesforce import Salesforce

session_id = ""
sf = Salesforce(session_id=session_id, instance_url="https://plurally2-dev-ed.develop.my.salesforce.com")

for account in sf.query_all("SELECT Id, Name FROM Account")["records"]:
    events = sf.query_all(f"SELECT Id FROM Event WHERE WhatId = '{account['Id']}'")["records"]

    for event in events:
        sf.Event.delete(event["Id"])
