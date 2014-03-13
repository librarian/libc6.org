Title: Лимитирование ресурсов виртуальной машины
Slug: limiting
Category: Виртуализация
Date: 2012-04-26 14:32
Source: False

[TOC]

В предыдущих сериях публикациях мы рассмотрели с вами вопросы [подготовки
хост-машины][2], создания и [клонирования][3] виртуальных машин. Сегодня я
поведаю о не менее важном вопросе — об ограничении использования ресурсов
виртуальными машинами.

## Введение в cgroups

Для ограничения ресурсов, используемых виртуальными машинами, я предлагаю
использовать **[cgroups][4]** — подсистему ядра, которая для установки
требуемых ограничений использует планировщих задач linux.

В рунете работа **cgroups** практически не освещена, в зарубежных интернетах,
в основном, всё ограничивается описанием знаменитого патча «[200 lines kernel
patch that does wonders][5]», кроме, пожалуй, [статьи Daniel Berrange][6].

В этой статье я хочу рассмотреть работу с **cgroups** применительно к
виртуальным машинам, но это совершенно не мешает использовать эту подсистему и
для выполнения обычных десктопных задач.

По сути, **cgroups** — это иерархическая файловая система, аналогичная /sys
или /proc, которая предоставляет простой интерфейс доступа к внутренним
механизмам распределения ресурсов в ядре. Понять, что представляет собой эта
файловая система, нам поможет пример: создадим точки монтирования и смонтируем
туда два контроллера — **cpu** и **blkio**, и посмотрим, что там внутри.

    
    
    # mkdir /cgroup
    # mkdir /cgroup/cpu
    # mkdir /cgroup/blkio
    # mount -t cgroup -ocpu cgroup /cgroup/cpu
    # mount -t cgroup -oblkio cgroup /cgroup/blkio
    # ls /cgroup/cpu
    cgroup.clone_children  cgroup.event_control  cgroup.procs  cpu.rt_period_us  cpu.rt_runtime_us  cpu.shares  notify_on_release  release_agent  sysdefault  tasks
    # ls /cgroup/blkio
    blkio.io_merged         blkio.io_service_time  blkio.throttle.io_service_bytes  blkio.throttle.write_bps_device   blkio.weight_device    tasks blkio.io_queued         blkio.io_wait_time     blkio.throttle.io_serviced       blkio.throttle.write_iops_device  cgroup.clone_children  notify_on_release blkio.io_service_bytes
    blkio.reset_stats  blkio.throttle.read_bps_device   blkio.time cgroup.event_control release_agent
    blkio.io_serviced blkio.sectors blkio.throttle.read_iops_device  blkio.weightcgroup.procs sysdefault
    

В файле **tasks** в каждой ветви дерева содержатся PID процессов, которые
будут управляться через определённую группу в cgroups. Таким образом можно
реализовывать иерархическую структуру лимитирования процессов. Cледует
учитывать, что лимиты применяются для всех процессов в группе.

## Лимитирование

### Лимитирование процессорной нагрузки

Немного о том, как можно ограничить процесс. Сделать это можно очень просто:

  * Выбираем PID, который хотим поместить в cgroups. 
  * Помещаем его в tasks.
  * Выставляем лимиты (присваиваем процессу вес, его можно выставить произвольно, но значение должно быть больше нуля). 
    

`echo $$ > /cgroup/cpu/tasks`

`echo 100 > /cgroup/cpu/cpu.shares`


Где **100** — вес, присвоенный текущему процессу bash.

В добавлении PID в tasks есть некоторые особенности. Например, можно
единовременно привязывать не более одного процесса, то есть, _echo PID1 PID2
..._ не сработает. Кроме того, следует учитывать, что echo не возвращает
корректный результат выполнения записи — для наиболее корректной реализации
нужно использовать системный вызов write().

У данного способа лимитирования есть существенный минус: лимиты нельзя жёстко
задать. Это ограничивает их использование в схеме предоставления услуг, когда
для виртуальной машины предполагается выделение жёсткого количества ресурсов.
Разработчики **cgroups** предполагают, что процессор будет использоваться на
100% (для чего он, собственно, и нужен), а не простаивать. Это реализуется при
помощи механизма весов.

Но этот минус зачастую является и большим плюсом. К примеру, возьмём три
виртуальные машины с весами 50, 30 и 20 соответственно, и одно ядро
процессора. Если на всех машинах будет максимальная загрузка, то каждой будет
выделено соответственно 50, 30 и 20 процентов CPU.

