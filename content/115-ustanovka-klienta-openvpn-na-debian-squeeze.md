Title: Установка клиента OpenVPN на Debian Squeeze
Slug: ustanovka-klienta-openvpn-na-debian-squeeze
Category: Администрирование
Date: 2012-08-20 22:32
Source: False

Про [установку сервера OpenVPN](//libc6.org/page/nastrojka-servera-openvpn-v-debian) можно прочитать в предыдущей статье.

Создадим ключи для Linux клиента:

    # cd /etc/openvpn/easy-rsa/2.0/
    # ./build-key linux
    Generating a 1024 bit RSA private key
    ......................................................................++++++
    .++++++
    writing new private key to 'linux.key'
    -----
    You are about to be asked to enter information that will be incorporated
    into your certificate request.
    What you are about to enter is what is called a Distinguished Name or a DN.
    There are quite a few fields but you can leave some blank
    For some fields there will be a default value,
    If you enter '.', the field will be left blank.
    -----
    Country Name (2 letter code) [RU]:
    State or Province Name (full name) [SPB]:
    Locality Name (eg, city) [SaintPetersburg]:
    Organization Name (eg, company) [Home]:
    Organizational Unit Name (eg, section) []:
    Common Name (eg, your name or your server's hostname) [linux]:linux.openvpn.local
    Name []:
    Email Address [postmaster@example.com]:
    
    Please enter the following 'extra' attributes
    to be sent with your certificate request
    A challenge password []:
    An optional company name []:
    Using configuration from /etc/openvpn/easy-rsa/2.0/openssl.cnf
    Check that the request matches the signature
    Signature ok
    The Subject's Distinguished Name is as follows
    countryName           :PRINTABLE:'RU'
    stateOrProvinceName   :PRINTABLE:'SPB'
    localityName          :PRINTABLE:'SaintPetersburg'
    organizationName      :PRINTABLE:'Home'
    commonName            :PRINTABLE:'linux.openvpn.local'
    emailAddress          :IA5STRING:'postmaster@example.com'
    Certificate is to be certified until Aug 19 12:02:08 2013 GMT (365 days)
    Sign the certificate? [y/n]:y
    
    
    1 out of 1 certificate requests certified, commit? [y/n]y
    Write out database with 1 new entries
    Data Base Updated

Теперь приступим к установке клиента на базе Debian Squeeze:

    # aptitude install openvpn
    # egrep -v '^;|^#|^$' /usr/share/doc/openvpn/examples/sample-config-files/client.conf > /etc/openvpn/linux.conf
    # vim /etc/openvpn/linux.conf

Делаем вот такой вот конфигурационный файл, a.b.c.d - адрес нашего VPN сервера:

    client
    dev tun
    proto udp
    remote a.b.c.d 1194
    resolv-retry infinite
    nobind
    persist-key
    persist-tun
    ca ca.crt
    cert linux.crt
    key linux.key
    ns-cert-type server
    comp-lzo
    verb 3

Загружаем с сервера клиентские сертификаты и файл центра сертификации:

    # scp root@a.b.c.d:/etc/openvpn/easy-rsa/2.0/keys/linux.* root@a.b.c.d:/etc/openvpn/easy-rsa/2.0/keys/ca.crt /etc/openvpn/
    The authenticity of host 'a.b.c.d (a.b.c.d)' can't be established.
    RSA key fingerprint is 53:f7:fe:32:af:00:b6:ff:cb:18:78:74:ea:30:12:d3.
    Are you sure you want to continue connecting (yes/no)? yes
    Warning: Permanently added 'a.b.c.d' (RSA) to the list of known hosts.
    root@a.b.c.d's password: 
    linux.crt 100% 3841     3.8KB/s   00:00    
    linux.csr 100%  696     0.7KB/s   00:00    
    linux.key 100%  887     0.9KB/s   00:00    
    root@a.b.c.d's password: 
    ca.crt 100% 1257     1.2KB/s   00:00

Итак, у нас есть всё что необходимо, запускаем (можно указывать без параметров, если сеть одна):

    # invoke-rc.d openvpn start linux

Я по умолчанию выключаю OpenVPN, особенно на ноутбуке, там после того, как он проснётся - линк автоматически не поднимается, равно как и при включении. А потом будешь ещё пару минут думать, а почему сеть не работает.

    # vim /etc/default/openvpn
    AUTOSTART="none"
