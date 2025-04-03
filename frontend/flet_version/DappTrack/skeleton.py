from flet import *

def trending_airdrop_skeleton(page):
    return Container(
        content=Row(
        
        controls=[
            Container(
                bgcolor='#E0E0E0',
                width=200,
                height=300,
            ),
            Container(
                bgcolor='#E0E0E0',
                width=200,
                height=300,
            ),
            Container(
                bgcolor='#E0E0E0',
                width=200,
                height=300,
            )
            ]
        )
    )

def create_home_skeleton(page):
    airdrop_card = Container(
        margin=margin.only(top=20),
        width=300,
        height=100,
        bgcolor='#E0E0E0',
        content=Column(
            controls=[
                Container(
                    
                    content=Row(
                        controls=[
                            Container(
                                height=100,
                                width=100,
                                border_radius=8,
                                bgcolor=' #FAFAFA'
                                    ),
                            # Text skeleton
                            Container(
                                content=Column(
                                controls=[
                                    Container(
                                        height=16,
                                        width=150,
                                        border_radius=8,
                                        bgcolor='#FAFAFA'
                                    ),
                                    Container(
                                        height=16,
                                        width=180,
                                        border_radius=8,
                                        bgcolor='#FAFAFA'
                                    ),
                                    Container(
                                        height=13,
                                        width=100,
                                        border_radius=8,
                                        bgcolor='#FAFAFA'
                                    ),
                                ]
                            )
                            )
                        ]
                    )
                )
            ]
        )
    )


    page_content =  Column(
        controls=[
            Row(
                alignment='spaceBetween',
                controls=[
                    # Top icons
                    Container(
                        width=43,
                        height=43,
                        border_radius=20,
                        bgcolor='#E0E0E0',

                    ),
                    Container(width=5),
                    Container(
                        width=238,
                        height=38,
                        border_radius=8.6,
                        bgcolor='#E0E0E0',
                    ),
                    Container(width=5),
                    Container(
                        width=43,
                        height=43,
                        border_radius=20,
                        bgcolor='#E0E0E0',

                    ),         
                    
                ]
            ),
            Container(height=15),
             # announcement
            Container(
                bgcolor='#E0E0E0',
                width=1500,
                padding=7,
                border_radius=10,
                content=Row(
                    controls=[
                        Column(
                            [
                                Container(
                                    height=16,
                                    width=100,
                                    border_radius=8,
                                    bgcolor='#FAFAFA'
                                ),
                                Container(
                                    height=14,
                                    width=200,
                                    border_radius=8,
                                    bgcolor='#FAFAFA'
                                ),
                                Container(
                                    height=14,
                                    width=50,
                                    border_radius=8,
                                    bgcolor='#FAFAFA'
                                ),

                            ],

                        ),
                        Container(
                            margin=margin.only(top=30),
                            bgcolor='#E0E0E0',
                            padding=padding.all(9),
                            width=37,
                            height=37,
                            border_radius=20,
                            alignment=alignment.bottom_left
                        ),

                    ],
                    alignment='spaceBetween'
                )
            ),
            Container(height=15),
            # Trending airdrop
            Container(
                height=22,
                width=150,
                border_radius=8,
                bgcolor='#E0E0E0'
                ),
            #cards
            Container(
                content=Row(
                
                controls=[
                    Container(
                        border_radius=6,
                        bgcolor='#E0E0E0',
                        width=200,
                        height=300,
                    ),
                    Container(
                        border_radius=6,
                        bgcolor='#E0E0E0',
                        width=200,
                        height=300,
                    ),
                    Container(
                        border_radius=6,
                        bgcolor='#E0E0E0',
                        width=200,
                        height=300,
                    )
                    ]
                )
            ),
            Container(height=20),
            # my airdrops
            Container(
                height=26,
                width=150,
                border_radius=8,
                bgcolor='#E0E0E0'
                ),
            
            # airdrop activiy overview
            Container(
                border_radius=10,
                padding=padding.only(left=20, top=10, bottom=10, right=10),
                width=500,
                bgcolor='#E0E0E0',
                content=Row(
                    alignment='spaceBetween',
                    controls = [ 
                        Column(
                            [
                                Container(
                                    height=17,
                                    width=80,
                                    border_radius=8,
                                    bgcolor='#FAFAFA'
                                ),
                                Container(
                                    height=15,
                                    width=200,
                                    border_radius=8,
                                    bgcolor='#FAFAFA'
                                ),
                            ]
                        ),
                        Container(width=5),
                        #progress ring
                        Container(
                            width=50,
                            height=50,
                            border_radius=25,
                            margin=margin.only(right=10),
                            bgcolor='#FAFAFA'
                            ),
                        
                    ]
                )
            ),
            Container(height=10),
            Row(
                alignment="spaceBetween",
                controls=[
                    #airdrop category
                    Container(
                        height=24,
                        width=150,
                        border_radius=8,
                        bgcolor='#E0E0E0'
                        ),
                    # see all
                    Container(
                        width=70,
                        height=36,
                        border_radius=5,
                        bgcolor='#E0E0E0'
                        )
                ]
            ),
            # mining
            Container(
                height=20,
                width=100,
                border_radius=8,
                bgcolor='#E0E0E0'
                ),
            Row(
                controls=[
                    airdrop_card, airdrop_card
                ]
            )


            
        ]
    )

    return Container(
        content=page_content)


