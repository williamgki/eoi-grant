import json
from datetime import datetime
from importlib import reload

import boto3
import openai
import sqlalchemy as sa


def test_handle_processes_message(tmp_path, monkeypatch):
    agenda_path = tmp_path / 'agenda.md'
    agenda_path.write_text('my agenda')

    monkeypatch.setenv('AGENDAS_PATH', str(agenda_path))
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{tmp_path}/db.sqlite')
    monkeypatch.setenv('SQS_QUEUE_URL', 'qurl')
    monkeypatch.setenv('OPENAI_API_KEY', 'secret-id')

    class DummySQS:
        def __init__(self):
            self.deleted = False

        def receive_message(self, **kwargs):
            return {
                'Messages': [
                    {'Body': json.dumps({'id': 1}), 'ReceiptHandle': 'rh'}
                ]
            }

        def delete_message(self, **kwargs):
            self.deleted = True

    class DummySecrets:
        def get_secret_value(self, SecretId):
            return {'SecretString': 'openai-key'}

    dummy_sqs = DummySQS()

    def client(service, *args, **kwargs):
        if service == 'sqs':
            return dummy_sqs
        if service == 'secretsmanager':
            return DummySecrets()
        raise ValueError(service)

    monkeypatch.setattr(boto3, 'client', client)

    class DummyChat:
        @staticmethod
        def create(*args, **kwargs):
            return {'choices': [{'message': {'content': 'ok'}}]}

    monkeypatch.setattr(openai, 'ChatCompletion', DummyChat)

    import services.scorer.main as mod
    reload(mod)

    meta = sa.MetaData()
    eoi_raw = sa.Table(
        'eoi_raw',
        meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('submitted_at', sa.DateTime),
        sa.Column('data', sa.JSON),
    )
    meta.create_all(mod.engine)

    with mod.engine.begin() as conn:
        conn.execute(
            eoi_raw.insert().values(
                id=1,
                submitted_at=datetime.utcnow(),
                data={'foo': 'bar'},
            )
        )

    mod.handle()

    with mod.engine.connect() as conn:
        row = conn.execute(mod.triage.select()).mappings().first()
    assert row['data'] == 'ok'
    assert dummy_sqs.deleted
