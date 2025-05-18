import base64

import pandas as pd

import scripts.upload_csv_lambda as upl
import scripts.csv_loader as csv_loader


def test_lambda_handler(monkeypatch):
    captured = {}

    def dummy_load_dataframe(df: pd.DataFrame) -> None:
        captured['df'] = df

    monkeypatch.setattr(csv_loader, 'load_dataframe', dummy_load_dataframe)

    csv_bytes = b'submitted_at,name\n01/01/24 10:00:00,Tester\n'
    event = {
        'body': base64.b64encode(csv_bytes).decode('utf-8'),
        'isBase64Encoded': True,
    }

    resp = upl.lambda_handler(event, None)

    assert resp['statusCode'] == 200
    assert 'df' in captured
    assert list(captured['df']['name']) == ['Tester']
