import base64
import io
import json

import pandas as pd

import scripts.csv_loader as csv_loader


def lambda_handler(event, context):
    """Receive a CSV payload and pass it to ``csv_loader``."""
    body = event.get("body", "")
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    df = pd.read_csv(io.StringIO(body), parse_dates=["submitted_at"], dayfirst=True)
    csv_loader.load_dataframe(df)
    return {"statusCode": 200, "body": json.dumps({"status": "ok"})}

