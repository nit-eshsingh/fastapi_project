import uvicorn
from fastapi import FastAPI, HTTPException, Response, Request
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize FastAPI app
app = FastAPI()

#  127.0.0.1:5432
# "user: postgres, localhost : 5432 , newpassword"
# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="Players",
    user="postgres",
    password="newpassword",
    host="localhost",
    port="5432"
)

@app.get("/api/orders/{order_id}", response_class=Response)
async def get_order(order_id: int):
    """
    Fetch order details by order ID and return XML.
    """
    try:
        cursor = conn.cursor()
        query = "SELECT order_data::TEXT FROM orders WHERE id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()

        if result:
            return Response(content=result[0], media_type="application/xml")
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orders", response_class=Response)
async def create_order(request: Request):
    """
    Accept an XML payload and create a new order.
    """
    try: # response.xsd
        order_xml = await request.body()  # Get raw XML data
        cursor = conn.cursor()
        query = "INSERT INTO orders (order_data) VALUES (%s) RETURNING id"
        cursor.execute(query, (order_xml.decode('utf-8'),))
        conn.commit()
        new_order_id = cursor.fetchone()[0]

        return Response(
            content=f"<success>Order created with ID {new_order_id}</success>",
            media_type="application/xml",
            status_code=201
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders", response_class=Response)
async def list_orders():
    """
    List all orders in XML format.
    """
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = "SELECT id, order_data::TEXT AS order_xml FROM orders"
        cursor.execute(query)
        results = cursor.fetchall()

        # Generate an XML response containing all orders
        response_xml = "<orders>"
        for row in results:
            response_xml += f"<order id='{row['id']}'>{row['order_xml']}</order>"
        response_xml += "</orders>"

        return Response(content=response_xml, media_type="application/xml") # text, bytes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app:app")