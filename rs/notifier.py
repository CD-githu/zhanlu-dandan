import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import storage


class Notifier:
    def __init__(self, config):
        self.config = config.get("push", {})
        self.push_type = self.config.get("type", "dingtalk")

    def build_message(self, notifications, batch_num=1, total_batches=1):
        if not notifications:
            return ""

        total_count = total_batches if batch_num == 1 else ""
        lines = ["【通知】云南省人社厅新通知：", ""]
        
        if total_batches > 1:
            lines.append(f"本次共 {total_count} 条通知，第 {batch_num}/{total_batches} 批")
            lines.append("")
            
        for item in notifications:
            date = item.get("date", "未知日期")
            source = item.get("source", "")
            title = item.get("title", "")
            url = item.get("url", "")
            lines.append(f"[{source}] {date}")
            lines.append(f"   {title}")
            lines.append(f"   {url}")
            lines.append("")

        return "\n".join(lines)

    def send_dingtalk(self, message):
        token = self.config.get("dingtalk_token", "")
        if not token:
            print("[ERROR] 未配置钉钉 access_token")
            storage.save_push_log(0, "error_no_token")
            return False

        url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
        
        message_bytes = len(message.encode('utf-8'))
        if message_bytes > 19000:
            print(f"[WARN] 消息过大 ({message_bytes} 字节)，将被截断")
            message = message[:6000] + "\n...（内容过长，已截断）"
            message_bytes = len(message.encode('utf-8'))
            
        data = {
            "msgtype": "text",
            "text": {"content": message}
        }

        try:
            resp = requests.post(url, json=data, timeout=10)
            result = resp.json()
            if result.get("errcode") == 0:
                print(f"[OK] 钉钉推送成功: {message_bytes} 字节")
                storage.save_push_log(message_bytes, "success")
                return True
            else:
                print(f"[ERROR] 钉钉推送失败: {result}")
                storage.save_push_log(0, f"error_{result.get('errmsg', '')}")
                return False
        except Exception as e:
            print(f"[ERROR] 钉钉推送异常: {e}")
            storage.save_push_log(0, f"error_{e}")
            return False

    def send_wechat(self, message):
        key = self.config.get("wechat_key", "")
        if not key:
            print("[ERROR] 未配置企业微信 key")
            storage.save_push_log(0, "error_no_key")
            return False

        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
        data = {
            "msgtype": "text",
            "text": {"content": message}
        }

        try:
            resp = requests.post(url, json=data, timeout=10)
            result = resp.json()
            if result.get("errcode") == 0:
                print(f"[OK] 企业微信推送成功: {len(message)} 字符")
                storage.save_push_log(len(message), "success")
                return True
            else:
                print(f"[ERROR] 企业微信推送失败: {result}")
                storage.save_push_log(0, f"error_{result.get('errmsg', '')}")
                return False
        except Exception as e:
            print(f"[ERROR] 企业微信推送异常: {e}")
            storage.save_push_log(0, f"error_{e}")
            return False

    def send_email(self, message):
        email_config = self.config.get("email", {})
        smtp_server = email_config.get("smtp", "")
        smtp_user = email_config.get("user", "")
        smtp_password = email_config.get("password", "")
        smtp_to = email_config.get("to", "")
        smtp_port = email_config.get("port", 465)

        if not all([smtp_server, smtp_user, smtp_password, smtp_to]):
            print("[ERROR] 未完整配置邮件信息")
            storage.save_push_log(0, "error_no_email_config")
            return False

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = smtp_to
        msg["Subject"] = "云南省人社厅新通知"
        msg.attach(MIMEText(message, "plain", "utf-8"))

        try:
            if smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()

            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, smtp_to, msg.as_string())
            server.quit()

            print(f"[OK] 邮件推送成功")
            storage.save_push_log(len(message), "success")
            return True
        except Exception as e:
            print(f"[ERROR] 邮件推送异常: {e}")
            storage.save_push_log(0, f"error_{e}")
            return False

    def send(self, notifications):
        if not notifications:
            print("[INFO] 无新通知，跳过推送")
            storage.save_push_log(0, "no_notifications")
            return False

        total_count = len(notifications)
        batch_size = 10
        total_batches = (total_count + batch_size - 1) // batch_size
        
        success_count = 0
        for i in range(0, total_count, batch_size):
            batch = notifications[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            message = self.build_message(batch, batch_num, total_count)
            print(f"\n[推送] 第 {batch_num}/{total_batches} 批 ({len(batch)} 条):")
            print(message[:200] if len(message) > 200 else message)
            
            if self.push_type == "dingtalk":
                result = self.send_dingtalk(message)
            elif self.push_type == "wechat":
                result = self.send_wechat(message)
            elif self.push_type == "email":
                result = self.send_email(message)
            else:
                print(f"[ERROR] 未知推送类型: {self.push_type}")
                return False
            
            if result:
                success_count += 1
                
            if batch_num < total_batches:
                import time
                time.sleep(1)
        
        return success_count == total_batches
