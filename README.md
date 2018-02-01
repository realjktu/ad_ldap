1. yum install -y epel-release

2. yum install -y git python python-pip cyrus-sasl-gssapi krb5-devel krb5-libs gcc python-devel openldap-devel gcc-c++ krb5-workstation

3. pip install -r requirements.txt

4. Update /etc/hosts. In order to use Kerberos need to have correct DNS resolution. Use /etc/hosts or related DNS server.

5. Configure Kerberos user config check_ldap_connection_krb5.ini or system /etc/krb5.conf

6. Edit ./check_ldap_connection_3.py script

7. Run the script: python check_ldap_connection_3.py
