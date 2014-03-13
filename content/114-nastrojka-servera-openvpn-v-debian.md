Title: Настройка сервера OpenVPN в Debian
Slug: nastrojka-servera-openvpn-v-debian
Category: Администрирование
Date: 2012-08-20 22:32
Source: False

### Вступление.

Я очень долго подходил к этому вопросу. Несколько раз пробовал по различным инструкциям сделать OpenVPN сервер, чтобы можно было без опаски ходить с открытых WiFi точек в кафешках, аутентифицировать себя каким-либо IP адресом, организовывать локальную сеть с шифрацией трафика между точками и прочая.

На деле же толку от этих инструкций ноль. То одно не работает, то другое. И без подготовки не разобраться на каком этапе проблема. Я постарался написать максимально простую инструкцию, по которой минимумом действий можно получить работающий OpenVPN. Я не буду рассматривать организацию какой-то сложной топологии сети, потому что я в этом вообще ничерта не разбираюсь.

В серии статей я постараюсь максимально просто, на уровне простых действий, рассказать как настроить сначала сервер на базе Debian Squeeze, клиент на Debian Squeeze, а потом клиент на Android и Windows. Также попробую рассмотреть различные проблемы с которыми можно столкнуться в ходе работ.

И, на момент написания статьи, я ещё этого не сделал, но хочу попробовать сделать себе внешний ipv6 адрес таким образом. Всем удачи, давайте приступим.

### Установка сервера OpenVPN на Debian Squeeze.

Изначально есть базовая установка Debian Squeeze, без каких-либо специфических пакетов.

Установим OpenVPN и Vim (ну или пользуйтесь nano):

    # aptitude install openvpn vim

Скопируем скрипты которые помогут нам создать сертификаты:

    # cp -R /usr/share/doc/openvpn/examples/easy-rsa/ /etc/openvpn

Отредактируем файл с переменными:

    # vim /etc/openvpn/easy-rsa/2.0/vars

Зададим размер ключа (чем больше, тем лучше и тем медленнее будет работать, ну и не рекомендую ставить 4096 например, поту что build-dh потом будет выполняться несколько часов):

    export KEY_SIZE=1024

Зададим время, через которое понадобится обновить ключи:

    export KEY_EXPIRE=365

Зададим параметры генерации SSL сертификата:

    export KEY_COUNTRY="RU"
    export KEY_PROVINCE="SPB"
    export KEY_CITY="SaintPetersburg"
    export KEY_ORG="Home"
    export KEY_EMAIL="postmaster@example.com"

Загрузим все переменные:

    # cd /etc/openvpn/easy-rsa/2.0/
    # . ./vars

Эта команда удаляет все сертификаты, которые были сгенерированы ранее (ну вдруг это не первая попытка):

    # . ./clean-all
    
Создаём центр сертификации. Это очень важный файл и крайне рекомендуется сохранить получившиеся файлы ещё где-нибудь. С помощью центра сертификации производится подписывание генерируемых сертификатов и подключится с сертификатом от другого центра не получится, даже если у него будут одинаковые параметры генерации.

    # . ./build-ca 
    Generating a 1024 bit RSA private key
    ........++
    .............................................................................................................................................................................................++
    writing new private key to 'ca.key'
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
    Common Name (eg, your name or your server's hostname) [output-meta]:openvpn.local
    Name []:Nikita Menkovich
    Email Address [postmaster@example.com]:

Создаём сертификат сервера, с его помощью будет производится проверка, что сервер это тот именно сервер.

    # . ./build-key-server server
    Generating a 1024 bit RSA private key
    .........................................++
    .....++
    writing new private key to 'server.key'
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
    Common Name (eg, your name or your server's hostname) [server]:server.openvpn.local
    Name []:server.openvpn.local
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
    commonName            :PRINTABLE:'server.openvpn.local'
    name                  :PRINTABLE:'server.openvpn.local'
    emailAddress          :IA5STRING:'postmaster@example.com'
    Certificate is to be certified until Aug 19 10:34:03 2013 GMT (365 days)
    Sign the certificate? [y/n]:y


Далее необходимо сгенерировать [параметры Диффи-Хеллмана](http://ru.wikipedia.org/wiki/%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC_%D0%94%D0%B8%D1%84%D1%84%D0%B8_%E2%80%94_%D0%A5%D0%B5%D0%BB%D0%BB%D0%BC%D0%B0%D0%BD%D0%B0), это займёт очень много времени если у вас не 1024, а 4096 бит (у меня заняло около двух часов), сходите попейте чаю, можете даже на обед сходить:

    # . ./build-dh 
    Generating DH parameters, 1024 bit long safe prime, generator 2
    This is going to take a long time
    .........+..........................................................................................+.............................................+.......................+....................+.....+..+.................++*++*++*

Копируем получившиеся сертификаты:

    # cp /etc/openvpn/easy-rsa/2.0/keys/{ca,server}.{crt,key} /etc/openvpn
    # cp /etc/openvpn/easy-rsa/2.0/keys/dh1024.pem /etc/openvpn

Сделаем конфигурационный файл:

    # zcat /usr/share/doc/openvpn/examples/sample-config-files/server.conf.gz > /etc/openvpn/server.conf
    # vim /etc/openvpn/server.conf

Раскомментируем эти строчки, a.b.c.d заменим на IP адрес, который висит на интерфейсе:

    ;local a.b.c.d
    ;push "redirect-gateway def1 bypass-dhcp"
    ;push "dhcp-option DNS 208.67.222.222"
    ;push "dhcp-option DNS 208.67.220.220"

DNS серверы можете указать свои. Опция redirect-gateway def1 указывает на то, что весь трафик после подключения должен идти через VPN.

Должен получится такой файл:

    # egrep -v '^;|^#|^$' /etc/openvpn/server.conf
    
    local a.b.c.d
    port 1194
    proto udp
    dev tun
    ca ca.crt
    cert server.crt
    key server.key  # This file should be kept secret
    dh dh1024.pem
    server 10.8.0.0 255.255.255.0
    ifconfig-pool-persist ipp.txt
    push "redirect-gateway def1 bypass-dhcp"
    push "dhcp-option DNS 208.67.222.222"
    push "dhcp-option DNS 208.67.220.220"
    keepalive 10 120
    comp-lzo
    persist-key
    persist-tun
    status openvpn-status.log
    verb 3



Перезапустим openvpn подключение server (файл же мы назвали server.conf, так что можно легко делать несколько подключений).

    # invoke-rc.d openvpn restart server

Теперь настроим перенаправление запросов из нашего тунеля в сеть:

    # echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    # sysctl -p
    # iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
    # iptables -A FORWARD -s 10.8.0.0/24 -j ACCEPT
    # iptables -A FORWARD -j REJECT
    # iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE

Разрешим доступ по udp к порту 1194:

    # iptables -A INPUT -p udp -m udp --dport 1194 -j ACCEPT

Сохраняем их и настраиваем автозапуск:

    # iptables-save > /etc/iptables.up.rules
    # cat /etc/network/if-up.d/iptables 
    #!/bin/sh
    iptables-restore < /etc/iptables.up.rules
    # chmod u+x /etc/network/if-up.d/iptables

Далее приступим к настройке [Linux клиента для OpenVPN](//libc6.org/page/ustanovka-klienta-openvpn-na-debian-squeeze).
