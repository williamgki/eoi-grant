from click.testing import CliRunner

import scripts.embed_agenda as embed_agenda


def test_embed_agenda_creates_index(tmp_path, monkeypatch):
    agenda_path = tmp_path / 'agenda.md'
    agenda_path.write_text('one\n\n two')

    def dummy_create(*, input, model):
        assert input == ['one', 'two']
        return {'data': [{'embedding': [1.0, 0.0]}, {'embedding': [0.0, 1.0]}]}

    monkeypatch.setattr(embed_agenda.openai.Embedding, 'create', dummy_create)

    added = []

    class DummyIndex:
        def __init__(self, d):
            self.d = d

        def add(self, vecs):
            added.extend(vecs.tolist())

    index_inst = DummyIndex(2)
    monkeypatch.setattr(embed_agenda.faiss, 'IndexFlatL2', lambda d: index_inst)

    written = {}

    def dummy_write_index(index, path):
        written['index'] = index
        written['path'] = path

    monkeypatch.setattr(embed_agenda.faiss, 'write_index', dummy_write_index)

    runner = CliRunner()
    out_path = tmp_path / 'index.faiss'
    result = runner.invoke(
        embed_agenda.main, ['--agenda', str(agenda_path), '--output', str(out_path)]
    )
    assert result.exit_code == 0
    assert index_inst.d == 2
    assert added == [[1.0, 0.0], [0.0, 1.0]]
    assert written == {'index': index_inst, 'path': str(out_path)}
