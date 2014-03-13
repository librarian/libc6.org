Title: Установка и настройка racoon и xl2tpd (IPsec/L2TP) в Debian
Slug: l2tp-ipsec-server-howto
Category: Администрирование
Date: 2012-10-08 00:34
Source: False

Эта связка исключительно хороша в том смысле, что подключится к ней можно со всех платформ (Windows, iOS, Android, Mac OS), используя встроенные в систему средства. В статье я хочу попытаться реализовать настройку в настолько же простом виде, как я это делал в статье по [OpenVPN](//libc6.org/page/nastrojka-servera-openvpn-v-debian).

Я сразу хочу сказать, что не имеет смысла читать другие статьи на эту тему. Может вы и получите как-то работоспособное решение, но оно скорее всего будет абсолютно бесполезным, потому что то у него часть клиентов не будет подключаться, или шифрование не будет работать так, как думаете вы (часто встречал конфигурацию по сертификатам, где а) сертификатами ничего не шифровалось б) можно было использовать _любой_ сертификат) или ещё какая фигня.

Я отдельно сделаю пост в котором соберу все плюсы и минусы OpenVPN и L2TP/IPsec, но это позже.

[TOC]

## Генерация сертификатов

Можно использовать скрипты из набора openssl для генерации сертификатов, но мне сильно понравились скрипты из комплекта OpenVPN, так что я поставил пакет, выдрал оттуда easy-rsa скрипты и выложил, так что пользуйтесь (понятно что параноики всё сделают то же самое, но сами).

    # wget http://i.libc6.org/media/opensource/easy-rsa.tar.gz
    # tar zxvf easy-rsa.tar.gz
    # vim /root/easy-rsa/2.0/vars