Часто возможна ситуация, когда виртуальной машине не нужны ресурсы в какой-то
момент времени. Допустим это будет вторая машина (с весом 30). Таким образом,
будут работать две машины с весами 50 и 20: одной машине будет выделено 71%
(50/(50+20)) ресурсов процессора, второй — 100% - 71% = 29%. Этот нюанс
распределения ресурсов позволит виртуальной машине при необходимости
использовать вплоть до полной мощности ядра.

### Лимитирование дисковой подсистемы

С дисками ситуация сложнее, хотя реализация лимитов там возможна более
жёсткая.

Посмотрим, что у нас есть внутри контроллера blkio, который отвечает за
управление дисковым IO.

    
    
    # cd /cgroup/blkio
    # ls
    blkio.io_merged blkio.io_service_bytes blkio.io_service_time blkio.reset_stats  blkio.time
    blkio.weight_device cgroup.event_control  release_agent blkio.io_queued
    blkio.io_serviced blkio.io_wait_time blkio.sectors blkio.weight cgroup.clone_children
    cgroup.procs notify_on_release tasks
    

Как вы можете видеть, есть несколько параметров ограничения производительности
дисковой подсистемы, а именно —

  * **iops** — количество операций ввода/вывода в секунду, 
  * **bps** — пропускная способность, 
  * **weight** — вес системы.

Чтобы указать, для какого диска и какого процесса нужно выставить **iops** или
**bps**, нужно определить _major_ и _minor_ диска (см. про [классификацию
устройств][7]) и переслать их в специальный файл (пример для bps):

    
    
    # ls -la /dev/sda
    brw-rw---- 1 root disk **8**, **0** Фев 11 13:59 /dev/sda
    # echo $$ > /cgroup/blkio/tasks
    # echo 3 > /proc/sys/vm/drop_caches
    # echo "8:0 1000000" > /cgroup/blkio/blkio.throttle.read_bps_device
    # echo "8:0 1000000" > /cgroup/blkio/blkio.throttle.write_bps_device
    # dd if=/dev/zero of=/tmp/zerofile bs=4K count=102400 oflag=direct
    # dd if=/tmp/zerofile of=/tmp/zerofile2 bs=4K count=102400
    25426+0 записей считано
    25425+0 записей написано
    скопировано 104140800 байт (104 MB), 102,21 c, 1,0 MB/c
    

Поэтому если вам необходимо использовать жёсткие лимиты, виртуальная машина
должна использовать отдельное блочное устройство (например раздел на LVM), у
которого будут _major_ и _minor_ . Для образов в виде файлов можно
использовать только контроллер **blkio.weight**.

Возникает закономерный вопрос, почему dd придерживается тех же лимитов, что мы
задали для интерпретатора bash. Всё очень просто: **cgroups** отслеживает и
детей, которые форкаются от родителя, и автоматически вносит их в tasks.

Следует отметить, что blkio.throttling* появляется, если включить в ядре
параметры **CONFIG_BLK_CGROUP** и **CONFIG_BLK_DEV_THROTTLING**. Рекомендую
ради интереса поискать в menuconfig по словам CGROUP и BLK — по умолчанию там
очень много всего интересного отключено.

К сожалению, **cgroups** лимитирует только обращения к диску без использования
кэширования. Если не сделать сброс кэшей или не указать у dd **oflag=direct**
или **iflag=direct**, лимиты применяться не будут. Подробнее об этом можно
почитать [здесь][8] и [здесь][9].

С **blkio.weight** всё проще: всё работает аналогично cpu.shares.

### Работа с cgroups от непривилегированного пользователя

В **cgroups** непривилегированный пользователь не может осуществлять запись.
Но есть набор утилит, входящих в проект [libcg][10], которые позволяют
работать с **cgroups**, не обладая административными привилегиями. В Debian их
можно установить вместе с пакетом **cgroup-bin**.

