import json
import types

import sqlalchemy as sa

import services.scorer.main as scorer


def setup_engine():
    engine = sa.create_engine('sqlite://')
    scorer.engine = engine
    scorer.metadata.create_all(engine)
    return engine


def create_eoi_raw(engine):
    eoi_raw = sa.Table(
        'eoi_raw',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('data', sa.JSON),
    )
    eoi_raw.create(engine)
    return eoi_raw


def test_process_message_openai_error(monkeypatch):
    engine = setup_engine()
    eoi_raw = create_eoi_raw(engine)
    with engine.begin() as conn:
        conn.execute(eoi_raw.insert().values(id=1, data={'foo': 'bar'}))

    dummy_sqs = types.SimpleNamespace(deleted=False)
    monkeypatch.setattr(scorer, 'sqs', dummy_sqs)
    monkeypatch.setattr(scorer, 'load_agenda', lambda: 'agenda')

    def raise_error(**_):
        raise RuntimeError('boom')

    monkeypatch.setattr(
        scorer.openai,
        'ChatCompletion',
        types.SimpleNamespace(create=raise_error),
    )

    msg = {'Body': json.dumps({'id': 1}), 'ReceiptHandle': 'rh'}
    scorer.process_message(msg)

    assert not dummy_sqs.deleted
    with engine.connect() as conn:
        row = conn.execute(sa.select(scorer.triage)).mappings().first()
    assert row is None


def test_handle_skips_when_no_messages(monkeypatch):
    calls = []

    class DummySQS:
        def __init__(self):
            self.count = 0

        def receive_message(self, **_):
            self.count += 1
            if self.count == 1:
                return {}
            raise KeyboardInterrupt()

    monkeypatch.setattr(scorer, 'sqs', DummySQS())
    monkeypatch.setattr(scorer, 'process_message', lambda msg: calls.append(msg))

    try:
        scorer.handle()
    except KeyboardInterrupt:
        pass

    assert calls == []
