import flet as ft

def main(page: ft.Page):
    page.title = "Routes Example"

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Flet app"), bgcolor=ft.Colors.RED_200),
                    
                    ft.Container(
                            bgcolor='yellow',
                            content=ft.ElevatedButton("Visit Store", on_click=lambda _: page.go("/store")),
                        ),
                ],
            )
        )
        if page.route == "/store":
            page.views.append(
                ft.View(
                    "/store",
                    [
                        ft.AppBar(title=ft.Text("Store"), bgcolor=ft.Colors.BLUE_200),
                        ft.Container(
                            bgcolor='yellow',
                            content=ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                        ),
                        
                    ],
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    page.theme = ft.Theme(
            page_transitions=ft.PageTransitionsTheme(
                android=ft.PageTransitionTheme.NONE,
                ios=ft.PageTransitionTheme.NONE,
                macos=ft.PageTransitionTheme.NONE,
                linux=ft.PageTransitionTheme.NONE,
                windows=ft.PageTransitionTheme.OPEN_UPWARDS
            )
        )

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(target=main)