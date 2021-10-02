from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from database import Session, engine
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from decorators import validate_auth

order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

session = Session(bind=engine)


@order_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    """
        ## A sample hello world route
        This returns Hello World
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token'
        )
    return {"message": "Hello World"}


@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Placing an order
        This requires the following
        - quantity: integer
        - pizza_size: str
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token'
        )
    
    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username==current_user).first()

    new_order = Order(
        quantity=order.quantity,
        pizza_size=order.pizza_size
    )

    new_order.user = user
    session.add(new_order)
    session.commit()

    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }

    return jsonable_encoder(response)


@order_router.get('/orders')
async def list_all_orders(Authorize:AuthJWT=Depends()):
    """
        ## List all orders
        This lists all orders made. In can be accessed by superusers
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username==current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()#filter(user_id=user.id)

        return jsonable_encoder(orders)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You're not a superuser")


@order_router.get('/get_order_by_id/{id}')
async def get_order_by_id(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Get an order by its ID
        This gets an order by its ID and is only accessed by Superuser
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username==user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id==id).first()

        return jsonable_encoder(order)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not allowed carry out request")


@order_router.get('/user/orders')
# @validate_auth
async def get_user_orders(Authorize:AuthJWT=Depends()):
    """
        ## Get a current user's orders
        This lists the orders made by the currently logged in users
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username==user).first()

    return jsonable_encoder(current_user.orders)


@order_router.get('/user/order/{id}')
async def get_specific_order(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Get a specific order by the currently logged in user
        This return an order by ID for the currently logged in user
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    subject = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username==subject).first()

    orders = current_user.orders

    for o in orders:
        if o.id == id:
            # import pdb; pdb.set_trace()
            return jsonable_encoder(o)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No order with such id")


@order_router.put('/order/update/{id}')
async def update_order(id:int, order:OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Updating an order
        This updates an order and requires the following fields
        - quantity: integer
        - pizza_size: str
    """
    try: 
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    order_to_update = session.query(Order).filter(Order.id==id).first()
    
    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size
    
    session.commit()

    return jsonable_encoder(order_to_update)


@order_router.patch('/order/update/{id}')
async def update_order_status(id:int,order:OrderStatusModel, Authorize:AuthJWT=Depends()):
    """
        ## Update an order's status
        This is for updating an order's status and requires ` order_status ` in string format
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    username = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username==username).first()

    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id==id).first()

        order_to_update.order_status = order.order_status

        session.commit()

        response = {
            'id': order_to_update.id,
            'quantity': order_to_update.quantity,
            'pizza_size': order_to_update.pizza_size,
            'order_status': order_to_update.order_status,
        }

        return jsonable_encoder(response)


@order_router.delete('/order/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_an_order(id: int, Authorize:AuthJWT=Depends()):
    """
        ## Delete an Order
        This deletes an order by its ID
    """

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    order_to_delete = session.query(Order).filter(Order.id==id).first()

    session.delete(order_to_delete)
    session.commit()

    return order_to_delete


