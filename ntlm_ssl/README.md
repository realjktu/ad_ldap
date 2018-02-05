1. yum install -y epel-release

2. yum install -y git python python-pip cyrus-sasl-ntlm gcc python-devel openldap-devel gcc-c++

3. pip install -r requirements.txt

4. Enable LDAP over SSL by the folloiwng document enable_LDAPS_ActiveDirectory.md

4. Enable NTLM on Windows 2008 https://support.microsoft.com/en-us/help/935834/how-to-enable-ldap-signing-in-windows-server-2008

6. Edit ./check_ldap_connection_ntlm_ssl.py script

7. Run the script: check_ldap_connection_ntlm_ssl.py
