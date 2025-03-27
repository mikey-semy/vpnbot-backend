from app.routes.base import BaseRouter



class APIv1(BaseRouter):
    def configure_routes(self):
        self.router.include_router(AuthRouter().get_router())
