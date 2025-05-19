import json
import logging
import os

import boto3
import openai
import sqlalchemy as sa
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def process_message(msg: dict) -> None:
    body = json.loads(msg['Body'])
    try:
        with engine.connect() as conn:
            row = conn.execute(
                sa.text('SELECT data FROM eoi_raw WHERE id=:id'),
                {'id': body['id']},
            ).mappings().first()
    except Exception as exc:  # pragma: no cover - logging only
        logger.exception('Database read failed: %s', exc)
        return

    if not row:
        logger.error('No entry for id %s', body['id'])
        return

    agenda = load_agenda()

    prompt = f"""
    You are evaluating Expressions of Interest (EOIs) for a safety-research grant.
    
    Agenda summary:
    {agenda}
    
    EOI submission (JSON):
    {row['data']}
    
    Task 1 – Decide the best next step  
     • review_research_areas  – applicant is mis-aligned with our agenda  
     • request_more_detail    – idea seems promising but vague  
     • challenge_fund         – idea fits and is detailed  
    
    Task 2 – For **each** path, write a polite email draft in the style of the examples below.  
    Return a JSON object with keys:  
      recommended_path, drafts.challenge_fund, drafts.request_more_detail, drafts.review_research_areas
    """

    try:
        resp = openai.ChatCompletion.create(
            model='openai/o3',
            messages=[{'role': 'user', 'content': prompt}],
        )
    except Exception as exc:  # pragma: no cover - logging only
        logger.exception('OpenAI request failed: %s', exc)
        return

    try:
        with engine.begin() as conn:
            conn.execute(
                triage.insert().values(
                    data=resp['choices'][0]['message']['content'],
                )
            )
    except Exception as exc:  # pragma: no cover - logging only
        logger.exception('Database write failed: %s', exc)
        return

    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg['ReceiptHandle'])


def handle() -> None:
    while True:
        try:
            msgs = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
            )
            if 'Messages' not in msgs:
                continue
            for msg in msgs['Messages']:
                process_message(msg)
        except Exception as exc:  # pragma: no cover - logging only
            logger.exception('Receive/process failed: %s', exc)
            time.sleep(5)


if __name__ == '__main__':
    handle()
