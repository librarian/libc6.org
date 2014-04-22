Title: Расширение зашифрованного раздела диска.
Slug: rasshirenie-zashifrovannogo-razdela-diska
Category: Администрирование
Date: 2012-05-14 01:45
Source: False

Как и обещал, увеличение зашифрованного раздела.

Приступим:

1\. Удаляем старый раздел (он ведь нам уже не нужен):

    $ sudo lvremove /dev/mapper/vg-home

2\. Теперь у нас освободилось немного дискового пространства, теперь можно приступать к увеличению разделов. Будем это делать снизу вверх. Для начала LVM:

    $ sudo lvresize -L+50G /dev/mapper/vg-crypthome 
      Extending logical volume crypthome to 90,00 GiB
      Logical volume crypthome successfully resized

3\. Сейчас можно посмотреть какой размер у нас имеют различные разделы диска:

    $ ls -lsha /dev/mapper/vg-crypthome
    0 lrwxrwxrwx 1 root root 7 Май 14 14:38 /dev/mapper/vg-crypthome -> ../dm-3

За LVM раздел /dev/mapper/vg-crypthome у нас отвечает устройство dm-3, а за зашифрованный раздел: dm-4

    $ ls -lsha /dev/dm-*
    0 brw-rw---- 1 root disk 254, 0 Май 14 03:36 /dev/dm-0
    0 brw-rw---- 1 root disk 254, 1 Май 14 03:36 /dev/dm-1
    0 brw-rw---- 1 root disk 254, 3 Май 14 14:38 /dev/dm-3
    0 brw-rw---- 1 root disk 254, 4 Май 14 12:34 /dev/dm-4

    $ grep 254 /proc/partitions 
     254        0    9764864 dm-0
     254        1    4001792 dm-1
     254        3   94371840 dm-3
     254        4   41942012 dm-4

Как видно, устройство dm-3 и dm-4 имеют разный размер. Это из-за того, что мы в пункте 2, его изменили.

4\. Изменим размер зашифрованного раздела:

    $ sudo cryptsetup resize crypt

    $ grep 254 /proc/partitions 
     254        0    9764864 dm-0
     254        1    4001792 dm-1
     254        3   94371840 dm-3
     254        4   94370812 dm-4

Теперь разделы имеют почти одинаковый размер.

5\. Изменяем размер файловой системы:

    $ sudo resize2fs /dev/mapper/crypt 
    resize2fs 1.41.12 (17-May-2010)
    Filesystem at /dev/mapper/crypt is mounted on /home; on-line resizing required
    old desc_blocks = 3, new_desc_blocks = 6
    Performing an on-line resize of /dev/mapper/crypt to 23592703 (4k) blocks.
    The filesystem on /dev/mapper/crypt is now 23592703 blocks long.

6\. Проверяем:

    $ df -h | grep /home
    /dev/mapper/crypt      89G  4,3G   80G   6% /home

Я оставил чуть чуть места, чтобы сделать в будущем, как появится время, ещё раздел для LVM снэпшотов. Хотя я не уверен, что снэпшоты зашифрованного раздела - хорошая идея. Об этом тоже напишу.
