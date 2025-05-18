# EOI Grant

## Quick start

```bash
git clone <repo>
cd eoi-grant
make init
make plan
python scripts/csv_loader.py --file sample.csv
```

## Release tarball

Create a compressed archive of the project without the `.git` directory:

```bash
make release
```
