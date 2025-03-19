from __future__ import annotations
import re

from random import random
from ipaddress import (
    IPv4Address,
    IPv6Address,
)
from dmarc import (
    SPF,
    DKIM,
    DMARCPolicy,
    DMARCDisposition,
    PolicyError,
    RecordSyntaxError,
)
from dmarc.ar import (
    authres,
    AuthenticationResult,
    SPFAuthenticationResult,
    DKIMAuthenticationResult,
    DMARCAuthenticationResult,
)
from dmarc.asyncresolver import (
    resolve,
    RecordNotFoundError,
    RecordMultiFoundError,
    RecordResolverError,
)
from dmarc.psl import get_public_suffix
from .asyncspf import query as SPFQuery

EMPTYSTRING = ''
linesep_splitter = re.compile(r'\n|\r\n?')

def unfold(text: str) -> str:
    return ''.join(linesep_splitter.split(text))

def split_address(address: str) -> tuple[str, str]:
    try:
        regex = r"""
        (.*?) ( \@ (?:  \[  (?: \\. | [^\]\\] ){0,999} (?: \] | \Z) | [^\[\@] )*) \Z
        """
        localpart, domain = re.match(regex, address, re.X | re.S).groups()
    except AttributeError:
        localpart = address
        domain = EMPTYSTRING
    
    if domain != EMPTYSTRING:
        domain = re.match(r'^\@?(.*?)\.*\Z', domain).group(1)
    
    return (localpart, domain)

async def check_spf(ip_addr: IPv4Address | IPv6Address, helo: str, mail_from: str) -> SPFAuthenticationResult:
    query = SPFQuery(i=str(ip_addr), s=mail_from, h=helo)
    result, code, expl = await query.check()
    
    return SPFAuthenticationResult(
        result = result,
        result_comment = query.get_header_comment(result),
        smtp_helo = helo if not mail_from else None,
        smtp_mailfrom = mail_from
    )

async def get_record(domain: str) -> tuple:
    org_domain = None
    try:
        record = await resolve(domain)
    except (RecordNotFoundError, RecordMultiFoundError):
        org_domain = get_public_suffix(domain)
        if org_domain != domain:
            record = await resolve(org_domain)
        else:
            raise
    
    return (record, org_domain)

async def check_dmarc(domain: str, auth_results: list[AuthenticationResult], ip_addr: IPv4Address | IPv6Address, psl=None) -> DMARCAuthenticationResult:
    if not domain:
        return authres(policy="domainerror")
    
    result = None
    comment = None
    policy = None
    try:
        record, org_domain = await get_record(domain)
        dmarc = DMARCPolicy(record, domain, org_domain, str(ip_addr), psl)
        _auth_results = []
        for x in auth_results:
            if isinstance(x, SPFAuthenticationResult):
                _auth_results.append(SPF.from_authres(x))
            elif isinstance(x, DKIMAuthenticationResult):
                _auth_results.append(DKIM.from_authres(x))
        dmarc.verify(auth_results=_auth_results)
        result = dmarc.result
    except PolicyError:
        result = dmarc.result
        # Selection of messages to which the policy error is to be applied
        # should be based on a random number and the policy pct= tag number.
        # (0.0 <= X < 1.0 * 100) < (0 <= P <= 100)
        if not random() * 100 < dmarc.policy.pct:
            result.disposition = DMARCDisposition.NONE
    except RecordNotFoundError:
        comment = "no record found"
        policy = "none"
    except RecordMultiFoundError:
        comment = "two or more records found"
        policy = "none"
    except RecordSyntaxError:
        comment = "record syntax error"
        policy = "none"
    except RecordResolverError:
        comment = "dns error"
        policy = "dnserror"
    
    return authres(result, result_comment=comment, header_from=domain, policy=policy)
