Title: Подключение к VPN нажатием на иконку
Slug: podkljuchenie-k-vpn-nazhatiem-na-ikonku
Category: Администрирование
Date: 2013-04-01 00:28
Source: False

Я в работе использую Ubuntu 12.04 и там, чтобы включить VPN нужно сделать несколько лишних действий:

 1. Подвести курсор к иконке Network Manager.
 2. Кликнуть
 3. Привести вниз, до VPN connections
 4. Выбрать нужное подключение

В общем на ноутбуке, без мышки, это изрядно бесит.

Так что я немного погуглил и сделал скрипт для запуска подключения и разместил его на панели Unity.

Итак, приступим:

 1\. Создаём скрипт:

    $ vim ~/bin/launch-vpn.sh
    #!/bin/bash
    connection="CONNECTION_NAME"
    if nmcli con status id "$connection" > /dev/null 2>&1;
    then
        nmcli con down id "$connection" > /dev/null 2>&1
    else
        nmcli con up id "$connection" > /dev/null 2>&1
    fi
    $ chmod u+x ~/bin/launch-vpn.sh

 2\. Создаём desktop файл, чтобы его добавить на панель запуска

    $ sudo mkdir -p /usr/local/share/applications/
    $ sudo vim /usr/local/share/applications/launch-vpn.desktop
    [Desktop Entry]
    Type=Application
    Terminal=true
    Icon=nm-vpn-active-lock
    Name=unmount-mount
    Exec=/home/user/bin/launch-vpn.sh
    Name=Launch VPN
    Terminal=false

 3\. Открываем директорию /usr/local/share/applications/ в Nautilus и перетаскиваем файл на панель запуска.
 4\. Радуемся!

Теперь VPN можно включить нажав Win+0 (ну это у меня).
