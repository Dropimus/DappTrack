from flet import *
import time
import threading
import asyncio
from time import sleep
from auth import get_referrals, track_airdrop_by_id, set_timer
from io import BytesIO
from datetime import datetime

native_color = '#161C2D'
BG = "#FEFCFF"
FWG = "#97b4ff"
FG = "#3450a1"
PINK = "#eb06ff"
FONT_SIZE = 15
HOME_PAGE_BG_COLOR = "#FEFCFF"
TOP_ICON_COLOR = "#F8F8F8"
APP_FONT = "montserrat"
APP_FONT_SBOLD = "montserrat-semi-bold"
APP_FONT_BOLD = "montserrat-bold"
POPPINS_BOLD = "poppins-bold"


class BuildPage:
    def __init__(self, page: Page, page_content):
        self.page_content = page_content
        self.page = page
        self.loading_indicator = None
        self.is_shimmering = True
        # self.page.horizontal_alignment = CrossAxisAlignment.CENTER
        # self.page.vertical_alignment = MainAxisAlignment.CENTER
        self.page.fonts = {
            "montserrat": "fonts/Montserrat-VariableFont_wght.ttf",
            "montserrat-bold": "fonts/Montserrat-Bold.ttf",
            "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",
            "poppins-bold": "fonts/Poppins-Bold.ttf",
        }

        self.base = Container(
            # border_radius=35,
            bgcolor="white",
            height=self.page.height * 10,
            padding=padding.only(left=10, right=10, top=50),
            content=self.page_content,
        )
        self.loading_indicator = None

        self.page.theme = Theme(
            page_transitions=PageTransitionsTheme(
                android=PageTransitionTheme.NONE,
                ios=PageTransitionTheme.NONE,
                macos=PageTransitionTheme.NONE,
                linux=PageTransitionTheme.NONE,
                windows=PageTransitionTheme.NONE,
            )
        )

    # Animation methods added to the parent class
    # for profile

    def shrink(self, e):
        if self.home_:
            self.home_.content.controls[0].width = 120
            self.home_.content.controls[0].scale = transform.Scale(
                0.8, alignment=alignment.center_right
            )

            self.page.update()

    def restore(self, e):
        if self.home_:
            self.home_.content.controls[0].width = 400
            self.home_.content.controls[0].scale = transform.Scale(
                1, alignment=alignment.center_right
            )
            self.page.update()

    def toggle_dropdown(self, e):
        self.dropdown_content.content.visible = (
            not self.dropdown_content.content.visible
        )
        self.dropdown_content.update()

    def shimmer_animation(self, skeleton_card):

        while self.is_shimmering:
            # if skeleton_card.content != self.create_track_skeleton():
            for control in skeleton_card.content.controls:
                control.opacity = 0.2 if control.opacity == 0.3 else 0.3
            self.page.update()
            sleep(0.5)

    def stop_shimmer(self):
        self.is_shimmering = False

    def on_skeleton_update(self):  # pass into the page instance
        self.stop_shimmer()

    async def show_success_message(self, message):
        success_message = AlertDialog(
            content=Text(f"{message}"),
            actions_alignment=MainAxisAlignment.END,
        )
        self.page.open(success_message)
        self.page.update()

        async def auto_close():
            await asyncio.sleep(1)
            self.page.close(success_message)
            self.page.update()

        asyncio.create_task(auto_close())

    def show_loading_indicator(self):
        if self.loading_indicator is None:
            self.loading_indicator = Column(
                controls=[
                    Container(
                        content=CupertinoActivityIndicator(
                            radius=20, color='black', animating=True),
                        alignment=alignment.center
                    )
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER
            )
            self.page_content.controls.append(self.loading_indicator)
            self.page.update()

    def hide_loading_indicator(self):
        if self.loading_indicator is not None:
            self.page_content.controls.remove(self.loading_indicator)
            self.loading_indicator = None
            self.page.update()


class LandingPage(BuildPage):
    def __init__(self, page: Page):
        self.page = page
        self.page_content = Container(
            height=self.page.height,
            bgcolor='#161C2D',
            content=Column(
                controls=[
                    Stack(
                        controls=[
                            Column(
                                controls=[
                                    Text('DropDash', color='blue'),
                                    Text('Stay Ahead', color='white')
                                ]
                            ),
                            Container(
                                content=Image(
                                    src='utils/landing-bubble.svg'
                                )
                            )
                        ]
                    ),
                ]
            )
        )

        super().__init__(page, self.page_content)


class SignupPage(BuildPage):
    def __init__(self, page: Page, signup_user, on_success_callback, login_page_url):
        self.page = page

        self.fullname_label = "Full Name"
        self.email_label = "Email"
        self.username_label = "Username"
        self.password_label = "Password"
        self.confirm_password_label = "Confirm Password"

        self.signup_user = signup_user
        self.on_success_callback = on_success_callback
        self.login_page_url = login_page_url
        self.loading_indicator = None
        self.success_message = None
        self.password_visible = False
        self.fullname_field = TextField(
            label="Full Name",
            border=InputBorder.NONE,
            content_padding=padding.all(14),
            bgcolor="#F8F8F8",
            width=300,
            color="black",
        )
        # self.fullname_field.on_change = lambda e: self.hide_label(
        #     e, self.fullname_field, self.fullname_label
        # )

        self.username_field = TextField(
            label="Username",
            width=300,
            border=InputBorder.NONE,
            bgcolor="#F8F8F8",
            color="black",
        )
        # self.username_field.on_change = lambda e: self.hide_label(
        #     e, self.username_field, self.username_label
        # )

        self.email_field = TextField(
            label="Email",
            width=300,
            border=InputBorder.NONE,
            bgcolor="#F8F8F8",
            color="black",
        )

        self.referral_field = TextField(
            label="Referral Code",
            width=300,
            border=InputBorder.NONE,
            bgcolor="#F8F8F8",
            color="black",
        )
        # self.email_field.on_change = lambda e: self.hide_label(
        #     e, self.email_field, self.email_label
        # )

        self.password_field = TextField(
            label="Password",
            password=True,
            border=InputBorder.NONE,
            bgcolor="#F8F8F8",
            width=300,
            color="black",
        )
        # self.password_field.on_change = lambda e: self.hide_label(
        #     e, self.password_field, self.password_label
        # )

        self.toggle_password_button = IconButton(
            icon=Icons.VISIBILITY_OFF, on_click=self.toggle_password_visibility
        )

        self.confirm_password_field = TextField(
            label="Confirm Password",
            password=True,
            border=InputBorder.NONE,
            bgcolor="#F8F8F8",
            width=300,
            color="black",
        )
        # self.confirm_password_field.on_change = lambda e: self.hide_label(
        #     e, self.confirm_password_field, self.confirm_password_field
        # )

        self.toggle_confirm_password_button = IconButton(
            icon=Icons.VISIBILITY_OFF,
            on_click=self.toggle_confirm_password_visibility,
        )

        self.signup_button = Container(
            content=Image(src="utils/sign_up.svg"), on_click=self.on_signup_click
        )

        # self.loading_indicator = Container(visible=False)

        self.page_content = Stack(
            controls=[
                Container(
            height=self.page.window.height,
            content=Stack(
                controls=[
                    Container(
                        top=-32,
                        content=Column(
                        controls=[
                            Row(
                                alignment="spaceBetween",
                                controls=[
                                    Column(
                                        controls=[
                                            Container(
                                                content=Image(
                                                    src="utils/dropdash-logo.png"
                                                )
                                            ),
                                            Container(
                                                content=Text(
                                                    "Create\nAccount",
                                                    weight="bold",
                                                    size=45,
                                                    color='black',
                                                ),
                                                # left=0,
                                                # bottom=660,
                                            ),
                                        ]
                                    ),
                                    Container(
                                        padding=padding.only(left=50),
                                        content=Image(
                                            src="utils/bubble-card.svg",
                                            height=470,
                                        ),
                                    ),
                                ],
                            ),
                        ]
                    ),
                    ),
                    Container(
                        top=320,
                        left=30,
                        alignment=alignment.center_right,
                        content=Column(
                            controls=[
                                    # Container(height=80),
                            Container(border_radius=8, content=self.fullname_field),
                            Container(border_radius=8, content=self.username_field),
                            Container(border_radius=8, content=self.email_field),
                            Container(border_radius=8, content=self.referral_field),
                            Container(
                                border_radius=8,
                                content=Stack(
                                    [self.password_field, self.toggle_password_button],
                                    alignment=alignment.center_right,
                                ),
                            ),
                            Container(
                                border_radius=8,
                                content=Stack(
                                    [
                                        self.confirm_password_field,
                                        self.toggle_confirm_password_button,
                                    ],
                                    alignment=alignment.center_right,
                                ),
                            ),
                            ],
                            # alignment=MainAxisAlignment.CENTER,
                            # horizontal_alignment=CrossAxisAlignment.CENTER,
                        ),
                    ),
                    Container(
                        top=670,
                        left=20,
                        content=Column(
                            controls=[
                                Container(height=10),
                                self.signup_button,
                                Row(
                                    controls=[
                                        Text(
                                        value="Already have an account? ", color="black"
                                    ),
                                    Container(
                                        on_click=self.login_page_url,
                                        content=Text(
                                            "Login",
                                            size=15,
                                            color='blue',
                                            style=TextStyle(
                                                decoration=TextDecoration.UNDERLINE
                                            ),
                                        ),
                                    ),
                                    ]
                                ),
                            ]
                        ),
                    ),
                
                ]
            ),
        )
            ]
        )

        self.page_con = Container(
            height=self.page.height,
            content=Stack(
                controls=[
                    Container(
                        padding=padding.only(
                            left=50,
                        ),
                        content=Text("Create\nAccount", weight="bold", size=40),
                        left=0,
                        bottom=660,
                    ),
                    Column(
                        controls=[
                            Container(height=80),
                            Container(border_radius=8, content=self.fullname_field),
                            Container(border_radius=8, content=self.username_field),
                            Container(border_radius=8, content=self.email_field),
                            Container(
                                border_radius=8,
                                content=Stack(
                                    [self.password_field, self.toggle_password_button],
                                    alignment=alignment.center_right,
                                ),
                            ),
                            Container(
                                border_radius=8,
                                content=Stack(
                                    [
                                        self.confirm_password_field,
                                        self.toggle_confirm_password_button,
                                    ],
                                    alignment=alignment.center_right,
                                ),
                            ),
                            Text("Or"),
                            Container(content=Image(src="utils/google_signup.svg")),
                            Container(height=10),
                            self.signup_button,
                            Row(
                                controls=[
                                    Text(
                                        value="Already have an account? ", color="black"
                                    ),
                                    Container(
                                        on_click=self.login_page_url,
                                        content=Text(
                                            "Login",
                                            size=15,
                                            style=TextStyle(
                                                decoration=TextDecoration.UNDERLINE
                                            ),
                                        ),
                                    ),
                                ]
                            ),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                    Container(
                        content=Image(
                            src="utils/bubble-card.svg",
                            height=450,
                        ),
                        right=0,
                    ),
                ],
                alignment=alignment.top_right,
            ),
        )
        super().__init__(page, self.page_content)

    def toggle_password_visibility(self, e):
        self.password_visible = not self.password_visible
        self.password_field.password = not self.password_visible
        self.toggle_password_button.icon = (
            Icons.VISIBILITY if self.password_visible else Icons.VISIBILITY_OFF
        )
        self.confirm_password_field.update()
        self.toggle_password_button.update()

    def toggle_confirm_password_visibility(self, e):
        self.password_visible = not self.password_visible
        self.confirm_password_field.password = not self.password_visible
        self.toggle_confirm_password_button.icon = (
            Icons.VISIBILITY if self.password_visible else Icons.VISIBILITY_OFF
        )
        self.confirm_password_field.update()
        self.toggle_confirm_password_button.update()

    async def handle_signup(self, e):
        self.show_loading_indicator()
        await asyncio.sleep(1)
        full_name = self.fullname_field.value
        username = self.username_field.value
        email = self.email_field.value
        referral_code = self.referral_field.value
        password = self.password_field.value
        confirm_password = self.confirm_password_field.value

        try:
            if (
                not full_name
                or not username
                or not email
                or not password
                or not confirm_password
            ):
                self.hide_loading_indicator()
                await self.show_success_message(
                    message="Please fill in all the fields!"
                )

            else:
                result = await self.signup_user(
                    full_name=full_name,
                    username=username,
                    email=email,
                    referral_code=referral_code,
                    password=password,
                    confirm_password=confirm_password,
                )
                print(f'This is the Signup result {result}')
                self.hide_loading_indicator()
                # self.output_text.value = result
                await self.show_success_message(message=result)

                if result == "Signup successful!, Please Login":
                    await asyncio.sleep(2)
                    self.on_success_callback()
        except Exception as ex:
            await self.show_success_message(message=str(ex))
        finally:
            self.page.update()

    async def on_signup_click(self, e):
        await self.handle_signup(e)


class LoginPage(BuildPage):
    def __init__(self, page: Page, login_user, on_success_callback, signup_page_url):
        self.page = page
        self.login_user = login_user
        self.signup_page_url = signup_page_url
        self.on_success_callback = on_success_callback
        self.username_label = "Username"
        self.password_label = "Password"
        self.password_visible = False

        self.username_field = TextField(
            label="Username",
            width=300,
            color="black",
            border=InputBorder.NONE,
            bgcolor="#F8F8F8",
        )
        # self.username_field.on_change = lambda e: self.hide_label(e, self.username_field, self.username_label)

        self.password_field = TextField(
            label="Password",
            password=True,
            width=300,
            color="black",
            border=InputBorder.NONE,
            bgcolor="#F8F8F8",
        )

        self.toggle_password_button = IconButton(
            icon=Icons.VISIBILITY_OFF, on_click=self.toggle_password_visibility
        )

        # self.password_field.on_change = lambda e: self.hide_label(e, self.password_field, self.password_label)

        self.remember_me = Checkbox(
            label="Remember Me",
            check_color="white",
            active_color="#161C2D",
            label_style=TextStyle(color="black"),
        )



        self.google_login_button = Container(
            Image(src="utils/google_login.svg"), on_hover=self.on_hover
        )
        self.login_button = Container(
            Image(src="utils/login.svg"),
            on_click=self.on_login_click,
        )

        self.page_content = Stack(
            controls=[
                Container(
            height=self.page.window.height,
            content=Stack(
                controls=[
                    Container(
                        top=-32,
                        content=Column(
                        controls=[
                            Row(
                                alignment="spaceBetween",
                                controls=[
                                    Column(
                                        controls=[
                                            Container(
                                                content=Image(
                                                    src="utils/dropdash-logo.png"
                                                )
                                            ),
                                            Container(
                                                content=Text(
                                                    "Log In",
                                                    weight="bold",
                                                    color="black",
                                                    size=50,
                                                ),
                                                # left=0,
                                                # bottom=670,
                                            ),
                                            Container(
                                                content=Text(
                                                    "Welcome back",
                                                    color="#004CFF",
                                                    size=22,
                                                    weight="bold",
                                                    font_family=APP_FONT,
                                                ),
                                            ),
                                        ]
                                    ),
                                    Container(
                                        padding=padding.only(left=50),
                                        content=Image(
                                            src="utils/bubble-card.svg",
                                            height=470,
                                        ),
                                    ),
                                ],
                            ),
                        ]
                    ),
                    ),
                    Container(
                        top=320,
                        left=30,
                        alignment=alignment.center_right,
                        content=Column(
                            controls=[
                                Container(border_radius=8, content=self.username_field),
                                Container(
                                    border_radius=8,
                                    content=Stack(
                                        [
                                            self.password_field,
                                            self.toggle_password_button,
                                        ],
                                        alignment=alignment.center_right,
                                    ),
                                ),
                                self.remember_me,
                                # Text("Or"),
                                self.google_login_button,
                                Container(height=10),
                            ],
                            # alignment=MainAxisAlignment.CENTER,
                            # horizontal_alignment=CrossAxisAlignment.CENTER,
                        ),
                    ),
                    Container(
                        top=525,
                        left=20,
                        content=Column(
                            controls=[
                                self.login_button,
                                Row(
                                    controls=[
                                        Text(
                                            value="Don't have an account?",
                                            color="black",
                                        ),
                                        Container(
                                            on_click=self.signup_page_url,
                                            content=Text(
                                                "Sign Up",
                                                size=15,
                                                font_family=APP_FONT_SBOLD,
                                                color="blue",
                                                style=TextStyle(
                                                    decoration=TextDecoration.UNDERLINE,
                                                ),
                                            ),
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ),
                ]
            ),
        )
            ]
        )

        # self.page_contentd = Container(
        #     height=self.page.window.height,
        #     content=Stack(
        #         controls=[
        #             Container(
        #                 padding=padding.only(
        #                     # left=20,
        #                 ),
        #                 content=Text("Log In", weight="bold", size=50, color="black"),
        #                 # left=0,
        #                 # bottom=670,
        #             ),
        #             Container(
        #                 padding=padding.only(
        #                     # left=20,
        #                 ),
        #                 content=Text(
        #                     "Welcome back", color="blue", size=22, font_family=APP_FONT
        #                 ),
        #                 # left=0,
        #                 # bottom=650,
        #             ),
        #             Column(
        #                 controls=[
        #                     Container(border_radius=8, content=self.username_field),
        #                     Container(
        #                         border_radius=8,
        #                         content=Stack(
        #                             [self.password_field, self.toggle_password_button],
        #                             alignment=alignment.center_right,
        #                         ),
        #                     ),
        #                     self.remember_me,
        #                     Text("Or"),
        #                     self.google_login_button,
        #                     Container(height=10),
        #                     self.login_button,
        #                     Row(
        #                         controls=[
        #                             Text(value="Don't have an account?", color="black"),
        #                             Container(
        #                                 on_click=self.signup_page_url,
        #                                 content=Text(
        #                                     "Sign Up",
        #                                     size=15,
        #                                     style=TextStyle(
        #                                         decoration=TextDecoration.UNDERLINE
        #                                     ),
        #                                 ),
        #                             ),
        #                         ]
        #                     ),
        #                 ],
        #                 # alignment=MainAxisAlignment.CENTER,
        #                 # horizontal_alignment=CrossAxisAlignment.CENTER,
        #             ),
        #             Container(
        #                 content=Image(
        #                     src="utils/bubble-card.svg",
        #                     height=450,
        #                 ),
        #                 right=0,
        #             ),
        #         ],
        #         alignment=alignment.top_right,
        #     ),
        # )
        super().__init__(page, self.page_content)

    def on_hover(self, e):
        self.google_login_button.bgcolor = "#ECEFF1" if e.data == "true" else None
        self.google_login_button.update()

    def toggle_password_visibility(self, e):
        self.password_visible = not self.password_visible
        self.password_field.password = not self.password_visible
        self.toggle_password_button.icon = (
            Icons.VISIBILITY if self.password_visible else Icons.VISIBILITY_OFF
        )
        self.password_field.update()
        self.toggle_password_button.update()

    async def handle_login(self, e):
        self.show_loading_indicator()
        await asyncio.sleep(1)

        username = self.username_field.value.lower() 
        password = self.password_field.value
        remember_me = self.remember_me.value

        try:
            if not username or not password:
                self.hide_loading_indicator()
                await self.show_success_message(
                    message="Please fill in all the fields!"
                )
            else:
                result = await self.login_user(
                    username=username, password=password, remember_me=remember_me
                )

                self.hide_loading_indicator()
                await self.show_success_message(message=result)

                if result == "Login successful!":
                    await asyncio.sleep(2)
                    await self.on_success_callback()
        except Exception as ex:
            await self.show_success_message(message=str(ex))

        finally:
            self.page.update()

    async def on_login_click(self, e):
        await self.handle_login(e)


class HomePage(BuildPage):
    def __init__(
        self,
        page: Page,
        user_json,
        upcoming_airdrops,
        goto_all_airdrops,
        goto_track,
        home_skeleton,
        # on_skeleton_update,
        trending_airdrops,
        top_menu_icons,
        airdrop_activity_overview,
        mining_airdrops,
        testnet_airdrops,
        # logout_user,
        goto_airdrop_upload,
    ):  # on_success_callback, add these later
        self.page = page
        self.user_json = user_json
        self.airdrop_activity_overview = airdrop_activity_overview
        self.goto_all_airdrops = goto_all_airdrops
        # self.logout_user = logout_user
        self.on_success_callback = "pass the func here"  # on_success_callback
        self.home_skeleton = home_skeleton

        self.total_airdrops = 213
        self.goto_airdrop_upload = goto_airdrop_upload
        self.trending_airdrops = trending_airdrops
        self.upcoming_airdrops = upcoming_airdrops
        self.top_menu_icons = top_menu_icons
        self.goto_track = goto_track
        self.mining_airdrops = mining_airdrops
        self.testnet_airdrops = testnet_airdrops

        self.page.theme = Theme(
            scrollbar_theme=ScrollbarTheme(
                track_color={
                    ControlState.HOVERED: Colors.TRANSPARENT,
                    ControlState.DEFAULT: Colors.TRANSPARENT,
                },
                track_visibility=False,  # Hide the track
                track_border_color=Colors.TRANSPARENT,
                thumb_visibility=False,  # Hide the thumb
                thumb_color={
                    ControlState.HOVERED: Colors.TRANSPARENT,
                    ControlState.DEFAULT: Colors.TRANSPARENT,
                },
                thickness=0,  # Set thickness to 0
                radius=0,  # Set radius to 0
                main_axis_margin=0,
                cross_axis_margin=0,
            )
        )

        self.main_content = Container(
            expand=True,
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Column(
                        height=850,
                        scroll="auto",
                        controls=[
                            Container(height=20),
                            Container(
                                bgcolor="#F8F8F8",
                                width=1500,
                                padding=7,
                                border_radius=10,
                                content=Row(
                                    controls=[
                                        Column(
                                            [
                                                Text(
                                                    "Announcement",
                                                    weight="bold",
                                                    color="black",
                                                    font_family=APP_FONT_SBOLD,
                                                    size=16,
                                                ),
                                                Text(
                                                    "Loro ipsum sffis sfisfihsf sfsjjjjjihihi hjjjjjjjjjjjf. \n sdhishfishfisifisfshis",
                                                    color="black",
                                                    weight="bold",
                                                    font_family=APP_FONT,
                                                ),
                                            ],
                                        ),
                                        Container(
                                            margin=margin.only(top=30),
                                            content=Image(
                                                src="icons/right-arrow-button.svg",
                                                width=20,
                                                height=20,
                                            ),
                                            bgcolor="black",
                                            padding=padding.all(9),
                                            width=37,
                                            height=37,
                                            border_radius=20,
                                            alignment=alignment.bottom_left,
                                        ),
                                    ],
                                    alignment="spaceBetween",
                                ),
                            ),
                            Container(height=10),
                            Column(
                                controls=[
                                    Text(
                                        "Trending Airdrops",
                                        color="black",
                                        size=22,
                                        font_family=APP_FONT_BOLD,
                                    ),
                                    self.trending_airdrops,
                                ]
                            ),
                            Container(height=20),
                            # Label to display progress
                            Row(
                                alignment="spaceBetween",
                                controls=[
                                    Text(
                                        "My Airdrops",
                                        size=22,
                                        font_family=APP_FONT_BOLD,
                                        weight="bold",
                                        color="black",
                                        text_align="center",
                                    ),
                                ],
                            ),
                            Container(
                                on_click=self.goto_track,
                                content=self.airdrop_activity_overview,
                            ),
                            Container(height=10),
                            Row(
                                alignment="spaceBetween",
                                controls=[
                                    Text(
                                        "Airdrop Categories",
                                        size=24,
                                        weight="bold",
                                        color="black",
                                        text_align="center",
                                    ),
                                    Container(
                                        # See All button
                                        on_click=self.goto_all_airdrops,
                                        content=Image(src="utils/see-all.svg"),
                                    ),
                                ],
                            ),
                            Container(
                                alignment=alignment.center,
                                content=Column(
                                    controls=[
                                        Container(
                                            content=Text(
                                                "Mining",
                                                color="black",
                                                font_family=APP_FONT,
                                                weight="bold",
                                                size=20,
                                            )
                                        ),
                                        self.mining_airdrops,
                                        Container(
                                            content=Text(
                                                "Testnet",
                                                color="black",
                                                font_family=APP_FONT,
                                                weight="bold",
                                                size=20,
                                            )
                                        ),
                                        self.testnet_airdrops,
                                    ]
                                ),
                            ),
                            Container(height=10),
                            Container(
                                content=Text(
                                    "Upcoming Airdrops",
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                    size=22,
                                )
                            ),
                            self.upcoming_airdrops,
                            Container(height=150),
                        ],
                    ),
                ]
            ),
        )
        self.page_content = Container(content=self.main_content)  # self.home_skeleton

        super().__init__(page, self.page_content)
        # self.page.run_task(self.update_skeleton)

    async def update_skeleton(self):
        await asyncio.sleep(1.8)
        self.on_skeleton_update()

        # Update the skeleton content
        self.trending_airdrop_skeleton.content = self.trending_airdrops

        # Refresh the page UI
        self.page.update()

    # def update_skeleton(self):
    #     self.on_skeleton_update()

    #     # Update the skeleton content
    #     self.page_content.content = self.main_content

    #     # Refresh the page UI
    #     self.page.update()

    def drop_down(self, e):
        if self.search_airdrop.height != 590 * 0.85:
            self.search_airdrop.height = 590 * 0.85
            self.page.update()
        else:
            self.search_airdrop.height = 0
            self.page.update()

    async def handle_logout(self, e):
        self.show_loading_indicator()
        await asyncio.sleep(1)
        try:
            result = await self.logout_user()
            self.hide_loading_indicator()
            await self.show_success_message(message=result)
            if result == "Logout successful":
                await asyncio.sleep(2)
                self.on_success_callback()
        except Exception as ex:
            await self.show_success_message(message=str(ex))

    async def on_logout_click(self, e):
        await self.handle_logout(e)


# Airdrop Tracker
class AnalyticPage(BuildPage):
    def __init__(
        self,
        page: Page,
        tracked_airdrops,
        on_skeleton_update,
        drop_down_menu,
        top_menu_icons,
        activity_circle,
        track_skeleton,
        active_url,
        pending_url,
        completed_url,
    ):
        self.page = page
        self.activity_circle = activity_circle
        self.tracked_airdrops = (
            tracked_airdrops  # tracked airdrop data sent without initialization
        )
        self.drop_down_menu = drop_down_menu
        self.top_menu_icons = top_menu_icons
        self.track_skeleton = track_skeleton
        # self.on_skeleton_update = on_skeleton_update
        self.active_url = active_url
        self.pending_url = pending_url
        self.completed_url = completed_url

        self.user_airdrop_data = Container(expand=True, content=self.track_skeleton)

        # self.menu_names = [
        #     Text('Active', font_family=APP_FONT, color='black'),
        #     'Completed',
        #     'Ended'
        # ]

        self.menu_names = Column(
            controls=[
                Container(
                    on_click=self.active_url,
                    content=Text(
                        "Active", size=16, font_family=APP_FONT_SBOLD, color="black"
                    ),
                ),
                Container(height=5),
                Container(
                    on_click=self.completed_url,
                    content=Text(
                        "Completed", size=16, font_family=APP_FONT_SBOLD, color="black"
                    ),
                ),
                Container(height=5),
                Container(
                    on_click=self.pending_url,
                    content=Text(
                        "Pending Reward",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
            ]
        )

        self.dropdown_content = self.drop_down_menu(
            menu_names=self.menu_names, on_click=self.toggle_dropdown
        )

        self.page_content = Container(
            expand=True,
            bgcolor="white",
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Container(height=10),
                    Stack(
                        controls=[
                            Column(
                                height=700,
                                controls=[
                                    Row(
                                        alignment="spaceBetween",
                                        controls=[
                                            Container(
                                                # padding=padding.only(left=10),
                                                content=Text(
                                                    "Airdrop Tracker",
                                                    color="black",
                                                    font_family=APP_FONT_SBOLD,
                                                    size=22,
                                                )
                                            ),
                                            Container(
                                                padding=padding.only(right=5),
                                                content=Image(
                                                    src="icons/drop-down.svg"
                                                ),
                                                on_click=self.toggle_dropdown,
                                            ),
                                        ],
                                    ),
                                    self.user_airdrop_data,
                                    # Container(height=10)
                                ],
                            ),
                            Container(
                                alignment=alignment.center_right,
                                content=self.dropdown_content,
                            ),
                        ],
                    ),
                ]
            ),
        )
        # asyncio.create_task(self.update_skeleton_periodically())

        super().__init__(page, self.page_content)
        self.page.run_task(self.update_skeleton)

    # async def update_skeleton(self):
    #     await asyncio.sleep(1.8)
    #     self.on_skeleton_update()

    #     # Update the skeleton content
    #     self.user_airdrop_data.controls.clear()
    #     self.user_airdrop_data.controls.append(await self.tracked_airdrops(50))

    #     # Refresh the page UI
    #     self.page.update()

    async def update_skeleton(self):
        await asyncio.sleep(1)
        self.on_skeleton_update()

        # Update the skeleton content
        self.user_airdrop_data.content = None
        self.user_airdrop_data.content = await self.tracked_airdrops()

        # Refresh the page UI
        self.page.update()


class RefferalsPage(BuildPage):
    def __init__(
        self,
        page: Page,
        user_json,
        top_menu_icons,
        referral_skeleton,
        on_skeleton_update,
    ):
        self.page = page
        self.referral_code = user_json.get('referral_code')
        self.top_menu_icons = top_menu_icons
        self.referral_skeleton = referral_skeleton
        self.on_skeleton_update = on_skeleton_update

        self.total_referrals = Container(
                                        content=Text(
                                            f"Loading...",
                                            color="black",
                                            font_family=APP_FONT_BOLD,
                                            size=15,
                                                )
                                        )

        # self.referral_code = "DQ345SST"

        self.on_text_copy = AlertDialog(
            title=Container(
                alignment=alignment.center,
                content=Text(
                    "Copied", font_family=APP_FONT_SBOLD, size=14, color="black"
                ),
            ),
            bgcolor="white",
            content=Container(content=Image(src="utils/check-mark.svg")),
            on_dismiss=lambda e: print("dismissed"),
        )

        self.page_content = Container(
            expand=True,
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Container(height=20),
                    Container(
                        content=Column(
                            height=700,
                            scroll="auto",
                            controls=[
                                Text(
                                    "Refer and Earn",
                                    color="black",
                                    font_family=APP_FONT_SBOLD,
                                ),
                                Text(
                                    "Invite your friends and earn Drop points for every signup\n using your referral code.",
                                    color="black",
                                    font_family=APP_FONT,
                                    weight="bold",
                                ),
                                Text(
                                    "You've Earned: 340 points",
                                    color="black",
                                    font_family=APP_FONT_SBOLD,
                                ),
                                Container(height=10),
                                Container(
                                    width=self.page.width * 10,
                                    height=250,
                                    border_radius=10,
                                    bgcolor="#F3F3F3",
                                    padding=padding.all(10),
                                    alignment=alignment.center,
                                    content=Column(
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=CrossAxisAlignment.CENTER,
                                        controls=[
                                            Container(
                                                padding=10,
                                                alignment=alignment.center,
                                                content=Text(
                                                    "Earn 1 Drop point per referral",
                                                    color="black",
                                                    font_family=APP_FONT,
                                                    weight="bold",
                                                ),
                                            ),
                                            Row(
                                                alignment=MainAxisAlignment.CENTER,
                                                controls=[
                                                    Container(
                                                        height=48,
                                                        width=156,
                                                        alignment=alignment.center,
                                                        border_radius=10,
                                                        bgcolor="white",
                                                        content=Text(
                                                            self.referral_code,
                                                            color="black",
                                                        ),
                                                    ),
                                                    Container(
                                                        on_click=self.open_dlg,
                                                        content=Image(
                                                            src="utils/referral/tap-to-copy.svg"
                                                        ),
                                                    ),
                                                ],
                                            ),
                                            Container(
                                                padding=padding.only(top=10, bottom=10),
                                                alignment=alignment.center,
                                                content=Text(
                                                    "Or Invite Via",
                                                    color="black",
                                                    font_family=APP_FONT,
                                                    weight="bold",
                                                ),
                                            ),
                                            Row(
                                                alignment=MainAxisAlignment.CENTER,
                                                controls=[
                                                    Container(
                                                        content=Image(
                                                            src="utils/referral/whatsapp.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/referral/facebook.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/referral/telegram.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/referral/others.svg"
                                                        )
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ),
                                Row(
                                    alignment="spaceBetween",
                                    controls=[
                                        Container(
                                            content=Text(
                                                "Referral List",
                                                color="black",
                                                font_family=APP_FONT_BOLD,
                                                size=22,
                                            )
                                        ),
                                        self.total_referrals,
                                    ],
                                ),
                                Container(
                                    padding=padding.only(bottom=40),
                                    content=self.referral_skeleton,
                                ),
                            ],
                        )
                    ),
                ]
            ),
        )

        super().__init__(page, self.page_content)
        self.page.run_task(self.update_skeleton)

    async def load_referral_data(self):
        query_data = await get_referrals()
        # print(f'user referrals {query_data.full_name}')
        referrals = Column(
            # height=600,
            # scroll='auto',
            controls=[
                
            ]
        )
        
    

        for user in query_data:
            print(f'this user {user}')
            name_display = user['username']
            referral =  Row(alignment='spaceBetween',
                                        controls = [Row(
                                        controls=[
                                            Image(src='letters/G.svg'),
                                            Text(f'{name_display}', color='black', font_family=APP_FONT_SBOLD),  
                                        ]
                                        
                                        ), Text('1 Drop', color='blue', font_family=APP_FONT_SBOLD)]
                                        )
            referrals.controls.append(referral)
        return {
            "referrals": referrals,
            "count": len(query_data)
        }



    async def update_skeleton(self):
        await asyncio.sleep(1.1)
        self.on_skeleton_update()
        data = await self.load_referral_data()
        referral_column = data["referrals"]
        referral_count = data["count"]
        prefix = 'user'
        if referral_count > 1:
            prefix = 'users'
        if referral_count < 1:
            pass
        self.total_referrals.content = Text(
                                            f"{referral_count} {prefix}",
                                            color="black",
                                            font_family=APP_FONT_BOLD,
                                            size=15,
                                                )
        # print(referral_count)

        # Update the skeleton content
        self.referral_skeleton.content = referral_column
        

        # Refresh the page UI
        self.page.update()

    def open_dlg(self, e):
        e.control.page.overlay.append(self.on_text_copy)
        self.on_text_copy.open = True
        self.page.set_clipboard(self.referral_code)
        e.control.page.update()


class ProfilePage(BuildPage):
    def __init__(
        self,
        page: Page,
        user_json,
        top_menu_icons,
        level_bar,
        account_settings_url,
        airdrop_activity_overview,
        profile_data,
        profile_skeleton,
        on_skeleton_update,
    ):
        self.page = page
        self.username = user_json.get('username')
        self.full_name = user_json.get('full_name')
        self.level = user_json.get('level')
        self.profile_data = profile_data
        self.top_menu_icons = top_menu_icons
        self.level_bar = level_bar
        self.airdrop_activity_overview = airdrop_activity_overview
        self.profile_skeleton = profile_skeleton
        self.account_settings_url = account_settings_url
        self.on_skeleton_update = on_skeleton_update

        self.on_logout_modal = AlertDialog(
            modal=True,
            title=Text(
                "Are you sure you want to proceed",
                font_family=APP_FONT_SBOLD,
                size=14,
                color="black",
            ),
            bgcolor="white",
            actions_alignment=MainAxisAlignment.CENTER,
            actions=[
                TextButton(
                    "Cancel",
                    on_click=self.handle_modal_close,
                    style=ButtonStyle(
                        color="black", text_style=TextStyle(font_family=APP_FONT_BOLD)
                    ),
                ),
                Container(width=10),
                Container(content=Image(src="utils/proceed.svg")),
            ],
        )

        self.page_content = Container(
            height=self.page.height,
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Column(
                        scroll="auto",
                        height=700,
                        controls=[
                            Container(height=20),
                            Row(
                                [
                                    Text(
                                        "Profile",
                                        size=22,
                                        color="black",
                                        font_family=APP_FONT_BOLD,
                                    )
                                ]
                            ),
                            Container(height=10),
                            Row(
                                controls=[
                                    Image(src="letters/G.svg"),
                                    Column(
                                        controls=[
                                            Text(
                                                f"Hello, {self.full_name}",
                                                size=22,
                                                color="black",
                                                font_family=APP_FONT_SBOLD,
                                            ),
                                            Text(
                                                f"@{self.username}",
                                                size=13,
                                                color="blue",
                                                font_family=APP_FONT_SBOLD,
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            self.airdrop_activity_overview,
                            Container(height=10),
                            Text(f"Level {self.level}", font_family=APP_FONT_SBOLD, color="black"),
                            self.level_bar(self.page),
                            Text(
                                "*Keep using DappTrack to increase your level.",
                                size=10,
                                color="black",
                                font_family=APP_FONT_SBOLD,
                            ),
                            self.profile_skeleton,
                            Container(
                                alignment=alignment.center_right,
                                content=Text(
                                    "see all",
                                    size=15,
                                    style=TextStyle(
                                        decoration=TextDecoration.UNDERLINE,
                                    ),
                                    color="blue",
                                    font_family=APP_FONT_BOLD,
                                ),
                            ),
                            Container(height=10),
                            Container(
                                on_click=self.account_settings_url,
                                content=Row(
                                    alignment="spaceBetween",
                                    controls=[
                                        Text(
                                            "Account settings",
                                            color="black",
                                            size=20,
                                            font_family=APP_FONT_BOLD,
                                        ),
                                        Container(
                                            Image(src="icons/arrow-head-right.svg")
                                        ),
                                    ],
                                ),
                            ),
                            Container(height=10),
                            Text(
                                "Notifications",
                                color="black",
                                font_family=APP_FONT_BOLD,
                            ),
                            Column(
                                controls=[
                                    Row(
                                        alignment="spaceBetween",
                                        controls=[
                                            Text(
                                                "Airdrop reminders.",
                                                size=16,
                                                color="black",
                                                weight="bold",
                                                font_family=APP_FONT,
                                            ),
                                            Switch(value=True),
                                        ],
                                    ),
                                    Row(
                                        alignment="spaceBetween",
                                        controls=[
                                            Text(
                                                "Reward claim reminders.",
                                                size=16,
                                                color="black",
                                                weight="bold",
                                                font_family=APP_FONT,
                                            ),
                                            Switch(value=True),
                                        ],
                                    ),
                                    Row(
                                        alignment="spaceBetween",
                                        controls=[
                                            Text(
                                                "Task completion notifications.",
                                                size=16,
                                                color="black",
                                                weight="bold",
                                                font_family=APP_FONT,
                                            ),
                                            Switch(value=True),
                                        ],
                                    ),
                                ]
                            ),
                            Container(height=10),
                            Container(
                                on_click=lambda e: self.page.open(self.on_logout_modal),
                                alignment=alignment.center,
                                content=Image(src="utils/logout.svg"),
                            ),
                            Container(height=20),
                        ],
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)
        self.page.run_task(self.update_skeleton)

    async def update_skeleton(self):
        await asyncio.sleep(1.8)
        self.on_skeleton_update()

        # Update the skeleton content
        self.profile_skeleton.content = await self.profile_data(5)

        # Refresh the page UI
        self.page.update()

    def handle_modal_close(self, e):
        self.page.close(self.on_logout_modal)


class SearchPage(BuildPage):
    def __init__(self, page: Page, top_menu_icons, search_suggestions):
        self.page = page
        self.top_menu_icons = top_menu_icons
        self.search_suggestions = search_suggestions
        self.page_content = Container(
            height=self.page.height * 10,
            alignment=alignment.center,
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Container(
                        content=Column(
                            controls=[
                                Container(height=20),
                                Row(
                                    controls=[
                                        Text(
                                            "Filter by",
                                            color="black",
                                            font_family=APP_FONT_SBOLD,
                                        )
                                    ]
                                ),
                                ResponsiveRow(
                                    controls=[
                                        Container(
                                            col={"xs": 12, "sm": 6, "md": 6, "lg": 6},
                                            content=Row(
                                                controls=[
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/all.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/general_airdrop.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/mining.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/testnets.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/nfts.svg"
                                                        )
                                                    ),
                                                ]
                                            ),
                                        ),
                                        Container(
                                            col={"xs": 12, "sm": 6, "md": 6, "lg": 6},
                                            content=Row(
                                                controls=[
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/socialfi.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/gamefi.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/promotional_airdrop.svg"
                                                        )
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/filter/others.svg"
                                                        )
                                                    ),
                                                ]
                                            ),
                                        ),
                                    ]
                                ),
                                self.search_suggestions,
                            ]
                        )
                    ),
                ]
            ),
        )

        super().__init__(page, self.page_content)


class SideMenuPage(BuildPage):
    def __init__(
        self,
        page: Page,
        user_json,
        go_back,
        home_url,
        notification_url,
        referral_url,
        watchlist_url,
        settings_url,
        airdrop_upload_url
    ):
        self.page = page
        self.username = user_json.get('username')
        self.dapp_points = user_json.get('dapp_points')
        self.go_back = go_back
        self.home_url = home_url
        self.notification_url = notification_url
        self.referral_url = referral_url
        self.watchlist_url = watchlist_url
        self.settings_url = settings_url
        self.airdrop_upload_url = airdrop_upload_url

        self.on_logout_modal = AlertDialog(
            modal=True,
            title=Text(
                "Are you sure you want to proceed",
                font_family=APP_FONT_SBOLD,
                size=14,
                color="black",
            ),
            bgcolor="white",
            actions_alignment=MainAxisAlignment.CENTER,
            actions=[
                TextButton(
                    "Cancel",
                    on_click=self.handle_modal_close,
                    style=ButtonStyle(
                        color="black", text_style=TextStyle(font_family=APP_FONT_BOLD)
                    ),
                ),
                Container(width=10),
                Container(content=Image(src="utils/proceed.svg")),
            ],
        )

        self.page_content = Container(
            bgcolor="white",
            padding=padding.only(left=20),
            content=Column(
                height=self.page.height,
                scroll="auto",
                controls=[
                    Row(
                        [
                            Image(src="letters/G.svg"),
                            Column(
                                controls=[
                                    Text(
                                        f"Hello {self.username}",
                                        font_family=APP_FONT,
                                        weight="bold",
                                        color="black",
                                    ),
                                    Row(
                                        [
                                            Text(
                                                f"Rewards: {self.dapp_points}",
                                                font_family=APP_FONT_BOLD,
                                                color="#004CFF",
                                            ),
                                            Image(src="utils/point-icon.svg"),
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.home_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Home",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.watchlist_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Watchlist",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.notification_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Notification",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.referral_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Refer a friend",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.settings_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Settings",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Contact us",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        )
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.airdrop_upload_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Upload Airdrop",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        )
                    ),
                    Container(height=10),
                    Container(
                        on_click=lambda e: self.page.open(self.on_logout_modal),
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Log out",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=100),
                    Container(
                        on_click=self.go_back,
                        padding=padding.only(right=20),
                        alignment=alignment.center,
                        content=Image(src="utils/button-x.svg"),
                    ),
                    Container(height=100),
                ],
            ),
        )

        super().__init__(page, self.page_content)

    def handle_modal_close(self, e):
        self.page.close(self.on_logout_modal)


class NotificationPage(BuildPage):
    def __init__(self, page: Page, go_back):
        self.page = page
        self.go_back = go_back

        self.page_content = Container(
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Container(
                                width=43,
                                height=43,
                                border_radius=20,
                                bgcolor="#F8F8F8",
                                alignment=alignment.center,
                                on_click=self.go_back,
                                content=Image(
                                    src="icons/arrow-left.svg", width=22, height=22
                                ),
                            ),
                            Text(
                                "Notification",
                                font_family=APP_FONT_BOLD,
                                size=20,
                                color="black",
                            ),
                        ]
                    ),
                    Container(
                        alignment=alignment.center_right,
                        content=Text(
                            "Mark all as read",
                            font_family=APP_FONT_BOLD,
                            size=16,
                            color="black",
                        ),
                    ),
                    Container(height=5),
                    Container(
                        height=86,
                        width=self.page.width * 10,
                        padding=10,
                        bgcolor="#DADADA",
                        border_radius=10,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Column(
                                    controls=[
                                        Text(
                                            "Timer Complete",
                                            font_family=APP_FONT_BOLD,
                                            color="black",
                                        ),
                                        Text(
                                            "Timer is up, claim your airdrop",
                                            weight="bold",
                                            font_family=APP_FONT,
                                            color="black",
                                        ),
                                    ]
                                ),
                                Container(
                                    alignment=alignment.bottom_center,
                                    content=Text(
                                        "Today at 15:07",
                                        size=11,
                                        weight="bold",
                                        font_family=APP_FONT,
                                        color="black",
                                    ),
                                ),
                            ],
                        ),
                    ),
                    Container(height=5),
                    Container(
                        height=86,
                        width=self.page.width * 10,
                        padding=10,
                        bgcolor="#DADADA",
                        border_radius=10,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Column(
                                    controls=[
                                        Text(
                                            "Timer Complete",
                                            font_family=APP_FONT_BOLD,
                                            color="black",
                                        ),
                                        Text(
                                            "Timer is up, claim your airdrop",
                                            weight="bold",
                                            font_family=APP_FONT,
                                            color="black",
                                        ),
                                    ]
                                ),
                                Container(
                                    alignment=alignment.bottom_center,
                                    content=Text(
                                        "Today at 15:07",
                                        size=11,
                                        weight="bold",
                                        font_family=APP_FONT,
                                        color="black",
                                    ),
                                ),
                            ],
                        ),
                    ),
                    Container(height=5),
                    Container(
                        height=86,
                        width=self.page.width * 10,
                        padding=10,
                        bgcolor="#DADADA",
                        border_radius=10,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Column(
                                    controls=[
                                        Text(
                                            "Timer Complete",
                                            font_family=APP_FONT_BOLD,
                                            color="black",
                                        ),
                                        Text(
                                            "Timer is up, claim your airdrop",
                                            weight="bold",
                                            font_family=APP_FONT,
                                            color="black",
                                        ),
                                    ]
                                ),
                                Container(
                                    alignment=alignment.bottom_center,
                                    content=Text(
                                        "Today at 15:07",
                                        size=11,
                                        weight="bold",
                                        font_family=APP_FONT,
                                        color="black",
                                    ),
                                ),
                            ],
                        ),
                    ),
                    Container(height=500),
                ]
            )
        )

        super().__init__(page, self.page_content)


class AirdropDetailPage(BuildPage):
    def __init__(self, page: Page, go_back, report_url, task_progress_bar, airdrop_data):
        self.page = page
        self.airdrop_data = airdrop_data
        # self.return_url = return_url
        self.airdrop_cost = "$0"
        self.go_back = go_back
        self.report_url = report_url
        self.timer_value = None
        self.task_progress_bar = task_progress_bar

        print(f'The specific AIRDROP D {self.airdrop_data}')

        self.on_join_modal = AlertDialog(
            modal=True,
            title=Text(
                "You have successfully joined this Airdrop",
                font_family=APP_FONT_SBOLD,
                size=14,
                color="black",
            ),
            bgcolor="white",
            content=Container(content=Image(src="utils/check-mark.svg")),
            actions_alignment=MainAxisAlignment.CENTER,
            actions=[
                TextButton(
                    "Close",
                    on_click=self.handle_modal_close,
                    style=ButtonStyle(
                        color="black", text_style=TextStyle(font_family=APP_FONT_BOLD)
                    ),
                ),
                Container(width=10),
                Container(content=Image(src="utils/join-more-airdrops.svg")),
            ],
        )

        self.days_field = TextField(
            value="00",
            keyboard_type=KeyboardType.NUMBER,
            input_filter=NumbersOnlyInputFilter(),
            text_style=TextStyle(font_family="Poppins Bold"),
            on_focus=self.clear_text,
        )

        self.hours_field = TextField(
            value="00",
            keyboard_type=KeyboardType.NUMBER,
            input_filter=NumbersOnlyInputFilter(),
            text_style=TextStyle(font_family="Poppins Bold"),
            on_focus=self.clear_text,
        )

        self.minutes_field = TextField(
            value="00",
            keyboard_type=KeyboardType.NUMBER,
            input_filter=NumbersOnlyInputFilter(),
            text_style=TextStyle(font_family="Poppins Bold"),
            on_focus=self.clear_text,
        )

        self.seconds_field = TextField(
            value="00",
            keyboard_type=KeyboardType.NUMBER,
            input_filter=NumbersOnlyInputFilter(),
            text_style=TextStyle(font_family="Poppins Bold"),
            on_focus=self.clear_text,
        )

        self.progress_label = Text(
            f"3:0:2:2", size=14, color="white", text_align="center"
        )

        # Circular ProgressRing
        self.progress_ring = ProgressRing(
            value=0.75,  # Completion percentage (75%)
            width=150,
            height=150,
            stroke_width=25,  # Thickness of the ring
            color="#FFAD33",
            bgcolor="white",
            stroke_cap="round",
        )
        self.timer_container = Stack(
            controls=[
                self.progress_ring,
                Container(
                    content=self.progress_label,
                    alignment=alignment.center,
                    width=150,
                    height=150,
                ),
            ],
        )

        self.timer_set = BottomSheet(
            maintain_bottom_view_insets_padding=True,
            bgcolor="white",
            content=Container(
                alignment=alignment.center,
                content=Column(
                    controls=[
                        Container(height=10),
                        Container(
                            alignment=alignment.center,
                            content=Text(
                                "Set timer to claim airdrop",
                                color="black",
                                size=20,
                                font_family=APP_FONT_BOLD,
                            ),
                        ),
                        Container(height=10),
                        Container(
                            margin=margin.only(left=80),
                            content=Row(
                                controls=[
                                    Column(
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=CrossAxisAlignment.CENTER,
                                        controls=[
                                            Container(
                                                width=50,
                                                height=50,
                                                border_radius=5.5,
                                                bgcolor="#161C2D",
                                                content=self.days_field,
                                            ),
                                            Container(
                                                alignment=alignment.center,
                                                content=Text(
                                                    "Days",
                                                    color="black",
                                                    size=8,
                                                    font_family=APP_FONT_BOLD,
                                                ),
                                            ),
                                        ],
                                    ),
                                    Column(
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=CrossAxisAlignment.CENTER,
                                        controls=[
                                            Container(
                                                width=50,
                                                height=50,
                                                border_radius=5.5,
                                                bgcolor="#161C2D",
                                                content=self.hours_field,
                                            ),
                                            Container(
                                                alignment=alignment.center,
                                                content=Text(
                                                    "HOURS",
                                                    color="black",
                                                    size=8,
                                                    font_family=APP_FONT_BOLD,
                                                ),
                                            ),
                                        ],
                                    ),
                                    Column(
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=CrossAxisAlignment.CENTER,
                                        controls=[
                                            Container(
                                                width=50,
                                                height=50,
                                                border_radius=5.5,
                                                bgcolor="#161C2D",
                                                content=self.minutes_field,
                                            ),
                                            Container(
                                                alignment=alignment.center,
                                                content=Text(
                                                    "MINUTES",
                                                    color="black",
                                                    size=8,
                                                    font_family=APP_FONT_BOLD,
                                                ),
                                            ),
                                        ],
                                    ),
                                    Column(
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=CrossAxisAlignment.CENTER,
                                        controls=[
                                            Container(
                                                width=50,
                                                height=50,
                                                border_radius=5.5,
                                                bgcolor="#161C2D",
                                                content=self.seconds_field,
                                            ),
                                            Container(
                                                alignment=alignment.center,
                                                content=Text(
                                                    "SECONDS",
                                                    color="black",
                                                    size=8,
                                                    font_family=APP_FONT_BOLD,
                                                ),
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                        ),
                        Container(height=100),
                        Container(
                            alignment=alignment.center,
                            margin=margin.only(left=60),
                            content=Row(
                                controls=[
                                    Container(
                                        width=128,
                                        height=29,
                                        border_radius=5,
                                        alignment=alignment.center,
                                        on_click=lambda _: self.page.close(
                                            self.timer_set
                                        ),
                                        border=border.all(1, color="black"),
                                        content=Text(
                                            "Cancel",
                                            size=14,
                                            font_family=APP_FONT_BOLD,
                                            color="black",
                                        ),
                                    ),
                                    Container(
                                        on_click=self.save_timer,
                                        content=Image(src="utils/save.svg"),
                                    ),
                                ]
                            ),
                        ),
                    ]
                ),
            ),
        )

        self.on_success_timer_set = Container(
            content=Column(
                controls=[
                    Text("Timer set", font_family=APP_FONT_BOLD, size=15),
                    Text(
                        f"We will notify you to claim your rewards every\n{self.timer_value}",
                        weight="bold",
                        font_family=APP_FONT,
                    ),
                ]
            )
        )

        self.task_content = Column(
            scroll="auto",
            controls=[
                Container(
                    padding=padding.only(left=20, top=10),
                    content=Row(
                        controls=[
                            Container(
                                content=Image(
                                    src="utils/airdrop_detail/task-progress-icon.svg"
                                )
                            ),
                            Column(
                                [
                                    Container(
                                        content=Text(
                                            "Overall Progress on task completed",
                                            size=12,
                                            font_family=APP_FONT,
                                            weight="bold",
                                            color="white",
                                        )
                                    ),
                                    Container(
                                        content=Text(
                                            "30%",
                                            size=14,
                                            font_family=APP_FONT,
                                            weight="bold",
                                            color="white",
                                        )
                                    ),
                                ]
                            ),
                        ]
                    ),
                ),
                Container(
                    padding=padding.only(left=20),
                    content=self.task_progress_bar(self.page),
                ),
                Container(
                    height=600,
                    bgcolor="#161C2D",
                    content=Tabs(
                        indicator_color="white",
                        indicator_tab_size=True,
                        selected_index=0,
                        animation_duration=10,
                        tabs=[
                            Tab(
                                text="All",
                                content=Column(
                                    scroll="auto",
                                    controls=[
                                        ExpansionTile(
                                            title=Row(
                                                controls=[
                                                    Text(
                                                        "Launch the Hot Telegram bot",
                                                        size=16,
                                                        font_family=APP_FONT,
                                                        weight="bold",
                                                        color="white",
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/airdrop_detail/share-box.svg"
                                                        )
                                                    ),
                                                ]
                                            ),
                                            subtitle=Container(
                                                content=Text(
                                                    "Mark as completed",
                                                    color="blue",
                                                    font_family=APP_FONT_BOLD,
                                                )
                                            ),
                                            affinity=TileAffinity.LEADING,
                                            controls=[
                                                Container(
                                                    margin=margin.only(left=30),
                                                    content=Column(
                                                        controls=[
                                                            Text(
                                                                "Estimedted Time: 5 min\n Reward: Hot token\n ",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                            Text(
                                                                "Step 1: join using the invite link. Click here",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                            Text(
                                                                "Step 2: Set up your seed phrase and claim Hot tokens",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                        ]
                                                    ),
                                                )
                                            ],
                                        ),
                                        ExpansionTile(
                                            title=Row(
                                                controls=[
                                                    Text(
                                                        "Launch the Hot Telegram bot",
                                                        size=16,
                                                        font_family=APP_FONT,
                                                        weight="bold",
                                                        color="white",
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/airdrop_detail/share-box.svg"
                                                        )
                                                    ),
                                                ]
                                            ),
                                            subtitle=Container(
                                                content=Text(
                                                    "Mark as completed",
                                                    color="blue",
                                                    font_family=APP_FONT_BOLD,
                                                )
                                            ),
                                            affinity=TileAffinity.LEADING,
                                            controls=[
                                                Container(
                                                    margin=margin.only(left=30),
                                                    content=Column(
                                                        controls=[
                                                            Text(
                                                                "Estimedted Time: 5 min\n Reward: Hot token\n ",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                            Text(
                                                                "Step 1: join using the invite link. Click here",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                            Text(
                                                                "Step 2: Set up your seed phrase and claim Hot tokens",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                            Text(
                                                                "Step 3: Set up your seed phrase and claim Hot tokens",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                            Text(
                                                                "Step 4: Set up your seed phrase and claim Hot tokens",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                        ]
                                                    ),
                                                )
                                            ],
                                        ),
                                        ExpansionTile(
                                            title=Row(
                                                controls=[
                                                    Text(
                                                        "Launch the Hot Telegram bot",
                                                        size=16,
                                                        font_family=APP_FONT,
                                                        weight="bold",
                                                        color="white",
                                                    ),
                                                    Container(
                                                        content=Image(
                                                            src="utils/airdrop_detail/share-box.svg"
                                                        )
                                                    ),
                                                ]
                                            ),
                                            subtitle=Container(
                                                content=Text(
                                                    "Mark as completed",
                                                    color="blue",
                                                    font_family=APP_FONT_BOLD,
                                                )
                                            ),
                                            affinity=TileAffinity.LEADING,
                                            controls=[
                                                Container(
                                                    margin=margin.only(left=30),
                                                    content=Column(
                                                        controls=[
                                                            Text(
                                                                "Estimedted Time: 5 min\n Reward: Hot token\n ",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                            Text(
                                                                "Step 1: join using the invite link. Click here",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                            Text(
                                                                "Step 2: Set up your seed phrase and claim Hot tokens",
                                                                font_family=APP_FONT,
                                                                weight="bold",
                                                                color="white",
                                                            ),
                                                        ]
                                                    ),
                                                )
                                            ],
                                        ),
                                        Container(height=300),
                                    ],
                                ),
                            ),
                            Tab(text="Completed", content=Text("fuck")),
                        ],
                    ),
                ),
            ],
        )

        self.timer_content = Column(
            controls=[
                Container(
                    alignment=alignment.center,
                    content=Text(
                        "Set Reminders to notify you to claim your Airdrops, so you don't miss out.",
                        size=12,
                        weight="bold",
                        color="black",
                        font_family=APP_FONT,
                    ),
                ),
                Container(
                    bgcolor="#161C2D",
                    border_radius=50,
                    padding=10,
                    height=600,
                    content=Container(
                        margin=margin.only(left=100, top=50),
                        content=Column(
                            controls=[
                                self.timer_container,
                                Container(height=10),
                                Container(
                                    on_click=lambda _: self.page.open(self.timer_set),
                                    margin=margin.only(right=100),
                                    content=Image(
                                        src="utils/airdrop_detail/new-reminder.svg"
                                    ),
                                ),
                            ]
                        ),
                    ),
                ),
            ]
        )

        self.additional_info_content = Container(
            bgcolor="#161C2D",
            border_radius=50,
            padding=10,
            content=Column(
                scroll="auto",
                controls=[
                    Container(
                        margin=margin.only(left=40),
                        width=273,
                        height=66,
                        bgcolor="white",
                        border_radius=9.45,
                        padding=8,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Column(
                                    [
                                        Text(
                                            "Expected TGE date",
                                            weight="bold",
                                            color="black",
                                            font_family=APP_FONT,
                                        ),
                                        Text(
                                            "4th January 2025",
                                            color="black",
                                            font_family=APP_FONT_BOLD,
                                        ),
                                    ]
                                ),
                                Image(src="utils/airdrop_detail/calender.png"),
                            ],
                        ),
                    ),
                    Container(
                        margin=margin.only(left=10, right=10),
                        content=Column(
                            controls=[
                                Text(
                                    "Eligibility requirements",
                                    size=18,
                                    font_family=APP_FONT,
                                    weight="bold",
                                    color="white",
                                ),
                                Text(
                                    "Do this and that then that and this then do this and that as well before tdoing this and the othre one to be eligible for this airdrop",
                                    weight="bold",
                                    font_family=APP_FONT,
                                    color="white",
                                ),
                                Divider(thickness=1),
                                Text(
                                    "Project Socials",
                                    size=18,
                                    weight="bold",
                                    font_family=APP_FONT,
                                    color="white",
                                ),
                                Text(
                                    "wwww.hot-penix.com",
                                    weight="bold",
                                    font_family=APP_FONT,
                                    color="white",
                                ),
                                Row(
                                    [
                                        Container(
                                            content=Row(
                                                [
                                                    Image(
                                                        src="utils/airdrop_detail/x.png"
                                                    ),
                                                    Text(
                                                        "Hot Protocol",
                                                        weight="bold",
                                                        font_family=APP_FONT,
                                                        color="white",
                                                    ),
                                                ]
                                            )
                                        ),
                                        Container(
                                            content=Row(
                                                [
                                                    Image(
                                                        src="utils/airdrop_detail/telegram.png"
                                                    ),
                                                    Text(
                                                        "Hot Protocol",
                                                        weight="bold",
                                                        font_family=APP_FONT,
                                                        color="white",
                                                    ),
                                                ]
                                            )
                                        ),
                                        Container(height=10),
                                    ]
                                ),
                            ]
                        ),
                    ),
                    Container(height=150),
                ],
            ),
        )

        self.tab_icons = {
            0: {
                "active": "utils/airdrop_detail/tab/task-active.svg",
                "idle": "utils/airdrop_detail/tab/task-idle.svg",
            },
            1: {
                "active": "utils/airdrop_detail/tab/timer-active.svg",
                "idle": "utils/airdrop_detail/tab/timer-idle.svg",
            },
            2: {
                "active": "utils/airdrop_detail/tab/additional-info-active.svg",
                "idle": "utils/airdrop_detail/tab/additional-info-idle.svg",
            },
        }
        self.airdrop_tab = Tabs(
            indicator_tab_size=True,
            selected_index=0,
            animation_duration=10,
            tabs=[
                Tab(
                    tab_content=Image(
                        src=self.tab_icons[0]["active"],
                    ),
                    content=Container(
                        bgcolor="#161C2D",
                        border_radius=50,
                        padding=10,
                        content=self.task_content,
                    ),
                ),
                Tab(
                    tab_content=Image(
                        src=self.tab_icons[1]["idle"],
                    ),
                    content=self.timer_content,
                ),
                Tab(
                    tab_content=Image(
                        src=self.tab_icons[2]["idle"],
                    ),
                    content=self.additional_info_content,
                ),
            ],
            label_padding=Padding(left=5, right=5, top=0, bottom=0),
            expand=1,
            on_change=self.update_tab_icons,
        )

        self.page_content = Container(
            # # Top icons
            height=self.page.height,
            content=Column(
                controls=[
                    Row(
                        alignment="spaceBetween",
                        controls=[
                            Container(
                                width=43,
                                height=43,
                                border_radius=20,
                                bgcolor="#F8F8F8",
                                alignment=alignment.center,
                                on_click=self.go_back,
                                content=Image(
                                    src="icons/arrow-left.svg", width=22, height=22
                                ),
                            ),
                            Text(
                                self.airdrop_data['name'],
                                font_family=APP_FONT_BOLD,
                                size=20,
                                color="black",
                            ),
                            PopupMenuButton(
                                bgcolor="white",
                                icon_color="black",
                                items=[
                                    PopupMenuItem(
                                        on_click=self.report_url,
                                        content=Text("Report", color="black"),
                                    ),
                                    PopupMenuItem(
                                        content=Text(
                                            "Cancel Participation", color="black"
                                        )
                                    ),
                                ],
                            ),
                        ],
                    ),
                    Container(
                        content=Column(
                            scroll="auto",
                            height=700,
                            controls=[
                                Container(
                                    padding=padding.all(10),
                                    content=Column(
                                        controls=[
                                            Row(
                                                alignment="spaceBetween",
                                                controls=[
                                                    Container(
                                                        border_radius=65,
                                                        width=130,
                                                        height=130,
                                                        content=Image(
                                                            src=self.airdrop_data['full_image_url']
                                                        ),
                                                    ),
                                                    Column(
                                                        controls=[
                                                            Container(
                                                                content=Text(
                                                                    self.airdrop_data['device_type'],
                                                                    weight="bold",
                                                                    font_family=APP_FONT,
                                                                    size=14,
                                                                    color="blue",
                                                                )
                                                            ),
                                                            Container(
                                                                content=Text(
                                                                    f"Category: {self.airdrop_data['category']}",
                                                                    weight="bold",
                                                                    font_family=APP_FONT,
                                                                    size=14,
                                                                    color="black",
                                                                )
                                                            ),
                                                            Container(
                                                                content=Text(
                                                                    f"Token: ${self.airdrop_data['expected_token_ticker']}",
                                                                    weight="bold",
                                                                    font_family=APP_FONT,
                                                                    size=14,
                                                                    color="black",
                                                                )
                                                            ),
                                                            Row(
                                                                controls=[
                                                                    Container(
                                                                        content=Text(
                                                                            f"Blockchain: {self.airdrop_data['chain']}",
                                                                            weight="bold",
                                                                            font_family=APP_FONT,
                                                                            size=14,
                                                                            color="black",
                                                                        )
                                                                    ),
                                                                    Image(
                                                                        src="utils/airdrop_detail/ton.svg"
                                                                    ),
                                                                ]
                                                            ),
                                                            Container(
                                                                content=Text(
                                                                    f"Rating: {self.airdrop_data['rating_value']}",
                                                                    weight="bold",
                                                                    font_family=APP_FONT,
                                                                    size=14,
                                                                    color="black",
                                                                )
                                                            ),
                                                            Container(
                                                                content=Text(
                                                                    f"{self.airdrop_data['airdrop_end_date']} Until Launch",
                                                                    weight="bold",
                                                                    font_family=APP_FONT,
                                                                    size=14,
                                                                    color="blue",
                                                                )
                                                            ),
                                                            self.build_join_container(airdrop_id=self.airdrop_data['id']),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                            Container(height=20),
                                            Text(
                                                f"Cost: {self.airdrop_cost}",
                                                size=FONT_SIZE,
                                                weight="bold",
                                                font_family=APP_FONT,
                                                color="black",
                                            ),
                                        ]
                                    ),
                                ),
                                Container(
                                    height=650,
                                    margin=0,
                                    content=self.airdrop_tab,
                                ),
                            ],
                        )
                    ),
                ]
            ),
        )
        # self.page_content = Stack(
        #     controls=[
        #         self.page_items,
        #         FloatingActionButton(bottom=60, right=20, tooltip='Add Airdrop', bgcolor='#000428',
        #                              icon=Icons.ADD, foreground_color='black'),

        #     ]
        # )

        super().__init__(page, self.page_content)

    def build_join_container(self, airdrop_id: int):
        async def handle_click(e):
            data = await track_airdrop_by_id(airdrop_id)
            print("tracked airdrop:", data)

            self.page.open(self.on_join_modal)

        return Container(
            on_click=handle_click,
            content=Image(
                    src="utils/airdrop_detail/join.svg"
                ),
        )

    def update_tab_icons(self, e):
        """Update the tab content images based on the selected tab index."""
        selected_index = self.airdrop_tab.selected_index

        # Iterate through all tabs and update their images
        for i, tab in enumerate(self.airdrop_tab.tabs):
            if i == selected_index:
                # Set the active image for the selected tab
                tab.tab_content.src = self.tab_icons[i]["active"]
            else:
                # Set the idle image for all other tabs
                tab.tab_content.src = self.tab_icons[i]["idle"]

        # Update the Tabs widget to reflect the changes
        self.airdrop_tab.update()

    def clear_text(self, e):
        e.control.value = ""
        self.page.update()

    async def save_timer(self, e):
        try:
            # Validate inputs
            days = int(self.days_field.value or 0)
            hours = int(self.hours_field.value or 0)
            minutes = int(self.minutes_field.value or 0)
            seconds = int(self.seconds_field.value or 0)

            # Convert to total seconds
            total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
            print(f"this is the total sec {total_seconds}")
            if total_seconds <= 0:
                raise ValueError("Please set a valid timer duration!")

            await set_timer(airdrop_id=self.airdrop_data['id'], total_seconds=total_seconds)
            self.timer_value = self.format_time(total_seconds)

            original_timer_set = self.timer_set.content

            self.timer_set.content = Container(
                alignment=alignment.center,
                width=self.page.window.width,
                content=Column(
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    controls=[
                        Container(height=50),
                        Text(
                            "Timer set",
                            color="black",
                            font_family=APP_FONT_BOLD,
                            size=20,
                        ),
                        Text(
                            f"We will notify you to claim your rewards every",
                            size=15,
                            color="black",
                            font_family=APP_FONT_SBOLD,
                        ),
                        Text(
                            f"{self.timer_value}",
                            size=15,
                            color="black",
                            font_family=APP_FONT_SBOLD,
                        ),
                        Container(content=Image(src="utils/check-mark.svg")),
                        Container(height=300),
                    ],
                ),
            )
            print(self.timer_set.content)
            # self.page.open(self.timer_set)

            self.page.update()
            time.sleep(2)
            self.page.close(self.timer_set)

            self.timer_set.content = original_timer_set
            time.sleep(1)

            self.page.update()
            # Start the timer
            self.start_timer(total_seconds)
        except ValueError as ex:
            self.page.snack_bar = Text(str(ex), color=colors.RED)
            self.page.snack_bar.update()

    def start_timer(self, total_seconds):
        def countdown():
            nonlocal total_seconds
            while total_seconds > 0:
                mins, secs = divmod(total_seconds, 60)
                hrs, mins = divmod(mins, 60)
                # self.page.dialog = Text()
                # self.page.update()
                time.sleep(1)  # Reduce by 1 second
                total_seconds -= 1
                time_value = f"{hrs:02}:{mins:02}:{secs:02}"

        countdown()

    def format_time(self, seconds):
        """Helper method to format total seconds into HH:MM:SS."""
        mins, secs = divmod(seconds, 60)
        hrs, mins = divmod(mins, 60)
        return f"{hrs:02}:{mins:02}:{secs:02}"

    def handle_modal_close(self, e):
        self.page.close(self.on_join_modal)


class AllAirdropsPage(BuildPage):
    def __init__(
        self,
        page: Page,
        top_menu_icons,
        airdrops,
        drop_down_menu,
        airdrop_list_skeleton,
        on_skeleton_update,
    ):
        self.page = page
        self.top_menu_icons = top_menu_icons
        self.airdrops = airdrops
        self.drop_down_menu = drop_down_menu
        self.airdrop_list_skeleton = airdrop_list_skeleton
        self.on_skeleton_update = on_skeleton_update

        self.menu_names = Column(
            controls=[
                Container(
                    # on_click=self.active_url,
                    content=Text(
                        "General Airdrop",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.completed_url,
                    content=Text(
                        "Testnets", size=16, font_family=APP_FONT_SBOLD, color="black"
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.pending_url,
                    content=Text(
                        "Retroactive",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.pending_url,
                    content=Text(
                        "Mining",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.pending_url,
                    content=Text(
                        "NFT Airdrops",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.pending_url,
                    content=Text(
                        "SocialFi",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.pending_url,
                    content=Text(
                        "GameFi",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.pending_url,
                    content=Text(
                        "WaitLists",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.pending_url,
                    content=Text(
                        "Promotional Airdrops",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
                Container(height=5),
                Container(
                    # on_click=self.pending_url,
                    content=Text(
                        "Others",
                        size=16,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                ),
            ]
        )

        self.dropdown_content = self.drop_down_menu(
            menu_names=self.menu_names, on_click=self.toggle_dropdown
        )

        self.airdrop_content = Container(content=self.airdrop_list_skeleton)

        self.page_content = Container(
            expand=True,
            bgcolor="white",
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Container(height=10),
                    Stack(
                        controls=[
                            Column(
                                expand=True,
                                controls=[
                                    Row(
                                        alignment="spaceBetween",
                                        controls=[
                                            Container(
                                                # padding=padding.only(left=10),
                                                content=Text(
                                                    "Airdrop Categories",
                                                    color="black",
                                                    font_family=APP_FONT_SBOLD,
                                                    size=22,
                                                )
                                            ),
                                            Container(
                                                padding=padding.only(right=5),
                                                content=Image(
                                                    src="icons/drop-down.svg"
                                                ),
                                                on_click=self.toggle_dropdown,
                                            ),
                                        ],
                                    ),
                                    Container(
                                        content=Text(
                                            "Top 100",
                                            font_family=APP_FONT,
                                            color="black",
                                            weight="bold",
                                        )
                                    ),
                                    # Container(height=5),
                                    self.airdrop_content,
                                    Container(height=10),
                                ],
                            ),
                            Container(
                                alignment=alignment.center_right,
                                content=self.dropdown_content,
                            ),
                        ],
                    ),
                ]
            ),
        )

        super().__init__(page, self.page_content)
        self.page.run_task(self.update_skeleton)

    async def update_skeleton(self):
        await asyncio.sleep(1.8)
        self.on_skeleton_update()

        # Update the skeleton content
        self.airdrop_content.content = await self.airdrops(10)

        # Refresh the page UI
        self.page.update()


class WatchlistPage(BuildPage):
    def __init__(
        self,
        page: Page,
        top_menu_icons,
        watchlist,
        airdrop_list_skeleton,
        on_skeleton_update,
    ):
        self.page = page
        self.top_menu_icons = top_menu_icons
        self.watchlist = watchlist
        self.airdrop_list_skeleton = airdrop_list_skeleton
        self.on_skeleton_update = on_skeleton_update
        self.airdrop_content = Container(content=self.airdrop_list_skeleton)

        self.page_content = Container(
            bgcolor="white",
            height=self.page.height * 10,
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Container(
                        height=self.page.height,
                        content=Column(
                            controls=[
                                Container(height=20),
                                Row(
                                    controls=[
                                        Text(
                                            "Watchlist",
                                            size=20,
                                            color="black",
                                            font_family=APP_FONT_BOLD,
                                        ),
                                    ]
                                ),
                                self.airdrop_content,
                            ]
                        ),
                    ),
                ],
            ),
        )
        super().__init__(page, self.page_content)
        self.page.run_task(self.update_skeleton)

    async def update_skeleton(self):
        await asyncio.sleep(1.8)
        self.on_skeleton_update()

        # Update the skeleton content
        self.airdrop_content.content = await self.watchlist(10)

        # Refresh the page UI
        self.page.update()


class SettingsPage(BuildPage):
    def __init__(
        self,
        page: Page,
        top_icons,
        account_settings_url,
        notification_settings_url,
        language_settings_url,
        terms_url,
        privacy_policy_url,
        version_info_url,
    ):
        self.page = page
        self.top_icons = top_icons
        self.account_settings_url = account_settings_url
        self.notification_settings_url = notification_settings_url
        self.language_settings_url = language_settings_url
        self.terms_url = terms_url
        self.privacy_policy_url = privacy_policy_url
        self.version_info_url = version_info_url

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    Container(
                        on_click=self.account_settings_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Account settings",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.notification_settings_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Notification settings",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.language_settings_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Language settings",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.terms_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Term & Condition",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.privacy_policy_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Privacy policy",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        on_click=self.version_info_url,
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Text(
                                    "Version info",
                                    size=20,
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                                Image(src="icons/arrow-head-right.svg"),
                            ],
                        ),
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


class AccountSettingsPage(BuildPage):
    def __init__(self, page: Page, top_icons, change_password_url, delete_account_url):
        self.page = page
        self.top_icons = top_icons
        self.change_password_url = change_password_url
        self.delete_account_url = delete_account_url

        self.on_save_modal = AlertDialog(
            title=Container(
                alignment=alignment.center,
                content=Text(
                    "Your changes has been saved",
                    font_family=APP_FONT_SBOLD,
                    size=14,
                    color="black",
                ),
            ),
            bgcolor="white",
            content=Container(content=Image(src="utils/check-mark.svg")),
            on_dismiss=lambda e: print("dismissed"),
        )

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Text(
                        "Fill your information correctly",
                        color="black",
                        font_family=APP_FONT,
                        weight="bold",
                    ),
                    Container(
                        content=Column(
                            controls=[
                                Text(
                                    "Edit information",
                                    color="blue",
                                    font_family=APP_FONT_BOLD,
                                    size=12,
                                ),
                                Container(height=5),
                                Text(
                                    "First name",
                                    weight="bold",
                                    font_family=APP_FONT_BOLD,
                                    color="black",
                                ),
                                Container(
                                    border_radius=8,
                                    content=TextField(
                                        value="John",
                                        height=44,
                                        content_padding=15,
                                        color="black",
                                        border=InputBorder.NONE,
                                        bgcolor="#F8F8F8",
                                    ),
                                ),
                                Text(
                                    "Last name",
                                    weight="bold",
                                    font_family=APP_FONT_BOLD,
                                    color="black",
                                ),
                                Container(
                                    border_radius=8,
                                    content=TextField(
                                        value="Doe",
                                        height=44,
                                        content_padding=15,
                                        color="black",
                                        border=InputBorder.NONE,
                                        bgcolor="#F8F8F8",
                                    ),
                                ),
                                Text(
                                    "Other name (optional)",
                                    weight="bold",
                                    font_family=APP_FONT_BOLD,
                                    color="black",
                                ),
                                Container(
                                    border_radius=8,
                                    content=TextField(
                                        value="JoDoe",
                                        height=44,
                                        content_padding=15,
                                        color="black",
                                        border=InputBorder.NONE,
                                        bgcolor="#F8F8F8",
                                    ),
                                ),
                                Text(
                                    "Username",
                                    weight="bold",
                                    font_family=APP_FONT_BOLD,
                                    color="black",
                                ),
                                Container(
                                    border_radius=8,
                                    content=TextField(
                                        value="JohnDoe",
                                        height=44,
                                        content_padding=15,
                                        color="black",
                                        border=InputBorder.NONE,
                                        bgcolor="#F8F8F8",
                                    ),
                                ),
                                Text(
                                    "Email address",
                                    weight="bold",
                                    font_family=APP_FONT_BOLD,
                                    color="black",
                                ),
                                Container(
                                    border_radius=8,
                                    content=TextField(
                                        value="JohnDoe@gmail.com",
                                        height=44,
                                        content_padding=15,
                                        color="black",
                                        border=InputBorder.NONE,
                                        bgcolor="#F8F8F8",
                                    ),
                                ),
                            ]
                        )
                    ),
                    Container(height=10),
                    Container(
                        on_click=lambda e: self.page.open(self.on_save_modal),
                        content=Image(src="utils/save-info.svg"),
                    ),
                    Container(height=20),
                    Container(
                        on_click=self.change_password_url,
                        content=Image(src="utils/change-password.svg"),
                    ),
                    Container(height=20),
                    Container(
                        alignment=alignment.center,
                        content=TextButton(
                            "Delete account",
                            on_click=self.delete_account_url,
                            style=ButtonStyle(
                                color="black",
                                text_style=TextStyle(font_family=APP_FONT_BOLD),
                            ),
                        ),
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


class ChangePasswordPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    Row(
                        controls=[
                            self.top_icons,
                            Container(content=Image(src="utils/save-password.svg")),
                        ]
                    ),
                    Container(height=10),
                    Column(
                        controls=[
                            Text(
                                "Old password",
                                weight="bold",
                                font_family=APP_FONT_BOLD,
                                color="black",
                            ),
                            Container(
                                border_radius=8,
                                content=TextField(
                                    password=True,
                                    can_reveal_password=True,
                                    color="black",
                                    border=InputBorder.NONE,
                                    bgcolor="#F8F8F8",
                                ),
                            ),
                            Text(
                                "New password",
                                weight="bold",
                                font_family=APP_FONT_BOLD,
                                color="black",
                            ),
                            Container(
                                border_radius=8,
                                content=TextField(
                                    password=True,
                                    can_reveal_password=True,
                                    color="black",
                                    border=InputBorder.NONE,
                                    bgcolor="#F8F8F8",
                                ),
                            ),
                            Text(
                                "Confirm password",
                                weight="bold",
                                font_family=APP_FONT_BOLD,
                                color="black",
                            ),
                            Container(
                                border_radius=8,
                                content=TextField(
                                    password=True,
                                    can_reveal_password=True,
                                    color="black",
                                    border=InputBorder.NONE,
                                    bgcolor="#F8F8F8",
                                ),
                            ),
                        ]
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


class DeleteAccountPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.on_delete_modal = AlertDialog(
            modal=True,
            title=Text(
                "Are you sure you want to proceed",
                font_family=APP_FONT_SBOLD,
                size=14,
                color="black",
            ),
            bgcolor="white",
            actions_alignment=MainAxisAlignment.CENTER,
            actions=[
                TextButton(
                    "Cancel",
                    on_click=self.handle_modal_close,
                    style=ButtonStyle(
                        color="black", text_style=TextStyle(font_family=APP_FONT_BOLD)
                    ),
                ),
                Container(width=10),
                Container(content=Image(src="utils/proceed.svg")),
            ],
        )

        self.lost_intrest = Container(
            width=370,
            height=44,
            border_radius=10,
            bgcolor="#DADADA",
            content=Checkbox(
                adaptive=True,
                label="I no longer find this service useful.",
                value=False,
                check_color="white",
                active_color="#161C2D",
                label_style=TextStyle(
                    color="black", weight="bold", font_family=APP_FONT
                ),
            ),
        )

        self.technical_issues = Container(
            width=370,
            height=44,
            border_radius=10,
            bgcolor="#DADADA",
            content=Checkbox(
                adaptive=True,
                label="I'm experiencing technical issues",
                value=False,
                check_color="white",
                active_color="#161C2D",
                label_style=TextStyle(
                    color="black", weight="bold", font_family=APP_FONT
                ),
            ),
        )

        self.no_longer_particpate = Container(
            width=370,
            height=44,
            border_radius=10,
            bgcolor="#DADADA",
            content=Checkbox(
                adaptive=True,
                label="I no longer participate in airdrops",
                value=False,
                check_color="white",
                active_color="#161C2D",
                label_style=TextStyle(
                    color="black", weight="bold", font_family=APP_FONT
                ),
            ),
        )
        self.additional_info = Container(
            height=160,
            width=369,
            border_radius=10,
            bgcolor="#DADADA",
            padding=padding.only(left=10, right=10),
            content=TextField(
                multiline=True,
                border="none",
                min_lines=1,
                max_lines=20,
                hint_text="Please provide any additional information or details.",
                text_style=TextStyle(
                    color="black", font_family=APP_FONT, weight="bold"
                ),
                hint_style=TextStyle(
                    color="black", font_family=APP_FONT, weight="bold"
                ),
            ),
        )

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    Text(
                        "Select reason",
                        color="blue",
                        font_family=APP_FONT_BOLD,
                        size=12,
                    ),
                    Column(
                        controls=[
                            self.lost_intrest,
                            self.technical_issues,
                            self.no_longer_particpate,
                            Container(height=10),
                            Container(
                                alignment=alignment.center_left,
                                content=Text(
                                    "Anything else you want to say",
                                    color="black",
                                    font_family=APP_FONT_BOLD,
                                ),
                            ),
                            self.additional_info,
                            Text(
                                "*All your data will be deleted from our server including your profile information.",
                                color="red",
                                font_family=APP_FONT_BOLD,
                            ),
                            Container(height=70),
                            Container(
                                on_click=lambda e: self.page.open(self.on_delete_modal),
                                content=Image(src="utils/delete-account.svg"),
                            ),
                        ]
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)

    def handle_modal_close(self, e):
        self.page.close(self.on_delete_modal)


class NotificationSettingsPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    Text(
                        "Select your notification preferences",
                        size=12,
                        color="black",
                        weight="bold",
                        font_family=APP_FONT,
                    ),
                    Row(
                        alignment="spaceBetween",
                        controls=[
                            Text(
                                "Airdrop reminders.",
                                size=16,
                                color="black",
                                weight="bold",
                                font_family=APP_FONT,
                            ),
                            Switch(value=True),
                        ],
                    ),
                    Row(
                        alignment="spaceBetween",
                        controls=[
                            Text(
                                "Reward claim reminders.",
                                size=16,
                                color="black",
                                weight="bold",
                                font_family=APP_FONT,
                            ),
                            Switch(value=True),
                        ],
                    ),
                    Row(
                        alignment="spaceBetween",
                        controls=[
                            Text(
                                "Task completion notifications.",
                                size=16,
                                color="black",
                                weight="bold",
                                font_family=APP_FONT,
                            ),
                            Switch(value=True),
                        ],
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


class LanguagePage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    Container(
                        content=Text(
                            "Selected language",
                            size=14,
                            color="black",
                            font_family=APP_FONT_BOLD,
                        )
                    ),
                    Container(
                        width=374,
                        height=40,
                        bgcolor="#161C2D",
                        border_radius=10,
                        alignment=alignment.center,
                        content=Text(
                            "English(UK)",
                            size=16,
                            color="white",
                            weight="bold",
                            font_family=APP_FONT,
                        ),
                    ),
                    Container(height=10),
                    Container(
                        content=Text(
                            "Select a language",
                            size=14,
                            color="black",
                            font_family=APP_FONT_BOLD,
                        )
                    ),
                    Container(height=10),
                    Container(
                        content=Text(
                            "More languages coming soon...",
                            weight="bold",
                            size=16,
                            color="black",
                            font_family=APP_FONT,
                        )
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


class TermsAndConditionPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        # Heading
        self.heading = Text(
            "DropDash Terms and Conditions",
            size=24,
            color="black",
            font_family=APP_FONT_BOLD,
        )
        self.last_updated = Text(
            "Last Updated: January 3, 2025",
            size=14,
            weight="bold",
            color="black",
            font_family=APP_FONT,
        )

        # Section 1: Acceptance of Terms
        self.section_1 = Text(
            "1. Acceptance of Terms", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_1_content = Text(
            "By using DropDash, you agree to comply with and be bound by these Terms and any additional terms, "
            "guidelines, or policies that may apply. DropDash reserves the right to modify or update these Terms at any time. "
            "You are responsible for reviewing these Terms regularly. Your continued use of the Service constitutes your "
            "acceptance of any changes.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 2: Eligibility
        self.section_2 = Text(
            "2. Eligibility", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_2_content = Text(
            "DropDash is open to users of all ages, including children. However, if you are under the age of 13, you may need "
            "parental consent to use certain features or interact with specific functionalities on the app. By using the Service, "
            "you represent and warrant that you comply with the applicable age requirements in your jurisdiction.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 3: User Account
        self.section_3 = Text(
            "3. User Account", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_3_content = Text(
            "To access certain features of DropDash, you may be required to create a user account. You are responsible for maintaining "
            "the confidentiality of your account credentials and for all activities that occur under your account. You agree to notify us "
            "immediately of any unauthorized use of your account.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 4: Services Provided
        self.section_4 = Text(
            "4. Services Provided", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_4_content = Text(
            "DropDash is a platform that tracks airdrops in the cryptocurrency space. We provide a variety of tools to help users track, "
            "organize, and manage airdrops, including notifications, search functionality, and more.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 5: User Conduct
        self.section_5 = Text(
            "5. User Conduct", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_5_content = Text(
            "You agree to use DropDash in compliance with all applicable laws and regulations. You must not:",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        self.section_5_bullets = [
            Text(
                "- Engage in fraudulent or misleading activity.",
                size=14,
                color="black",
                font_family=APP_FONT,
                weight="bold",
            ),
            Text(
                "- Attempt to hack, interfere with, or disrupt the functionality of the Service.",
                size=14,
                color="black",
                font_family=APP_FONT,
                weight="bold",
            ),
            Text(
                "- Use the Service for any unlawful or harmful purpose.",
                size=14,
                color="black",
                font_family=APP_FONT,
                weight="bold",
            ),
        ]

        # Section 6: Privacy
        self.section_6 = Text(
            "6. Privacy", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_6_content = Text(
            "Your privacy is important to us. Please review our Privacy Policy to understand how we collect, use, and protect your personal information.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 7: Intellectual Property
        self.section_7 = Text(
            "7. Intellectual Property",
            size=18,
            color="black",
            font_family=APP_FONT_BOLD,
        )
        self.section_7_content = Text(
            "All content, features, and functionality provided by DropDash, including but not limited to text, graphics, logos, and software, "
            "are the property of DropDash or its licensors and are protected by copyright, trademark, and other intellectual property laws. "
            "You may not use, copy, or distribute any content from DropDash without permission.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 8: Limitation of Liability
        self.section_8 = Text(
            "8. Limitation of Liability",
            size=18,
            color="black",
            font_family=APP_FONT_BOLD,
        )
        self.section_8_content = Text(
            "DropDash provides the Service 'as is' and makes no warranties or representations about the accuracy or reliability of the content. "
            "In no event will DropDash be liable for any direct, indirect, incidental, special, or consequential damages arising out of your use of the Service.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 9: Indemnification
        self.section_9 = Text(
            "9. Indemnification", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_9_content = Text(
            "You agree to indemnify, defend, and hold harmless DropDash and its affiliates, officers, employees, and agents from any claims, liabilities, "
            "losses, or expenses arising out of your use of the Service or violation of these Terms.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 10: Termination
        self.section_10 = Text(
            "10. Termination", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_10_content = Text(
            "DropDash reserves the right to suspend or terminate your account at any time if you violate these Terms or for any other reason, with or without notice. "
            "Upon termination, your right to access the Service will immediately cease.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 11: Third-Party Links
        self.section_11 = Text(
            "11. Third-Party Links", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_11_content = Text(
            "DropDash may contain links to third-party websites or services. These links are provided for your convenience, and we are not responsible for the content, "
            "privacy policies, or practices of third-party websites.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 12: Governing Law
        self.section_12 = Text(
            "12. Governing Law", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_12_content = Text(
            "These Terms are governed by and construed in accordance with the laws of the jurisdiction in which DropDash operates, without regard to its conflict of law principles.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 13: Dispute Resolution
        self.section_13 = Text(
            "13. Dispute Resolution", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_13_content = Text(
            "Any disputes arising out of or related to these Terms will be resolved through binding arbitration in accordance with the rules of the relevant arbitration body. "
            "You agree to submit to the jurisdiction of the arbitration body for the resolution of any disputes.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 14: Changes to Terms
        self.section_14 = Text(
            "14. Changes to Terms", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_14_content = Text(
            "DropDash reserves the right to modify or update these Terms at any time. Any changes will be posted on this page, and the revised Terms will take effect immediately upon posting. "
            "Your continued use of the Service after any such changes constitutes your acceptance of the new Terms.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 15: Contact Information
        self.section_15 = Text(
            "15. Contact Information", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_15_content = Text(
            "If you have any questions or concerns regarding these Terms, please contact us at:",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )
        self.contact_email = Text(
            "Email: support@dropdash.com",
            color="black",
            selectable=True,
            font_family=APP_FONT,
            weight="bold",
        )
        self.contact_address = Text(
            "Address: [Your Company Address]",
            color="black",
            selectable=True,
            font_family=APP_FONT,
            weight="bold",
        )

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    Column(
                        height=700,
                        scroll="auto",
                        controls=[
                            self.heading,
                            self.last_updated,
                            self.section_1,
                            self.section_1_content,
                            self.section_2,
                            self.section_2_content,
                            self.section_3,
                            self.section_3_content,
                            self.section_4,
                            self.section_4_content,
                            self.section_5,
                            self.section_5_content,
                            self.section_5_bullets,
                            self.section_6,
                            self.section_6_content,
                            self.section_7,
                            self.section_7_content,
                            self.section_8,
                            self.section_8_content,
                            self.section_9,
                            self.section_9_content,
                            self.section_10,
                            self.section_10_content,
                            self.section_11,
                            self.section_11_content,
                            self.section_12,
                            self.section_12_content,
                            self.section_13,
                            self.section_13_content,
                            self.section_14,
                            self.section_14_content,
                            self.section_15,
                            self.section_15_content,
                            self.contact_email,
                            self.contact_address,
                            Container(height=20),
                        ],
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


class PrivacyPolicyPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        # Heading
        self.heading = Text(
            "DropDash Privacy Policy", size=24, color="black", font_family=APP_FONT_BOLD
        )
        self.last_updated = Text(
            "Last Updated: January 3, 2025",
            size=14,
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Introduction
        self.introduction = Text(
            "Your privacy is important to us. This Privacy Policy explains how DropDash collects, uses, shares, "
            "and protects your personal information. By using DropDash, you agree to the terms of this Privacy Policy.",
            size=14,
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 1: Information We Collect
        self.section_1 = Text(
            "1. Information We Collect",
            size=18,
            color="black",
            font_family=APP_FONT_BOLD,
        )
        self.section_1_content = Text(
            "We may collect the following types of information from you:\n"
            "- Personal Information: Such as your name, email address, or other contact details when you create an account.\n"
            "- Usage Data: Information about how you use the app, including interactions, preferences, and device information.\n"
            "- Cookies and Tracking: Data collected through cookies and similar technologies to improve user experience.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 2: How We Use Your Information
        self.section_2 = Text(
            "2. How We Use Your Information",
            size=18,
            color="black",
            font_family=APP_FONT_BOLD,
        )
        self.section_2_content = Text(
            "We use the information we collect for the following purposes:\n"
            "- To provide and improve the DropDash service.\n"
            "- To personalize user experience and send relevant notifications.\n"
            "- To communicate with you regarding updates, features, or customer support.\n"
            "- To ensure security and prevent fraud.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 3: Sharing Your Information
        self.section_3 = Text(
            "3. Sharing Your Information",
            size=18,
            color="black",
            font_family=APP_FONT_BOLD,
        )
        self.section_3_content = Text(
            "We do not sell your personal information. However, we may share your information in the following circumstances:\n"
            "- With service providers that help us operate the app.\n"
            "- If required by law or to protect our rights and users.\n"
            "- In connection with a business transaction, such as a merger or acquisition.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 4: Data Security
        self.section_4 = Text(
            "4. Data Security", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_4_content = Text(
            "We take reasonable measures to protect your personal information from unauthorized access, disclosure, or misuse. "
            "However, no security system is completely foolproof, and we cannot guarantee the absolute security of your data.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 5: Your Privacy Rights
        self.section_5 = Text(
            "5. Your Privacy Rights", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_5_content = Text(
            "Depending on your location, you may have the following rights:\n"
            "- Access and update your personal information.\n"
            "- Request deletion of your data.\n"
            "- Opt-out of marketing communications.\n"
            "- Contact us for further details or to exercise your rights.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 6: Children's Privacy
        self.section_6 = Text(
            "6. Children's Privacy", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_6_content = Text(
            "DropDash is open to users of all ages, including children. We are committed to protecting children's privacy. "
            "If you are under 13, you may need parental consent to use certain features. We do not knowingly collect personal information "
            "from children without appropriate consent.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 7: Changes to This Privacy Policy
        self.section_7 = Text(
            "7. Changes to This Privacy Policy",
            size=18,
            color="black",
            font_family=APP_FONT_BOLD,
        )
        self.section_7_content = Text(
            "We may update this Privacy Policy from time to time. Any changes will be posted on this page with an updated 'Last Updated' date. "
            "Your continued use of DropDash after any changes constitutes acceptance of the revised Privacy Policy.",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Section 8: Contact Information
        self.section_8 = Text(
            "8. Contact Information", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.section_8_content = Text(
            "If you have any questions or concerns regarding this Privacy Policy, please contact us at:",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )
        self.contact_email = Text(
            "Email: support@dropdash.com",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )
        self.contact_address = Text(
            "Address: [Your Company Address]",
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    Column(
                        height=700,
                        scroll="auto",
                        controls=[
                            self.heading,
                            self.last_updated,
                            self.introduction,
                            self.section_1,
                            self.section_1_content,
                            self.section_2,
                            self.section_2_content,
                            self.section_3,
                            self.section_3_content,
                            self.section_4,
                            self.section_4_content,
                            self.section_5,
                            self.section_5_content,
                            self.section_6,
                            self.section_6_content,
                            self.section_7,
                            self.section_7_content,
                            self.section_8,
                            self.section_8_content,
                            self.contact_email,
                            self.contact_address,
                            Container(height=20),
                        ],
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


class VersionInfoPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        # Heading
        self.heading = Text(
            "DropDash Version Information",
            size=24,
            color="black",
            font_family=APP_FONT_BOLD,
        )

        # Introduction
        self.introduction = Text(
            "Welcome to the DropDash Version Info page. Here you can find details about the current version of the app, "
            "updates, and what's new in this release.",
            size=14,
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Current Version
        self.current_version = Text(
            "Current Version: 1.0.0", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.release_date = Text(
            "Release Date: January 3, 2025",
            size=14,
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # What's New Section
        self.whats_new_heading = Text(
            "What's New in Version 1.0.0",
            size=18,
            color="black",
            font_family=APP_FONT_BOLD,
        )
        self.whats_new_content = Text(
            "- Launch of DropDash with core features:\n"
            "  - Airdrop tracking and notifications.\n"
            "  - Search functionality for airdrops.\n"
            "  - User-friendly interface designed for all age groups.\n"
            "- Optimized performance for a seamless experience.\n"
            "- Enhanced security features to protect user data.",
            size=14,
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Known Issues
        self.known_issues_heading = Text(
            "Known Issues", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.known_issues_content = Text(
            "- Some minor lag on App initialization.\n"
            "- Minor UI glitches.\n"
            "- Minor UI glitches.\n"
            "We are actively working to resolve these issue in future updates.",
            size=14,
            color="black",
            font_family=APP_FONT,
            weight="bold",
        )

        # Contact for Feedback
        self.feedback_heading = Text(
            "Feedback and Support", size=18, color="black", font_family=APP_FONT_BOLD
        )
        self.feedback_content = Text(
            "We value your feedback! If you encounter any issues or have suggestions, please reach out to us:\n"
            "- Email: dropdash.team@gmail.com\n",
           
            size=14,
            color="black",
            font_family=APP_FONT,
            weight="bold",
            selectable=True,
        )

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    Column(
                        height=700,
                        scroll="auto",
                        controls=[
                            self.heading,
                            self.introduction,
                            self.current_version,
                            self.release_date,
                            self.whats_new_heading,
                            self.whats_new_content,
                            self.known_issues_heading,
                            self.known_issues_content,
                            self.feedback_heading,
                            self.feedback_content,
                            Container(height=20),
                        ],
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


############## POP UP MENU PAGES ######################
class ReportPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.scam = Container(
            width=370,
            height=44,
            border_radius=10,
            bgcolor="#DADADA",
            content=Checkbox(
                adaptive=True,
                label="Suspicious or Scam Activity",
                value=False,
                check_color="white",
                active_color="#161C2D",
                label_style=TextStyle(
                    color="black", weight="bold", font_family=APP_FONT
                ),
            ),
        )

        self.no_reward = Container(
            width=370,
            height=44,
            border_radius=10,
            bgcolor="#DADADA",
            content=Checkbox(
                adaptive=True,
                label="Non-Receipt of Rewards",
                value=False,
                check_color="white",
                active_color="#161C2D",
                label_style=TextStyle(
                    color="black", weight="bold", font_family=APP_FONT
                ),
            ),
        )

        self.false_instructions = Container(
            width=370,
            height=44,
            border_radius=10,
            bgcolor="#DADADA",
            content=Checkbox(
                adaptive=True,
                label="Unclear or False Instructions",
                value=False,
                check_color="white",
                active_color="#161C2D",
                label_style=TextStyle(
                    color="black", weight="bold", font_family=APP_FONT
                ),
            ),
        )

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    Container(
                        height=550,
                        width=440,
                        border_radius=50,
                        bgcolor="#161C2D",
                        padding=40,
                        content=Column(
                            controls=[
                                self.scam,
                                self.no_reward,
                                self.false_instructions,
                                Container(height=20),
                                Container(
                                    alignment=alignment.center_left,
                                    content=Text(
                                        "Others",
                                        color="white",
                                        font_family=APP_FONT_BOLD,
                                    ),
                                ),
                                Container(
                                    height=160,
                                    width=369,
                                    border_radius=10,
                                    bgcolor="#DADADA",
                                    padding=padding.only(left=10, right=10),
                                    content=TextField(
                                        autofocus=True,
                                        multiline=True,
                                        border="none",
                                        min_lines=1,
                                        max_lines=20,
                                        hint_text="Please provide any additional information or details.",
                                        text_style=TextStyle(
                                            color="black",
                                            font_family=APP_FONT,
                                            weight="bold",
                                        ),
                                        hint_style=TextStyle(
                                            color="black",
                                            font_family=APP_FONT,
                                            weight="bold",
                                        ),
                                    ),
                                ),
                                Container(height=10),
                                Container(content=Image(src="utils/submit-report.svg")),
                            ]
                        ),
                    ),
                ]
            ),
        )
        super().__init__(page, self.page_content)


################ SUB CATEGORY PAGES ####################

############### Airdrop Tracker Sub Pages


class ActivePage(BuildPage):
    def __init__(self, page: Page, top_menu_icons):
        self.page = page
        self.top_menu_icons = top_menu_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Container(height=10),
                    Text("Active", size=20, font_family=APP_FONT_SBOLD, color="black"),
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class CompletedPage(BuildPage):
    def __init__(self, page: Page, top_menu_icons):
        self.page = page
        self.top_menu_icons = top_menu_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Container(height=10),
                    Text(
                        "Completed", size=20, font_family=APP_FONT_SBOLD, color="black"
                    ),
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class PendingPage(BuildPage):
    def __init__(self, page: Page, top_menu_icons):
        self.page = page
        self.top_menu_icons = top_menu_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_menu_icons,
                    Container(height=10),
                    Text(
                        "Pending Reward",
                        size=20,
                        font_family=APP_FONT_SBOLD,
                        color="black",
                    ),
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


########### <>>>>>>>>>>>> 


# class AirdropUploadPage(BuildPage):
#     def __init__(self, page: Page, post_airdrop):
#         self.page = page
#         self.post_airdrop = post_airdrop
#         self.image_data = None

#         # Form fields for adding an airdrop
#         self.name_input = TextField(label="Airdrop Name",color='black', width=400)
#         self.chain_dropdown = Dropdown(label="Blockchain Chain", bgcolor='grey100',color='black',options=[
#             dropdown.Option("Ethereum"),
#             dropdown.Option("BSC"),
#             dropdown.Option("Sui"),
#             dropdown.Option("Sol"),
#             dropdown.Option("Near"),
#             dropdown.Option("TON"),
#             dropdown.Option("Arbitrum"),
#         ], 
#         width=400)
#         self.funding_input = TextField(label='Funding', color='black', width=400, keyboard_type=KeyboardType.NUMBER)
#         self.status_dropdown = Dropdown(label="Status", bgcolor='grey100',color='black',options=[
#             dropdown.Option("Active"),
#             dropdown.Option("Upcoming"),
#             dropdown.Option("Closed"),
#         ], width=400)
#         self.device_dropdown = Dropdown(label="Device Type",bgcolor='grey100',color='black', options=[
#             dropdown.Option("Desktop"),
#             dropdown.Option("Mobile"),
#             dropdown.Option("Desktop & Mobile"),
#         ], width=400)
#         self.description_input = TextField(label="Description", multiline=True, color='black',width=400)
#         self.category_dropdown = Dropdown(label="Category",bgcolor='grey100',color='black', options=[
#                     dropdown.Option("General Airdrops"),
#                     dropdown.Option("Mining"),
#                     dropdown.Option("Testnets"),
#                     dropdown.Option("NFTs"),
#                     dropdown.Option("SocialFi"),
#                     dropdown.Option("GameFi"),
#                     dropdown.Option("Promotional Airdrops"),
#                     dropdown.Option("Others"),
#                 ])
#         self.external_url_input = TextField(label="External Tracking URL", color='black',width=400)
#         self.start_date_picker = TextField(label="Start Date (YYYY-MM-DD)", color='black',width=400)
#         self.end_date_picker = TextField(label="End Date (YYYY-MM-DD)", color='black',width=400)
#         self.token_ticker = TextField(label="Expected Token Ticker", color='black',width=400)
#         self.twitter_handle = TextField(label="Twitter", color='black',width=400)
#         self.telegram_handle = TextField(label="Telegram", color='black',width=400)
#         self.discord_handle = TextField(label="Discord", color='black',width=400)
#         self.select_image_button = ElevatedButton("Select Image", on_click=lambda _: file_picker.pick_files(allow_multiple=False))

        
#         self.submit_button = ElevatedButton("Submit Airdrop", on_click=self.handle_airdrop_upload)
        
#         # Layout
#         self.page_content = Container(
#             height=self.page.window.height,
#             content=Column(
#                 height=self.page.height,
#                 scroll='auto',
#                 controls=[
                    
#                     Container(height=10),
#                     self.name_input,
#                     self.chain_dropdown,
#                     self.status_dropdown,
#                     self.device_dropdown,
#                     self.funding_input,
#                     self.description_input,
#                     self.category_dropdown,
#                     self.external_url_input,
#                     self.start_date_picker,
#                     self.end_date_picker,
#                     self.token_ticker,
#                     self.twitter_handle,
#                     self.telegram_handle,
#                     self.discord_handle,
#                     self.submit_button,
#                 ]
#             ),
#         )

#         super().__init__(page, self.page_content)

#     async def handle_date_change(self, e: ControlEvent):
#         """handle the date change asynchronously."""
#         selected_date = e.control.value.strftime("%Y-%m-%d")
#         self.airdrop_start_date.value = f"Selected date: {selected_date}"
#         self.airdrop_start_date.update()

#     def pick_image(self, e):
#         """trigger FilePicker to select the image."""
#         self.image_upload_input.pick_files(dialog_title="Choose an image")

#     def on_file_result(self, e: FilePickerResultEvent):
#         if e.files:
#             valid_extensions = [".png", ".jpg", ".jpeg"]
#             file_path = e.files[0].path
#             self.image_data = BytesIO(open(file_path, "rb").read())

#             if any(file_path.endswith(ext) for ext in valid_extensions):
#                 snack_bar = SnackBar(
#                     Text(f"Selected: {file_path}"), open=True
#                 )
#             else:
#                 snack_bar = SnackBar(
#                     Text("Invalid file type. Please select a PNG, JPG, or JPEG."),
#                     open=True,
#                 )
#                 self.image_data = None
#         else:
#             self.image_data = None
#             snack_bar = SnackBar(Text("File selection was cancelled"), open=True)

#         self.page.overlay.append(snack_bar)
#         self.page.update()

    
#     async def handle_airdrop_upload(self, e: ControlEvent):
#         """Handle the airdrop upload asynchronously."""
#         self.show_loading_indicator()
#         await asyncio.sleep(1)  # Simulate async process

       

#         name = self.name_input.value
#         chain = self.chain_dropdown.value
#         status = self.status_dropdown.value
#         device = self.device_dropdown.value
#         funding = self.funding_input.value
#         description = self.description_input.value
#         category = self.category_dropdown.value
#         external_airdrop_url = self.external_url_input.value
#         airdrop_start_date = self.start_date_picker.value
#         airdrop_end_date = self.end_date_picker.value
#         token_ticker = self.token_ticker.value
#         twitter = self.twitter_handle.value
#         telegram = self.telegram_handle.value
#         discord = self.discord_handle.value

#         if not (
#             name
#             and self.image_data
#             and description
#             and category
#             and airdrop_start_date
#         ):
#             snack_bar = SnackBar(Text("Please fill all fields!"), open=True)
#             self.page.overlay.append(snack_bar)
#             self.page.update()
#             return
        
#         form_data = {
#             "name": name,
#             "chain": chain,
#             "status": status,
#             "device": device,
#             "funding": float(funding or 0),
#             "description": description,
#             "category": category,
#             "external_airdrop_url": external_airdrop_url,
#             "expected_token_ticker": token_ticker,
#             "airdrop_start_date": airdrop_start_date,
#             "airdrop_end_date": airdrop_end_date,
#             "project_socials": {
#                 "twitter": twitter,
#                 "telegram": telegram,
#                 "discord": discord,
#             },
#         }

#         try:
#             result = await self.post_airdrop(
#                 image_data=self.image_data,
#                 form_data=form_data
                
#             )
#             await self.show_success_message("Airdrop created successfully!")
#         except Exception as ex:
#             await self.show_success_message(f"Error: {str(ex)}")
#         finally:
#             self.page.update()


class AirdropUploadPage(BuildPage):
    def __init__(self, page: Page, post_airdrop):
        self.page = page
        self.post_airdrop = post_airdrop
        self.image_data = None
        self.choosen_date = {}
        

        self.cupertino_date_picker_start = CupertinoDatePicker(
            date_picker_mode=CupertinoDatePickerMode.DATE_AND_TIME,
            on_change=self.handle_start_date_change,
        )
        
        self.cupertino_date_picker_end = CupertinoDatePicker(
            date_picker_mode=CupertinoDatePickerMode.DATE_AND_TIME,
            on_change=self.handle_end_date_change,
        )

        self.start_date_text = Text(f"{self.choosen_date.get('start_date', 'No date selected')}",
                size=12,
                font_family=APP_FONT_SBOLD,
                color="black"
                )
        self.end_date_text = Text(f"{self.choosen_date.get('end_date', 'No date selected')}",
                size=12,
                font_family=APP_FONT_SBOLD,
                color="black"
                )
        # File Picker
        self.file_picker = FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(self.file_picker)

        # Form fields
        self.name_input = TextField(label="Airdrop Name", color='black', width=400)
        self.chain_dropdown = Dropdown(label="Blockchain Chain", bgcolor='grey100', color='black', options=[
            dropdown.Option("Eth"), dropdown.Option("Bsc"), dropdown.Option("Sui"),
            dropdown.Option("Sol"), dropdown.Option("Near"), dropdown.Option("Ton"), dropdown.Option("Arb")
        ], width=400)
        self.funding_input = TextField(label='Funding', color='black', width=400)
        self.cost_input = TextField(label='Cost To Complete', color='black', width=400)
        self.status_dropdown = Dropdown(label="Status", bgcolor='grey100', color='black', options=[
            dropdown.Option("Active"), dropdown.Option("Upcoming"), dropdown.Option("Closed")
        ], width=100)
        self.device_dropdown = Dropdown(label="Device Type", bgcolor='grey100', color='black', options=[
            dropdown.Option("Desktop"), dropdown.Option("Mobile"), dropdown.Option("Desktop & Mobile")
        ], width=100)
        self.description_input = TextField(label="Description", multiline=True, color='black', width=400)
        self.category_dropdown = Dropdown(label="Category", bgcolor='grey100', color='black', options=[
            dropdown.Option("standard"), dropdown.Option("retroactive"), dropdown.Option("socialfi"),
            dropdown.Option("gamefi"), dropdown.Option("mining") ,dropdown.Option("nft"), dropdown.Option("testnet"),
            dropdown.Option("trading"), dropdown.Option("protocol")
        ], width=150)
        self.external_url_input = TextField(label="External Tracking URL", color='black', width=400)
        self.start_date_picker = CupertinoFilledButton(
            "Select Start Date",
            on_click=lambda e: self.page.open(
                CupertinoBottomSheet(
                    self.cupertino_date_picker_start,
                    height=216,
                    bgcolor='#161C2D',
                    padding=padding.only(top=6),
                )
            ))
        self.end_date_picker = CupertinoFilledButton(
            "Selct End Date",
            on_click=lambda e: self.page.open(
                CupertinoBottomSheet(
                    self.cupertino_date_picker_end,
                    height=216,
                    bgcolor='#161C2D',
                    padding=padding.only(top=6),
                )
            ))
        self.token_ticker = TextField(label="Expected Token Ticker $", color='black', width=400)
        self.twitter_handle = TextField(label="Twitter", color='black', width=400)
        self.telegram_handle = TextField(label="Telegram", color='black', width=400)
        self.discord_handle = TextField(label="Discord", color='black', width=400)

        self.select_image_button = ElevatedButton("Select Image", on_click=lambda _: self.file_picker.pick_files(allow_multiple=False))
        self.submit_button = ElevatedButton("Submit Airdrop", on_click=self.handle_airdrop_upload)

        # Layout
        self.page_content = Container(
            expand=True,
            content=Column(
                height=600,
                scroll='auto',
                controls=[
                    self.name_input, self.chain_dropdown, self.funding_input, self.cost_input,
                    Row([self.status_dropdown, self.device_dropdown, self.category_dropdown,]),
                     self.description_input, self.external_url_input,
                    
                    Row(
                        alignment='spaceBetween',
                        controls=[
                        Column([
                            self.start_date_picker,
                            self.start_date_text
                        ]),
                        Column([
                            self.end_date_picker,
                            self.end_date_text
                        ]),
                    ]),
                    
                     self.token_ticker, self.twitter_handle,
                    self.telegram_handle, self.discord_handle, Row([self.select_image_button, self.submit_button])
                ]
            ),
        )
        super().__init__(page, self.page_content)
        
    
    def handle_start_date_change(self, e: ControlEvent):
        self.choosen_date['start_date'] = e.control.value.strftime('%Y-%m-%dT%H:%M:%S')
        
        self.start_date_text.value = f"{self.choosen_date['start_date']}"
        self.page.update()  

    def handle_end_date_change(self, e: ControlEvent):
        self.choosen_date['end_date'] = e.control.value.strftime('%Y-%m-%dT%H:%M:%S')
        
        self.end_date_text.value = f"{self.choosen_date['end_date']}"
        self.page.update()  
   
            

    async def on_file_result(self, e: FilePickerResultEvent):
        if e.files:
            valid_extensions = [".png", ".jpg", ".jpeg"]
            file_path = e.files[0].path
            if any(file_path.endswith(ext) for ext in valid_extensions):
                self.image_data = BytesIO(open(file_path, "rb").read())
                print(f'{file_path} image added')
                await self.show_success_message(message=f"Selected: {file_path}")

                # self.page.snack_bar = SnackBar(Text(f"Selected: {file_path}"), open=True)
            else:
                self.image_data = None
                self.page.snack_bar = SnackBar(Text("Invalid file type. Please select a PNG, JPG, or JPEG."), open=True)
        else:
            self.image_data = None
            self.page.snack_bar = SnackBar(Text("File selection was cancelled"), open=True)
        self.page.update()

    async def handle_airdrop_upload(self, e: ControlEvent):
        self.page.update()
        await asyncio.sleep(1)

        form_data = {
            "name": self.name_input.value,
            "chain": self.chain_dropdown.value,
            "status": self.status_dropdown.value,
            "device": self.device_dropdown.value,
            "funding": float(self.funding_input.value or 0),
            "cost_to_complete": float(self.cost_input.value or 0), #
            "description": self.description_input.value,
            "category": self.category_dropdown.value,
            "external_airdrop_url": self.external_url_input.value,
            "expected_token_ticker": self.token_ticker.value,
            "airdrop_start_date": self.start_date_text.value,
            "airdrop_end_date": self.end_date_text.value,
            "project_socials": {
                "twitter": self.twitter_handle.value,
                "telegram": self.telegram_handle.value,
                "discord": self.discord_handle.value,
            },
        }
        # print(f'airdrop Data: {form_data}')
        if not form_data["name"] or not self.image_data or not form_data["description"] or not form_data["category"] or not form_data["airdrop_start_date"]:
            self.page.snack_bar = SnackBar(Text("Please fill all fields!"), open=True)
            self.page.update()
            return

        try:
            print(f'airdrop Data: {form_data}')
            await self.post_airdrop(image_data=self.image_data, form_data=form_data)
            await self.show_success_message(message='Airdrop created successfully')
            # print('yp airdrop')

            # self.page.snack_bar = SnackBar(Text("Airdrop created successfully!"), open=True)
        except Exception as ex:
            self.page.snack_bar = SnackBar(Text(f"Error: {str(ex)}"), open=True)
        finally:
            self.page.update()


############## Airdrop Categories


class GeneralAirdropPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class TestnetsPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class RetroactivePage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class MiningPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class NftAirdropPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class SocialFiPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class GameFiPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class PromotionalAirdropsPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class WaitlistPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class OthersPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)


class EmptyPage(BuildPage):
    def __init__(self, page: Page, top_icons):
        self.page = page
        self.top_icons = top_icons

        self.page_content = Container(
            height=self.page.window.height,
            content=Column(
                controls=[
                    self.top_icons,
                    Container(height=10),
                    # page content goes here
                ]
            ),
        )
        super().__init__(page, self.page_content)
