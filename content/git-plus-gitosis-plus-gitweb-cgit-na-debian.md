Title: git+gitosis+gitweb(cgit) на Debian.
Slug: git-plus-gitosis-plus-gitweb-cgit-na-debian
Category: Администрирование
Date: 2010-11-06 19:26
Source: False

Небольшая инструкция описывающая установку описанного в теме комплекта на
Debian

Не буду рассказывать почему выбрал именно git для системы контроля версий --
сам не знаю, скорее всего просто потому что пользоваться ей достаточно просто.
По поводу остального -- gitosis это единственное, что позволяет делать
многопользовательский доступ, не требует висящего демона и просто
настраивается. Выбор веб интерфейса остаётся за Вами, лично мне больше
понравился cgit, он достаточно быстр и, в принципе, более функционален.
Установка будет описывать работу именно с ним. Конфигурационный файл для
gitweb я также добавлю в конце поста. Предполагается, что вебсервер уже
установлен, папка, в которой будут располагаться папки виртхостов: /var/www,
gitosis устанавливается в /srv/gitosis. Также предполагается, что имеются
некоторые основы работы с ключами и вы понимаете различием между публичным и
приватным ключом(применительно к SSH)

Итак приступим Для начала добавим репозиторий, где лежит пакетик с cgit:

    
    echo "deb http://debian.stbuehler.de/debian/ stbuehler main" >> /etc/apt/sources.list
    apt-key add --keyserver keys.gnupg.net --recv-keys 80121CD2479689D8
    apt-get update

Установим необходимое ПО и будем разруливать настройки потихоньку: aptitude
install git-core gitosis cgit Настроим gitosis:

    
    su gitosis
    cd $HOME

Создадим ключик для того чтобы gitosis сам для себя мог делать изменения:

    
    ssh-keygen -t rsa
    gitosis-init < .ssh/id_rsa.pub

Потом клонируем папку, в которой будет происходить настройка gitosis:

    
    
    git clone gitosis@localhost:gitosis-admin.git
    

В папке /srv/gitosis будет создана папка gitosis-admin, с настройками
программы. Заходим в неё, редактируем файл gitosis.conf и добавляем
пользователей:

    
    
    [gitosis]
    [group gitosis-admin]
    writable = gitosis-admin
    members = gitosis@server.name
    [group repo1]
    members = user1 user2
    writable = repo_name
    [repo repo2]
    gitweb = yes
    cgit = yes
    owner = Owner name
    description = server.name git repo
    

Добавление пользователей происходит очень просто, нужно просто добавить
публичный ключ в папку gitosis-admin/keydir, например:

    
    echo "ssh-rsa ..... localuser@hostname" > keydir/user1.pub

Это добавляет ключ для доступа пользователя user1 Применяем изменения:

    
    git commit -a -m "Info about added data"
    git push

Затем создаём репозиторий:

    
    mkdir -p ../repositories/repo_name.git

Переходим в него

    
    cd ../repositories/repo_name.git

Выполняем инициализацию репозитория:

    
    git init --bare

У себя также делаем инициализацию, забираем репозиторий к себе и коммитим то,
что нам нужно:

    
    cd projects/repo_name
    git init
    git remote add origin gitosis@server.name:repo_name.git
    git pull origin master
    git commit -a -m "initial commit"
    git push origin master

Настраиваем Apache

    
    apitude install apache2

Добавляем в конфиг виртхоста:

    
    <VirtualHost _:80>
        ServerAdmin webmaster@localhost
        ServerName git.server.name
        DocumentRoot /var/www/git.server.name/public/
        DirectoryIndex index
        Options Indexes FollowSymlinks ExecCGI
        Alias /cgit.css /usr/share/cgit/cgit.css
        Alias /cgit.png /usr/share/cgit/cgit.png
        ScriptAlias /index /usr/lib/cgi-bin/cgit.cgi
        <Directory "/var/www/git.server.name/public">
            RewriteEngine on
            RewriteCond %{REQUEST_FILENAME} !-f
            RewriteCond %{REQUEST_FILENAME} !-d
            RewriteRule ^._ /index/$0 [L,PT]
        </Directory>
    
        ErrorLog /var/log/apache2/git.server.name.error.log
        LogLevel warn
        CustomLog /var/log/apache2/git.server.name.access.log combined
    
    </VirtualHost>

Теперь создаём конфиг для cgit /etc/cgitrc

    
    virtual-root=/
    enable-index-links=1
    enable-log-filecount=1
    enable-log-linecount=1
    snapshots=tar.gz tar.bz2 zip
    css=/cgit.css
    logo=/cgit.png
    root-title=git.server.name
    
    
    
    
    
    # scan-path=/srv/gitosis/repositories
    
    
    
    
    
    
    repo.url=repo_name.git
    repo.path=/srv/gitosis/repositories/repo_name.git/
    repo.desc=maxsites.ru repository
    repo.owner=Maxsites Team
    repo.clone-url=ssh://gitosis@server.name:repo_name.git

Если раскомментировать scan_path, то cgit будет брать все репозитории из
папки, иначе нужно задавать их вручную, как я описал выше. Использование
projects.list(то есть генерируемого списка на основе опции cgit=yes) возможно
только на Gentoo, где включён в gitosis специальный патч, реализующий данную
функциональность(надо будет на досуге покопаться).

Для gitweb таких ограничений нет, там всё работает корректно из коробки. Вот
содержимое файла /etc/gitweb.conf

    
    
    $projects_list = "/srv/gitosis/gitosis/projects.list";
    $projectroot = '/srv/gitosis/repositories';
    $gitosis_conf = '/srv/gitosis/repositories/gitosis-admin.git/gitosis.conf';
    $export_ok = "";
    $strict_export = "true";
    

Теперь перезапускаем Apache, идём на git.server.name и радуемся :)
