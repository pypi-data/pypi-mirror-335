import re
import os
import pymongo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sys
def ub_track_request(key_in_use, SKU, URL, response, status_code,request_type,request_limit,projectcode,feedid,developer_name):
    lengthhh = len(response.text)
    # lengthhh = len(response)
    print(lengthhh)
    response_size_kb = lengthhh / 1024
    rounded_value = round(response_size_kb, 2)
    request_limit = float(request_limit)
    if ':' in projectcode:
        projectcode = projectcode.split(":")[1].split("]")[0]
    else:
        projectcode = projectcode.strip()
    conn = "mongodb://admin:tP_kc8-7$mn1@192.168.2.51:27017/?authSource=admin"
    db_name = f'xbyte_proxy_usage_{projectcode}'
    ub_limit_of_request(conn, db_name,request_limit, feedid, projectcode,key_in_use)
    import datetime
    Date = datetime.date.today() + datetime.timedelta(days=0)
    TDate = Date.strftime("%Y_%m_%d")
    collection_name = f'{feedid}_unblocker_request_tracker_{TDate}'


    connmn = pymongo.MongoClient("mongodb://admin:tP_kc8-7$mn1@192.168.2.51:27017/?authSource=admin")
    mydb = connmn[db_name]
    collection = mydb[collection_name]
    collection.insert_one({
        'project_name': projectcode,
        'developer_name': developer_name,
        'key_in_use': key_in_use,
        'service_provider': 'unblocker',
        'SKU': SKU,
        'URL': URL,
        'status_code': status_code,
        request_type: 1,
        'response_size':rounded_value
    })
    #convert GB to KB
    request_limits = request_limit * 1_048_576
    total_sum = sum(doc.get('response_size', 0) for doc in collection.find({}, {'response_size': 1}))
    if total_sum >= request_limits:
        ################### Limit Exceed #################
        input("Press ENTER to send an email notification. DO NOT close the window directly.")
        print("🔴 Limit Exceeded! Sending Email Alert...")

        ################# Mail Generated #############

        try:
            mail_content = []
            mail_content.append("<html><head>")
            mail_content.append(
                """<style>table, th, td {border: 1px solid black; border-collapse: collapse;}th, td {padding: 8px;} body {font-family: Verdana !important;}</style>"""
            )
            mail_content.append("</head><body><br>")

            mail_content.append("""<table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; text-align: center;"><tbody><tr style="background-color:#77D3EE; text-align:center;">""")
            mail_content.append("""<th style= "width:100px;"><b>Key In Use</b></th>""")
            mail_content.append("""<th style="width:100px;"><b>Developer Name</b></th>""")
            mail_content.append("""<th style="width:100px;"><b>Status Code</b></th>""")
            mail_content.append("""<th style="width:100px;"><b>Count</b></th>""")
            mail_content.append("""<th style="width:100px;"><b>Total Size</b></th></tr>""")
            pipeline = [
                {
                    "$group": {
                        "_id": {
                            "status_code": "$status_code",
                            "key_in_use": "$key_in_use",
                            "developer_name": "$developer_name",
                            "service_provider": "$service_provider"
                        },
                        "total_review_retry_count": {"$sum": 1},
                        "total_response_size": {"$sum": "$response_size"}  # Summing Response Sizes
                    }
                },
                {"$sort": {"_id.status_code": 1}}
            ]
            report_data = list(collection.aggregate(pipeline))

            if report_data:
                for row in report_data:
                    status_code = row["_id"]["status_code"]
                    count = row["total_review_retry_count"]
                    key_in_use = row["_id"]["key_in_use"]
                    developer_name = row["_id"]["developer_name"]
                    total_response_sizee = row["total_response_size"]
                    total_response_size = round(total_response_sizee / 1_048_576, 2)
                    mail_content.append(f"""<tr>
                                    <td style="word-wrap:break-word; max-width:250px;"><a href="{key_in_use}" target="_blank">{key_in_use}</a></td>
                                    <td>{developer_name}</td>
                                    <td>{status_code}</td>
                                    <td>{count}</td>
                                    <td>{total_response_size}</td>
                                </tr>""")

            mail_content.append("</tbody></table>")
            mail_content.append("<p>This is system generated mail - Do Not Reply</p></body></html>")
            body = "".join(mail_content)
            # Email Configuration
            emailId = "alert.xbyte.internal@gmail.com"
            emailpass = "bkcadyrxpgrjyshx"
            # send_to = ["forward.pc@xbyte.io"]
            send_to = ["bhumika.bhatti@xbyte.io"]
            # cc = ["pruthak.acharya@xbyte.io", "bhavesh.parekh@xbyte.io", "anil.prajapati@xbyte.io"]
            cc = ["bhumika.bhatti@xbyte.io"]
            bcc = ["bhumika.bhatti@xbyte.io"]
            from datetime import datetime
            try:
                msg = MIMEMultipart()
                msg['From'] = emailId
                msg['To'] = ",".join(send_to)
                msg['CC'] = ",".join(cc)
                msg['BCC'] = ",".join(bcc)
                msg['Subject'] = f"[Alert:{projectcode}] Proxy Usage Report Feed ID {feedid}: {datetime.now().strftime('%d/%m/%Y')}"
                msg.attach(MIMEText(body, 'html'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(emailId, emailpass)
                server.sendmail(emailId, send_to + cc + bcc, msg.as_string())
                server.quit()
                print("✅ Email Sent Successfully!")
            except Exception as e:
                print(f"❌ Error sending email: {e}")
        except Exception as e:
            print(e)
        ########### Program Exit #########
        print("Exiting program...")
        os._exit(1)

def ub_limit_of_request(conn,db_name,request_limit,feedid,projectcode,key_in_use):
    connmn = pymongo.MongoClient(conn)
    mydb = connmn[db_name]
    collection = mydb["input_unblocker_limit_log"]
    from datetime import datetime
    current_time = datetime.now().strftime('%Y_%m_%dT%H:%M:%S')
    record = collection.find_one({'feedid': feedid, 'projectcode': projectcode, "request_limit": request_limit})
    if not record:
        collection.insert_one({
            'key_in_use': key_in_use,
            'feedid': feedid,
            'projectcode': projectcode,
            'request_limit': request_limit,
            'Datetime': current_time
        })
if __name__ == '__main__':
    ub_track_request("brd-customer-hl_4fc8c816-zone-unlocker_xb_2824_chewy:k4gwpbb6ymct@zproxy.lum-superproxy.io:22225",'B0CKZCX4D7','https://www.amazon.com/dp/B0CKZCX4D7','(function(f,b){function g(){try{b.PerformanceObserver&&"function"===typeof b.PerformanceObserver&&)','200','review_retry_count','0.1','3155','13302','Bhumika Bhatti')