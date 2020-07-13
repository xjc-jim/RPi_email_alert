#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#date:2020/02/20
#name:email_alert_system.py
#作者：聪明的瓦肯人
#微信公众号：工科生日常
#网站：http://www.tech-xjc.com

#导入自己的邮件报警模块send_mail
import send_mail

#导入树霉派GPIO模块
import RPi.GPIO as GPIO
import time
import threading

#导入POP3收邮件相关模块
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib

#设置GPIO引脚编号模式为BOARD
GPIO.setmode(GPIO.BOARD)
#设置11号引脚为输出，初始化为低电平
GPIO.setup(11,GPIO.OUT,initial=GPIO.LOW)

#task变量用于存储消息，并在thread1线程中作出判断
task = ''
#收邮件地址，口令与POP3服务器
email = '154****381@qq.com'
password_pop3 = 'qnf******pctbacj'
pop3_server = 'pop.qq.com'
#guess_charset用于解析邮件的编码格式，要根据不同的编码进行解码
def guess_charset(msg):
    charset = msg.get_charset()
    print(charset)
    if charset is None:
        content_type = msg.get('Content-Type','').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
            print(charset)
    return charset

#decode_str用于解码邮件头部信息字符
def decode_str(s):
    value,charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

#根据邮件类型解析内容并打印
def print_info(msg,indent=0):
    if indent == 0:
        for header in ['From','To','Subject']:
            value = msg.get(header,'')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
                else:
                    hdr,addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name,addr)
            print('%s%s:%s' % (' ' * indent,header,value))
    #判断邮件是否为multipart类型，粗略的理解为复合消息（比如text与html）        
    if (msg.is_multipart()):
        parts = msg.get_payload()
        #将不同内容编码分块，并重新执行print_info递归一直到part不再是multipart类型
        for n,part in enumerate(parts):
            print('%spart %s' % (' ' * indent,n))
            print('%s-------------------' % (' ' * indent))
            print_info(part,indent + 1)
    #part不再是multipart则执行else
    else:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            #获取内容
            content = msg.get_payload(decode=True)
            #解析编码类型
            charset = guess_charset(msg)
            if charset:
                #根据编码类信进行解码
                content = content.decode(charset)
                if content_type=='text/plain':
                    global task
                    task = content
            print('%sText:%s' % (' ' * indent,content))

#灯光闪烁驱离函数
def light_blinker():
    while True:
        if task == '闪烁驱离':
            #1是高电平，0是低电平
            GPIO.output(11,1)
            time.sleep(0.5)
            GPIO.output(11,0)
            time.sleep(0.5)
            print('\n正在闪烁驱离！')
        if task == '停止闪烁':
            GPIO.output(11,0)
            print('\n已停止闪烁！')
            time.sleep(1)
        #if task == '停机':
         #   break
            
#连接到POP3服务器，注意QQ需要SSL加密
server_pop3 = poplib.POP3_SSL(pop3_server,port=995)
#是否显示调试信息，0是关，1是开
server_pop3.set_debuglevel(0)
#打印POP3欢迎消息
print(server_pop3.getwelcome().decode('utf-8'))
#身份认证
server_pop3.user(email)
server_pop3.pass_(password_pop3)
#返回邮件编号
resp,mails,octets = server_pop3.list()
index_former = len(mails)

def get_mail():
    while True:
        #打印邮件数量与大小
        #print('Messages:%s.Size:%s'% server.stat())
        resp,mails,octets = server_pop3.list()
        index_now = len(mails)
        #根据邮件数量差值判断是否有新邮件
        new_msg = index_now - index_former
        global index_former
        index_former = index_now
        #获取最新邮件，lines中存储了最新邮件原始文本的所有行
        resp,lines,octets = server_pop3.retr(index_now)
    
        if new_msg > 0:
            print('********************************************************')
            print('\n有一封新邮件！')
            print(mails)
            #msg_content存储了邮件的原始信息,以回车相连（str）
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            print('--------------------------------------------------------')
            #通过parsestr将msg_content转换为email类
            msg = Parser().parsestr(msg_content)
            print(msg)
            print('--------------------------------------------------------')
            print_info(msg)
            print(task)
            print('********************************************************')
            if task == '停机':
                break

#新建线程thread1，thread2
thread1 = threading.Thread(target=light_blinker,name='blinker')
#设置thread1为守护线程
thread1.setDaemon(True)
thread2 = threading.Thread(target=send_mail.check_send_alert,name='alert')
thread2.setDaemon(True)
thread3 = threading.Thread(target=get_mail,name='getMail')
thread1.start()
thread2.start()
thread3.start()
#thread1.join()
#thread2.join()
thread3.join()
#退出循环，解除服务
server_pop3.quit()
send_mail.server_smtp.quit()
#释放GPIO口资源
GPIO.cleanup()
print('＊＊＊＊＊＊＊＊＊＊已停机！＊＊＊＊＊＊＊＊＊＊')
