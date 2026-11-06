"""Governance exception types."""
class GovernanceError(Exception): pass
class AuthorizationDenied(GovernanceError): pass
class ConfigurationError(GovernanceError): pass
class ReplayDetected(AuthorizationDenied): pass
