#!/usr/bin/env python
import ldap
import ldap.sasl


def main():
    domain = 'domain1.local'
    address = 'ldaps://dc1.domain1.local:636'

    username = 'cyberx1'
    password = 'cruvuttj@4338'

    with LDAPClient(host=address, username=username, password=password, domain=domain) as ldap_client:
        users = ldap_client.get_user(username=username)
        users = list(users)

        for user in users:
            print user


# ------------------------------------------------------------

class LDAPClient(object):
    def __init__(self, host, username, password, domain, distinguished_name=None, authentication_mechanism='DIGEST-MD5'):
        self.host = host
        self.username = username
        self.password = password
        self.domain = domain
        self.authentication_mechanism = authentication_mechanism

        self.distinguished_name = distinguished_name if distinguished_name else self._domain_to_distinguished_name(domain)
        self._session = None

    def connect(self):
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        session = ldap.initialize(self.host, trace_level=0)
        session.set_option(ldap.OPT_REFERRALS, 0)
        session.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        session.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
        session.set_option( ldap.OPT_X_TLS_DEMAND, True )
        session.set_option( ldap.OPT_DEBUG_LEVEL, 255 )

        session.set_option(ldap.OPT_REFERRALS, 0)

        sasl_auth = ldap.sasl.sasl({
            ldap.sasl.CB_AUTHNAME: self.username,
            ldap.sasl.CB_PASS: self.password,
        },
            self.authentication_mechanism
        )

        session.sasl_interactive_bind_s("", sasl_auth)

        self._session = session
        return self

    def disconnect(self):
        if self._session:
            self._session.unbind_s()

        self._session = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, type, value, traceback):
        return self.disconnect()

    def execute_query(self, query):

        if not self._session:
            raise RuntimeError('LDAP session is not opened')

        ldap_result_id = self._session.search(self.distinguished_name, ldap.SCOPE_SUBTREE, query)
        result_all_type, result_all_data = self._session.result(ldap_result_id, 1)
        for result_type, result_data in result_all_data:
            if result_type is not None:
                yield result_data

    def get_user(self, username=None):
        if not username:
            username = self.username

        query = '(SAMAccountName={username})'
        results = self.execute_query(query.format(username=username))

        for result in results:
            yield LDAPUser(result)

    @staticmethod
    def _domain_to_distinguished_name(domain):
        return ','.join(map(lambda x: 'dc=' + x, domain.split('.')))


LDAP_USER_FORMAT = '''Logon Name: {logon_name}
UPN: {user_principal_name}
Full Name: {full_name}
First Name: {first_name}
Last Name: {last_name}
Email: {email}
Display Name: {display_name}
Groups: {groups}'''


class LDAPUser(object):
    def __init__(self, raw_user):

        self._raw_user = raw_user

        self.groups = list(self._parse_groups())

        self.logon_name = self._parse_string('sAMAccountName', '')
        self.user_principal_name = self._parse_string('userPrincipalName', '')
        self.full_name = self._parse_string('name', '')
        self.first_name = self._parse_string('givenName', '')
        self.last_name = self._parse_string('sn', '')
        self.email = self._parse_string('mail', '')
        self.display_name = self._parse_string('displayName', '')

    def __str__(self):
        return LDAP_USER_FORMAT.format(
            logon_name=self.logon_name,
            user_principal_name=self.user_principal_name,
            full_name=self.full_name,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            display_name=self.display_name,
            groups=self.groups)

    def _parse_groups(self):

        member_of = set()
        items = self._raw_user.get('memberOf', [])
        for item in items:
            member_of = member_of.union(map(lambda x: x.lower().strip(), item.split(',')))

        for item in member_of:
            if not item.startswith('cn='):
                continue

            yield item[3:]

    def _parse_string(self, key, default=None, multi=False):
        result = self._raw_user.get(key, [])
        if len(result):
            return result if multi else result[0]
        return default


if __name__ == '__main__':
    main()
