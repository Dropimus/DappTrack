from typing import Callable, Any
import flet as ft
from enum import Enum
from user_controls.app_bar import AppBar


class DataStrategyEnum(Enum):
    QUERY = 0
    ROUTER_DATA = 1
    CLIENT_STORAGE = 2
    STATE = 3

# class Router:
#     def __init__(self, page, data_strategy=DataStrategyEnum.QUERY):
#         self.data_strategy = data_strategy
#         self.data = dict()
#         self.routes = {}
#         self.body = ft.Container()
#         self.navigation_stack = ['/']
#         self.page = page

#     def set_route(self, stub: str, view: Callable):
#         self.routes[stub] = view
    
#     def set_routes(self, route_dictionary: dict):
#         """Sets multiple routes at once. Ex: {"/": IndexView }"""
#         self.routes.update(route_dictionary)

#     def route_change(self, route):

#         _page = route.route.split("?")[0]
#         queries = route.route.split("?")[1:]
#         if not self.navigation_stack or self.navigation_stack[-1] != _page:
#             if len(self.navigation_stack) > 5:
#                 self.navigation_stack.pop(0)
#             self.navigation_stack.append(_page)
#         # if _page not in self.navigation_stack:
#         #     self.navigation_stack.append(_page)

        
#             print(f"Appended {_page} to navigation stack")
#         else:
#             print(f"Route {_page} already exists in navigation stack, not appending.")

        
#         print(f"Current navigation stack: {self.navigation_stack}") 

#         print(_page)
#         for item in queries:
#             key = item.split("=")[0]
#             value = item.split("=")[1]
#             self.data[key] = value.replace('+', ' ')

#         self.body.content = self.routes[_page](self)
#         self.body.update()

#     def set_data(self, key, value):
#         self.data[key] = value

#     def get_data(self, key):
#         return self.data.get(key)

#     def get_query(self, key):
#         return self.data.get(key)



class Router:
    def __init__(self, page, data_strategy=None):
        self.data_strategy = data_strategy
        self.data = dict()
        self.routes = {}
        self.page = page
        self.body = ft.Container()
        self.page.bottom_appbar = AppBar(self.page)  # Main container for navigation
        # self.page_view = page.views  # Manage views for back navigation
        self.page.on_view_pop = self.view_pop 
        # self.update_icon = update_icon(page=self.page, clicked_icon='/')
        
        
    def set_route(self, stub: str, view: Callable):
        self.routes[stub] = view

    def set_routes(self, route_dictionary: dict):
        """Sets multiple routes at once. Ex: {"/": IndexView }"""
        self.routes.update(route_dictionary)


    def route_change(self, route):
        # Extract route and query parameters
        _page = route.route.split("?")[0]
        print(f'the page {_page}')
        queries = route.route.split("?")[1:]
        self.data = {item.split("=")[0]: item.split("=")[1].replace('+', ' ') for item in queries}


        # Manage page views for back navigation
        if not self.page.views or self.page.views[-1].route != _page:
            self.page.views.append(
                ft.View(
                    _page,
                    controls=[self.routes[_page](self)],
                )
            )

        # Update the body only if the content has changed
        # self.body.content = self.page_view
        self.page.update()

    def view_pop(self, view):
        """Handles the view pop event."""
        if len(self.page.views) > 1:
            # Pop the current view and navigate to the previous one
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.go(top_view.route)
        else:
            print("No views left to pop!")

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data.get(key)

    def get_query(self, key):
        return self.data.get(key)

    def go_back(self):
        """Programmatically triggers the view_pop functionality."""
        if len(self.page.views) > 1:
            self.view_pop(self.page.views[-1])
        else:
            print("No previous views to go back to!")

  