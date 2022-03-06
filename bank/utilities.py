from datetime import datetime, timedelta
from reportlab.pdfgen import canvas as canvas_pdf

class DocumentUtility():

    @staticmethod
    def generate_contract(client):
       pass

    
    @staticmethod
    def generate_ticket(transaction, account):
        canvas = canvas_pdf.Canvas("media/receipt/{}.pdf".format(transaction.auth_number), pagesize=(1275, 1650))
        canvas.setFont("Helvetica", 28)
        if transaction.ammount < 0:
            canvas.drawImage('static/templates/withdrawal.jpg',
                        0, 0, width=1275, height=1650)
        else:
            canvas.drawImage('static/templates/deposit.jpg',
                        0, 0, width=1275, height=1650)

        timestamp = transaction.timestamp - timedelta(hours=7)
        canvas.drawString(340, 1330, account.branch.name)
        canvas.drawString(340, 1270, datetime.strftime(timestamp, "%d/%m/%Y"))
        canvas.drawString(340, 1210, datetime.strftime(timestamp, "%H:%M:%S"))
        canvas.drawString(340, 1150, transaction.auth_number)
        canvas.drawString(370, 1050, "$"+str(abs(transaction.ammount)))
        canvas.drawString(370, 1000, account.hidden_name())
        canvas.drawString(490, 950, "**** **** **** "+account.card.number[:4])
        canvas.save()

    @staticmethod
    def generate_receipt(transaction, teller, origin, destiny):
        canvas = canvas_pdf.Canvas("media/receipt/{}.pdf".format(transaction.auth_number), pagesize=(1275, 1650))
        canvas.setFont("Helvetica", 28)
        canvas.drawImage('static/templates/receipt.jpg',
                        0, 0, width=1275, height=1650)
       
        timestamp = transaction.timestamp - timedelta(hours=7)
        canvas.drawString(450, 1340, origin.hidden_name())
        canvas.drawString(450, 1280, datetime.strftime(timestamp, "%d/%m/%Y"))
        canvas.drawString(450, 1220, datetime.strftime(timestamp, "%H:%M:%S"))
        canvas.drawString(450, 1150, transaction.auth_number)
        canvas.drawString(545, 985, "**** **** **** "+origin.card.number[:4])
        canvas.drawString(545, 885, "**** **** **** "+destiny.card.number[:4])
        canvas.drawString(545, 835, destiny.hidden_name())
        canvas.drawString(710, 680, "$"+str(transaction.ammount))
        canvas.drawString(710, 630, transaction.concept)
        canvas.save()
    
    @staticmethod
    def generate_statement(data):
        canvas = canvas_pdf.Canvas("media/statement/{}.pdf".format(data["client"]["number"]), pagesize=(1275, 1650))
        canvas.setFont("Helvetica", 28)
        canvas.drawImage('static/templates/statement_data.jpg',
                        0, 0, width=1275, height=1650)
       
        canvas.drawString(590, 1340, data["client"]["name"])
        canvas.drawString(590, 1290, data["client"]["address"])
        canvas.drawString(590, 1240, data["client"]["place"])
        canvas.drawString(590, 1190, data["client"]["zip_code"])
        
        canvas.drawString(630, 1080, data["start_date"])
        canvas.drawString(820, 1080, data["end_date"])
        canvas.drawString(590, 1030, data["cutoff_date"])
        canvas.drawString(590, 980, data["client"]["account_number"])
        canvas.drawString(590, 930, data["client"]["number"])
        canvas.drawString(590, 880, data["client"]["rfc"])

        canvas.drawString(590, 770, data["branch"]["name"])
        canvas.drawString(590, 720, data["branch"]["number"])
        canvas.drawString(590, 670, data["branch"]["address"])
        canvas.drawString(590, 620, data["branch"]["place"])
        canvas.drawString(590, 570, data["branch"]["zip_code"])

        
        canvas.drawString(590, 450, "$"+str(data["prev_balance"]))
        canvas.drawString(590, 400, "$"+str(data["deposits"]))
        canvas.drawString(590, 350, "$"+str(data["withdrawals"]))
        canvas.drawString(590, 300, "$"+str(data["final_balance"]))
        canvas.drawString(590, 250, "$"+str(data["avg_balance"]))

        canvas.showPage()
        canvas.setFont("Helvetica", 25)
        canvas.drawImage('static/templates/statement_transactions.jpg',
                        0, 0, width=1275, height=1650)
        
        y = 1325
        for t in data["movements"]:
            canvas.drawString(90, y, t["date"])
            canvas.drawString(245, y, t["concept"][:10])
            canvas.drawString(425, y, t["auth_num"])
            if t["deposit"]:
                canvas.drawString(665, y, "$"+ str(t["deposit"]))
            else:
                canvas.drawString(665, y, "-")
            if t["withdrawal"]:
                canvas.drawString(840, y, "$"+ str(t["withdrawal"]))
            else:
                canvas.drawString(840, y, "-")
            canvas.drawString(1020, y, "$"+str(t["balance"]))
            y-=49
            if y < 270:
                y = 1310
                canvas.showPage()
                canvas.setFont("Helvetica", 25)
                canvas.drawImage('static/templates/statement_transactions.jpg',
                                0, 0, width=1275, height=1650)

        canvas.save()


class ValidationUtility():
    @staticmethod
    def valid_initial_ammount(account, ammount):
        pass

    @staticmethod
    def valid_existing_ammount(account, ammount):
        pass

    @staticmethod
    def valid_account(account_number):
        pass

class SendUtility():
    @staticmethod
    def send_current_ammount(client, ammount):
        pass

    @staticmethod
    def send_receipt(client, send_receipt):
        pass

    @staticmethod
    def send_statement(client, statement):
        pass


    @staticmethod
    def send_error(client, error):
        pass