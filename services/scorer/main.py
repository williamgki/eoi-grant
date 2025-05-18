import json
import os

import boto3
import openai
import sqlalchemy as sa

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///eoi.db')
QUEUE_URL = os.environ['SQS_QUEUE_URL']
AGENDAS_PATH = os.getenv('AGENDAS_PATH', 'knowledge/research_agenda.md')

secrets = boto3.client('secretsmanager')
openai.api_key = secrets.get_secret_value(SecretId=os.environ['OPENAI_API_KEY'])['SecretString']

sqs = boto3.client('sqs')
engine = sa.create_engine(DATABASE_URL)
metadata = sa.MetaData()
triage = sa.Table(
    'triage',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('data', sa.JSON, nullable=False),
)
metadata.create_all(engine)

def load_agenda() -> str:
    with open(AGENDAS_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def handle() -> None:
    msgs = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1)
    if 'Messages' not in msgs:
        return
    msg = msgs['Messages'][0]
    body = json.loads(msg['Body'])
    with engine.connect() as conn:
        row = conn.execute(sa.text('SELECT data FROM eoi_raw WHERE id=:id'), {'id': body['id']}).mappings().first()
    agenda = load_agenda()
    prompt = f"Agenda:\n{agenda}\n\nEntry:\n{row['data']}"
    resp = openai.ChatCompletion.create(model='openai/o3', messages=[{'role': 'user', 'content': prompt}])
    with engine.begin() as conn:
        conn.execute(triage.insert().values(data=resp['choices'][0]['message']['content']))
    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg['ReceiptHandle'])


if __name__ == '__main__':
    handle()