Ну и раз мы скрипты взяли из записи про [настройку OpenVPN](//libc6.org/page/nastrojka-servera-openvpn-v-debian), то и инструкцию возьмём оттуда же:

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

    # cd /usr/share/doc/openvpn/examples/easy-rsa/2.0
    # . ./vars

Эта команда удаляет все сертификаты, которые были сгенерированы ранее (ну вдруг это не первая попытка):

    # . ./clean-all
    
Создаём центр сертификации. Это очень важный файл и крайне рекомендуется сохранить получившиеся файлы ещё где-нибудь. С помощью центра сертификации производится подписывание генерируемых сертификатов и подключится с сертификатом от другого центра не получится, даже если у него будут одинаковые параметры генерации.

    # . ./build-ca 
    Generating a 1024 bit RSA private key
    ........++
    .....................................................
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
    .........+...........................................................

Ну, с сертификатами сервера мы закончили. Давайте теперь настроим сам racoon

## Установка и настройка racoon

Для начала установим **racoon**:

    # aptitude install racoon

При установке выбирайте метод настройки **direct**.

Записываем UID и GID нового пользователя и его группы.

Сконфигурируем racoon (XX.XX.XX.XX - внешний IP адрес):

    # vim /etc/racoon/racoon.conf

    path include "/etc/racoon";
    path pre_shared_key "/etc/racoon/psk.txt";
    path certificate "/etc/racoon/certs";
    path script "/etc/racoon/scripts";

    listen {
            isakmp           XX.XX.XX.XX [500];
            isakmp_natt      XX.XX.XX.XX [4500];
            strict_address;
    }
    
    remote anonymous {
            # Алгоритм обмена ключами, есть два варианта aggresive и main. 
            # Выбирайте main, это более безопасно
            exchange_mode main;
            doi ipsec_doi;
            # Как часто менять ключи. Нужен баланс между паранойей и не паранойей
            # Собственно шифрование пакетов просходит при помощи ключей которые
            # Генерируют сервер и клиент. Сертификаты используются только для аутентификации
            lifetime time 24 hour;
            passive on;
            generate_policy on;
            proposal_check obey;
            # Включить механизм NAT-T
            nat_traversal on;
            # Разрешить принимать фрагментированые пакеты IKE (может с MTU проблемы)
            ike_frag on;
            # Указываем что мы должны проверять идентификаторы сертификата (ASN)
            # Чтобы враг не мог подключиться и авторизоваться произвольным сертификатом
            # ASN это строка типа /C=US/ST=CA/L=SanFrancisco/
            # O=Fort-Funston/CN=cn.example.com/emailAddress=me@myhost.mydomain
            # Вы её задаёте при генерации сертификата
            verify_identifier on;
            my_identifier asn1dn;
            peers_identifier asn1dn;
            # DPD - dead peer detection. Обнаружение мертвых соседей.
            # keep-alive раз в 10 сек.
            dpd_delay 10;
            # Сколько ждать ответа на keep-alive. По истечении - следующий. 
            dpd_retry 5;
            # Макс. количество неудач, после которых сосед считается мертвым.
            dpd_maxfail 5;
            # Посылаем запрос на сертификат
            send_cr on;
            # Проверяем пришедший сертификат.
            verify_cert on;
            # Разрешаем отправку своего сертификата 
            send_cert on;
            # Непосредственно сертификат и ключ сервера
            certificate_type x509 "server.crt" "server.key";
            # Корневой сертификат для проверки
            ca_type x509 "ca.crt";
    
            proposal {
                    # Можно выбрать aes, но как-то не все клиенты его поддерживают
                    encryption_algorithm 3des;
                    # Алгоритм вычисления хэшей пакетов. Можно поставить md5 но не рекомендуется. 
                    # Также можно использовать sha256, но клиент под Android его не понимает
                    hash_algorithm sha1;
                    # Авторизация по сертификатам
                    authentication_method rsasig;
                    # Размер ключа Диффи-Хелмана. Длина ключа 1024 бита.
                    dh_group modp1024;
            }
    }
    
    sainfo anonymous
    {
            encryption_algorithm     aes,3des;
            authentication_algorithm hmac_sha1;
            compression_algorithm    deflate;
            pfs_group                modp1024;
    }

Скопируем сертификаты:

    # mkdir -p /etc/racoon/certs
    # cp /root/easy-rsa/2.0/keys/ca.* /etc/racoon/certs/
    # cp /root/easy-rsa/2.0/keys/server.* /etc/racoon/certs/
    # cp /root/easy-rsa/2.0/keys/dh1024.pem /etc/racoon/certs/

Создадим базу политик безопасности, без них клиенты за NAT не будут работать:

    # vim /etc/ipsec-tools.conf 
    #!/usr/sbin/setkey -f
    spdadd 0.0.0.0/0 [l2tp] 0.0.0.0/0 udp -P out ipsec
            esp/transport//require;
    spdadd 0.0.0.0/0 0.0.0.0/0 [l2tp] udp -P in ipsec
            esp/transport//require;


Для работы IPsec необходимо разрешить протоколоы ESP и AH, а также открыть порты для IKE (_udp/500_, _udp/4500_):

    # iptables -A INPUT -p esp -j ACCEPT
    # iptables -A INPUT -p ah -j ACCEPT
    # iptables -A INPUT -p udp --dport 500 -j ACCEPT
    # iptables -A INPUT -p udp --dport 4500 -j ACCEPT

    # iptables -A OUTPUT -p esp -j ACCEPT
    # iptables -A OUTPUT -p ah -j ACCEPT
    # iptables -A OUTPUT -p udp --dport 500 -j ACCEPT
    # iptables -A OUTPUT -p udp --sport 4500 -j ACCEPT

## Установка и настройка xl2tpd

Установим пакет **xl2tpd**:

    # aptitude install xl2tpd

Правим конфигурационный файл xl2tpd:

    # vim /etc/xl2tpd/xl2tpd.conf 
    [global]
    ipsec saref = yes
    force userspace = yes
    listen-addr = XX.XX.XX.XX
    [lns default]
    local ip = 10.203.123.200
    ip range = 10.203.123.201-10.203.123.210
    refuse pap = yes
    require authentication = yes
    ppp debug = yes
    length bit = yes
    pppoptfile = /etc/ppp/options.xl2tpd

При указании локальной сети учитывайте, что удалённая локальная сеть обязательно должна не совпадать с вашей. То есть если на сервере и в офисе будет локальная сеть 10.10.10.1 - ничего работать не будет.

Правим конфигурационный файл pppd:

    # vim /etc/ppp/options.xl2tpd
    ms-dns 8.8.8.8
    ms-dns 8.8.4.4
    require-mschap-v2
    asyncmap 0
    auth
    crtscts
    lock
    hide-password
    modem
    debug
    name l2tpd
    proxyarp
    lcp-echo-interval 10
    lcp-echo-failure 100

Добавляем авторизацию по паролю в xl2tpd:

    # vim  /etc/ppp/chap-secrets 
    # Secrets for authentication using CHAP
    # client	server	secret			IP addresses
    client * password *


P.S. Я не знаю что такое WINS, поэтому я их убрал. DNS серверы вы можете указать свои.

Для того чтобы L2TP трафик мог ходить нам нужно открыть на фаерволе порт _udp/1701_, дополнительно делаем так, чтобы в этот порт не попал не IPsec трафик:

    # iptables -A INPUT -p udp -m policy --dir in --pol ipsec -m udp --dport 1701 -j ACCEPT
    # iptables -A OUTPUT -p udp -m policy --dir out --pol ipsec -m udp --dport 1701 -j ACCEPT
    # iptables -A FORWARD -i ppp+ -m state --state NEW,RELATED,ESTABLISHED -j ACCEPT 

Настраиваем NAT, чтобы ходить в сеть с IP VPN сервера.

    # iptables -t nat -A POSTROUTING -o eth0 -s 10.203.123.1/24 -j MASQUERADE
    # iptables -A FORWARD -s 10.203.123.0/24 -j ACCEPT 
    # vim /etc/sysctl.conf
    net.ipv4.ip_forward = 1
    net.ipv4.conf.default.rp_filter = 0
    net.ipv4.conf.default.accept_source_route = 0
    net.ipv4.conf.all.send_redirects = 0
    net.ipv4.conf.default.send_redirects = 0
    net.ipv4.icmp_ignore_bogus_error_responses = 1

    # sysctl -p

Сохраним настройки фаервола, чтобы они применялись при старте системы:
    
    # iptables-save > /etc/iptables.up.rules
    # cat /etc/network/if-up.d/iptables 
    #!/bin/sh
    iptables-restore < /etc/iptables.up.rules
    # chmod u+x /etc/network/if-up.d/iptables


## Проверка

Перезапускаем, проверяем что всё работает и сервер слушает тот порт, что нужно:

    # invoke-rc.d setkey restart
    Flushing IPsec SA/SP database: done.
    Loading IPsec SA/SP database: 
     - /etc/ipsec-tools.conf
    done.
    done.

    # invoke-rc.d racoon restart
    Stopping IKE (ISAKMP/Oakley) server: racoon.
    Starting IKE (ISAKMP/Oakley) server: racoon.

    # invoke-rc.d xl2tpd restart
    Restarting xl2tpd: xl2tpd.

    # netstat -nlp | egrep "1701|500|4500"
    udp        0      0 XX.XX.XX.XX:500         0.0.0.0:*                           1819/racoon     
    udp        0      0 XX.XX.XX.XX:4500        0.0.0.0:*                           1819/racoon     
    udp        0      0 XX.XX.XX.XX:1701        0.0.0.0:*                           1866/xl2tpd     
     
## Настройка клиента

### Генерация сертификата клиента

Создадим ключи для клиента:

    # cd /root/easy-rsa/2.0/
    # . ./vars
    # ./build-key-pkcs12 client

Нам необходимо использовать именно формат pkcs12, потому что только этот формат сертификатов поддерживается Windows и Android. При этом обычные key и crt файлы сохранятся.

Забираем к себе файлы _ca.crt_, _client.crt_, _client.key_, _client.p12_.

### Linux клиент (отсутсвует)

_Мне не удалось пока получить работающий конфиг для линуксового клиента причём соединение IPsec устанавливается, но xl2tpd отваливается по таймауту._

_Если у кого-нибудь всё таки есть решение, или готов помочь мне с этим вопросом - буду рад любой информации._

_На текущий момент у меня на сервере бежит два VPN сервера: racoon+xl2tpd для Android/Windows клиентов и OpenVPN для Linux-клиентов._

### Android клиент

В качестве основы берём Android 4.0.3 на Huawei Honor (я использую английскую локаль, так что не серчайте).

Для подключения нам понадобится _ca.crt_ и _client.p12_. Кладём их в корень карты памяти.

**Menu -> System Settings -> Security -> Screen Lock** 

Выставляете там пароль на экран блокировки (иначе VPN не включить и сертификаты не инсталлировать). Далее там же:

**Install from SD card**

Выбираете CA и сам сертификат. Сертификат назовите как-нибудь по человечески, а не как он там предлагает.

Далее:

**System Settings -> More... -> VPN -> Add VPN Network**

    Name: Имя подключения
    Type: L2TP/IPSec RSA
    Server address: XX.XX.XX.XX или доменное имя ассоциированое в этот адрес
    IPSec user certificate: Выбираете сертификат
    IPSec CA certificate: ca.crt

Сохраняем.

Далее жмём на название подключения

    Username: client
    Password: password

Жмём Connect и теперь можно безопасно сидеть в кафешке и лазать по сайтам.

### Windows клиент

_Для автора самым сложным всегда будет попытка понять что, куда и зачем делается в Windows и те проблемы, с которыми играючи справляются спецы - настоящий тёмный лес на вражеской территории_

Самое главное - правильно установить сертификат доступа. С этим я провозился порядочно долго. Вроде нажал - импортировать сертификат. И даже CA на всякий случай тоже (хотя в p12 и CA есть, и ключ, и сертификат). Не получается аленький цветочек. Оказывается сертификат берётся не из хранилища пользователя (вы ведь работаете не с правами администратора, правда?). У меня Windows 7, чего и вам советую.

Импорт сертификата выглядит так:

**"Пуск"** -> **Выполнить** (это такая строчка с поиском) -> **mmc** -> **Запустить от имени администратора** -> **Файл** -> **Добавить или удалить оснастку**.

Выбираете "Сертификаты", Добавить, для учётной записи компьютера, локальным компьютером. Жмём Ок.

Выбираете **Сертификаты**, **Личное**, **Меню: Действие** -> **Все задачи** -> **Импорт**

Далее выбираете сертификат (нужно в Обзоре выбрать "Файл обмена личной информацией (*.pfx, *.p12)"), будьте внимательны, выбирайте именно _client.p12_, а то я много раз _client.crt_ импортировал. Вводите пароль, выбираете "Автоматически выбрать хранилище на основе типа сертификата", Далее, Готово.

Теперь настраиваем клиент:

**Центр управления сетями и общим доступом** -> **Настройка нового подключения или сети** -> **Подключение к рабочему месту** -> **Использовать моё подключение к Интернету (VPN)**

    Интернет адрес: XX.XX.XX.XX или доменное имя ассоциированое в этот адрес
    Имя: любое

Далее

    Имя пользователя: client
    Пароль: password

Далее, будет долгая проверка типа подключения по окончании которой вы успешно подключитесь.

    
## FAQ

В этом разделе я буду постепенно пополнять список вопросов и ответов, возможно с вариантами решения (если мне удастся воспроизвести проблему).

### Подключение не доходит до racoon

Проверьте настройки вашего фаервола, причём как со стороны сервера, так и со стороны клиента.

Важно чтобы были открыты udp порты 500, 1701, 4500 и разрешён трансфер протоколов ESP (протокол номер 50) и AH (51).

В Linux можно смотреть идёт ли вообще какой-либо трафик по разрешающим правилам:

    # iptables -L -v -n
    Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
     pkts bytes target     prot opt in     out     source               destination         
    
        5  2360 ACCEPT     udp  --  *      *       0.0.0.0/0            0.0.0.0/0           udp dpt:500 
        4  5960 ACCEPT     udp  --  *      *       0.0.0.0/0            0.0.0.0/0           udp dpt:4500 

Так это должно выглядеть если правило работает, если pkts и bytes - 0, тогда какое-то из правил запрещает прохождение трафика. Например это может быть что-то вроде:

    # iptables-save
    -A FORWARD -j REJECT --reject-with icmp-port-unreachable 
    -A INPUT -p udp -m udp --dport 500 -j ACCEPT 

А должно быть наоборот: сначала ACCEPT, потом REJECT. Ну это в фаерволе типа - запретить вообще всё и разрешить то, что нужно (рекомендую именно такой тип).

Также следует учитывать, что только ОДНА сторона может быть за NAT.

Ещё следует учитывать, что могут быть хитрые роутеры, которые не будут пропускать ipsec трафик в принципе, хоть у них и может быть написано, что они поддерживают IPsec. Они тем самым говорят, что поддерживают _свой_ вариант IPsec.

## Заключение

Я с удовольствием в комментариях отвечу на вопросы по инструкции по возможности помогу решить проблемы которые у вас возникли. Надеюсь статья вам поможет.

## Использованные материалы

 1. [IPsec теория и практика](http://lissyara.su/articles/freebsd/security/ipsec2/)
 2. [IPsec L2TP VPN server](http://en.gentoo-wiki.com/wiki/IPsec_L2TP_VPN_server)
 3. Openswan: Building and Integrating Virtual Private Networks

*[ESP]: Encapsulated security payload. Протокол номер 50. Он отличается от AH немногим, он также аутентифицирует пакет, но и добавляет различные политики безопасности, и может даже зашифровать их.
*[IKE]: Internet key exchange daemon. Механизм безопасного обмена ключами.
*[AH]: Протокол номер 51 (посмотреть протоколы можно в /etc/protocols). Он не аутентфицирует заголовок IP пакета, как можно бы было подумать из названия, он аутентифицирует данные передаваемые в пакете, но не шифрует их.
*[NAT-T]: Механизм позволяющий шифрованому трафику проходить через NAT. Трафик при этом посылается UDP пакетом на порт 4500.
