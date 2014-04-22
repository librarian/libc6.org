Title: Установка OpenVPN на Android.
Slug: openvpn-android
Category: Администрирование
Date: 2012-08-22 22:58
Source: False

Сразу оговорюсь, что работа OpenVPN требует прав root на телефоне. Также скажу, что всё это я тестировал на своём [Huawei Honor](//libc6.org/page/obzor-smartfona-huawei-honor-u8860).

Итак, нам понадобится:

1. [OpenVPN Installer](https://play.google.com/store/apps/details?id=de.schaeuffelhut.android.openvpn.installer)
2. [OpenVPN Settings](https://play.google.com/store/apps/details?id=de.schaeuffelhut.android.openvpn)
3. [Tun.ko Installer](https://play.google.com/store/apps/details?id=com.aed.tun.installer)
4. [Busybox](https://play.google.com/store/apps/details?id=stericson.busybox)

Приступим:

Устанавливаем всё вышеперечисленное на телефон. Первым запускаем _Busybox_. Устанавливаем его в **/system/bin**.

Далее открываем _Tun.ko Installer_, скачиваем и загружаем tun/tap драйвер для вашего устройство. В дальнейшем нужно будет открывать эту программу после каждой перезагрузки телефона, чтобы подгрузить модуль tun/tap.

После этого открываем _OpenVPN Installer_ устанавливаем бинарник OpenVPN в **/system/xbin**.

Запускаем _OpenVPN Settings_, проверяем что везде у нас горит зелёненькое при тестировании (**Меню -> Prerequisites**). В **Меню -> Advanced** смотрим, чтобы "Path to openvpn binary" был `/system/xbin/openvpn`.

Далее генерируем на сервере OpenVPN новые сертификаты и делаем конфигурацию

    # cd /etc/openvpn/easy-rsa/2.0/
    # . ./vars 
    NOTE: If you run ./clean-all, I will be doing a rm -rf on /etc/openvpn/easy-rsa/2.0/keys
    # ./build-key android
    Generating a 1024 bit RSA private key
    .++++++
    .....++++++
    writing new private key to 'android.key'
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
    Common Name (eg, your name or your server's hostname) [android]:android.openvpn.local
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
    commonName            :PRINTABLE:'android.openvpn.local'
    emailAddress          :IA5STRING:'postmaster@example.com'
    Certificate is to be certified until Aug 22 08:51:31 2013 GMT (365 days)
    Sign the certificate? [y/n]:y
    
    
    1 out of 1 certificate requests certified, commit? [y/n]y
    Write out database with 1 new entries
    Data Base Updated

Копируем сертификаты и **ca.crt** к себе на компьютер.

Создаём файл **android.conf** следующего содержания (a.b.c.d заменить на IP или доменное имя VPN сервера):

    client
    dev tun
    proto udp
    remote a.b.c.d 1194
    resolv-retry infinite
    nobind
    persist-key
    persist-tun
    ca ca.crt
    cert android.crt
    key android.key
    ns-cert-type server
    comp-lzo
    verb 3

Загружаем сертификаты, ca.crt и android.conf в директорию openvpn на карточке памяти.

Открываем _OpenVPN Settings_, видим, что появился пункт: android.conf.

Включаем OpenVPN, включаем подключение android.conf и, вуаля - всё работает. Если что-то не заработает, то делаете долгое нажатие на android.conf и выбираете View Log File. Вывод лога будет хранится в android.log в директории openvpn на SD карте. Если что не сработает - пишите, постараюсь помочь.
