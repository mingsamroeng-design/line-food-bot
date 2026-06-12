from flask import Flask, request

from linebot.v3.webhook import WebhookHandler

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)

from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

from linebot.v3.exceptions import (
    InvalidSignatureError,
)

from config import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
    PORT,
)

from bill import (
    create_bill,
    add_member,
    add_item,
    set_vat,
    set_service,
    calculate,
    get_bill,
)

app = Flask(__name__)

configuration = Configuration(
    access_token=LINE_CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(
    LINE_CHANNEL_SECRET
)


@app.route("/")
def home():
    return "🍽️ Ming Food Bot is running!"


@app.route("/callback", methods=["POST"])
def callback():

    signature = request.headers.get(
        "X-Line-Signature",
        ""
    )

    body = request.get_data(
        as_text=True
    )

    try:

        handler.handle(
            body,
            signature
        )

    except InvalidSignatureError:

        return (
            "Invalid signature",
            400
        )

    except Exception as e:

        print(e)

        return (
            "Internal Server Error",
            500
        )

    return "OK"


@handler.add(
    MessageEvent,
    message=TextMessageContent
)
def handle_message(event):

    text = event.message.text.strip()

    try:
        group_id = event.source.group_id

    except Exception:

        group_id = event.source.user_id

    reply = ""

    # ======================
    # สร้างบิลใหม่
    # ======================
    if text == "/new":

        create_bill(group_id)

        reply = (
            "🍽️ สร้างบิลใหม่เรียบร้อย\n\n"
            "/addmember ชื่อ\n"
            "/additem เมนู ราคา คน1,คน2"
        )

    # ======================
    # เพิ่มสมาชิก
    # ======================
    elif text.startswith("/addmember"):

        name = (
            text
            .replace("/addmember", "")
            .strip()
        )

        if name == "":

            reply = "กรุณาระบุชื่อสมาชิก"

        else:

            add_member(
                group_id,
                name
            )

            reply = f"✅ เพิ่มสมาชิก {name}"

    # ======================
    # เพิ่มรายการอาหาร
    # ======================
    elif text.startswith("/additem"):

        data = (
            text
            .replace("/additem", "")
            .strip()
        )

        parts = data.split()

        if len(parts) < 3:

            reply = (
                "รูปแบบคำสั่ง\n\n"
                "/additem เมนู ราคา คน1,คน2"
            )

        else:

            try:

                item_name = parts[0]

                price = float(parts[1])

                eaters = (
                    parts[2]
                    .split(",")
                )

                add_item(
                    group_id,
                    item_name,
                    price,
                    eaters
                )

                reply = (
                    f"✅ เพิ่มรายการ {item_name}\n"
                    f"ราคา {price:.2f} บาท"
                )

            except ValueError:

                reply = "ราคาไม่ถูกต้อง"

    # ======================
    # VAT
    # ======================
    elif text.startswith("/vat"):

        percent = float(
            text.replace(
                "/vat",
                ""
            ).strip()
        )

        set_vat(
            group_id,
            percent
        )

        reply = (
            f"✅ VAT {percent}%"
        )

    # ======================
    # Service Charge
    # ======================
    elif text.startswith("/service"):

        percent = float(
            text.replace(
                "/service",
                ""
            ).strip()
        )

        set_service(
            group_id,
            percent
        )

        reply = (
            f"✅ Service {percent}%"
        )

    # ======================
    # Show Bill
    # ======================
    elif text == "/show":

        bill = get_bill(group_id)

        msg = []

        msg.append("📋 รายการปัจจุบัน")
        msg.append("")

        msg.append("👥 สมาชิก")

        if len(bill["members"]) == 0:

            msg.append("- ไม่มี")

        else:

            for member in bill["members"]:

                msg.append(f"• {member}")

        msg.append("")
        msg.append("🍽️ รายการอาหาร")

        if len(bill["items"]) == 0:

            msg.append("- ไม่มี")

        else:

            for item in bill["items"]:

                people = ", ".join(item["members"])

                msg.append(
                    f"• {item['name']} {item['price']:.2f}"
                )

                msg.append(
                    f"   👥 {people}"
                )

        msg.append("")
        msg.append(
            f"VAT : {bill['vat']}%"
        )

        msg.append(
            f"Service : {bill['service']}%"
        )

        reply = "\n".join(msg)    

    # ======================
    # Summary
    # ======================
    elif text == "/summary":

        result, subtotal, service, vat = calculate(
            group_id
        )

        total = (
            subtotal
            + service
            + vat
        )

        msg = []

        msg.append(
            "🍽️ สรุปค่าอาหาร"
        )

        msg.append("")

        msg.append(
            f"Subtotal : {subtotal:.2f}"
        )

        msg.append(
            f"Service : {service:.2f}"
        )

        msg.append(
            f"VAT : {vat:.2f}"
        )

        msg.append("")

        msg.append(
            f"รวมทั้งสิ้น : {total:.2f}"
        )

        msg.append("")

        for person in result:

            msg.append(
                f"{person} : {result[person]:.2f} บาท"
            )

        reply = "\n".join(
            msg
        )
        
    # ======================
    # คำสั่งอื่นๆ
    # ======================
    else:

        reply = (
            "📋 คำสั่งที่รองรับ\n\n"
            "/new\n"
            "/addmember ชื่อ\n"
            "/additem เมนู ราคา คน1,คน2\n"
            "/show\n"
            "/vat 7\n"
            "/service 10\n"
            "/summary"
        )

    with ApiClient(
        configuration
    ) as api_client:

        line_bot_api = MessagingApi(
            api_client
        )

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=reply
                    )
                ]
            )
        )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=True
    )