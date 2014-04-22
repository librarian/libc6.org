Title: Установка Redmine на Debian Squeeze.
Slug: installing-redmine-on-debian-squeeze
Category: Администрирование
Date: 2011-12-10 03:00
Source: False

Я сейчас не очень люблю переводить чужие статьи, поскольку вся прелесть изложения теряется (по крайней мере после моего перевода), но эта статья настолько качественная и интересная, что я решил пересмотреть свой взгляд и разместить перевод у себя на блоге.

Даже я из, казалось бы, такой простой темы как установка приложения подчерпнул много знаний не столько о процессе установки, сколько о том, как можно управлять apt и dpkg в Debian. Также, я оценил глубину исследования вопроса, особенно аппеляции к багтрекеру Debian, к сожалению, в современных Linux блогах это редкость.

Перевод статьи [Installing Redmine with MySQL Thin and Redmine on Debian Squeeze][article] автор Kevin Locke.


[Redmine][redmine] это система для управления проектами, часто называемая лидирующей в своей области, построенная на базе фреймворка [Ruby on Rails][ror]. Она предоставляет функционал багтрекера, контроля времени, вики страниц, диаграмм Гантта и календаря, поддержкой нескольких проектов, разделением уровней доступа по ролям. Эта статья описывает процесс установки Redmine на Debian Squeeze, с использованием MySQL для хранения данных, thin для обслуживания ruby и nginx для фронтэнда.

### Соглашение об используемых обозначениях

В статье показываются различные команды, которые могут быть запущены от обычного (непривилигерованного) пользователя, используя $ для обозначения приглашения, для команд, которые должны быть запущены от суперпользователя root, используют приглашение #. Рекомендуется запускать эти программы используя sudo или аналогичную программу.

## Процесс установки

### Установка MySQL


    # aptitude install mysql-server


### (Опционально) Настройка MySQL для использования UTF-8 по умолчанию

Хотя это и не требуется, удобно установить UTF-8 кодировкой по умолчанию в MySQL, а также используя локаль UTF-8 вне MySQL. Чтобы настроить кодировку по умолчанию, добавьте следующее в /etc/mysql/my.cnf:



    [client]
    default-character-set = utf8
    [mysql]
    default-character-set = utf8
    [mysqld]
    default-character-set = utf8
    default-collation = utf8_unicode_ci
    character-set-server  = utf8
    collation-server  = utf8_unicode_ci



### Создаём базу данных для Redmine в  MySQL

Независимо от того, настроена ли кодировка по умолчанию для использования UTF-8, база данных Redmine должна быть создана с кодировкой UTF-8, независимо от того, какая кодировка указана глобально для всей базы данных, и указывание отличной от UTF-8 кодировки будет вызывать только проблемы связанные с различными кодировками. К сожалению, Redmine не может использовать утилиту dbconfig-common для создания базы данных в кодировке UTF-8 в Squeeze (смотри баги [599140][599140] и [599374][599374]). Чтобы обойти эту ситуацию, создадим базу данных до того, как мы будем устанавливать Redmine, используя следующие команды:


    $ mysql -u root -p
    mysql> CREATE USER 'redmine'@'localhost' IDENTIFIED BY 'newpassword';
    mysql> CREATE DATABASE redmine_default CHARACTER SET = 'utf8';
    mysql> GRANT ALL PRIVILEGES ON redmine_default.* TO 'redmine'@'localhost';


Замечу, что возможно использовать другое имя и/или другой парольк базе данных. Для того, чтобы использовать другое им, модифицируйте команду и удостоверьтесь, что приоритет debconf установлен в значение low (можно осуществить это выставив значение переменной окружения DEBIAN_PRIORITY=low) когда будет уставливаться redmine.

### Установка Redmine, thin, и nginx


    # aptitude install redmine redmine-mysql+M thin nginx ssl-cert

В команде выше, флаг "+M" добавлен к пакету redmine-mysql для того, чтобы пометить пакет как автоматически установленный, так что, если пакет redmine будет удалён, пакет redmine-mysql будет автоматически удалён. Также отметьте, что пакет ssl-cert является опциональным. Он предоставляет SSL сертификат (именуемый ssl-cert-snakeoil.pem), который может быть использован для работы по HTTPS.

В меню, появившемся при установке, выберите yes для использования dbconfig-common, выберите mysql, в качестве базы данных и предоставьте пароли MySQL пользователей root и redmine, когда потребуется. dbconfig-common заметит, что база данных уже создана и заполнит её без изменения кодировки, что в итоге даст нам таблицы имеюзие кодировку UTF-8.

