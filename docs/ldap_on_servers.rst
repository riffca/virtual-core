=============================================
LDAP authentication based on the virtual core
=============================================



Ubuntu
------

`apt-get install libpam-ldap ldap-utls`


ldap-utils is recommended, not required.

On the configuration you will need to supply your LDAP URL (with https)
and your base DN. You probably will want to allow users to change their
passwords (with impact on the LDAP server). The server is not authenticated.

This will change the PAM configuration on /etc/pam.d. It will also
change /etc/ldap.conf

If you are using your own certificate authority, you will need to add
the certificate of the authority, by changing the `TLS_CACERT` parameter
on /etc/ldap/ldap.conf . Be careful with auto-reconfiguration

Finally do

`pam-auth-update`


And you should be done

https://wiki.debian.org/LDAP/PAM



(uid limitation - pam_filter)


CentOS 5
--------

We do this manually

* Make sure openldap-clients and nss_ldap is installed
* Copy your CA certificate to /etc/openldap/cacerts
* Make sure /etc/ldap.conf has (among other things)::

    URI ldaps://PATH_TO_YOUR_LDAP_SERVER
    BASE your_base
    pam_password exop
    ssl on
    port 636
    tls_cacertfile /etc/openldap/cacerts/cacert.pem

* Make sure /etc/openldap/ldap.conf has (among other things)::

    URI ldaps://PATH_TO_YOUR_LDAP_SERVER
    BASE your_base
    TLS_CACERT /etc/openldap/cacerts/cacert.pem
    
* Edit /etc/nsswitch.conf to include ldap (on password, group and shadow)
* Edit at least /etc/pam.d/system-auth and add in appropriate places::

    auth        sufficient    pam_ldap.so use_first_pass
    account     [default=bad success=ok user_unknown=ignore] pam_ldap.so
    password    sufficient    pam_ldap.so use_authtok
    session     optional      pam_ldap.so

* Restart nscd

CentOS 6
--------

* Install openldap-clients, sssd, pam_ldap and nss-pam-ldapd
* Make sure sssd is running
* on /etc/nsswitch.con use sss instead of ldap
* Here is an example of a sssd.conf file::

    [sssd]
    domains = LDAP
    services = nss
    config_file_version = 2

    [nss]
    filter_groups = root
    filter_users = root

    [domain/LDAP]
    enumerate=true
    cache_credentials = TRUE

    id_provider = ldap
    auth_provider = ldap
    ldap_schema = rfc2307
    chpass_provider = ldap

    ldap_uri = YOU_SERVER
    ldap_search_base = YOUR_BASE


* Copy your CA certificate to /etc/openldap/cacerts
* Make sure /etc/pam_ldap.conf has (among other things)::

    URI ldaps://PATH_TO_YOUR_LDAP_SERVER
    BASE your_base
    pam_password exop
    ssl on
    port 636
    tls_cacertfile /etc/openldap/cacerts/cacert.pem

* Make sure /etc/openldap/ldap.conf has (among other things)::

    URI ldaps://PATH_TO_YOUR_LDAP_SERVER
    BASE your_base
    TLS_CACERT /etc/openldap/cacerts/cacert.pem
    
* Edit at least /etc/pam.d/system-auth and add in appropriate places::

    auth        sufficient    pam_ldap.so use_first_pass
    account     [default=bad success=ok user_unknown=ignore] pam_ldap.so
    password    sufficient    pam_ldap.so use_authtok
    session     optional      pam_ldap.so


CentOS 7
--------

*needs review*

follow instructions for centos 5, caveats:

On CentOS install nss_ldap and nss-pam-ldapd

/etc/nslcd.conf - ldap server (instead of /etc/ldap.conf)

make sure nslcd is started

make sure /etc/pam.d/system-auth is the only file of interest (e.g. password-auth)


authconfig --enableldap --enableldapauth --ldapserver=ldap://ldap.YOUR-DOMAIN:389/ \
  --ldapbasedn="BASE-DN" --enablecache --disablefingerprint --kickstart

https://wiki.centos.org/AdrianHall/CentralizedLDAPAuth
