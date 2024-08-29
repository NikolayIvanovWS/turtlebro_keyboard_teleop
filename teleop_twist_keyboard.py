#!/usr/bin/env python

from __future__ import print_function
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy
from geometry_msgs.msg import Twist
import sys
from select import select
import termios
import tty

# Сообщение, объясняющее управление роботом с клавиатуры
msg = """
Чтение данных с клавиатуры и публикация данных в Twist!
---------------------------
 Управление движением:
        w    
   a         d
        s    
 
anything else : stop
q/z - изменение линейной скорости и скорости поворота на 10% одновременно
u/j - изменение только линейной скорости на 10%
e/c - изменение только скорости поворота на 10%
Если скорость домножается на коэффициент 1.1, она увеличивается на 10%, если на 0.9 - уменьшается на 10%
CTRL-C для выхода
"""

# Словарь для управления движением робота в зависимости от нажатой клавиши
moveBindings = {
    'w': (1, 0, 0),   # вперед
    'a': (0, 0, 1),   # влево
    'd': (0, 0, -1),  # вправо
    's': (-1, 0, 0),  # назад
}

# Словарь для управления изменением скорости робота
speedBindings = {
    'q': (1.1, 1.1),  # увеличить линейную и угловую скорость
    'z': (0.9, 0.9),  # уменьшить линейную и угловую скорость
    'u': (1.1, 1),    # увеличить только линейную скорость
    'j': (0.9, 1),    # уменьшить только линейную скорость
    'e': (1, 1.1),    # увеличить только угловую скорость
    'c': (1, 0.9),    # уменьшить только угловую скорость
}

class PublishMove():
    def __init__(self):
        # Создаем объект для публикации сообщений типа Twist в топик 'cmd_vel'
        self.publisher = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.speed = 0.0
        self.turn = 0.0

    def update(self, x, y, th, speed, turn):
        # Обновляем параметры движения
        self.x = x
        self.y = y
        self.th = th
        self.speed = speed
        self.turn = turn

    def stop(self):
        # Останавливаем робота
        self.done = True
        self.update(0, 0, 0, 0, 0)
        self.run()

    def run(self):
        # Публикуем текущие параметры движения в топик
        twist = Twist()
        twist.linear.x = self.x * self.speed
        twist.linear.y = self.y * self.speed
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = self.th * self.turn
        self.publisher.publish(twist)

def getKey(settings, timeout):
    # Получаем нажатую клавишу с клавиатуры
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select([sys.stdin], [], [], timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def saveTerminalSettings():
    # Сохраняем текущие настройки терминала
    return termios.tcgetattr(sys.stdin)

def restoreTerminalSettings(old_settings):
    # Восстанавливаем сохраненные настройки терминала
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def vels(speed, turn):
    # Форматируем строку для вывода текущих значений скорости
    return "Текущие параметры:\tСкорость %s\tПоворот %s " % (speed, turn)

if __name__ == "__main__":
    settings = saveTerminalSettings()  # Сохраняем настройки терминала

    rospy.init_node('teleop_twist_keyboard')  # Инициализируем ROS-ноду

    pub_move = PublishMove()  # Создаем объект для управления движением робота

    # Получаем параметры скорости и угла поворота из параметров ROS-ноды
    speed = rospy.get_param("~speed", 0.5)
    turn = rospy.get_param("~turn", 0.75)
    speed_limit = rospy.get_param("~speed_limit", 2)
    turn_limit = rospy.get_param("~turn_limit", 2)
    key_timeout = rospy.get_param("~key_timeout", 0.5)

    x = 0
    y = 0
    th = 0

    try:
        pub_move.update(x, y, th, speed, turn)  # Инициализируем параметры движения

        print(msg)  # Выводим инструкции на экран
        print(vels(speed, turn))  # Выводим текущие значения скорости и угла поворота

        while True:
            key = getKey(settings, key_timeout)  # Получаем нажатую клавишу
            if key in moveBindings.keys():
                # Обновляем параметры движения в зависимости от нажатой клавиши
                x = moveBindings[key][0]
                y = moveBindings[key][1]
                th = moveBindings[key][2]
            elif key in speedBindings.keys():
                # Обновляем значения скорости в зависимости от нажатой клавиши
                speed = min(speed_limit, speed * speedBindings[key][0])
                turn = min(turn_limit, turn * speedBindings[key][1])
                if speed == speed_limit:
                    print("Достигнут предел линейной скорости!")
                if turn == turn_limit:
                    print("Достигнут предел угловой скорости!")
                print(vels(speed, turn))
            else:
                # Если нажата любая другая клавиша, останавливаем робота
                if key == '' and x == 0 and y == 0 and th == 0:
                    continue
                x = 0
                y = 0
                th = 0
                if key == '\x03':  # Проверка нажатия Ctrl-C
                    break

            pub_move.update(x, y, th, speed, turn)  # Обновляем параметры движения
            pub_move.run()  # Публикуем новые значения

    except Exception as e:
        print(e)

    finally:
        pub_move.stop()  # Останавливаем робота
        restoreTerminalSettings(settings)  # Восстанавливаем настройки терминала
