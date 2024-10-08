# turtlebro_keyboard_teleop
Универсальное управление роботами TurtleBro и Brover E с клавиатуры для ROS

# Установка

Установку программы необходимо производить не на робота, а на компьютер:

```
cd ~/catkin_ws/src
git clone https://github.com/voltbro/turtlebro_keyboard_teleop
cd ../
catkin_make
```

# Запуск телеуправления

Перед тем, как запускать программу для телеуправления роботом, необходимо произвести сетевые настройки

__Сетевые настройки__

Видео-урок по сетевым настройкам: https://vk.com/video-206862623_456239323

Для переноса ядра ROS c робота на компьютер необходимо установить в терминале вашего ПК корректные сетевые переменные ROS_MASTER_URI и ROS_HOSTNAME: 
```
export ROS_MASTER_URI=http://<IP-address_robot>:11311/
export ROS_HOSTNAME=IP-address_PC
```

После выполнения сетевых настроек необходимо в этом же терминале запустить программу для телеуправления:

```
rosrun turtlebro_keyboard_teleop teleop_twist_keyboard.py
```

Также можно запускать программу со своими параметрами:
```
rosrun turtlebro_keyboard_teleop teleop_twist_keyboard.py _speed:=0.9 _turn:=0.8
```

# Использование программы
```
Чтение данных с клавиатуры и публикация данных в Twist!
---------------------------
Управление движением:
        w    
   a         d
        s    


q/z : увеличить/уменьшить линейную и угловую скорости на 10%
u/j : увеличить/уменьшить только линейную скорость на 10%
e/c : увеличить/уменьшить только угловую скорость на 10%

CTRL-C для выхода
```

