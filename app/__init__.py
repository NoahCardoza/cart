from fastapi import FastAPI

from app.bootstrap import cors, exceptions
from app.routes.authentication import auth_router
from app.routes.cart import cart_router
from app.routes.category import category_router
from app.routes.product import product_router
from app.routes.search import search_router
from app.routes.user import user_router

app = FastAPI()
app.include_router(cart_router, prefix="/cart", tags=["cart"])
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(category_router, prefix="/category", tags=["category"])
app.include_router(product_router,prefix="/product", tags=["product"] )

cors.setup_cors(app)
exceptions.setup_exception_handlers(app)
