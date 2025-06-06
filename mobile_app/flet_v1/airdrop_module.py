from flet import *
from widgets import activity_circle
import asyncio

image_src = "https://avatars.githubusercontent.com/u/5041459?s=88&v=4"


async def text_controls(field, value):
    controls = []
    field_container = Container(
        content=Text(field, color="white"), padding=padding.only(bottom=2)
    )
    if value == "Confirmed":
        value_container = Container(
            content=Text(
                value,
                color="green",
            )
        )
    elif value == "Unconfirmed":
        value_container = Container(
            content=Text(
                value,
                color="red",
            )
        )

    controls.append(field_container)
    controls.append(value_container)

    return controls


async def status_controls(value):
    controls = []
    field_container = Container(
        content=Text("Status", color="white"), padding=padding.only(bottom=2)
    )
    if value == "Confirmed":
        value_container = Container(
            content=Text(
                value,
                color="green",
            )
        )
    elif value == "Unconfirmed":
        value_container = Container(
            content=Text(
                value,
                color="red",
            )
        )

    controls.append(field_container)
    controls.append(value_container)

    return controls


async def newtask(task_href, task_name, task_img, task_status, task_time, page):

    task_container = Container(
        on_click=task_href,
        border_radius=10,
        padding=padding.only(left=20, top=25),
        border=border.all(color="rgba(255, 255, 255, 0.2)", width=1),
        blur=15,
        bgcolor="rgba(255, 255, 255, 0.1)",
        content=Row(
            alignment="spaceBetween",
            controls=[
                Column(
                    controls=[
                        Row(
                            controls=[
                                Container(
                                    content=CircleAvatar(foreground_image_src=task_img),
                                    padding=padding.only(right=10, bottom=2),
                                ),
                                Container(
                                    padding=padding.only(right=10, bottom=2, left=2),
                                    content=Text(
                                        task_name, weight="bold", size=15, color="white"
                                    ),
                                ),
                            ]
                        ),
                        Container(
                            padding=padding.only(bottom=5),
                            content=Row(controls=status_controls(task_status)),
                        ),
                    ]
                ),
                Container(
                    padding=padding.only(right=20, top=50),
                    content=Text(task_time, color="white60"),
                ),
            ],
        ),
    )
    return task_container