def create_track_skeleton(page):
    return Container(
    alignment=alignment.center,
    
    content=Column(

    
    controls=[
        Container(
                border_radius=10,
                padding=padding.only(left=20, top=10, bottom=10, right=10),
                width=page.width,
                bgcolor='#E0E0E0',
                content=Row(
                    alignment='spaceBetween',
                    controls = [ 
                        Column(
                            [
                                Container(
                                    height=17,
                                    width=80,
                                    border_radius=8,
                                    bgcolor='#FAFAFA'
                                ),
                                Container(
                                    height=15,
                                    width=200,
                                    border_radius=8,
                                    bgcolor='#FAFAFA'
                                ),
                            ]
                        ),
                        Container(width=5),
                        # progress ring
                        Container(
                            width=50,
                            height=50,
                            border_radius=25,
                            margin=margin.only(right=10),
                            bgcolor='#FAFAFA'
                            ),
                        
                    ]
                )
            ),
        ResponsiveRow(
            spacing=10,
            controls=[
                Container(
                    col={'xs': 6,"sm": 4, "md": 4, "lg": 2},
                    border_radius=6,
                    width=180,
                    height=375,
                    bgcolor='#E0E0E0',
                ),
                
                Container(
                    col={'xs': 6,"sm": 4, "md": 4, "lg": 2},
                    border_radius=6,
                    width=180,
                    height=375,
                    bgcolor='#E0E0E0',
                ),
                Container(
                    col={'xs': 6,"sm": 4, "md": 4, "lg": 2},
                    border_radius=6,
                    width=180,
                    height=375,
                    bgcolor='#E0E0E0',
                ),
                Container(
                    col={'xs': 6,"sm": 4, "md": 4, "lg": 2},
                    border_radius=6,
                    width=180,
                    height=375,
                    bgcolor='#E0E0E0',
                ),
                Container(
                    col={'xs': 6,"sm": 4, "md": 4, "lg": 2},
                    border_radius=6,
                    width=180,
                    height=375,
                    bgcolor='#E0E0E0',
                ),
                Container(
                    col={'xs': 6,"sm": 4, "md": 4, "lg": 2},
                    border_radius=6,
                    width=180,
                    height=375,
                    bgcolor='#E0E0E0',
                ),
                
            ]
        ),
        
    ]
    )
    )


