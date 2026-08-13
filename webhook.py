import asyncio
import io
import hmac
import hashlib
import json
import aiohttp
import discord

from flask import Flask, request, jsonify

import config
import store


app = Flask(__name__)
def verify_signature(payload, signature):

    if not signature:
        return False

    expected = hmac.new(
        config.CHIP_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        signature,
        f"sha256={expected}"
    )

# =========================
# DISCORD CLIENT
# =========================

bot_client = None


def set_bot(client):

    global bot_client

    bot_client = client



# =========================
# SUCCESS CHANNEL EMBED
# =========================
def send_order_dm(user_id, order_id):

    if not bot_client:
        print("Discord bot not connected")
        return

    async def dm():
        try:
            user = await bot_client.fetch_user(int(user_id))

            embed = discord.Embed(
                title="🌯 Your order is locked in!",
                description=(
                    "✅ **You're locked in!**\n\n"
                    f"Order ID: **#{order_id}**\n\n"
                    "Your order has been accepted and is being processed."
                ),
                color=discord.Color.green()
            )

            await user.send(embed=embed)

            print("✅ Order DM sent")

        except Exception as e:
            print("DM ERROR:", e)

    asyncio.run_coroutine_threadsafe(
        dm(),
        bot_client.loop
    )
def send_success_embed(
    title,
    description,
    color=discord.Color.green()
):

    if not bot_client:

        print(
            "Discord bot not connected"
        )

        return



    channel = bot_client.get_channel(
        config.SUCCESS_CHANNEL_ID
    )


    if not channel:

        print(
            "Success channel not found"
        )

        return



    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )


    embed.set_footer(
        text="Cheapotle Drops 🌯"
    )


    embed.timestamp = discord.utils.utcnow()



    asyncio.run_coroutine_threadsafe(

        channel.send(
            embed=embed
        ),

        bot_client.loop

    )



# =========================
# SEND CHIP CONFIRMATION IMAGE
# =========================

async def send_confirmation_image(
    entry_id,
    user_id
):

    if not bot_client:

        print(
            "Discord bot not connected"
        )

        return



    try:

        user = await bot_client.fetch_user(
            int(user_id)
        )


    except Exception as e:

        print(
            "User fetch failed:",
            e
        )

        return



    url = (

        f"{config.CHIP_API_URL}"
        f"/v1/entries/{entry_id}/confirmation.png"

    )


    headers = {

        "X-Api-Key":
        config.CHIP_API_KEY

    }



    # Retry because confirmation image can take time to render

    for attempt in range(1, 6):

        try:

            async with aiohttp.ClientSession() as session:


                async with session.get(

                    url,

                    headers=headers

                ) as response:



                    if response.status == 200:


                        image = await response.read()



                        file = discord.File(

                            io.BytesIO(image),

                            filename="chipotle_confirmation.png"

                        )



                        await user.send(

                            "🎉 **Your Cheapotle order is complete!** 🌯\n\n"
                            "Here is your Chipotle confirmation:",

                            file=file

                        )



                        print(

                            "✅ Confirmation image sent to:",

                            user_id

                        )


                        return



                    print(

                        f"⏳ Confirmation image not ready "
                        f"({attempt}/5):",

                        response.status

                    )



        except Exception as e:

            print(

                "Confirmation image error:",

                e

            )



        await asyncio.sleep(10)



    print(

        "❌ Confirmation image failed after retries:",

        entry_id

    )



# =========================
# WEBHOOK RECEIVER
# =========================

@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():
    raw_body = request.get_data()
    signature = request.headers.get(
        "X-Signature"
    )

    if not verify_signature(
        raw_body,
        signature
    ):
        print(
            "❌ Invalid webhook signature"
        )

        return jsonify(
            {
                "error": "invalid signature"
            }
        ), 401


    payload = request.json


    print(
        "🔥🔥 WEBHOOK HIT 🔥🔥"
    )


    print(
        payload
    )



    event = payload.get(
        "event"
    )


    entry_id = payload.get(
        "entry_id"
    )



    print(
        "EVENT:",
        event
    )


    print(
        "ENTRY ID:",
        entry_id
    )



    order = store.get_order_by_entry(
        entry_id
    )



    if not order:


        print(
            "No matching order"
        )


        return jsonify(
            {
                "ok": True
            }
        )



    order_id = order[0]


    user_id = order[1]



    print(
    "MATCHED ORDER:",
    order_id
)


    send_order_dm(
        user_id,
        order_id
)


# =========================
# LOCKED
# =========================


    

    if event == "entry.locked":


        send_success_embed(

            "🔒 Someone locked in their meal!",

            "🌯 Drop entry secured.\n\n"
            "🔥 Waiting for the drop to fire."

        )



    # =========================
    # PLACED
    # =========================

    elif event == "entry.placed":


        send_success_embed(

            "🎉 Order placed successfully!",

            "🌯 Someone secured their meal!\n\n"
            "🔥 Cheapotle Drop completed."

        )



    # =========================
    # CONFIRMATION
    # =========================

    elif event == "entry.confirmation":


        confirmation = payload["data"].get(
            "confirmation_code"
        )



        store.add_confirmation(

            order_id,

            confirmation

        )



        print(

            "✅ Confirmation saved:",

            confirmation

        )



        asyncio.run_coroutine_threadsafe(

            send_confirmation_image(

                entry_id,

                user_id

            ),

            bot_client.loop

        )



        send_success_embed(

            "🎉 Someone just scored an order! 🌯",

            "🔥 Another Cheapotle drop secured!\n\n"
            "━━━━━━━━━━━━━━\n"
            "✅ Status: COMPLETED\n"
            "🌯 Meal: Secured\n"
            "━━━━━━━━━━━━━━"

        )



    # =========================
    # FAILED
    # =========================

    elif event == "entry.failed":


        if store.is_refunded(order_id):

            print(
                "⚠️ Already refunded, skipping"
            )


            return jsonify(
                {
                    "ok": True
                }
            )



            store.mark_refunded(
                order_id
        )



        send_success_embed(

            "❌ Order failed",

            "Wallet refund processed.",

            discord.Color.red()

        )



    # =========================
    # SKIPPED
    # =========================

    elif event == "entry.skipped":


        if store.is_refunded(order_id):

            print(
                "⚠️ Already refunded, skipping"
            )


            return jsonify(
                {
                    "ok": True
                }
            )



        store.mark_refunded(
    order_id
)



        send_success_embed(

            "⚠️ Drop skipped",

            "Wallet refund processed.",

            discord.Color.orange()

        )



    else:

        print(

            "Unknown event:",

            event

        )



    return jsonify(
        {
            "ok": True
        }
    )



# =========================
# START WEBHOOK
# =========================

# =========================
# START WEBHOOK
# =========================

import os

def start_webhook():

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 25300))
    )


if __name__ == "__main__":
    start_webhook()
