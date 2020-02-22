#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#date:2020/02/20
#name：send_mail.py
#作者：聪明的瓦肯人
#微信公众号：工业光线
#网站：http://www.tech-xjc.com

#导入树莓派GPIO模块
import RPi.GPIO as GPIO
#导入发邮件相关模块
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
import smtplib
import time

#设置GPIO口引脚编号为BOARD模式
GPIO.setmode(GPIO.BOARD)
#设置7号引脚为输入模式，默认拉低电平
GPIO.setup(7,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#设置16号引脚为输出模式，默认低电平
GPIO.setup(16,GPIO.OUT,initial=GPIO.LOW)

msg = MIMEText("警告：\n非法人员闯入!请立即采取相关措施！", 'plain', 'utf-8')
# 输入Email地址和口令:
from_addr ='1547613381@qq.com'
password_smtp ='qnfsngbfwpctbacj'
# 输入收件人地址:
to_addr4 = '3444526584@qq.com'
# 输入SMTP服务器地址:
smtp_server = 'smtp.qq.com'

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

#构造头部From信息
msg['From'] = _format_addr('树莓派邮件警报器 <%s>' % from_addr)
#构造头部Subject信息
msg['Subject'] = Header('Alert from raspberry pi', 'utf-8').encode()

#连接SMTP服务器
server_smtp = smtplib.SMTP(smtp_server, 25) # SMTP协议默认端口是25
#是否显示调试信息，1显示，0不显示
server_smtp.set_debuglevel(0)
#登录
server_smtp.login(from_addr, password_smtp)

def check_send_alert():
#轮询7号引脚状态，高电平触发邮件发送
    while True:
        state = GPIO.input(7)
        GPIO.output(16,state)
        if state == 1:
            server_smtp.sendmail(from_addr,to_addr4, msg.as_string())
            print('\n*****已发送警报邮件！*****')
            #1分钟后再检测状态，是否再次发送邮件
            time.sleep(60)
