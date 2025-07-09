from fastapi import HTTPException
from fast_api import FastAPI
from model import Product
from db import collection
from bson import ObjectId

app=FastAPI()

#add new product

@app.post("/products")
async def add_product(product:Product):
    product_dict=product.model_dump()                  # Convert Pydantic model to dictionary
    result = await collection.insert_one(product_dict) # Insert the product into the database
    product_dict["_id"]=str(result.inserted_id)        # Convert ObjectId to string
    return product_dict                                 # Return the product with its ID

# Get all products

@app.get("/products")
async def get_all_products():
    product=[]                                          # Initialize an empty list to store products
    curser=collection.find()                            # Find all products in the collection
    async for document in curser:                       # Iterate through each document in the cursor
        document["id"]=str(document["_id"])             # Convert ObjectId to string and add to document
        product.append(document)                        # Append each product to the list
    return product                                      # Return the list of products

#Get product by ID

@app.get("/products/{product_id}")                    
async def get_product_by_id(product_id:str):
    try:
        obj_id = ObjectId(product_id)                                               # Convert product_id to ObjectId
    except:
        raise HTTPException(status_code=400, detail = "Invalid product ID format")  # Raise error if conversion fails 
    product = await collection.find_one({"_id":obj_id})                             # Find product by ObjectId
    if product:                                                                     # If product is found
        product["_id"]=str(product["_id"])                                          # Convert ObjectId to string
        return product
    else:
        raise HTTPException(status_code = 404, detail="product not found")      # Raise error if product not found
  
# Delete product by ID
 
@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    try:
        obj_id =ObjectId(product_id)  
    except:
        raise HTTPException(status_code = 400, detail= "Invalid product ID format")
    result = await collection.delete_one({"_id":obj_id})                                 # Delete product by ObjectId
    if result.deleted_count ==  1:                                                       # Check if a product was deleted
        return {"message": "product deleted successfully"}
    else:
        raise HTTPException(status_code = 404, detail= "product not found")               # Raise error if product not found

# Update product by ID

@app.put("/products/{product_id}")
async def update_product(product_id: str, update_data: Product):
   
    data = update_data.model_dump(exclude_none=True)                                   # Convert Pydantic model to dictionary, excluding None values

    if not data:
        raise HTTPException(status_code=400, detail="Nothing to update.")

    result = await collection.update_one({"_id": ObjectId(product_id)},{"$set": data})  # Update product by ObjectId with new data

    if result.matched_count == 0:                                                         # Check if a product was found to update
        raise HTTPException(status_code=404, detail="Product not found.")

    return {"message": "Updated successfully"}
