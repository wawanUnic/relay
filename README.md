# relay. Управление реле на платформе RaspberryPi

![Image alt](https://github.com/wawanUnic/relay/blob/main/screenshots/pageMobile.png)


## 1. Установка на Raspberry 64bit

Тестировалось на машине: raspberryPi 4, 2Gb RAM, 64Gb SSD

Настройка производится для сервера relay.chu.by с адресом 78.10.222.186

Работаем от пользователя Pi (пользователь с привелегированными правами)

Креды для аутентификации на сайте relay:wW0000

Задействованные порты:

```
22* - SSH - управление сервером, обмен файлами. Вход только по ключу. Закрыт от внешнего подключения
80 - HHTP - веб-интерфейс (витрина). Постоянное перенаправление на HTTPs
443 - HTTPs - веб-интерфейс (витрина). Расшифровываеет и перенаправляет соединение на порт 8888
8000 - HTTP - внутренний веб-интерфейс (витрина). Закрыт от внешнего подключения
```
## 2. Создадим ключи для SSH

Скопируем содержимое закрытого ключа из консоли и сохраним его в пустом формате на ПК с помощью текстового редактора

Имя файла не критично. Важно: приватный ключ должен содержать:
```
-----НАЧНИТЕ ОТКРЫВАТЬ ЗАКРЫТЫЙ КЛЮЧ OPENSSH-----
...
-----END OPENSSH ПРИВАТНЫЙ КЛЮЧ-----
```
Публичный ключ скопируем в папку .ssh

На ПК загрузим PuTTYgen. В меню: нажмите Conversions->Import key и найдем сохраненный файл закрытого ключа
Он загрузится в программу. Нажмем «Сохранить закрытый ключ» в формате PuTTY .ppk в D:\Program Files\PuTTY\KEYs
Загрузим файл .ppk в свой профиль SSH уже в программе PuTTY: Connection->SSH->Auth->Credentials
Connection - keepAlive 15 sec
Сохраним свой профиль в PuTTY
```
ssh-keygen
cd .ssh
ls -l
nano id_rsa
mv id_rsa.pub authorized_keys
chmod 644 authorized_keys
```

## 3. Запретим на вход по паролю

sudo nano /etc/ssh/sshd_config:
```
PubkeyAuthentication yes
PasswordAuthentication no
```
sudo service ssh restart

## 4. Обновим систему

Обновим систему и установим дополнительные пакеты
```
sudo apt update
sudo apt upgrade
sudo apt install mc
sudo reboot
sudo apt-get install python3-pip
sudo apt install python3-venv
```

## 5. Копируем исходные файлы

Создаем папку relay. Копируем в неё исходные файлы. Права на исполнение давать не нужно

## 6. Создаем виртуальное окружение

Создаем вирт.окружение
```
cd /home/relay
python3 -m venv env
source env/bin/activate
pip install Flask
pip install Flask-Bootstrap
pip install RPi.GPIO
pip list
python myServer.py -- Эту команду не запускать! Это только для ручного тестирования
```

Версии добавленных пакетов и их зависимостей
```
blinker         1.8.2
click           8.1.7
dominate        2.9.1
Flask           3.0.3
Flask-Bootstrap 3.3.7.1
itsdangerous    2.2.0
Jinja2          3.1.4
MarkupSafe      2.1.5
pip             23.0.1
RPi.GPIO        0.7.1
setuptools      66.1.1
visitor         0.1.3
Werkzeug        3.0.4
```

## 7. Добавляем сервис в systemD

sudo nano /etc/systemd/system/myServer.service:
```
[Unit]
Description=myServer
After=network-online.target nss-user-lookup.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/relay
Environment="PYTHONPATH=/home/pi/relay/env/lib/python3.11/site-packages" - Версия Python может быть другой. Уже существует как минимум 3.12. Необходимо проверить какая версия в папке
ExecStartPre=/usr/bin/sleep 10
ExecStart=/home/pi/relay/env/bin/python3.11 /home/pi/relay/myServer.py - Версия Python может быть другой. Уже существует как минимум 3.12. Необходимо проверить какая версия в папке

RestartSec=10
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Настраивам systemD:
```
sudo systemctl daemon-reload
sudo systemctl enable --now myServer.service
systemctl status myServer.service
```

## 8. Устанавливаем кэширующий прокси-сервер

Устанавливаем nginx:
```
sudo apt install nginx
sudo ufw status (?)
sudo systemctl enable nginx
sudo systemctl start nginx
systemctl status nginx
```

Правим настройки sudo nano /etc/nginx/sites-available/myServer:
```
server {
    listen 80;
    listen [::]:80;
    server_name relay.chu.by;
    access_log /var/log/nginx/relay.chu.by-access.log;
    error_log /var/log/nginx/relay.chu.by-error.log;

location / {
    proxy_pass http://localhost:8888;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Создаем линк, проверяем ошибки, перезапускаем:
```
sudo ln -s /etc/nginx/sites-available/myServer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 9. Защищаем шифрованием

Об особенностях установки можно почитать [тут](https://serveradmin.ru/ustanovka-i-nastroyka-nginx-php-fpm-php7-1-na-centos-7/#_ssl_Lets_Encrypt) и [тут](https://serveradmin.ru/nginx-proxy_pass/)

Иногда бывает ошибка с /etc/ssl/certs/dhparam.pem. Тогда нужно сформировать новый ключ командой: sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096

Ключ генерируется около 10-20 минут!

```
sudo apt install certbot
sudo certbot certonly
sudo nginx -t
Если ошибка с /etc/ssl/certs/dhparam.pem, тогда еще нужна команда: sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096
sudo nginx -t
sudo systemctl restart nginx
```

Добавляем переадресацию на шифрованное соединение sudo nano /etc/nginx/sites-available/myServer:
```
server {
    listen 80;
    listen [::]:80;
    server_name relay.chu.by;
    return 301 https://relay.chu.by$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443;
    server_name relay.chu.by;
    access_log /var/log/nginx/relay.chu.by-access.log;
    error_log /var/log/nginx/relay.chu.by-error.log;

    keepalive_timeout 60;
    ssl_certificate /etc/letsencrypt/live/relay.chu.by/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/relay.chu.by/privkey.pem;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECD>
    ssl_dhparam /etc/ssl/certs/dhparam.pem;
    add_header Strict-Transport-Security 'max-age=604800';

location / {
    proxy_pass http://localhost:8888;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Можно посмотреть статус бота и принудительно обновить:
```
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

## 10. Добавляем базовую аутентификацию

Опция -c создает новый файл со связками
```
sudo apt-get install apache2-utils
sudo htpasswd -c /etc/nginx/htpasswd user_name
```

Проверим файл:
```
nano /etc/nginx/htpasswd
```

Конфигурируем sudo nano /etc/nginx/sites-available/myServer
```
server {
    listen 80;
    listen [::]:80;
    server_name relay.chu.by;
    return 301 https://relay.chu.by$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443;
    server_name relay.chu.by;
    access_log /var/log/nginx/relay.chu.by-access.log;
    error_log /var/log/nginx/relay.chu.by-error.log;

    keepalive_timeout 60;
    ssl_certificate /etc/letsencrypt/live/relay.chu.by/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/relay.chu.by/privkey.pem;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECD>
    ssl_dhparam /etc/ssl/certs/dhparam.pem;
    add_header Strict-Transport-Security 'max-age=604800';

location / {
    proxy_pass http://localhost:8888;
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/htpasswd;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Перезапускаем nginx:
```
sudo nginx -t
sudo systemctl restart nginx
```
