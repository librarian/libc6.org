Title: Debian in Ram. Загрузка Debian в оперативную память. Debirf.
Slug: debian-in-ram-zagruzka-debian-v-operativnuju-pamjat-debirf
Category: Администрирование
Date: 2009-06-16 19:30
Source: False

В общем бродил тут по интернетам, по дебиановским форумам в поисках инструкций
на тему: "Как загрузить Linux в оперативную память" В общем нашёл удобное
решение в виде пакета [debirf][1]. Этот пакет(на самом деле это просто набор
bash скриптов) предоставляет удобный интерфейс для установки и создания образа
дистрибутива при помощи debootstrap, initramfs-tools и bash, для упаковки его
в образы initrd. Дополнительно позволяет делать образы iso, которые при помощи
того же unetbootin можно закатать на флэшку. В общем, это прекрасный
инструмент для создания собственного livecd.

Для того чтобы этот пакет появился у Вас, в Debian Lenny(в squeeze, sid и
выше, а также в Ubuntu этот пакет должен быть), нужно добавить в
**/etc/apt/sources.list**

    
    deb http: //cmrg.fifthhorseman.net/debian unstable debirf
    deb-src http: //cmrg.fifthhorseman.net/debian unstable debirf
    

И импортировать gpg ключ репозитория:

    
    wget http: //fifthhorseman.net/dkg.gpg -O -- | sudo apt-key add --
    sudo aptitude update
    sudo aptitude install debirf

Теперь, после установки, можно начать создавать свой супер-мега-дистрибутив.
Небольшое техническое отступление, debirf работает с так называемыми
"сценариями". По умолчанию **debirf** предоставляет 3 сценария установки:
**xkiosk** -- система с очень простым WM и Iceweasel. **rescue** -- типичные
rescuecd утилиты типа install lvm2 lsof hdparm partimage pciutils testdisk
foremost mdadm smartmontools eject wodim ddrescue cryptsetup sdparm. (Набор
весьма маленький, однако легко можно добавить нужные Вам утилиты) **minimal**
-- базовая установка Debian. Тут сказать нечего, это, так сказать основа для
будущей системы. Итак, приступим к установке непосредственно livecd: Создадим
папку с говорящим названием ;)

    
    mkdir ~/mycooldebiandistro
    cd ~/mycooldebiandistro

Распакуем один из образов:

    
    tar xzf /usr/share/doc/debirf/example-profiles/minimal.tgz

Теперь в папке будет папка minimal, в ней соответственно **debirf.conf** и
папка **modules**, с сценариями установки, можно воспользоваться базовыми
сценарями из **/usr/share/debirf/modules/** В файле **debirf.conf** можно
задать следующие параметры:

    
    DEBIRF_LABEL="debirf—minimal" //hostname дистрибутива
    #DEBIRF_BUILDD=/home/user/mycooldebiandistro //папка где будем собирать наш дистрибутив
    #DEBIRF_SUITE=lenny //указываем имя версии дистрибутива
    #DEBIRF_DISTRO=debian //Указываем дистрибутив который будем собирать
    #DEBIRF_MIRROR=http: //mirrors.kernel.org/${DEBIRF_DISTRO} //То, откуда скачивать пакеты для дистрибутива
    #DEBIRF_KEYRING=ТУТIDКЛЮЧА //для подписи нашего debootstrap
    export http_proxy=Прокси
    

Итак, сценарии мы распаковали, с версиями дистрибутива определились. Будем
начинать сборку:

    
    debirf make minimal

Следует, однако, заметить, что по умолчанию собирается generic ядро для этого
дистрибутива. Чтобы задать своё ядро(а я так и сделал) нужно запускать с
параметром -k

    
    debirf make -k /path/to/kelnel.deb minimal

В моём случаеэто выглядело так:

    
    debirf make -k … /linux—image—2.6.30—lib.30_2.6.30—lib.30—10.00. Custom_i386.deb xkiosk

Пока оно там скачивается, собирается в 2 файла, можно смело пойти перекусить
или ещё чего(а с моими медленными интернетами ещё и поспать можно было бы ;)
После этого скопируем initrd и vmlinuz файлы в /boot и добавим запись о них в
menu.lst

    
    cp vmlinuz—2.6.30—lib.30 /boot/
    cp debirf—xkiosk_lenny_2.6.30—lib.30.cgz /boot/

И прописываем в /boot/grub/menu.lst следующее:

    
    title Cool Debian Distro
    root (hd0, 0)
    kernel /boot/vmlinuz—2.6.30—lib.30
    initrd /boot/debirf—xkiosk_lenny_2.6.30—lib.30.cgz

После этого можно перезагружаться в свежую систему.

   [1]: http://cmrg.fifthhorseman.net/wiki/debirf