### Настройка thin

Для настройки thin, сперва создайте директорию, в которой будут хранится лог файлы создаваемые thin:


    # mkdir /var/log/thin
    # chmod 755 /var/log/thin


Если доступ к логам thin должен быть в будущем запрещён, для этой директории можно будет изменить владельца на root:adm и выставлены права 2750, для ограничения доступа только от пользователей группы adm.

Далее, создайте конфигурационный файл thin используя следующие команды:


    $ thin config --config /tmp/redmine.yml --chdir /usr/share/redmine \
        --environment production --socket /var/run/redmine/sockets/thin.sock \
        --daemonize --log /var/log/thin/redmine.log --pid /var/run/thin/redmine.pid \
        --user www-data --group www-data --servers 1 --prefix /redmine
    # mv /tmp/redmine.yml /etc/thin/redmine.yml
    # chown root:root /etc/thin/redmine.yml
    # chmod 644 /etc/thin/redmine.yml

Заметьте, что флаг --servers может быть изменён исходя из потребностей производительности. Также, флаг --prefix может быть изменён или опущен для изменения префикса URL по которому будет доступен Redmine. Использование префикса /redmine предоставит доступ по адресу [http://host/redmine][hostredmine], отсутствие префикса будет предоставлять доступ к корню сайта [http://host/][host]

В конце, добавим логи thin в конфигурацию logrotate для архивирования и сжатия старых логов, создав файл  /etc/logrotate.d/thin со следующим содержимым:


    /var/log/thin/*.log {
            daily
            missingok
            rotate 52
            compress
            delaycompress
            notifempty
            create 640 root adm
            sharedscripts
            postrotate
                    /etc/init.d/thin restart >/dev/null
            endscript
    }

Если доступ к логам thin запрещён (как описано выше), измените строку create на create 640 root adm. Также заметьте, что указанная выше конфигурация будет вызывать перезапуск thin один раз в день для записи в следующий лог файл. Это не оптимально и будет вызывать некоторый период недоступности. Предложения по предотвращению перезапуска приветствуются.

### Настройка nginx

Перво-наперво, создайте концигурационный файл с именем /etc/nginx/proxy_opts и следующим содержимым:

    # Общие опции используемые всеми proxy
    proxy_set_header        Host $http_host;

    # Следующие заголовки не используются redmine, но будут полезны для плагинов
    # и других веб приложений
    proxy_set_header        X-Real-IP $remote_addr;
    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Proto $scheme;

    # И другие опции для proxy


Далее создайте конфигурационный файл с именем  /etc/nginx/sites-available/redmine и следующим содержимым или интегрируйте содержимое в имеющийся сайт:

    upstream redmine_thin_servers {
      server unix:/var/run/redmine/sockets/thin.0.sock;
      # Добавьте дополнительные копии, если используете несколько копий thin
      #server unix:/var/run/redmine/sockets/thin.1.sock;
    }

    server {

      listen   80; ## listen for ipv4
      listen   [::]:80 default ipv6only=on; ## listen for ipv6

      # Выставлено специально для виртуальных хостов, для использования server_name_in_redirect
      server_name  localhost;
      server_name_in_redirect off;

      access_log  /var/log/nginx/localhost.access.log;
      error_log  /var/log/nginx/localhost.error.log;

      # Заметка: В документации сказано, что proxy_set_header должна работать
      #          в блоке location, но тестирование показало, что это не
      #          поддерживается так-что мы поместили её внутрь блока server
      include /etc/nginx/proxy_opts;
      proxy_redirect off;

      # Заметка: Должен совпадать с префиксом заданным при конфигурации thin
      #          или / если никакого префикса не задано
      location /redmine {
        root   /usr/share/redmine/public;

        error_page 404  404.html;
        error_page 500 502 503 504  500.html;

        # Отправляем важную информацию по HTTPS
        # Удалите, если ssl не используется
        # Заметка 1:  Измените $host на SSL CN если используется несколько хостов
        # Заметка 2:  Учитывайте префикс заданный в конфиге
        rewrite ^/redmine/login(.*) https://$host$request_uri permanent;
        rewrite ^/redmine/my/account(.*) https://$host$request_uri permanent;
        rewrite ^/redmine/my/password(.*) https://$host$request_uri permanent;
        rewrite ^/redmine/admin(.*) https://$host$request_uri permanent;

        try_files $uri/index.html $uri.html $uri @redmine_thin_servers;
      }

      location @redmine_thin_servers {
        proxy_pass http://redmine_thin_servers;
      }
    }

    # HTTPS сервер (должно совпадать с HTTP сервером выше с небольшим количеством изменений
    # Опционально: удалите директивы для перенаправления, если не планируете использовать этот блок
    server {

      listen   443; ## listen for ipv4
      listen   [::]:443 default ipv6only=on; ## listen for ipv6

      server_name  localhost;
      server_name_in_redirect off;

      access_log  /var/log/nginx/localhost-ssl.access.log;
      error_log  /var/log/nginx/localhost-ssl.error.log;

      include /etc/nginx/proxy_opts;
      proxy_redirect off;

      # Заметка:  Замените ssl_certificate{,_key} на свой SSL сертификат, если
      #           не используете пакет ssl-cert
      ssl  on;
      ssl_certificate  /etc/ssl/certs/ssl-cert-snakeoil.pem;
      ssl_certificate_key  /etc/ssl/private/ssl-cert-snakeoil.key;

      location /redmine {
        root   /usr/share/redmine/public;

        error_page 404  404.html;
        error_page 500 502 503 504  500.html;

        try_files $uri/index.html $uri.html $uri @redmine_thin_servers;
      }

      location @redmine_thin_servers {
        proxy_pass http://redmine_thin_servers;
      }
    }

Если файл /etc/nginx/proxy_opts вам не нравится, просто замените include /etc/nginx/proxy_opts; необходимыми опциями (как минимум желательно прописать proxy_set_header Host).

Итак, если информация выше не была совмещена с уже созданным конфигурационным файлом сайта, удалите сайт по умолчанию и включите сайт с Redmine используя следующие команды:


    # rm /etc/nginx/sites-enabled/default
    # ln -s ../sites-available/redmine /etc/nginx/sites-enabled/redmine


### Дополнительные багфиксы

Сейчас присутствует баг в Redmine (возможно в библиотеке Ruby libactionpack-ruby) в Squeeze, из-за которого невозможно загрузить страницу с профилем пользователя. Для причин смотрите баги [628899][628899], [629067][629067] и [633305][633305], и внесите соответствующие исправления. Как минимум рекомендуется осуществить исправление из [комментария к 629067][62906737], изменив строку 476 в файле /usr/lib/ruby/1.8/action_view/helpers/url_helper.rb указанным образом.

### Перезапуск и тестирование

В конце концов перезапустите nginx и thin, для того, чтобы применить изменения:


    # /etc/init.d/thin restart
    # /etc/init.d/nginx restart

Далее проследуйте по ссылке [http://localhost/redmine][localhostredmine] (используя hostname и префикс настроенные выше). Должна появится стартовая странится Redmine. Нажмите "Sign in" и введите имя пользователя admin, с паролем admin. Затем произведите настройку используя [Redmine Guide][guide] в качестве справочника. Наиболее важно изменить "Host name and path", на URL, который будет использоваться пользователями Redmine, поскольку он распознаётся как адрес прокси, а не как доступное внешне имя сервера.

### Решение проблем

Если страница Redmine не грузится, есть несколько советов по решению проблем:

* Проверьте лог ошибок nginx /var/log/nginx/error.log на предмет соответствующих ошибок.
* Проверьте лог ошибок thin /var/log/thin/redmine.0.log.
* Включите режим отладки в конфигурации thin, перезапустите его и проверьте лог ошибок thin.
* Измените конфигурационный файл thin для использования IP адреса и порта, для того, чтобы подключаться напрямую к thin, из браузера, чтобы определить, ошибка в thin или с nginx.

Желаю удачи в диагностировании и решении проблем, не стесняйтесь публиковать их в комментариях или багтрекерах; искать помощи или информировать других о проблеме или решении.

### Наслаждайтесь

Сейчас Redmine должен быть готов к использованию. Раскажите о нём  пользователям,  вливайтесь в сообщество Redmine и наслаждайтесь!

[article]: http://www.debian-administration.org/article/673/Installing_Redmine_with_MySQL_Thin_and_Redmine_on_Debian_Squeeze
[redmine]: http://www.redmine.org/
[ror]: http://rubyonrails.org/
[hostredmine]: http://host/redmine
[host]: http://host/
[628899]: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=628899
[629067]: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=629067
[633305]: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=633305
[62906737]: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=629067#37
[localhostredmine]: http://localhost/redmine
[guide]: http://www.redmine.org/projects/redmine/wiki/Guide
[hostname]: http://www.redmine.org/projects/redmine/wiki/RedmineSettings#Host-name-and-path
