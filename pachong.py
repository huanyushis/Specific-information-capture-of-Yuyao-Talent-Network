import json
import time
import requests
import pymysql
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def change(data):
    if data:
        return ",".join(data)
    else:
        return "无"


def send_message(info):
    if len(info) == 0:
        print("无需发送")
        return
    msg_from = '1174601344@qq.com'  # 发送方邮箱
    passwd = 'jlpnihnhhvkfgefd'  # 填入发送方邮箱的授权码(填入自己的授权码，相当于邮箱密码)
    msg_to = ['2748392993@qq.com']  # 收件人邮箱
    subject = "余姚人才网"
    content = "<table><tr><th>职位名称</th><th>公司名称</th><th>日期</th><th>新条目</th></tr>"
    for i in info:
        content += f'''<tr><td style="color: red">{i[0]}</td>
                        <td style="color: red">{i[1]}</td>
                        <td style="color: red">{i[2][:4] + i[2][5:7] + i[2][8:10]}</td>
                        <td style="color: red">new</td></tr>'''
    content += "</table>"
    msg = MIMEText(content, 'html', 'utf-8')
    # 放入邮件主题
    msg['Subject'] = subject
    # 也可以这样传参
    # msg['Subject'] = Header(subject, 'utf-8')
    # 放入发件人
    msg['From'] = msg_from
    # 放入收件人
    msg['To'] = msg_to[0]

    try:
        # 通过ssl方式发送，服务器地址，端口
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        # 登录到邮箱
        s.login(msg_from, passwd)
        # 发送邮件：发送方，收件方，要发送的消息
        s.sendmail(msg_from, msg_to, msg.as_string())
        print('成功')
    except s.SMTPException as e:
        print(e)
    finally:
        s.quit()


db = pymysql.connect("localhost", "root", "mysql", "waimao_information", charset='utf8')
cursor = db.cursor()

sql = """SELECT MAX(updateTime) FROM info;"""

cursor.execute(sql)
data = cursor.fetchone()
max_time = data[0]
input = "外贸"
n = 1
max = 0
info = []
flag = 0
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
while True:
    response = requests.get(
        "http://gqh.nbrc.com.cn/front-gateway/company/noLogin/getJobList?keyName=" + str(input) + "&pageNumber=" + str(
            n) + "&orderBy=&cj_publish_time=&salaryEq=&benefitsLike=",
        headers=headers)
    datas = json.loads(response.text)
    for a in datas['data']['list']:
        if a['updateTime'] <= str(max_time):
            flag = 1
            break
        info.append([a['name'], a['companyName'], a['updateTime'], a['salaryDesc'], change(a['benefitsList']),
                     a['educationDesc'], a['workExperienceDesc'], a['rcCompanyInfo']['industryTypeDesc'],
                     a['rcCompanyInfo']['natureDesc']])
    if not max:
        max = datas['data']['page']['totalPage']
    if n > max or flag:
        break
    n += 1
send_message(info)

for i in info:
    sql = f'''INSERT INTO info VALUES ("{i[0]}","{i[1]}","{i[2]}","{i[3]}","{i[4]}","{i[5]}","{i[6]}","{i[7]}","{i[8]}");'''
    cursor.execute(sql)
db.commit()
db.close()
