import sqlite3


DB = "database.db"


# =========================
# DATABASE SETUP
# =========================

def setup():

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        user_id TEXT PRIMARY KEY,
        balance REAL DEFAULT 0
    )
    """)



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        group_link TEXT,
        pickup_name TEXT,
        pickup_time TEXT,
        status TEXT DEFAULT 'Pending',
        chip_entry_id TEXT,
        drop_id TEXT,
        confirmation TEXT,
        refunded INTEGER DEFAULT 0,
        api_response TEXT,
        api_error TEXT,
        created_at TEXT
    )
    """)



    # =========================
    # ORDER MIGRATIONS
    # =========================

    cursor.execute(
        "PRAGMA table_info(orders)"
    )


    columns = [

        row[1]

        for row in cursor.fetchall()

    ]



    if "chip_entry_id" not in columns:

        cursor.execute(
            """
            ALTER TABLE orders
            ADD COLUMN chip_entry_id TEXT
            """
        )



    if "drop_id" not in columns:

        cursor.execute(
            """
            ALTER TABLE orders
            ADD COLUMN drop_id TEXT
            """
        )



    if "confirmation" not in columns:

        cursor.execute(
            """
            ALTER TABLE orders
            ADD COLUMN confirmation TEXT
            """
        )



    if "refunded" not in columns:

        cursor.execute(
            """
            ALTER TABLE orders
            ADD COLUMN refunded INTEGER DEFAULT 0
            """
        )



    if "api_response" not in columns:

        cursor.execute(
            """
            ALTER TABLE orders
            ADD COLUMN api_response TEXT
            """
        )



    if "api_error" not in columns:

        cursor.execute(
            """
            ALTER TABLE orders
            ADD COLUMN api_error TEXT
            """
        )



    if "created_at" not in columns:

        cursor.execute(
            """
            ALTER TABLE orders
            ADD COLUMN created_at TEXT
            """
        )



    conn.commit()

    conn.close()



# =========================
# WALLET SYSTEM
# =========================

def create_wallet(user_id):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT OR IGNORE INTO wallets
        (
            user_id,
            balance
        )
        VALUES (?,?)
        """,
        (
            str(user_id),
            0
        )
    )


    conn.commit()

    conn.close()



def get_balance(user_id):

    create_wallet(user_id)


    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT balance
        FROM wallets
        WHERE user_id = ?
        """,
        (
            str(user_id),
        )
    )


    result = cursor.fetchone()


    conn.close()


    if result:

        return result[0]


    return 0



def add_balance(user_id, amount):

    create_wallet(user_id)


    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE wallets
        SET balance = balance + ?
        WHERE user_id = ?
        """,
        (
            amount,
            str(user_id)
        )
    )


    conn.commit()

    conn.close()



def deduct_balance(user_id, amount):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE wallets
        SET balance = balance - ?
        WHERE user_id = ?
        """,
        (
            amount,
            str(user_id)
        )
    )


    conn.commit()

    conn.close()



# =========================
# ORDER SYSTEM
# =========================

def create_order(
    user_id,
    group_link,
    pickup_name,
    pickup_time
):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO orders
        (
            user_id,
            group_link,
            pickup_name,
            pickup_time
        )

        VALUES (?,?,?,?)
        """,
        (
            str(user_id),
            group_link,
            pickup_name,
            pickup_time
        )
    )


    order_id = cursor.lastrowid


    conn.commit()

    conn.close()


    return order_id



def attach_chip_entry(
    order_id,
    chip_entry_id,
    drop_id
):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders

        SET
            chip_entry_id = ?,
            drop_id = ?,
            status = ?

        WHERE order_id = ?
        """,
        (
            str(chip_entry_id),
            str(drop_id),
            "Submitted",
            order_id
        )
    )


    conn.commit()

    conn.close()



def save_api_response(
    order_id,
    response
):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders

        SET api_response = ?

        WHERE order_id = ?
        """,
        (
            str(response),
            order_id
        )
    )


    conn.commit()

    conn.close()



def save_api_error(
    order_id,
    error
):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders

        SET api_error = ?

        WHERE order_id = ?
        """,
        (
            str(error),
            order_id
        )
    )


    conn.commit()

    conn.close()



def get_order_by_entry(entry_id):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            order_id,
            user_id,
            status,
            refunded

        FROM orders

        WHERE chip_entry_id = ?
        """,
        (
            str(entry_id),
        )
    )


    order = cursor.fetchone()


    conn.close()


    return order



def update_order_status(
    order_id,
    status
):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders

        SET status = ?

        WHERE order_id = ?
        """,
        (
            status,
            order_id
        )
    )


    conn.commit()

    conn.close()



def add_confirmation(
    order_id,
    confirmation
):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders

        SET confirmation = ?

        WHERE order_id = ?
        """,
        (
            confirmation,
            order_id
        )
    )


    conn.commit()

    conn.close()



def get_orders(user_id):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            order_id,
            user_id,
            group_link,
            pickup_name,
            pickup_time,
            status,
            chip_entry_id
        FROM orders
        WHERE user_id = ?
        ORDER BY order_id DESC
        """,
        (
            str(user_id),
        )
    )


    orders = cursor.fetchall()

    conn.close()

    return orders



# =========================
# REFUND PROTECTION
# =========================

def is_refunded(order_id):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT refunded

        FROM orders

        WHERE order_id = ?
        """,
        (
            order_id,
        )
    )


    result = cursor.fetchone()


    conn.close()


    if result:

        return result[0] == 1


    return False



def mark_refunded(order_id):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE orders

        SET refunded = 1

        WHERE order_id = ?
        """,
        (
            order_id,
        )
    )


    conn.commit()

    conn.close()
    # =========================
# MARK ORDER FAILED
# =========================

def mark_order_failed(
    order_id,
    error
):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE orders
        SET
            status = ?,
            api_error = ?,
            refunded = ?
        WHERE order_id = ?
        """,
        (
            "Failed",
            str(error),
            1,
            order_id
        )
    )

    conn.commit()

    conn.close()
