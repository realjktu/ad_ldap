# Enable LDAP over SSL (LDAPS) for Microsoft Active Directory servers
By default Microsoft active directory servers will offer LDAP connections over *unencrypted* connections (boo!).

The steps below will create a new self signed certificate appropriate for use with and thus enabling LDAPS for an AD server. Of course the "self-signed" portion of this guide can be swapped out with a real vendor purchased certificate if required.

Steps have been tested successfully with Windows Server 2012R2, but *should* work with Windows Server 2008 without modification. Will require both a system with OpenSSL (ideally Linux/OSX) and (obviously) a Windows Active Directory server.

- [Create root certificate](#create-root-certificate)
- [Import root certificate into trusted store of domain controller](#import-root-certificate-into-trusted-store-of-domain-controller)
- [Create client certificate](#create-client-certificate)
- [Accept and import certificate](#accept-and-import-certificate)
- [Reload active directory SSL certificate](#reload-active-directory-ssl-certificate)
- [Test LDAPS using `ldp.exe` utility](#test-ldaps-using-ldpexe-utility)
- [Reference](#reference)

## Create root certificate
From the OpenSSL machine, create new private key and root certificate. Answer country/state/org questions as suitable:

```sh
$ openssl genrsa -des3 -out ca.key 4096
$ openssl req -new -x509 -days 3650 -key ca.key -out ca.crt
```

You should now have a resulting `ca.key` and `ca.crt` - hold onto these.

## Import root certificate into trusted store of domain controller
- From the active directory server, open `Manage computer certificates`.
- Add the generated `ca.crt` to the certificate path `Trusted Root Certification Authorities\Certificates`.
- Done.

## Create client certificate
We will now create a client certificate to be used for LDAPS, signed against our generated root certificate.

From the active directory server:

- Create a new `request.inf` definition with the following contents - replacing `ACTIVE_DIRECTORY_FQDN` with the qualified domain name of your active directory server:

	```
	[Version]
	Signature="$Windows NT$"

	[NewRequest]
	Subject = "CN=ACTIVE_DIRECTORY_FQDN"
	KeySpec = 1
	KeyLength = 1024
	Exportable = TRUE
	MachineKeySet = TRUE
	SMIME = FALSE
	PrivateKeyArchive = FALSE
	UserProtected = FALSE
	UseExistingKeySet = FALSE
	ProviderName = "Microsoft RSA SChannel Cryptographic Provider"
	ProviderType = 12
	RequestType = PKCS10
	KeyUsage = 0xa0

	[EnhancedKeyUsageExtension]
	OID = 1.3.6.1.5.5.7.3.1 ; Server Authentication
	```
- Run the following to create a new client certificate request of `client.csr` (note: it's *critical* this is run from the active directory server to ensure a private key -> certificate association):

	```
	C:\> certreq -new request.inf client.csr
	```

Back to our OpenSSL system:
- Create `v3ext.txt` containing the following:

	```
	keyUsage=digitalSignature,keyEncipherment
	extendedKeyUsage=serverAuth
	subjectKeyIdentifier=hash
	```
- Create a certificate `client.crt` from certificate request `client.csr` and root certificate (with private key):

	```sh
	$ openssl x509 -req -days 3650 -in client.csr -CA ca.crt -CAkey ca.key -extfile v3ext.txt -set_serial 01 -out client.crt
	```
- Verify generated certificate:

	```sh
	$ openssl x509 -in client.crt -text
	```
- Ensure the following `X509v3 extensions` are **all present**:
	- `X509v3 Key Usage: Digital Signature, Key Encipherment`
	- `X509v3 Extended Key Usage: TLS Web Server Authentication`
	- `X509v3 Subject Key Identifier`

## Accept and import certificate
- From the active directory server with `client.crt` present, run the following:

	```
	C:\> certreq -accept client.crt
	```
- Open `Manage computer certificates`, the new certificate should now be present under `Personal\Certificates`. Ensure that:
	- Certificate has a private key association.
	- The "Intended Purposes" is defined as "Server Authentication".
	- Certificate name is the FQDN of the active directory server.

## Reload active directory SSL certificate
Alternatively you can just reboot the server, but this method will instruct the active directory server to simply reload a suitable SSL certificate and if found, enable LDAPS:

- Create `ldap-renewservercert.txt` containing the following:

	```
	dn:
	changetype: modify
	add: renewServerCertificate
	renewServerCertificate: 1
	-
	```
- Run the following command:

	```
	C:\> ldifde -i -f ldap-renewservercert.txt
	```

## Test LDAPS using `ldp.exe` utility
- From _another_ domain controller, firstly install our generated root certificate `ca.crt` to the certificate path `Trusted Root Certification Authorities\Certificates`.
- Open utility:

	```
	C:\> ldp.exe
	```
- From `Connection`, select `Connect`.
- Enter name of target domain controller.
- Enter `636` as port number (this is the LDAPS port).
- Click `OK` to confirm the connection works.
- You're all done!

## Reference
- Enable LDAP over SSL with a third-party certification authority: https://support.microsoft.com/en-us/kb/321051
- LDAP renewServerCertificate: https://msdn.microsoft.com/en-us/library/cc223311.aspx
- How to Enable LDAPS in Active Directory (similar outcome to above): http://www.javaxt.com/tutorials/windows/how_to_enable_ldaps_in_active_directory
- DigiCert LDAPS certificate install guide: https://www.digicert.com/ssl-certificate-installation-microsoft-active-directory-ldap-2012.htm
