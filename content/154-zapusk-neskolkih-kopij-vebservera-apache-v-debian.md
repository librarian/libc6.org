Title: Запуск нескольких копий вебсервера Apache в Debian
Slug: zapusk-neskolkih-kopij-vebservera-apache-v-debian
Category: Администрирование
Date: 2012-09-14 01:01
Source: False

У FreeBSD есть классный функционал по работе с вебсервером Apache. Называется профили. [Инструкцию](http://wiki.apache.org/httpd/RunningMultipleApacheInstances) по использованию можно прочитать на официальном сайте Apache.

Я объясню почему этот функционал нереально крут. С его помощью вы можете запустить, например, несколько версий PHP на одном сервере, или запустить prefork для отдельного пользователя, в то время как остальные будут использовать itk. В общем чрезвычайно полезная штука.

Я сильно расстраивался по поводу того, как это классно сделано в FreeBSD и какие мы все нищеброды в Linux.

Но нет, в Linux тоже можно запустить несколько копий вебсервера.

Всё описано в документе /usr/share/doc/apache2/README.multiple-instances

И установка будет выглядеть вообще просто:

     # /usr/share/doc/apache2.2-common/examples/setup-instance new
     # vim /etc/apache2-new/ports.conf

Не забудьте поменять порт в ports.conf
