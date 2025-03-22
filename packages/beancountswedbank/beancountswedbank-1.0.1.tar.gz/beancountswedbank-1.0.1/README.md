# Beancount Swedbank Importer

beancount-swedbank-importer provides a python import script for beancount to
import CSV exports from swedbank online banking.


## Usage

### Installation

Install `beancountwedbank` from pip like this:

```bash
    pip install beancountswedbank
```


### Configuration

Write a configuration file, eg. `config.py`, (or extend your existing one) to include this:

```python
    import beangulp
    import beancountswedbank


    CONFIG = [
        beancountswedbank.CSVImporter('Nyckelkonto', 'Assets:Your:Nyckelkonto', 'SEK'),
    ]


    if __name__ == '__main__':
        main = beangulp.Ingest(CONFIG)
        main()
```

`Nyckelkonto` is the literal name of the account as you can see it in the
online banking website. It will be used by `beancount` to match the 4th
column of the exported CSV file.


### Daily use

 1. Download the CSV file from your Swedbank online banking,
 2. Run `config.py extract transaction_file.csv`


## License

This package is licensed under the MIT License.

