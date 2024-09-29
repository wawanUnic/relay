# relay. Управление реле на платформе RaspberryPi

## 1. Установка на Raspberry 64bit

Тестировалось на машине: raspberryPi 4, 2Gb RAM, 64Gb SSD

Настройка производится для сервера relay.chu.by с адресом 78.10.222.186

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
sudo apt install python3.12-venv
```