Установив пакет, посмотрим, какие утилиты входят в его состав:

    
    
    $ ls /usr/*bin/cg*
    /usr/bin/cgclassify  /usr/bin/cgdelete  /usr/bin/cgget  /usr/bin/cgsnapshot  /usr/sbin/cgconfigparser
    /usr/bin/cgcreate    /usr/bin/cgexec    /usr/bin/cgset  /usr/sbin/cgclear    /usr/sbin/cgrulesengd
    

Наиболее полезными для нас будут **cgcreate** и **cgdelete**, а также скрипт,
который, прочитав конфигурационный файл, будет автоматически при старте
системы создавать нужные группы — **cgconfigparser**.

Произведём настройку **cgconfig** так, чтобы при старте системы у нас
автоматически монтировалась нужная файловая система:

    
    
    $ cat /etc/cgconfig.conf
    mount {
        cpu     = /cgroup/cpu;
        cpuacct = /cgroup/cpuacct;
        devices = /cgroup/devices;
    #   memory  = /cgroup/memory;
        blkio   = /cgroup/blkio;
    #   freezer = /cgroup/freezer;
        cpuset  = /cgroup/cpuset;
    }
    $ sudo /etc/init.d/cgconfig restart
    

Контроллеры freezer и memory нам особо не нужны, а memory, к тому же,
отказывается монтироваться автоматически, и его при необходимости нам нужно
будет монтировать вручную.

Создадим группу, чтобы наш непривилегированный пользователь %username%
username мог заниматься самосовершенствованием:

    
    
    $ sudo cgcreate -f 750 -d 750 -a username:libvirt -t username:libvirt -g cpu,blkio:username
    

где:

  * -f и -d устанавливают права доступа на файлы и директории внутри группы, соответственно;
  * -a и -t устанавливают владельца на параметры подсистемы и файл tasks
  * -g создает для указанных контроллеров cpu и blkio группы относительно корня (например, в данном случае, это будут, соответственно, /cgroup/cpu/username и /cgroup/blkio/username).

После этого вы увидите, что в директориях /cgroup/cpu и /cgroup/blkio создана
директория username, в которую указанный пользователь username сможет
записывать задания для cgroups.

Очень удобно при запуске виртуальной машины создавать группу и прописывать там
лимиты, а при остановке — удалять группу:

    
    
    $ sudo cgdelete cpu,blkio:username
    

При использовании cgroups в обслуживании виртуальных машин можно несколько
автоматизировать процесс задания лимитов и создания групп. В файле
/etc/libvirt/qemu.conf можно задать контроллеры, с которыми qemu может
работать. Также можно добавить список устройств, к которым может иметь доступ
виртуальная машина:

    
    
    cgroup_controllers = [ "cpu", "devices", "memory", "cpuset", "blkio" ]
    cgroup_device_acl = [
        "/dev/null", "/dev/full", "/dev/zero",
        "/dev/random", "/dev/urandom",
        "/dev/ptmx", "/dev/kvm", "/dev/kqemu",
        "/dev/rtc", "/dev/hpet", "/dev/net/tun",
    ]
    

Для выставления весов cpu и blkio удобно использовать virsh (часть библиотеки
libvirt, см. в статье о [подготовке хост-системы][2]):

    
    
    $ virsh schedinfo --set cpu_shares=1024 debian_guest
    $ virsh blkiotune debian_guest --weight 1024
    

При этом в **/cgroup/cpu/sysdefault/libvirt/qemu/debian_guest/cpu.shares**
значение изменится на 1024. Но, к сожалению, в дереве sysdefault обычный
пользователь не может менять параметры.

### Лимитирование сетевой нагрузки

С ресурсами процессора и диска мы потихоньку разобрались. Теперь осталось
самое главное — сеть. Нам важно получить жёсткое разграничение полосы и при
этом приемлемые значения задержки и нагрузки на сервер. То, чем мы сейчас
будем заниматься, по-научному называется shaping и QoS (Quality of Service).
Выделить полосу несложно — гораздо сложнее рассмотреть различные сценарии
использования виртуальной машины.

Допустим, нам необходимо выделить виртуальной машине полосу 5 мбит.
Теоретически, вопрос простой, решается добавлением для [tc][11] правила
(полоса с минимальной задержкой):

    
    
    tc qdisc add dev debian_guest root handle 1: htb default 20
    tc class add dev debian_guest parent 1: classid 1:1 htb rate 5mbit burst 15k
    

Но исследование вопроса показывает, что такого простого разделения
недостаточно.

Предположим, что у нас идёт большой поток трафика по HTTP, и до сервера
достучаться сложно.

Это решается расставлением приоритетов.

    
    
    tc class add dev debian_guest parent 1:1 classid 1:10 htb rate 5mbit burst 15k prio 1
    

Все остальные:

    
    
    tc class add dev debian_guest parent 1:1 classid 1:20 htb rate 5mbit burst 15k prio 2
    tc qdisc add dev debian_guest parent 1:10 handle 10: sfq perturb 10
    

