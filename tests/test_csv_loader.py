import json

from click.testing import CliRunner

import scripts.csv_loader as csv_loader


def test_csv_loader(tmp_path, monkeypatch):
    csv_path = tmp_path / 'sample.csv'
    csv_path.write_text('submitted_at,name\n01/01/24 10:00:00,Tester\n')

    messages = []

    class DummySQS:
        def send_message(self, QueueUrl, MessageBody):
            messages.append(json.loads(MessageBody))

    monkeypatch.setattr(csv_loader, 'sqs', DummySQS())
    monkeypatch.setenv('DATABASE_URL', 'sqlite://')
    runner = CliRunner()
    result = runner.invoke(csv_loader.main, ['--file', str(csv_path)])
    assert result.exit_code == 0
    assert messages and messages[0]['id'] == 1
