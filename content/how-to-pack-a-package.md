Title: Как собирать и распространять пакеты для Debian-based дистрибутивов
Slug: how-to-pack-a-package
Category: Администрирование
Date: 2013-10-30 22:20
Source: False

[TOC]

## Введение

Нечасто, но случается, в жизни системного администратора такой момент, когда для работы системы нужно собрать пакет с более новой версией софта или наложить патч на систему.

Или вообще создать пакет со своей программой, чтобы штатными, для операционной системы, методами устанавливать и контролировать процесс обновления программы. Хотя это уже не совсем забота системного администратора.

Итак, у нас есть желание собрать пакет и сделать это правильно.

Я не буду рассказывать как сделать пакет с нуля, я хочу рассказать именно о том, как его собирать. Предполагается, что пакет уже есть со всем необходимым.

## Что нам понадобится

	sudo apt-get install dpkg-dev devscripts

## Как делать не стоит

Как видно из названия: всё что описано ниже, делать не стоит, но если хочется, то можно и так обойтись.

Не знаю как у вас, а у меня моя рабочая машина наполовину состоит из пакетов, которые идут из бэкпортов, ppa и прочих сторонних репозиториев.

Что из этого следует? Из этого следует, что могут быть ошибки связанные с неправильной линковкой библиотек (например частая ситуация, когда не просто неправильно линкуется скомпилированый файл, а несколько меняется логика работы самой системы сборки программы в зависимости от имеющихся версий). Но если вы для себя собираете, то этот способ вполне подойдёт.

Наиболее часто встречающийся у меня способ сборки — взять официальный пакет из более старшей версии и собрать его для своего дистрибутива. Этот процесс называется бэкпортированием.

Давайте рассмотрим например пакетирование supervisor, в wheezy используется 3.0a8, а нам нужна самая свежая версия 3.0. В sid на текущий момент есть только 3.0b2.