SSH нужно ставить выше:

    
    
    tc filter add dev debian_guest parent 1:0 protocol ip prio 10 u32 match ip tos 0x10 0xff flowid 1:10
    

ICMP-пакеты тоже нужно ставить повыше:

    
    
    tc filter add dev debian_guest parent 1:0 protocol ip prio 10 u32 match ip protocol 1 0xff flowid 1:10
    

TCP ACK также имеют высший приоритет:

    
    
    tc filter add dev debian_guest parent 1: protocol ip prio 10 u32 match ip protocol 6 0xff match u8 0x05 0x0f at 0 match u16 0x0000 0xffc0 at 2 match u8 0x10 0xff at 33 flowid 1:10
    

А все остальные пусть идут... Со вторым приоритетом.

А это у нас входящий трафик:

    
    
    tc qdisc add dev debian_guest handle ffff: ingress
    tc filter add dev debian_guest parent ffff: protocol ip prio 50 u32 match ip src 0.0.0.0/0 police rate 5mbit burst 15k drop flowid :1
    

Можно добавить ещё 100500 разных правил, но нужно учитывать специфику
виртуальной машины — может, что-то нужно закрыть, и т.п.

А вообще не помешает закрыть всякие IRC порты (6667-6669), торренты
(6881-6889) и прочие богомерзкие сервисы.

При остановке можно удалять правила, которые не потребуются в дальнейшем:

    
    
    tc qdisc del dev debian_guest root
    tc qdisc del dev debian_guest ingress
    

Статистику по интерфейсу легко можно посмотреть:

    
    
    tc -s -d qdisc show dev debian_guest
    tc -s -d class show dev debian_guest
    tc -s -d filter show dev debian_guest
    

Соответственно, можно посмотреть, сколько трафика поступает на интерфейс и
уходит с него, и легко настроить всякие рисовалки графиков.

Очень удобно можно совмещать правила iptables и tc при помощи модуля mangle
(да поможет вам Google) и потом управлять этим трафиком через tc. Например,
нам нужно пометить трафик для bittorent и выделить для него полосу в 1
килобит:

    
    
    tc class add dev debian_guest parent 1:1 classid 1:30 htb rate 1kbit prio 3
    tc qdisc add dev debian_guest parent 1:30 handle 30: sfq perturb 10
    iptables -t mangle -A POSTROUTING -o debian_guest --sport 6881:6889 -j MARK --set-mark 30
    iptables -t mangle -A POSTROUTING -o debian_guest --dport 6881:6889 -j MARK --set-mark 30
    

## Заключение

Прочитав цикл статей ([1][12], [2][2], [3][3] и [4][13]), вы сможете
установить и настроить систему виртуализации KVM, управляющий тулкит libvirt,
собрать свой собственный образ виртуальной машины. Всё это позволит вам
сэкономить ресурсы, повысить надёжность системы (за счёт живого мигрирования
гостевых систем), упростит создание бэкапов (например при помощи LVM
снапшотов).

Надеюсь, мне удалось донести до вас некоторую полезную информацию, и мой опыт,
изложенный в данной серии статей, поможет вам сэкономить своё время.

На этом первый цикл статей завершается. Если что-то интересно — спрашивайте в
комментариях, я всегда готов ответить на возникающие вопросы.

   [1]: http://sprinthost.ru/img/articles/20100622_Habrahabr_Limiting/tux_in_jail.png
   [2]: http://habrahabr.ru/blogs/virtualization/120717/
   [3]: http://habrahabr.ru/blogs/virtualization/121218/
   [4]: http://www.kernel.org/doc/Documentation/cgroups/
   [5]: http://marc.info/?l=linux-kernel&m=128978361700898&w=2
   [6]: http://berrange.com/posts/2009/12/03/using-cgroups-with-libvirt-and-lxckvm-guests-in-fedora-12/
   [7]: http://www.kernel.org/pub/linux/docs/device-list/devices.txt
   [8]: https://www.redhat.com/archives/libvir-list/2011-February/msg00177.html
   [9]: http://www.mjmwired.net/kernel/Documentation/cgroups/blkio-controller.txt
   [10]: http://libcg.sourceforge.net/
   [11]: http://lartc.org/howto/
   [12]: http://habrahabr.ru/blogs/virtualization/120432/
   [13]: http://habrahabr.ru/blogs/virtualization/122425/
