Title: Подготовка хост-машины
Slug: setup
Category: Виртуализация
Date: 2012-04-26 14:29
Source: False

[TOC]

## Вступление

![tuxandbeastie][1]

Как и было обещано в [предыдущей статье][2], сегодня мы поговорим о базовой
настройке хост-машины для работы KVM.

Для начала необходимо узнать, есть ли у нашего процессора необходимые
инструкции для поддержки виртуализации.

    
    $ egrep '(vmx|svm)' /proc/cpuinfo

Если есть — это замечательно.

## Подготовка операционной системы

Установку Debian Squeeze я, пожалуй, описывать не буду: если уж вы добрались
до KVM, то установка системы — плёвое дело.

Устанавливать нужно будет 64-битную OS, поскольку необходимые пакеты есть
только для этой архитектуры.

В Debian Squeeze «свежесть» пакетов с KVM и сопутствующих программами нас
совсем не устраивает, поскольку очень много всяких фиксов и фич попросту
пройдут мимо нас. Поэтому мы добавим репозитории Debian Sid и experimental:

    
    deb [http://ftp.ru.debian.org/debian][3] sid main contrib non-free
    deb-src [http://ftp.ru.debian.org/debian][3] sid main contrib non-free
    
    deb [http://ftp.ru.debian.org/debian][3] experimental main contrib non-free
    deb-src [http://ftp.ru.debian.org/debian][3] experimental main contrib non-free

Указываем, что у нас базовый дистрибутив stable, а не то, что подумала
система:

    
    # echo 'APT::Default-Release "stable";' > /etc/apt/apt.conf.d/default

Оттуда нам понадобятся пакеты:

    
    # aptitude -t experimental install linux-image-2.6.39-1-amd64 qemu-kvm virtinst libvirt-bin

Из стабильного репозитория нам будут нужны:

    
    # aptitude install uml-utilities bridge-utils

На вашем рабочем десктопе вы можете поставить **virt-manager** (GUI-утилита),
который позволит удобно создавать нужные конфигурации виртуальных машин.

### Ядро

Ядро чем «свежее» — тем лучше (в известных пределах конечно: из git, например,
я бы ставить не рекомендовал). Хорошим вариантом будет 2.6.39, вышедшее
недавно.

Следует отметить, что в стандартном ядре отсутствует модуль для поддержки
записи в UFS2, и если планируется запускать гостевую FreeBSD, потребуется
собрать ядро с этим модулем. Ну и, конечно, в Debian-овском ядре отсутствуют
свежие версии cgroups.

Что должно быть включено в ядре для использования максимального объема
требуемого функционала:

    
    CONFIG_VIRTIO_BLK=y
    CONFIG_VIRTIO_NET=y
    CONFIG_VIRTIO_CONSOLE=y
    CONFIG_HW_RANDOM_VIRTIO=y
    CONFIG_VIRTIO=y
    CONFIG_VIRTIO_RING=y
    CONFIG_VIRTIO_PCI=y
    CONFIG_VIRTIO_BALLOON=y
    CONFIG_CGROUPS=y
    CONFIG_CGROUP_NS=y
    CONFIG_CGROUP_FREEZER=y
    CONFIG_CGROUP_DEVICE=y
    CONFIG_CGROUP_CPUACCT=y
    CONFIG_CGROUP_MEM_RES_CTLR=y
    CONFIG_CGROUP_MEM_RES_CTLR_SWAP=y
    CONFIG_CGROUP_MEM_RES_CTLR_SWAP_ENABLED=y
    CONFIG_CGROUP_SCHED=y
    CONFIG_BLK_CGROUP=y
    CONFIG_NET_CLS_CGROUP=y

Затем идём по [ссылке][4] и устанавливаем все deb-пакеты оттуда, копируем
insmod.static в /sbin/insmod.static (это нужно, поскольку в работе libguestfs
использует статически скомпилированную версию insmod, а в Debian и Ubuntu
такого файла [просто нет][5], однако в последней версиии [febootstrap][6] эту
проблему устранили, insmod.static более не нужно загружать на сервер).
libguestfs позволяет нам получать доступ к диску VDS через API libguestfs(C,
Perl, Python, PHP) или через утилиту guestfish.

### Первый блин

Сейчас мы установили все, необходимое для запуска VDS, их доступа в сеть и
установки самой виртуальной машины.

Давайте попробуем что-нибудь поставить, например, тот же самый Debian. Пока
без настройки сети, просто, по умолчанию.

Скачиваем установщик netinstall:

    
    $ wget http://cdimage.debian.org/debian-cd/6.0.1a/i386/iso-cd/debian-6.0.1a-i386-netinst.iso

Редактируем **/etc/libvirt/qemu.conf**, чтобы виртуальные машины работали у
нас от непривилегированного пользователя:

    
    user = "username"
    group = "libvirt"

Поскольку у нас будут использоваться tun-устройства, нужно выставить
capability **CAP_NET_ADMIN**, сделать это можно как для отдельного
исполняемого файла, так и для пользователя в целом, или настроить чтобы
libvirt не сбрасывал нужные права для qemu/kvm.

Выставляем для отдельного файла:

    
    sudo setcap cap_net_admin=ei /usr/bin/kvm

Или выставляем для пользователя в целом в файле
**/etc/security/capability.conf**:

    
    cap_net_admin username

Или выставляем соответствующую настройку в **/etc/libvirt/qemu.conf**:

    
    clear_emulator_capabilities = 0

Добавим пользователя в группу libvirt и kvm:

    
    # adduser username libvirt
    # adduser username kvm

Запустим установку виртуальной машины:

    
    $ virt-install --connect qemu:///system -n debian_guest -r 512 --arch=i686 --vcpus=1 --os-type=linux --os-variant=debiansqueeze --disk debian-6.0.1a-i386-netinst.iso,device=cdrom --disk debian_guest.img,bus=virtio,size=2,sparse=false,format=raw --network=default,model=virtio --hvm --accelerate --vnc

Подробно разберём параметры, которые мы указали:

  * **--connect qemu:///system** URL, по которому мы подключаемся к KVM. Подключаться можно через ssh.
  * **-n debian_guest** Имя гостевой системы.
  * **-r 512** Выделяемый объём оперативной памяти в мегабайтах.
  * **--arch=i686** Архитектура гостевой операционной системы.
  * **--vcpus=1** Количество виртуальных процессоров, доступных гостю.
  * **--os-type=linux --os-variant=debianlenny** Специфичные для данной операционной системы параметры.
  * **--disk debian-6.0.1a-i386-netinst.iso,device=cdrom** Загружаемся с диска, образ которого указали.
  * **--disk debian_guest.img,bus=virtio,size=2,sparse=false,format=raw** Создаём образ системы размером 2Гб, который сразу помещаем на диск (можно создать образ нулевого размера, но тогда возможна фрагментация, что получается несколько медленнее). Формат простой, можно сделать с dd файл. Драйвер диска virtio, использовать лучше virtio, чем ide: производительность их отличается если не на порядок, то в разы.
  * **--network=default,model=virtio** Сетевые настройки по умолчанию. В этом случае libvirt создаст мост, сделает dhcp сервер и выдаст через него адрес для доступа виртуальной машины.
  * **--hvm** Полная виртуализация — то есть, можно использовать собственные ядра.
  * **--accelerate** Работа через /dev/kvm.
  * **--vnc** Запускаем VNC, чтобы подключаться к текстовой консоли.

### Утилиты настройки и управления

Для управления установкой и для клонирования виртуальных машин у нас есть две
замечательные утилиты — графическая и консольная: **virt-manager** и
**virsh**, соответственно. Конечно, консольная версия намного богаче по
возможностям, но ничто не сравнится с видом графиков, от которых сердце
сисадмина млеет.

Думаю с **virt-manager** вы и сами разберётесь, давайте попробуем покопаться в
консольных внутренностях **virsh**. Вот несколько команд которые стоит
выполнить и посмотреть что из этого получится:

    
    $ virsh --connect qemu:///system list --all
    $ virsh --connect qemu:///system dominfo debian_guest
    $ virsh --connect qemu:///system stop debian_guest

Чтобы тысячу раз не писать **--connect qemu:///system**, добавьте:

    
    export VIRSH_DEFAULT_CONNECT_URI= qemu:///system

В .bashrc или просто выполните эту команду в терминале.

### Подготовка сети

В официальной документации предлагается использовать несколько вариантов
организации сети: NAT, bridged и прямое использование сетевых карт. И, к
сожалению, в различных примерах, которые я нашел в сети и на официальном
сайте, рассматриваются только NAT и bridged сети.

В моей конфигурации используются TUN/TAP устройства, на которые с eth0
маршрутизируется трафик. Коротко опишу, почему выбран именно такой способ
маршрутизации:

NAT нам не подходит, поскольку каждая VDS должна быть доступна из сети
напрямую.

Схема с мостами не очень надёжная, поскольку теоретически есть возможность
"захвата" IP адреса чужой виртуальной машины.

Итак:

    
    <interface type='ethernet'>
        <mac address='52:54:00:ef:40:1d'/>
        <ip address='10.10.10.100'/>
        <target dev='debian_guest'/>
        <model type='virtio'/>
    </interface>
    

Данный участок конфигурации нужно указывать непосредственно в конфигурационном
файле гостя, расположенного по адресу **/etc/libvirt/qemu/debian_guest.xml**.
Редактировать лучше всего через:

    
    $ virsh edit debian_guest

Тогда конфигурация обновится на лету, при условии, что машина не запущена. В
противном случае нужно будет подождать, пока она остановится, и запустить ее
снова.

Создадим необходимое нам виртуальное устройство.

Для начала нам нужно дать нашему пользователю возможность беспарольного
обращения к системным командам. Для этого добавим в sudoers:

    
    $ sudo visudo
    
    Cmnd_Alias      QEMU = /sbin/ifconfig, /sbin/modprobe, /usr/sbin/brctl, /usr/sbin/tunctl, /sbin/sysctl, /bin/ip, /usr/bin/cgcreate, /usr/bin/cgdelete, /sbin/tc
    username      ALL=(ALL:ALL) NOPASSWD: QEMU

Включим возможность форвардинга и проксирования arp-запросов:

    
    sudo sysctl net.ipv4.conf.all.forwarding=1
    sudo sysctl net.ipv4.conf.all.proxy_arp=1

Также можно добавить эти параметры в /etc/sysctl.conf и применить их:

    
    sudo sysctl -p

Создадим виртуальную сетевую карту и поднимем устройство:

    
    sudo tunctl -b -u username -t debian_guest
    sudo ifconfig debian_guest 0.0.0.0 up

Создадим маршрут на нужное нам устройство с нужного IP-адреса:

    
    sudo ip route add 10.10.10.100 dev debian_guest

Теперь можно запустить VDS:

    
    $ virsh start debian_guest

Подключившись к консоли, мы увидим, что сети нет, но у нас появилось
устройство **eth1**, вместо **eth0**. Это произошло потому, что система при
загрузке в **/etc/udev/rules.d/70-persistent-net.rules** прописывает mac-адрес
сетевой карты, и если mac сменился, она создаёт ещё одну запись о сетевой
карте, вроде этой:

    
    SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="xx:xx:xx:xx:xx:xx", ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="eth*", NAME="eth1"

Нужно удалить этот файл и перезагрузить VDS — после этого сетевая карта
определится корректно.

Пропишем новые сетевые настройки в гостевой системе:

    
    # ifconfig eth0 10.10.10.100 netmask 255.255.255.0
    # route add default gw 10.10.10.10

**10.10.10.10** - это IP-адрес хост-системы. Теперь мы сможем попинговать другие машины. 

Добавим DNS-серверы в /etc/resolv.conf, и будет совсем замечательно:

    
    nameserver 8.8.8.8

К слову, замечу, что оказалось очень удобно называть сетевые устройства,
принадлежащие VDS, также, как и сами VDS — отпадает необходимость искать, кому
принадлежит устройство tap0 или vnet0, или как там ещё можно их обозвать.

Если понадобится выдать виртуальной машине ещё один IP-адрес, достаточно будет
просто на хост-машине прописать ещё один маршрут:

    
    # ip route add 10.10.10.101 dev debian_guest

А в гостевой системе создать алиас для сетевого устройства:

    
    # ifconfig eth0:1 10.10.10.101

## В следующей части

В следующей статье я расскажу о том, как создать образ VDS, что вообще
меняется от системы к системе, и как эти параметры можно удобно менять.

   [1]: http://sprinthost.ru/img/articles/20100606_Habrahabr_Setup/tux_n_beastie_small.jpg
   [2]: http://habrahabr.ru/blogs/virtualization/120432/
   [3]: http://ftp.ru.debian.org/debian
   [4]: http://libguestfs.org/download/binaries/debian-packages/
   [5]: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=627353
   [6]: http://libguestfs.org/download/binaries/debian-packages/febootstrap_3.6-1_amd64.deb
