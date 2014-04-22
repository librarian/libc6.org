Title: Баг с удалением устройства под LVM snapshot.
Slug: bag-s-udaleniem-ustrojstva-pod-lvm-snapshot
Category: Администрирование
Date: 2012-05-14 20:39
Source: False

Наткнулся тут вот только что.

Хотел сделать устройство для снапшотов своего закриптованного домика.

    $ sudo lvcreate -L40G -s -n backup /dev/vg/crypthome

Однако он отказался монтироваться, обосновывая тем, что не знает какая там файловая система (а какая она - никакая, там зашифрованный раздел). В общем и пока решил данными не рисковать, удалить раздел, чтобы туда-сюда потом подвигать и дальше продолжить играться с LVM.

    $ sudo lvremove /dev/vg/backup
    Can't remove open logical volume "backup"

А как он вообще может быть открыт, если он даже не примонтирован никуда. Ладно, попробуем отключить:

    $ sudo lvchange -an /dev/vg/backup
    LV vg/backup in use: not deactivating

Отлично, теперь он ещё и не деактивируется.

Решение удалось нагуглить в баге [#549691](http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=549691). 

    $ sudo dmsetup remove vg-backup
    $ sudo lvremove /dev/vg/backup

Я потом может покопаюсь, узнаю почему всё именно так. Ну и идею подключить снэпшоты для шифрованного раздела не хочется отбрасывать. Завтра спрошу у знающих людей.
