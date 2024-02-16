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
context_id = None


# DONE
def get_order_details(order_id):
    try:
        # Connect to the database
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()

        # Query order details and associated products
        cursor.execute('''
            SELECT o.order_number, o.order_date, p.product_id, o.phone_number, o.status,
                   op.quantity, p.type, p.stock, p.price, op.size, op.color
            FROM orders o
            JOIN order_products op ON o.order_number = op.order_number
            JOIN products p ON op.product_id = p.product_id
            WHERE o.order_number = ?
        ''', (int(order_id),))

        # Fetch the result
        result = cursor.fetchall()

        # Close the connection
        conn.close()

        return result

    except sqlite3.Error as e:
        # Handle database-related errors
        print(f"Error retrieving order details: {str(e)}")
        return None


async def handle_order_track(intent_name, parameters):
    try:
        order_id = parameters.get('number')
        logger.info(f"Received Intent: {intent_name}")
        logger.info(f"Received Parameters: {parameters}")
        logger.info(f"Order ID: {order_id}")

        if not order_id:
            raise ValueError("Order ID not provided")

        # Retrieve order details from the database
        order_details = get_order_details(int(order_id))

        if not order_details:
            raise ValueError(f"Order with ID {order_id} not found")

        # Construct the fulfillment message with product information
        elements = [
            {
                "title": f"Order ID {int(order_id)} : {order_details[0][4]}",
                # Index 4 corresponds to the status in the tuple
                "subtitle": f"{order_details[0][1]}",
            }
        ]

        for product in order_details:
            elements.append({
                "title": f"{product[6]} - Quantity: {product[5]}",  # Adjust indices based on your tuple structure
                "subtitle": f"Price: {product[8]}, Size: {product[-1]}, Colors: {product[-2]}",
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

    except ValueError as ve:
        # Handle specific data errors
        logger.error(f"ValueError in handle_order_track: {str(ve)}", exc_info=True)
        raise HTTPException(status_code=404, detail=f"Order not found: {str(ve)}")

    except sqlite3.Error as e:
        # Handle database-related errors
        logger.error(f"Error in handle_order_track: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        # Log the unexpected exception
        logger.error(f"Unexpected error in handle_order_track: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def handle_retrieve_prod_info(intent_name, parameters):
    global context_prod

    try:
        prod_id = int(parameters.get('prod'))
        context_prod = prod_id
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
            # If product with given prod_id not found
            fulfillment_message = {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": ["Product ID does not match. Please try again carefully."]
                        }
                    }
                ]
            }
        else:
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
                                    "type": "image",
                                    "payload": {
                                        "url": "https://i.ibb.co/M6QpTq0/mens-sizes.jpg"
                                        # Replace with the actual path to your image file
                                    }
                                }
                            }
                        },
                        "platform": "FACEBOOK"
                    },
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
    '''
    :param intent_name: to add item
    :param parameters: quantity,size,color
    :return: add quantity,size,color to their global variables
    '''
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
    '''
    :param intent_name: intent name
    :param parameters: phone_number
    :return: Unique order id to user, saves order, saves order_product, changes stock of product, end of convo
    '''

    global context_phone
    global context_size
    global context_color
    global context_quantity
    global context_prod

    DATABASE_PATH = 'orders.db'  # Update with the correct path to your database file

    # NO need to send global variables
    async def insert_order(order_id, phone, status, context_product, context_quantity, context_color,
                           context_size):
        try:
            # Connect to the database
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # Insert the order information into the 'orders' table
            cursor.execute('''
                INSERT INTO orders (order_number, order_date, order_time, phone_number, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, datetime.datetime.now().date(), datetime.datetime.now().strftime('%H:%M'), phone, status))

            cursor.execute('''
                            INSERT INTO order_products (order_number, product_id, quantity, color, size)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (order_id, context_product, context_quantity, context_color, context_size))

            cursor.execute('''
                        UPDATE products
                        SET stock = stock - ?
                        WHERE product_id = ?
                    ''', (context_quantity, context_product))

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
        await insert_order(order_id, context_phone, "Initiated", context_prod, context_quantity, context_color,
                           context_size)

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
        raise HTTPException(status_code=500, detail="Internal Server Error")  # ##


async def change_order(intent_name, parameters):
    try:
        order_id = parameters.get('number')
        logger.info(f"Received Intent: {intent_name}")
        logger.info(f"Received Parameters: {parameters}")
        logger.info(f"Order ID: {order_id}")

        if not order_id:
            raise ValueError("Order ID not provided")

        # Retrieve order details from the database
        order_details = get_order_details(int(order_id))

        if not order_details:
            raise ValueError(f"Order with ID {order_id} not found")
        context_id = order_id

        # Construct the fulfillment message with product information
        elements = [
            {
                "title": f"Order ID {int(order_id)} : {order_details[0][4]}",
                # Index 4 corresponds to the status in the tuple
                "subtitle": f"{order_details[0][1]}",
            }
        ]

        for product in order_details:
            elements.append({
                "title": f"{product[6]} - Quantity: {product[5]}",  # Adjust indices based on your tuple structure
                "subtitle": f"Price: {product[8]}, Size: {product[-1]}, Colors: {product[-2]}",
            })

        for product in order_details:
            logger.info(product[2])
            prod = product[2]

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
                },
                {
                    "quickReplies": {
                        "title": "What would you like to do ?",
                        "quickReplies": [
                            f"Delete Order:{order_id}",
                            f"Change Details:{prod}",
                            "Change Phone Number"
                        ]
                    },
                    "platform": "FACEBOOK"
                }
            ]
        }

        # Log the response
        logger.info(f"Generated Response: {fulfillment_message}")

        # Return fulfillment message
        return JSONResponse(content=fulfillment_message)

    except ValueError as ve:
        # Handle specific data errors
        logger.error(f"ValueError in handle_order_track: {str(ve)}", exc_info=True)
        raise HTTPException(status_code=404, detail=f"Order not found: {str(ve)}")

    except sqlite3.Error as e:
        # Handle database-related errors
        logger.error(f"Error in handle_order_track: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        # Log the unexpected exception
        logger.error(f"Unexpected error in handle_order_track: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def delete_order(intent_name, parameters):
    pass
@app.post("/")
async def handle_request(request: Request, payload: Payload):
    '''
    :param request: request obj (not used)
    :param payload: payload
    :return: runs function based on intent
    '''

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
        elif intent_name == "order.change - custom":
            return await change_order(intent_name, parameters)
        elif intent_name == "order.change - custom - delete":
            return await delete_order(intent_name, parameters)

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
