Title: Segmentation fault в PHP из-за ImageMagick.
Slug: segmentation-fault-php-imagemagick
Category: Администрирование
Date: 2012-10-28 23:19
Source: False

Неделю боролся с дикой проблемой. Апач ни с того ни с сего начал валиться в сегфолт и писал что-то типа:

    apache2[16717]: segfault at 7fd2efb87ed2 ip 00007fd2efb87ed2 sp 00007fd2eb941e78 error 14 in libnss_files-2.11.3.so[7fd2f239a000+c000]

Или так:

    apache2[22399]: segfault at 7fa4e9c24d3d ip 00007fa4e9c24d3d sp 00007fa4e5449e40 error 14 in libltdl.so.7.2.1[7fa4ec437000+9000]

Или даже так:

    apache2[25028]: segfault at 7f8ec2314d33 ip 00007f8ec2314d33 sp 00007f8ebf4c2e40 error 14 in xmlrpc.so[7f8ec4341000+12000]

Или вот так:

    apache2[30175]: segfault at 7fe7ea16fd3d ip 00007fe7ea16fd3d sp 00007fe7e94dbe40 error 14 in memcache.so[7fe7ef30d000+17000]

А ещё ругается на GeoIP и все остальные расширения, _кроме_ imagick.so.

Я пробовал перемешивать порядок загрузки, выгружать модули, анализировать корки, но последнее на что я думал - это ImageMagick.

Ну и попробовал его отключить и вуаля - всё работает прекрасно.

В итоге наткнулся на два прекрасных бага: [#568349](http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=568349) и [#652960](http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=652960).

Если коротко, то imagemagick так работает с libgomp1, что создание больше чем одного треда - сваливает php, а за ним и весь Apache в корку.
