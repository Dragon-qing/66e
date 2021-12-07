import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from lxml import etree


def spider():
    session = requests.session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    url = "http://www.66ys.co/"
    response = session.get(url)
    html = etree.HTML(response.content)
    # 获取所有的当日推荐电影
    movie_list = html.xpath('//div[@class="tjlist"]/ul/li')
    # 获取每个电影对应的链接地址
    link_list = html.xpath('//div[@class="tjlist"]/ul/li/a/@href')
    magnet = ''
    index = 0
    # 遍历每个电影的html页面
    for link in link_list:
        res = session.get(link)
        # 创建element对象
        temp_html = etree.HTML(res.content.decode("gbk"))
        # 电影名称
        movie_name = temp_html.xpath('//h1/text()')
        # 磁力链接
        temp_mag = temp_html.xpath('//td[contains(text(),"磁力")]/a/@href')
        # 磁力资源描述
        temp_name = temp_html.xpath('//td[contains(text(),"磁力")]/a/text()')

        movie_img = temp_html.xpath('//div[@id="text"]/p[1]/img/@src')
        if len(movie_img):
            try:
                res = session.get(movie_img[0])
                if res.ok:
                    with open(f"./image_{index}.jpg", "wb") as f:
                        f.write(res.content)
            except:
                print(movie_name[0] + "图片获取失败")

        magnet += "{}\n".format(movie_name[0])
        for x, y in zip(temp_name, temp_mag):
            magnet += "\n{}:\n{}\n".format(x, y)
        magnet += '\n'
        index += 1
    # 将磁力链接存入文本中
    with open("./magnet.txt", "wb") as f:
        f.write(bytes(magnet, encoding="utf-8"))

    movie_name_list = []
    html = """
    <html> 
     <head></head> 
     <body> """
    index = 0
    for i in movie_list:
        # 获取每个电影名
        movie_name = (i.xpath('./p/a/text()'))
        # 获取每个电影的链接
        movie_link = (i.xpath('./p/a/@href'))
        movie_name_list.append(movie_name[0])

        html += """
            <div>
                <p>{0}</p>
                <img src="cid:image_{2:x}" alt="{0}">
                <br>
                <a href={1} target="_blank">{1}</a>
            </div>
            <hr>
        """.format(movie_name[0], movie_link[0], index)
        index += 1
    html += """
    </body> 
    </html> 
    """
    with open("./temp.html", "wb") as f:
        f.write(bytes(html, "utf-8"))
    return movie_name_list


def sendMail():
    # 初始化
    email_host = 'smtp.163.com'
    email_user = 'w1259337898@163.com'
    email_pass = '授权码'
    sender = 'w1259337898@163.com'
    receivers = ['1259337898@qq.com']

    # 创建MIMEMultipart对象
    message = MIMEMultipart("related")
    message["From"] = sender
    message["To"] = ";".join(receivers)
    message["Subject"] = "电影推荐"

    # 正文
    movie_name = spider()
    with open("./temp.html", "rb") as f:
        content = f.read()
    part1 = MIMEText(content, "html", "utf-8")
    message.attach(part1)
    index = 0
    for name in movie_name:
        try:
            with open(f"./image_{index}.jpg", "rb") as f:
                sendImageFile = f.read()
                image = MIMEImage(sendImageFile)
                image.add_header('Content-ID', "<image_%x>" % index)
                message.attach(image)
        except:
            print(f"<image_{index}>" + name + " 相关图片未获取到")
        finally:
            index += 1

    # 附件
    with open('./magnet.txt', "rb") as f:
        content2 = f.read()
    part2 = MIMEText(content2, "plain", "utf-8")
    part2['Content-Type'] = 'application/octet-stream'
    part2['Content-Disposition'] = 'attachment;filename="magnet.txt"'
    message.attach(part2)
    # 发送
    try:
        # receivers = receivers + [sender]
        email_smtp = smtplib.SMTP_SSL(email_host, 465)
        # email_smtp.connect(email_host, 25)
        email_smtp.login(email_user, email_pass)
        email_smtp.sendmail(sender, receivers, message.as_string())
        print("success!")
    except smtplib.SMTPException as e:
        print("error", e)


if __name__ == '__main__':
     sendMail()
    # spider()
