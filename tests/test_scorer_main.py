import json
import types

import sqlalchemy as sa

import services.scorer.main as scorer


def test_handle_processes_message(monkeypatch):
    messages = [
        {
            'Body': json.dumps({'id': 1}),
            'ReceiptHandle': 'r1',
        }
    ]

    class DummySQS:
        def __init__(self):
            self.calls = 0
            self.deleted = False

        def receive_message(self, **kwargs):
            assert kwargs.get('WaitTimeSeconds') == 20
            self.calls += 1
            if self.calls == 1:
                return {'Messages': messages}
            raise KeyboardInterrupt()

        def delete_message(self, QueueUrl, ReceiptHandle):
            self.deleted = True
            assert ReceiptHandle == 'r1'

    dummy_sqs = DummySQS()
    monkeypatch.setattr(scorer, 'sqs', dummy_sqs)

    def dummy_create(**_):
        return {'choices': [{'message': {'content': 'ok'}}]}

    monkeypatch.setattr(scorer.openai, 'ChatCompletion', types.SimpleNamespace(create=dummy_create))
    monkeypatch.setattr(scorer, 'load_agenda', lambda: 'agenda')

    engine = sa.create_engine('sqlite://')
    scorer.engine = engine
    scorer.metadata.create_all(engine)
    eoi_raw = sa.Table(
        'eoi_raw',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('data', sa.JSON),
    )
    eoi_raw.create(engine)
    with engine.begin() as conn:
        conn.execute(eoi_raw.insert().values(id=1, data={'foo': 'bar'}))

    try:
        scorer.handle()
    except KeyboardInterrupt:
        pass

    with engine.connect() as conn:
        row = conn.execute(sa.select(scorer.triage)).mappings().first()

    assert dummy_sqs.deleted
    assert row['data'] == 'ok'
