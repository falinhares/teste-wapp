from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://teste:teste@cluster0.cwu6cpl.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        res.message("Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below: \n\n*Type\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣️To know our *working hours* \n 4️⃣ To get our *address*")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 1:
            res.message("Você pode nos contactar pelo seguinte email:...")
        elif option == 2:
            res.message("Entrou no modo de pedido...")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message("lista de opções aqui!!")
        elif option == 3:
            res.message("Nossos horários de funcionamento")
        elif option == 4:
            res.message("Nossos endereços")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message(
                "You can choose from one of the options below: \n\n*Type\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣️To know our *working hours* \n 4️⃣ To get our *address*")
        elif 1 <= option <= 9:
            cakes = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
            selected = "Bolo "+cakes[option -1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Ótima escolha!")
            res.message("Entrar endereço")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Obrigado por comprar")
        res.message(f"Seu pedido: {selected} foi recebido")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message(
            "Obrigado por comprar de novo conosco. You can choose from one of the options below: \n\n*Type\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣️To know our *working hours* \n 4️⃣ To get our *address*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)

if __name__ == "__main__":
    app.run()
