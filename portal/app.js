const e = React.createElement;

function App() {
  const [draft, setDraft] = React.useState('');
  const [copy, setCopy] = React.useState('');
  const [saved, setSaved] = React.useState(null);

  async function save() {
    const resp = await fetch('/api/drafts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ draft, copy }),
    });
    const data = await resp.json();
    setSaved(data.id);
  }

  return e('div', null,
    e('textarea', { value: draft, onChange: (ev) => setDraft(ev.target.value) }),
    e('textarea', { value: copy, onChange: (ev) => setCopy(ev.target.value) }),
    e('button', { onClick: save }, 'Save'),
    saved && e('div', null, `Saved as ${saved}`),
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(e(App));
