import datetime
import logging
import sqlite3

from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


# Define Pydantic models for request validation
class QueryResult(BaseModel):
    intent: dict
    parameters: dict


class Payload(BaseModel):
    queryResult: QueryResult


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

context_prod = None
context_color = None
context_size = None
context_quantity = None
context_phone = None
context_contact = None


async def handle_order_track(intent_name, parameters):
    try:
        order_id = parameters.get('number')
        logger.info(f"Received Intent: {intent_name}")
        logger.info(f"Received Parameters: {parameters}")
        logger.info(f"Order ID: {order_id}")

        if not order_id:
            raise ValueError("Order ID not provided")

        # Dummy status for the order
        dummy_status = "Processing"

        # Dummy product information
        products = [
            {"name": "Product1", "quantity": 3},
            {"name": "Product2", "quantity": 2},
            # Add more products if needed
        ]

        # Construct the fulfillment message with product information
        elements = [
            {
                "title": f"{int(order_id)} : {dummy_status}",
                "subtitle": f"Order ID: {order_id}",
            }
        ]

        for product in products:
            elements.append({
                "title": f"{product['name']} - Quantity: {product['quantity']}",
                "subtitle": "Product description goes here.",
            })

        fulfillment_message = {
            "fulfillmentMessages": [
                {
                    "payload": {
                        "facebook": {
                            "attachment": {
                                "type": "template",
                                "payload": {
                                    "template_type": "generic",
                                    "elements": elements
                                }
                            }
                        }
                    },
                    "platform": "FACEBOOK"
                }
            ]
        }

        # Log the response
        logger.info(f"Generated Response: {fulfillment_message}")

        # Return fulfillment message
        return JSONResponse(content=fulfillment_message)

    except (ValueError, TypeError) as e:
        # Handle specific data parsing errors
        logger.error(f"Error in handle_order_track: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid data in payload: {str(e)}")

    except Exception as e:
        # Log the unexpected exception
        logger.error(f"Unexpected error in handle_order_track: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def handle_retrieve_prod_info(intent_name, parameters):
    global context_prod
    try:
        prod_id = int(parameters.get('prod'))
        logger.info(f"Received Intent: {intent_name}")
        logger.info(f"Received Parameters: {parameters}")
        logger.info(f"Product ID: {prod_id}")

        if not prod_id:
            raise ValueError("Product ID not provided")

        # Connect to the SQLite database asynchronously

        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()

        # Existing code
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (prod_id,))
        product_info = cursor.fetchone()

        # Modify this part
        if not product_info:
            raise ValueError(f"Product with ID {prod_id} not found")

        # Access tuple elements using integer indices
        title = f"{product_info[0]} - {product_info[1]}"  # Assuming 'type' is at index 1, and 'name' is at index 2
        subtitle = f"Stock: {product_info[2]}\nPrice: {product_info[3]}\nSizes: {product_info[4]}"


        # Construct the fulfillment message with product attributes
        fulfillment_message = {
            "fulfillmentMessages": [
                {
                    "payload": {
                        "facebook": {
                            "attachment": {
                                "type": "template",
                                "payload": {
                                    "template_type": "generic",
                                    "elements": [
                                        {
                                            "title": title,
                                            "subtitle": subtitle,
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "platform": "FACEBOOK"
                },
                {
                    "quickReplies": {
                        "title": "Would you like to order this product?",
                        "quickReplies": ["Yea, sure", "No thanks."]
                    },
                    "platform": "FACEBOOK"
                }
            ],
            "outputContexts": [
                {
                    "name": "projects/newagent-cvrj/locations/global/agent/sessions/your-session-id/contexts/order_confirmation",
                    "lifespanCount": 2,
                    "parameters": {
                        "prod_id": prod_id
                    }
                }
            ]
        }

        # Log the response
        logger.info(f"Generated Response: {fulfillment_message}")

        # Return fulfillment message
        return JSONResponse(content=fulfillment_message)

    except (ValueError, TypeError) as e:
        # Handle specific data parsing errors
        logger.error(f"Error in handle_retrieve_prod_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid data in payload: {str(e)}")

    except Exception as e:
        # Log the unexpected exception
        logger.error(f"Unexpected error in handle_retrieve_prod_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def handle_order_query_retrieve_prod_info_yes(intent_name, parameters):
    global context_prod
    logger.info(context_prod)

    fulfillment_message = {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "Please mention your prefered quantity, size and color"
                    ]
                }
            }
        ]
    }

    logger.info(fulfillment_message)

    return JSONResponse(content=fulfillment_message)


async def add_items(intent_name, parameters):
    global context_size
    global context_color
    global context_quantity

    try:
        # Extract relevant information from the parameters
        context_quantity = parameters.get('number')
        context_color = parameters.get('color')
        context_size = parameters.get('size')


        fulfillment_message = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Anything else or should i conform this?"
                        ]
                    }
                }
            ]
        }
        return JSONResponse(content=fulfillment_message)

    except ValueError as e:
        # Handle specific errors
        logger.error(f"Error handling retrieve_cust_info: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error handling retrieve_cust_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def handle_retrieve_cust_info(intent_name, parameters):
    global context_phone
    global context_size
    global context_color
    global context_quantity
    global context_prod

    DATABASE_PATH = 'orders.db'  # Update with the correct path to your database file

    async def insert_order(order_id, time, phone, contact, status,product_id,context_quantity,context_color,context_size):
        try:
            # Connect to the database
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Insert the order information into the 'orders' table
            cursor.execute('''
                INSERT INTO orders (order_number, order_date, phone, status)
                VALUES (?, ?, ?, ?)
            ''', (order_id, time, phone, status))

            cursor.execute('''
                            INSERT INTO order_products (order_number, product_id, price, size, color)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (order_id, product_id, context_quantity,context_color,context_size))

            cursor.execute('''I''')
            # Commit the changes and close the connection
            conn.commit()
            conn.close()

        except Exception as e:
            # Handle database-related errors
            logger.error(f"Error inserting order into database: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    # Modify your existing code to call the insert_order method after generating the order_id
    try:
        # Extract relevant information from the parameters
        context_phone = parameters.get('phone-number')

        logger.info(f"Customer Phone Number: {context_phone}")
        logger.info(f"Customer Quantity: {context_quantity}")
        logger.info(f"Customer Size: {context_size}")
        logger.info(f"Customer Color: {context_color}")

        import random
        order_id = f'{random.randint(1000, 9999)}'

        # Insert order into the 'orders' table
        await insert_order(order_id, datetime.datetime.now(), context_phone, context_contact,"Initiated",context_prod,context_quantity,context_color,context_size)

        fulfillment_message = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            f"Your order has been confirmed {order_id}. Please keep this safe."
                        ]
                    }
                }
            ]
        }
        logger.info(fulfillment_message)
        return JSONResponse(content=fulfillment_message)

    except ValueError as e:
        # Handle specific errors
        logger.error(f"Error handling retrieve_cust_info: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error handling retrieve_cust_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/")
async def handle_request(request: Request, payload: Payload):
    try:
        # Extract the necessary information from the payload
        intent_name = payload.queryResult.intent.get("displayName")
        parameters = payload.queryResult.parameters

        # Logging
        logger.info(f"Received Intent: {intent_name}")
        logger.info(f"Received Parameters: {parameters}")

        # Handle specific intent
        if intent_name == "order.track - order_id":
            return await handle_order_track(intent_name, parameters)
        elif intent_name == "product.retrive_info":
            return await handle_retrieve_prod_info(intent_name, parameters)
        elif intent_name == "order.conformation":
            return await handle_order_query_retrieve_prod_info_yes(intent_name, parameters)
        elif intent_name == "order.retrive_cust_info":
            logger.info(payload)
            return await handle_retrieve_cust_info(intent_name, parameters)
        elif intent_name == "order.add_item":
            return await add_items(intent_name, parameters)


        else:
            return JSONResponse(content={"fulfillmentText": "Unhandled intent"})

    except KeyError as e:
        # Handle missing keys in the payload
        raise HTTPException(status_code=400, detail=f"Missing key in payload: {str(e)}")

    except (ValueError, TypeError) as e:
        # Handle specific data parsing errors
        raise HTTPException(status_code=400, detail=f"Invalid data in payload: {str(e)}")

    except Exception as e:
        # Log the unexpected exception
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