Идём на страничку с [пакетом](http://packages.debian.org/sid/supervisor) и выкачиваем исходник пакета (колонка справа, dsc файл):

	$ mkdir packages; cd packages
	$ dget -u http://ftp.de.debian.org/debian/pool/main/s/supervisor/supervisor_3.0b2-1.dsc
	$ ls -1
	supervisor-3.0b2
	supervisor_3.0b2-1.debian.tar.gz
	supervisor_3.0b2-1.dsc
	supervisor_3.0b2.orig.tar.gz


Теперь нам нужно взять архив с последней версией supervisor:

	$ wget https://pypi.python.org/packages/source/s/supervisor/supervisor-3.0.tar.gz

Далее нам необходимо обновить версию пакета:

	$ cd supervisor-3.0b2
	$ uupdate --upstream-version 3.0.0 ../supervisor-3.0.tar.gz
	New Release will be 3.0.0-0ubuntu1.
	Symlinking to pristine source from supervisor_3.0.0.orig.tar.gz...
	-- Untarring the new sourcecode archive ../supervisor-3.0.tar.gz
	Unpacking the debian/ directory from version 3.0b2-1 worked fine.
	Remember: Your current directory is the OLD sourcearchive!
	Do a "cd ../supervisor-3.0.0" to see the new package
	$ cd ../supervisor-3.0.0

А теперь можно приступать к процедуре сборки (вот именно это и неправильно делать по причинам описанным выше):

	$ debuild -i -us -uc

После сборки в директории появится deb файл, который можно корректно установить:

	$ ls -1
	supervisor-3.0.0
	supervisor_3.0.0-0ubuntu1_all.deb
	supervisor_3.0.0-0ubuntu1_amd64.build
	supervisor_3.0.0-0ubuntu1_amd64.changes
	supervisor_3.0.0-0ubuntu1.debian.tar.gz
	supervisor_3.0.0-0ubuntu1.dsc
	supervisor-3.0.0.orig
	supervisor_3.0.0.orig.tar.gz
	supervisor-3.0b2
	supervisor_3.0b2-1.debian.tar.gz
	supervisor_3.0b2-1.dsc
	supervisor_3.0b2.orig.tar.gz
	supervisor-3.0.tar.gz

## Как стоит делать

В силу обозначенных выше причин, необходимо использовать подготовленное окружение, которое будет содержать в себе минимальный набор пакетов которые соответствуют тому окружению, в котором собираются пакеты для дистрибутива.

Понятно, что ничего изобретать для этого не нужно и всё уже есть готовое и миллионы раз протестированое: (c)debootstrap.

Однако debootstrap просто скачивает и распаковывает окружение, а чтобы там что-то собрать нужно сделать туда chroot, кучу всего примонтировать, в общем, тоже много однообразной и скучной работы.

Поэтому разработчики дистрибутива сделали pbuilder (есть ещё sbuild, который собственно и используется на сборочных серверах, о том почему pbuilder, а не sbuild почитать можно [здесь](http://askubuntu.com/questions/53014/why-use-sbuild-over-pbuilder)), который позволяет собирать пакеты в чистых окружениях.

Pbuilder очень хорошо кастомизируется через файлик pbuilderrc, но и тут разработчики подсуетились и сделали pbuilder-dist, который берёт на себя заботу по поддержке многоплатформенности.

К сожалению из коробки он есть только в Ubuntu, в пакете ubuntu-dev-tools. Но для Debian его можно взять из [PPA](https://launchpad.net/ubuntu-dev-tools).

Пользоваться им чрезвычайно просто:

Создаём окружение:

	$ pbuilder-dist wheezy amd64 create

Собираем пакет:

	$ cd packages
	$ pbuilder wheezy amd64 build supervisor_3.0.0-0ubuntu1.dsc

И после окончания процедуры сборки готовый пакет появится в ~/pbuilder/wheezy_results

А что насчёт кастомизации, спросите вы? Ничего не изменилось, pbuilder всё также подхватывает свою конфигурацию из, например, ~/.pbuilderrc

Это решение подкупает меня своей простотой и удобством.

Возникает резонный вопрос, а что дальше с пакетами делать.

## Настраиваем репозиторий

Как я уже неоднократно жаловался в блоге, в интернете миллиарды инструкций на все случаи жизни, но среди них нет ни одной нормальной. Они либо неполные, либо не работают, либо работают, но не так, как нужно (или правильно).

Такая же фигня с созданием репозиториев. Большая часть инструкций предлагает использовать что-то типа apt-ftparchive, а потом руками подписывать репозиторий (если вообще это предлагают делать). Наверняка ведь разработчики подумали как автоматизировать эту задачу и есть готовые хорошие инструменты.

Таким инструментом я могу назвать reprepro.

Его использует много кто, например официальный репозиторий nginx создан с помощью reprepro.

Однако у него есть минус — лишние директории в корне архива, поэтому я стараюсь отделять рабочую директорию от доступного из сети репозитория.

Я также не могу сказать, что reprepro работает идеально, иногда у него бывают совершенно невразумительные ошибки, которые требуют добавления не очень очевидных опций, но на фоне остальных, он работает очень хорошо.

Приступим.

Я не хочу рассказывать как генерировать GPG ключ и как с ним обращаться, за меня это отлично сделал [@cancel](http://blog.regolit.com/2013/03/06/understanding-gnupg).

Создадим директорию где будет работать reprepro:

	$ mkdir repository
	$ cd repository
	$ mkdir conf

В директории conf будет два файла: 

 * options отвечает за опции reprepro
 * distributions отвечает за настройки репозиториев

Содержание файла options:

	verbose
	basedir /home/jdoe/repository
	ask-passphrase

Содержание файла distributions:

	Origin: repository.example.com
	Label: apt repository
	Codename: wheezy
	Architectures: i386 amd64 source 
	Components: main
	Description: APT Repository for libc6.org packages.
	SignWith: jdoe@example.com
	Pull: wheezy


Теперь пришло время для добавления пакета:

	$ reprepro includedeb wheezy ~/packages/supervisor_3.0.0-0ubuntu1_all.deb
	$ reprepro includedsc wheezy ~/packages/supervisor_3.0.0-0ubuntu1.dsc

Как видно, мы не только включили сам пакет, но и исходники. Я вообще советую всегда это делать.

Как я уже говорил выше, у reprepro проблема с тем, что если вы хотите выложить репозиторий в сеть, то при открытии сайта с ним, помимо необходимых директорий dists и pool будет ещё и conf и db, поэтому я советую отделять мух от котлет и выкладывать пакеты отдельно, у меня это, например, делает команда:

	$ rsync -avz --delete pool dists jdoe@example.com:/var/www/repository.example.com/public_html/

## Заключение

Я не могу сказать, что я эксперт в создании пакетов, но определённые практики уже стали для меня привычны. Я в равной степени использую и «простой» и «правильный» способы.

Как обычно, если у Вас возникают вопросы, задавайте, я постараюсь ответить.
