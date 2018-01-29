1. yum install -y epel-release

2. yum install -y git python python-pip cyrus-sasl-gssapi krb5-devel krb5-libs gcc python-devel openldap-devel gcc-c++ krb5-workstation

3. pip install -r requirements.txt

4. Update /etc/hosts

5. Configure Kerberos user config check_ldap_connection_krb5.ini or system /etc/krb5.conf

6. Edit and run ./check_ldap_connection_3.py script
