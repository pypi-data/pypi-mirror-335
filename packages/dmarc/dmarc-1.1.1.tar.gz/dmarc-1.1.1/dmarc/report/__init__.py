from __future__ import annotations

import pkgutil
from xmlschema import (
    XMLSchema,
    etree_tostring,
)
from dmarc import (
    Enum,
    DMARCResult,
    DMARCAlignment,
    DMARCDisposition,
    DMARCPolicyOverride,
    SPFResult,
    SPFDomainScope,
    DKIMResult,
    SPF,
    DKIM,
)

DMARCSchema = XMLSchema(pkgutil.get_data(__name__, "schemas/dmarc.xsd"))
DMARCRelaxedSchema = XMLSchema(pkgutil.get_data(__name__, "schemas/dmarc-relaxed.xsd"))

class ReportType:
    
    def __iter__(self):
        for key in self.__dict__:
            if self.__dict__[key] is not None:
                yield key
    
    def __getitem__(self, name):
        return self.__dict__[name]
    
    def as_dict(self):
        def convert_value(value):
            if isinstance(value, Enum):
                return value.value
            elif isinstance(value, ReportType):
                return value.as_dict()
            elif isinstance(value, list):
                return [convert_value(x) for x in value]
            else:
                return value
        
        return {key: convert_value(self[key]) for key in iter(self)}

class Report(ReportType):
    
    def __init__(self, report_metadata: ReportMetadata, policy_published: PolicyPublished, record: list[Record], version: float|None = None):
        self.version = version
        self.report_metadata = report_metadata
        self.policy_published = policy_published
        self.record = record

class ReportMetadata(ReportType):
    """Report generator metadata.
    """
    def __init__(self, org_name: str, email: str, report_id: str, date_range: DateRange, extra_contact_info: str|None = None, error: list[str]|None = None):
        self.org_name = org_name
        self.email = email
        self.extra_contact_info = extra_contact_info
        self.report_id = report_id
        self.date_range = date_range
        self.error = error

class DateRange(ReportType):
    """The time range in UTC covered by messages in this report,
    specified in seconds since epoch.
    """
    def __init__(self, begin: int, end: int):
        self.begin = begin
        self.end = end

class PolicyPublished(ReportType):
    """The DMARC policy that applied to the messages in
    this report.
    """
    def __init__(
            self,
            domain: str,
            p: DMARCDisposition,
            pct: int,
            sp: DMARCDisposition|None = None,
            adkim: DMARCAlignment|None = None,
            aspf: DMARCAlignment|None = None,
            fo: str|None = None
    ):
        """
        Args:
            domain:    The domain at which the DMARC record was found
            
            p:         The policy to apply to messages from the domain,
                       DMARCDisposition
            
            sp:        The policy to apply to messages from subdomains,
                       DMARCDisposition
            
            adkim:     The DKIM alignment mode,
                       DMARCAlignment
            
            aspf:      The SPF alignment mode,
                       DMARCAlignment
            
            pct:       The percent of messages to which policy applies
            
            fo:        Failure reporting options in effect
        """
        self.domain = domain
        self.p = p
        self.sp = sp
        self.adkim = adkim
        self.aspf = aspf
        self.pct = pct
        self.fo = fo

class Record(ReportType):
    """The authentication results that were evaluated by the receiving system
    for the given set of messages.
    """
    def __init__(self, row: Row, identifiers: Identifiers, auth_results: AuthResults):
        self.row = row
        self.identifiers = identifiers
        self.auth_results = auth_results

class SPFAuthResult(SPF, ReportType):
    pass

class DKIMAuthResult(DKIM, ReportType):
    pass

class AuthResults(ReportType):
    """There may be no DKIM signatures, or multiple DKIM
    signatures. There will always be at least one SPF result.
    """
    def __init__(self, spf: list[SPFAuthResult], dkim: list[DKIMAuthResult]|None = None):
        self.dkim = dkim
        self.spf = spf

class Identifiers(ReportType):
    
    def __init__(self, header_from: str, envelope_from: str|None = None, envelope_to: str|None = None):
        """
        Args:
            header_from:    The RFC5322.From domain
            envelope_from:  The RFC5321.MailFrom domain
            envelope_to:    The envelope recipient domain
        """
        self.header_from = header_from
        self.envelope_from = envelope_from
        self.envelope_to = envelope_to

class Row(ReportType):
    
    def __init__(self, source_ip: str, count: int, policy_evaluated: PolicyEvaluated):
        """
        Args:
            source_ip:        The connecting IP
            
            count:            The number of matching messages
            
            policy_evaluated: The DMARC disposition applying to matching messages,
                              PolicyEvaluated
            
        """
        self.source_ip = source_ip
        self.count = count
        self.policy_evaluated = policy_evaluated

class PolicyOverrideReason(ReportType):
    
    def __init__(self, policy_override: DMARCPolicyOverride, comment: str|None = None):
        self.type = policy_override
        self.comment = comment

class PolicyEvaluated(ReportType):
    """Taking into account everything else in the record,
    the results of applying DMARC.
    """
    def __init__(self, disposition: DMARCDisposition, spf: DMARCResult, dkim: DMARCResult, reason: list[PolicyOverrideReason]|None = None):
        self.disposition = disposition
        self.dkim = dkim
        self.spf = spf
        self.reason = reason
