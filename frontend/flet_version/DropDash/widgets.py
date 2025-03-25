from flet import *



BG = '#041955'
FWG = '#97b4ff'
FG = '#3450a1'
PINK = '#eb06ff'




#   # Animation Functions

# def shrink(page, current_page):
#     if current_page:
#         current_page.content.width = 120
#         current_page.content.scale = transform.Scale(
#             0.6, alignment=alignment.center_right
#         )

#         current_page.alignment = alignment.center_right
#         # current_page.animate = animation.Animation(500, AnimationCurve.EASE_IN_OUT)
#         current_page.update()
#         page.update()

# def restore(page, current_page):
#     if current_page:
#         current_page.content.width = 400
#         current_page.content.scale = transform.Scale(
#             1, alignment=alignment.center_right
#         )
#         page.update()




def airdrop_activity_overview(page, percent, total_airdrops):
    print(total_airdrops)
    page.fonts = {
            "montserrat": "utils/fonts/Montserrat-VariableFont_wght.ttf",
            "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",

        }
    progress_label = Text(
            total_airdrops,  
            size=15,
            color='black',
            text_align="center"  
        )
        
        # Circular ProgressRing 
    progress_ring = ProgressRing(
            value=0.75,  # Completion percentage (75%)
            width=45,
            height=45,  
            stroke_width=6,  # Thickness of the ring
            color='#004CFF', 
            bgcolor='#C7D6FB',  
            stroke_cap = 'round' 
        )
    progress_container = Stack(
            controls=[
                progress_ring, 
                Container(   
                    content=progress_label,
                    alignment=alignment.center,  
                    width=45,  
                    height=45,
                )
            ],
        )

            # Create colored circles for "Rewarded" and "Pending"
    completion_dot_color = Container(
                width=12,
                height=12,
                bgcolor='#004CFF',  # Match the color of the progress ring
                border_radius=8,  # Make it circular
            )
            
    pending_dot_color = Container(
                width=12,
                height=12,
                bgcolor='#C7D6FB',  # Match the background color of the progress ring
                border_radius=8,  # Make it circular
            )

    activity_overview = Container(
            border_radius=10,
            padding=padding.only(left=20, top=10, bottom=10, right=10),
            width=1500,
            border=border.all(color="rgba(66, 133, 244, 1)", width=1),
            content=Row(
                alignment='spaceBetween',
                controls = [ 
                    Column(
                        [
                            Text(
                                "Airdrops Engaged in",  
                                size=17,
                                weight="bold",
                                font_family="montserrat-semi-bold",
                                color='black',
                                text_align="center"  
                            ),
                            Row([
                                Row([
                                    completion_dot_color,  
                                    Text(
                                        "Completed",
                                        font_family="montserrat", 
                                        weight='bold', 
                                        size=15,
                                        color='black',
                                        text_align="center"  
                                    ),
                                ]),
                                Row([
                                    pending_dot_color, 
                                    Text(
                                        "Pending",
                                        font_family="montserrat",  
                                        weight='bold', 
                                        size=15,
                                        color='black',
                                        text_align="center"  
                                    ),
                                ])
                            ])
                        ]
                    ),
                    Container(width=5),
                    Container(
                        padding=padding.only(right=10),
                        content=progress_container),
                    
                ]
            )
    )
    
    return activity_overview

def activity_circle(completion_percent):
    progress_label = Text(
            f'{completion_percent}%',  
            size=14,
            color='black',
            text_align="center"  
        )
        
        # Circular ProgressRing 
    progress_ring = ProgressRing(
            value=0.75,  # Completion percentage (75%)
            width=45,
            height=45,  
            stroke_width=6,  # Thickness of the ring
            color='#004CFF', 
            bgcolor='#C7D6FB',
            stroke_cap = 'round'  
            
        )
    progress_container = Stack(
            controls=[
                progress_ring, 
                Container(   
                    content=progress_label,
                    alignment=alignment.center,  
                    width=45,  
                    height=45,
                )
            ],
        )

    return progress_container


def drop_down_menu(menu_names, on_click):
    menu_items = []
          
    menu = Card(
        elevation=3,
        content=Container(
            bgcolor='white',
            width=190,

            visible=False, 
            # shadow=BoxShadow(
            #     blur_radius=1,  
            #     color="grey100",  
            #     offset=Offset(-4, 4)  # Positioning of the shadow 
            # ),
            padding=padding.only(left=10, right=10, bottom=10),
            content=Column(
                controls=[
                    Row(
                        controls=[
                            Container(width=136),
                            Container(
                                padding=padding.only(left=10),
                                alignment=alignment.center_right,
                                content=Image(src='icons/x.svg'),
                                on_click=on_click,
                            ),
                            
                        ]
                    ),
                    menu_names,
                
                    
                    
                    
                    
                    

                    
                    
                ]
            )
    )
    )
  
    return menu


def top_menu_icons(left_icon, left_icon_action, search_bar, search_bar_action, notification_action):
    icons = Row(alignment='spaceBetween',

                    controls=[
                        # Menu Icon
                       Container(
                            content=Image(src=left_icon, width=22, height=22),
                            width=43,  
                            height=43,  
                            on_click=left_icon_action,
                            border_radius=20, 
                            bgcolor='#F8F8F8',  
                            alignment=alignment.center  # 
                        ),
                        Container(width=5),
                        Container(on_click=search_bar_action,
                                content=search_bar),
                        Container(width=5),
                        Container(
                                on_click=notification_action,
                                content=Image(src="icons/notification-2-line.svg", badge='20',width=22, height=22),  
                                width=43,  
                                height=43,  
                                border_radius=20, 
                                bgcolor='#F8F8F8',  
                                alignment=alignment.center  # 
                                ),
                        

                    ]
                    )

    return icons


def timer_circle(timer):
    progress_label = Text(
            f'3:0:2:2',  
            size=14,
            color=colors.WHITE,
            text_align="center"  
        )
        
        # Circular ProgressRing 
    progress_ring = ProgressRing(
            value=0.75,  # Completion percentage (75%)
            width=150,
            height=150,  
            stroke_width=25,  # Thickness of the ring
            color='#FFAD33', 
            bgcolor='white',
            stroke_cap = 'round'  
            
        )
    timer_container = Stack(
            controls=[
                progress_ring, 
                Container(   
                    content=progress_label,
                    alignment=alignment.center,  
                    width=150,  
                    height=150,
                )
            ],
        )

    return timer_container


def top_icons(page, go_back, page_name):
    page.fonts = {
            "montserrat": "fonts/Montserrat-VariableFont_wght.ttf",
            "montserrat-bold": 'fonts/Montserrat-Bold.ttf',
            "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",
        }
    return Row(                    
        controls=[
            
            Container(
                width=43,
                height=43,
                border_radius=20,
                bgcolor='#F8F8F8',
                alignment=alignment.center,
                on_click=go_back,
                content=Image(src='icons/arrow-left.svg', width=22, height=22)
            ),
            Container(width=20),
            Text(page_name, font_family='montserrat-bold',size=20, color='black')

        ]

    )


def level_bar(page):
    level_bar = ProgressBar(
        width=500,
        height=20,
        border_radius=5,
        value=0.3,
        color='#161C2D',
        bgcolor='#95989A'


    )

    return level_bar

def task_progress_bar(page):
    task_progress_bar = ProgressBar(
        width=300,
        height=15,
        border_radius=10,
        value=0.3,
        color='white',
        bgcolor='#95989A'


    )

    return task_progress_bar