async def trending_airdop_card(
    airdrop_name,
    airdrop_cost,
    airdrop_category,
    airdrop_image,
    airdrop_detail_url,
    page,
    ):
    page.fonts = {
        "montserrat": "utils/fonts/Montserrat-VariableFont_wght.ttf",
        "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",
    }
    trending_airdop = Card(
        elevation=3,
        content=Container(
            on_click=airdrop_detail_url,
            border_radius=6,
            bgcolor="#F8F8F8",
            width=200,
            content=Column(
                [
                    Stack(
                        [
                            Container(
                                content=Image(
                                    src="utils/rectangle-card.svg",
                                    width=200,
                                )
                            ),
                            Container(
                                margin=margin.only(left=50, top=55),
                                width=97,
                                height=97,
                                bgcolor="grey",
                                content=Image(src=airdrop_image),
                                border_radius=50,
                            ),
                        ]
                    ),
                    Container(
                        alignment=alignment.center,
                        content=Text(
                            airdrop_name,
                            color="black",
                            size=17,
                            font_family="montserrat-semi-bold",
                        ),
                    ),
                    Container(
                        margin=margin.only(left=30, right=30, top=10),
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Column(
                                    [
                                        Container(
                                            content=Text(
                                                "Category",
                                                color="black",
                                                font_family="montserrat-semi-bold",
                                            )
                                        ),
                                        Container(
                                            content=Text(
                                                airdrop_category,
                                                color="black",
                                                font_family="montserrat",
                                                weight="bold",
                                            )
                                        ),
                                    ]
                                ),
                                Column(
                                    [
                                        Container(
                                            content=Text(
                                                "Cost",
                                                color="black",
                                                font_family="montserrat-semi-bold",
                                            )
                                        ),
                                        Container(
                                            content=Text(
                                                airdrop_cost,
                                                color="black",
                                                font_family="montserrat",
                                                weight="bold",
                                            )
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ),
                    Container(
                        margin=margin.only(left=70, bottom=10),
                        content=Text(
                            "Join now",
                            color="blue",
                            size=16,
                            font_family="montserrat-semi-bold",
                        ),
                    ),
                ]
            ),
        ),
    )

    return trending_airdop


async def upcoming_airdrops_card(name, category, cost, airdrop_detail_url, image_url, page):
    page.fonts = {
        "montserrat": "utils/fonts/Montserrat-VariableFont_wght.ttf",
        "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",
    }
    upcoming_airdrop = Card(
        elevation=3,
        content=Container(
            on_click=airdrop_detail_url,
            border_radius=6,
            bgcolor="#F8F8F8",
            width=200,
            content=Column(
                [
                    Stack(
                        [
                            Container(
                                content=Image(
                                    src="utils/rectangle-card.svg",
                                    width=200,
                                )
                            ),
                            Container(
                                margin=margin.only(left=50, top=55),
                                width=97,
                                height=97,
                                bgcolor="grey",
                                content=Image(src=image_url),
                                border_radius=50,
                            ),
                        ]
                    ),
                    Container(
                        alignment=alignment.center,
                        content=Text(name, color="black", size=17, weight="bold"),
                    ),
                    Container(
                        margin=margin.only(left=30, right=30, top=10),
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Column(
                                    [
                                        Container(
                                            content=Text(
                                                "Category",
                                                color="black",
                                                font_family="montserrat-semi-bold",
                                            )
                                        ),
                                        Container(
                                            content=Text(
                                                category,
                                                color="black",
                                                font_family="montserrat",
                                                weight="bold",
                                            )
                                        ),
                                    ]
                                ),
                                Column(
                                    [
                                        Container(
                                            content=Text(
                                                "Cost",
                                                color="black",
                                                font_family="montserrat-semi-bold",
                                            )
                                        ),
                                        Container(
                                            content=Text(
                                                f"${cost}",
                                                color="black",
                                                font_family="montserrat",
                                                weight="bold",
                                            )
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ),
                    Container(height=10),
                    Container(
                        margin=margin.only(left=30, bottom=10),
                        content=Text(
                            "Add to watchlist",
                            color="blue",
                            size=16,
                            font_family="montserrat-semi-bold",
                        ),
                    ),
                ]
            ),
        ),
    )
    return upcoming_airdrop


async def user_airdrop_card(
    page, name, duration, status, completion_percent, airdrop_detail_url
    ):
    page.fonts = {
        "montserrat": "utils/fonts/Montserrat-VariableFont_wght.ttf",
        "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",
    }
    APP_FONT_SBOLD = "montserrat-semi-bold"
    APP_FONT = "montserrat"

    card_width = 100
    card_height = 100
    # print(f'fuck you w {page.window.width / 2.2}')
    # print(f'fuck you h {page.window.height / 2.4}')
    # print(f'fuck you w {page.width / 2.6}')
    # print(f'fuck you H {page.height / 2.2}')

    # print(f'actual width {page.width}')

    airdrop_card = Card(
        elevation=3,
        width=180,
        height=375,
        is_semantic_container=False,
        content=Container(
            on_click=airdrop_detail_url,
            alignment=alignment.center,
            # shadow=BoxShadow(
            #     blur_radius=1,
            #     color="grey100",
            #     offset=Offset(-4, 4)  # Positioning of the shadow
            # ),
            # width=180,
            # height=375,
            border_radius=8,
            bgcolor="#F8F8F8",
            content=Column(
                controls=[
                    Stack(
                        controls=[
                            Container(
                                height=120,
                                content=Image(
                                    src="utils/rectangle-card.svg",
                                    width=page.width,
                                    # height=page.height,
                                    fit=ImageFit.COVER,
                                ),
                            ),
                            Container(
                                alignment=alignment.center,
                                margin=margin.only(left=40, top=40),
                                width=card_width,
                                height=card_height,
                                bgcolor="grey",
                                content=Image(src="5983122776472535666.jpg"),
                                border_radius=50,
                            ),
                        ]
                    ),
                    Container(
                        alignment=alignment.center,
                        padding=padding.only(left=10, right=10),
                        content=Text(
                            name, color="black", size=17, font_family=APP_FONT_SBOLD
                        ),
                    ),
                    Container(
                        alignment=alignment.center,
                        content=Text(
                            duration,
                            color="blue",
                            size=14,
                            font_family=APP_FONT,
                            weight="bold",
                        ),
                    ),
                    Container(
                        alignment=alignment.center,
                        content=Text(
                            status, color="#161C2D", size=20, font_family=APP_FONT_SBOLD
                        ),
                    ),
                    Container(
                        alignment=alignment.center,
                        content=Image(src="utils/track/complete-tasks.svg"),
                    ),
                    Container(height=10),
                    Container(
                        padding=padding.only(left=10, right=10),
                        content=Row(
                            alignment="spaceBetween",
                            controls=[
                                Container(
                                    content=Text(
                                        "Task\nCompleted",
                                        weight="bold",
                                        font_family=APP_FONT,
                                        color="black",
                                    )
                                ),
                                activity_circle(completion_percent=completion_percent),
                            ],
                        ),
                    ),
                    Container(height=10),
                ]
            ),
        ),
    )
    return airdrop_card


async def airdrop_card(page, image_url, name, airdrop_detail_url):
    page.fonts = {
        "montserrat": "fonts/Montserrat-VariableFont_wght.ttf",
        "montserrat-bold": "fonts/Montserrat-Bold.ttf",
        "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",
    }
    airdrop = Card(
        elevation=2,
        content=Container(
        border_radius=10,
        height=100,
        width=340,
        bgcolor="#161C2D",
        on_click=airdrop_detail_url,
        content=Row(
            [
                Container(height=100, width=100, content=Image(
                    height=100,
                    width=100,
                    src=image_url)),
                Container(
                    padding=padding.only(top=10, bottom=10),
                    content=Column(
                        controls=[
                            Text(
                                name,
                                color="white",
                                size=16,
                                font_family="montserrat",
                                weight="bold",
                            ),
                            Row(
                                controls=[
                                    Text(
                                        "Rating:",
                                        size=16,
                                        color="white",
                                        font_family="montserrat",
                                        weight="bold",
                                    ),
                                    Image(src="utils/arrow-up.svg"),
                                    Text(
                                        "100",
                                        color="#FFAD33",
                                        font_family="montserrat",
                                        weight="bold",
                                    ),
                                    Image(src="utils/arrow-down.svg"),
                                    Text(
                                        "20",
                                        color="#FFAD33",
                                        font_family="montserrat",
                                        weight="bold",
                                    ),
                                ]
                            ),
                            Text(
                                "19K users",
                                size=13,
                                color="white",
                                font_family="montserrat",
                                weight="bold",
                            ),
                            Container(height=10),
                        ]
                    ),
                ),
            ]
        ),
    )
    )
    return airdrop


async def search_suggestions(page, name, image, upvotes, downvotes, is_verified, total_users):
    page.fonts = {
        "montserrat": "utils/fonts/Montserrat-VariableFont_wght.ttf",
        "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",
    }
    APP_FONT_SBOLD = "montserrat-semi-bold"
    APP_FONT = "montserrat"
    suggestion = Container(
        expand=True,
        content=Column(
            controls=[
                Container(height=5),
                Row(
                    controls=[
                        Container(width=10),
                        Container(content=Image(src=image)),
                        Container(
                            padding=padding.only(top=10, bottom=10),
                            width=page.width * 107,
                            content=Column(
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                name,
                                                size=15,
                                                font_family=APP_FONT_SBOLD,
                                                color="black",
                                            ),
                                            Image(src="utils/verified_check.svg"),
                                        ]
                                    ),
                                    Row(
                                        [
                                            Row(
                                                controls=[
                                                    Image(src="utils/arrow-up.svg"),
                                                    Text(
                                                        upvotes,
                                                        color="#FFAD33",
                                                        font_family=APP_FONT_SBOLD,
                                                    ),
                                                ]
                                            ),
                                            Row(
                                                controls=[
                                                    Image(src="utils/arrow-down.svg"),
                                                    Text(
                                                        downvotes,
                                                        color="#FFAD33",
                                                        font_family=APP_FONT_SBOLD,
                                                    ),
                                                ]
                                            ),
                                            Container(width=20),
                                            Row(
                                                controls=[
                                                    Text(
                                                        f"{total_users}K users",
                                                        color="black",
                                                        weight="bold",
                                                        font_family=APP_FONT,
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                    Container(content=Image(src="utils/line.svg")),
                                ]
                            ),
                        ),
                    ]
                ),
            ]
        ),
    )

    return suggestion