def create_referral_skeleton(page):
    return Container(
        content=Column(
            controls=[
                Row(alignment='spaceBetween',
                                            controls = [        
                                                
                                                Row(
                                                    controls=[
                                                        Container(bgcolor='#E0E0E0', height=60, width=60, border_radius=30), #profile
                                                        Container(bgcolor='#E0E0E0', height=20, width=170, border_radius=6), #name
                                                        
                                                        ]
                                            ), 
                                                Container(bgcolor='#E0E0E0', height=20, width=44, border_radius=6) # point earned
                                            ]
                ),
                Row(alignment='spaceBetween',
                                            controls = [        
                                                
                                                Row(
                                                    controls=[
                                                        Container(bgcolor='#E0E0E0', height=60, width=60, border_radius=30), #profile
                                                        Container(bgcolor='#E0E0E0', height=20, width=170, border_radius=6), #name
                                                        
                                                        ]
                                            ), 
                                                Container(bgcolor='#E0E0E0', height=20, width=44, border_radius=6) # point earned
                                            ]
                ),
                Row(alignment='spaceBetween',
                                            controls = [        
                                                
                                                Row(
                                                    controls=[
                                                        Container(bgcolor='#E0E0E0', height=60, width=60, border_radius=30), #profile
                                                        Container(bgcolor='#E0E0E0', height=20, width=170, border_radius=6), #name
                                                        
                                                        ]
                                            ), 
                                                Container(bgcolor='#E0E0E0', height=20, width=44, border_radius=6) # point earned
                                            ]
                ),
                Row(alignment='spaceBetween',
                                            controls = [        
                                                
                                                Row(
                                                    controls=[
                                                        Container(bgcolor='#E0E0E0', height=60, width=60, border_radius=30), #profile
                                                        Container(bgcolor='#E0E0E0', height=20, width=170, border_radius=6), #name
                                                        
                                                        ]
                                            ), 
                                                Container(bgcolor='#E0E0E0', height=20, width=44, border_radius=6) # point earned
                                            ]
                ),
                Row(alignment='spaceBetween',
                                            controls = [        
                                                
                                                Row(
                                                    controls=[
                                                        Container(bgcolor='#E0E0E0', height=60, width=60, border_radius=30), #profile
                                                        Container(bgcolor='#E0E0E0', height=20, width=170, border_radius=6), #name
                                                        
                                                        ]
                                            ), 
                                                Container(bgcolor='#E0E0E0', height=20, width=44, border_radius=6) # point earned
                                            ]
                ),
    
    ])    
    )

def create_profile_skeleton():
    return Container(
          content=Column(
            controls=[
                Container(
                    border_radius=6,
                    width=90,
                    height=22,
                    bgcolor='#E0E0E0',
                ),
                
                Row(
                    controls=[
                        # Drop points
                        Container(
                            border_radius=6,
                            width=40,
                            height=22,
                            bgcolor='#E0E0E0',
                        ),
                        Container(
                            border_radius=6,
                            width=60,
                            height=15,
                            bgcolor='#E0E0E0',
                        ),
                    ]
                ),
                Row(
                    alignment='spaceBetween',
                    controls=[
                        # recent activity
                        Container(
                            border_radius=6,
                            width=80,
                            height=15,
                            bgcolor='#E0E0E0',
                        ),
                        # hour ago
                        Container(
                            border_radius=6,
                            width=50,
                            height=15,
                            bgcolor='#E0E0E0',
                        ),
                    ]
                ),
                # recent airdrop 
                Row(
                    controls=[
                        Container(
                            border_radius=6,
                            height=400,
                            width=200,
                            bgcolor='#E0E0E0',
                        ),
                        Container(
                            border_radius=6,
                            height=400,
                            width=200,
                            bgcolor='#E0E0E0',
                        ),
                        Container(
                            border_radius=6,
                            height=400,
                            width=200,
                            bgcolor='#E0E0E0',
                        ),
                    ]
                )
            ]
          )
    )


def create_airdrop_list_skeleton():
    airdrop_card = Container(
        width=340,
        height=100,
        bgcolor='#E0E0E0',
        border_radius=10,
        margin=margin.only(left=10),
        content=Column(
            controls=[
                Container(
                    
                    content=Row(
                        controls=[
                            Container(
                                height=100,
                                width=100,
                                border_radius=8,
                                bgcolor=' #FAFAFA'
                                    ),
                            # Text skeleton
                            Container(
                                content=Column(
                                controls=[
                                    Container(
                                        height=16,
                                        width=160,
                                        border_radius=8,
                                        bgcolor='#FAFAFA'
                                    ),
                                    Container(
                                        height=16,
                                        width=200,
                                        border_radius=8,
                                        bgcolor='#FAFAFA'
                                    ),
                                    Container(
                                        height=13,
                                        width=110,
                                        border_radius=8,
                                        bgcolor='#FAFAFA'
                                    ),
                                    
                                ]
                            )
                            )
                        ]
                    )
                )
            ]
        )
    )

    skeleton = Column(
        controls=[]
    )
    for i in range(10):
        skeleton.controls.append(
            Container(
                # padding=padding.only(left=20),
                content=airdrop_card
            )
        )
    return Container(content=skeleton)



