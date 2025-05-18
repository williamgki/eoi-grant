import json
import os

import boto3
import click
import pandas as pd
from sqlalchemy import Column, DateTime, Integer, MetaData, Table, JSON, create_engine

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///eoi.db')
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

engine = create_engine(DATABASE_URL)
metadata = MetaData()

eoi_raw = Table(
    'eoi_raw',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('submitted_at', DateTime, nullable=False),
    Column('data', JSON, nullable=False),
)
metadata.create_all(engine)

sqs = boto3.client('sqs') if SQS_QUEUE_URL else None

@click.command()
@click.option('--file', 'file_path', required=True, type=click.Path(exists=True))
def main(file_path: str) -> None:
    """Load CSV rows into the database and notify SQS."""
    df = pd.read_csv(file_path, parse_dates=['submitted_at'], dayfirst=True)

    with engine.begin() as conn:
        for _, row in df.iterrows():
            result = conn.execute(
                eoi_raw.insert().values(
                    submitted_at=row['submitted_at'],
                    data=row.to_dict(),
                )
            )
            pk = result.inserted_primary_key[0]
            if sqs:
                sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps({'id': pk}))

if __name__ == '__main__':
    main()
