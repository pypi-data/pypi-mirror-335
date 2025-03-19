# DMARC (Domain-based Message Authentication, Reporting & Conformance)

DMARC email authentication module implemented in Python.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dmarc.

```console
$ pip install dmarc
```

## Usage

```python
>>> from dmarc import SPF, DKIM, SPFResult, DKIMResult, DMARCPolicy
>>> # Represent verified SPF and DKIM status
>>> spf = SPF(domain='news.example.com', result=SPFResult.PASS)
>>> dkim = DKIM(domain='example.com', result=DKIMResult.PASS)
>>> dmarc = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
>>> dmarc.verify(auth_results=[spf, dkim, DKIM('mailer.example.net', DKIMResult.PASS)])
>>> adict = dmarc.result.as_dict()
>>> 
>>> # RR resolver example
>>> from dmarc.resolver import resolve, RecordNotFoundError, RecordMultiFoundError
>>> from dmarc.psl import get_public_suffix
>>> domain = 'news.example.com'
>>> try:
...     record = resolve(domain)
... except (RecordNotFoundError, RecordMultiFoundError):
...     org_domain = get_public_suffix(domain)
...     if org_domain != domain:
...         record = resolve(org_domain)
... 
>>> # Aggregate report xml document to dict example
>>> from dmarc.report import DMARCRelaxedSchema
>>> from dmarc.tests.report.test_report import TEST_XML_DOCUMENT
>>> adict = DMARCRelaxedSchema.to_dict(TEST_XML_DOCUMENT)
>>> 
```

### Milter configuration with Postfix

1. Start `dmarc.milter` module or run via Systemd — see
   [`contrib/`](contrib/dmarcmilter.service).
2. Start a Postfix instance with a configuration like
   `smtpd_milters = inet:127.0.0.1:9000`

## License
[MIT](https://choosealicense.com/licenses/mit/)
