from flet import *
from typing import Any, Optional, Union
from airdrop_module import (
    search_suggestions,
    trending_airdop_card, 
    airdrop_card, 
    upcoming_airdrops_card, user_airdrop_card)
from build_page import (
    LandingPage,
    SignupPage, 
    LoginPage, 
    HomePage, 
    SearchPage, 
    SideMenuPage,
    NotificationPage,
    AnalyticPage,
    AirdropDetailPage,
    AirdropUploadPage,
    AllAirdropsPage,
    RefferalsPage,
    ProfilePage,
    WatchlistPage,
    SettingsPage,
    AccountSettingsPage,
    NotificationSettingsPage,
    ChangePasswordPage,
    DeleteAccountPage,
    LanguagePage,
    ReportPage,
    TermsAndConditionPage,
    PrivacyPolicyPage,
    VersionInfoPage,
    # Airdrop Tracker Sub pages
    ActivePage,
    CompletedPage,
    PendingPage,
    )
from widgets import (
    airdrop_activity_overview, 
    activity_circle,
    drop_down_menu,
    top_menu_icons,
    task_progress_bar,
    drop_down_menu,
    top_icons,
    level_bar)
from auth import (
    signup_user, 
    login_user, 
    get_user_data, 
    fetch_referrals,
    post_airdrop, 
    logout_user
    )
import time
import asyncio
from collections import OrderedDict
from skeleton import (
    create_home_skeleton,
    create_track_skeleton, 
    trending_airdrop_skeleton, 
    create_referral_skeleton, 
    create_profile_skeleton,
    create_airdrop_list_skeleton
    )
from time import sleep
import os
from airdrop_list import airdrop_list


    

   




    
    # def goto_all_airdrops():
    #     page.remove(home.base)
    #     page.add(main_page.base)
    #     page.update()
    
    
APP_FONT = 'montserrat'
APP_FONT_SBOLD = 'montserrat-semi-bold'
APP_FONT_BOLD = 'montserrat-bold'



# async def splash_screen(page: Page):
#     page.bgcolor = '#161C2D'
#     page.window.width = 390
#     page.window.height = 900
#     splash_icon = Container(
#         expand=True,
#         alignment=alignment.center,
#         content=Image(src='splas.png', width=300, height=300)
#     )
#     page.controls.append(splash_icon)
#     await page.update_async()
#     await asyncio.sleep(2)

async def main(page: Page):
    page.bgcolor = 'white'
    page.name
    current_page_id = '/' 
    page.border_radius = 35
    page.adaptive = True
    page.title = "DropDash"
    page.padding = 0
    page.spacing = 0
    page.vertical_alignment = 'stretch'

    page.window.orientation = Orientation.PORTRAIT
    page.window.width = 390
    page.window.height = 900

    
    
    

    user_signed_in = False

    def event(e):
        if e.data == 'detach' and page.platform == PagePlatform.ANDROID:
            os._exit(1)
    
    page.on_app_lifecycle_state_change = event






    class LimitedCache(OrderedDict):
        def __init__(self, max_size=5):
            self.max_size = max_size
            super().__init__()

        def __setitem__(self, key, value):
            if len(self) >= self.max_size:
                self.popitem(last=False)  # remove the oldest item
            super().__setitem__(key, value)


    async def handle_login_success():
        user_json = await get_user_data()
        print(f'Current User Data:: {user_json}')

        class AppState:
            def __init__(self, page):
                self.page = page
                self.page_cache = LimitedCache(max_size=5)
                self.active_page = None
                self.navigation_stack = ['/']
                self.active_page = None
                self.is_shimmering = True
                self.page.fonts = {
                    "montserrat": "fonts/Montserrat-VariableFont_wght.ttf",
                    "montserrat-bold": 'fonts/Montserrat-Bold.ttf',
                    "montserrat-semi-bold": "fonts/Montserrat-SemiBold.ttf",
                }

                
                # when adding a new page remember .base to avoid AttributeError 
            def shimmer_animation(self, skeleton_card):
                
                while self.is_shimmering:
                    # if skeleton_card.content != self.create_track_skeleton():
                    for control in skeleton_card.content.controls:
                        control.opacity = 0.2 if control.opacity == 0.3 else 0.3
                    page.update()
                    sleep(0.5)

            def stop_shimmer(self):
                self.is_shimmering = False

            def on_skeleton_update(self): # pass into the page instance
                self.stop_shimmer()


            async def navigate_to(self, e, page_id):
                
                # if self.navigation_stack and self.navigation_stack[-1] == page_id:
                #     return
                if self.active_page == page_id:
                    return
                self.active_page = page_id
                page.controls.clear()
                if self.navigation_stack and self.navigation_stack[-1] != page_id:
                    self.navigation_stack.append(page_id)
                    print('page appended')
                
                self.active_page = page_id
                if page_id == '/':
                    print('Home button clicked')
                    update_icon('home')

                                    
                    page.add(Container(content=home.base))
                    

                elif page_id == '/notification':
                    self.is_shimmering = True
                    notification = await create_notification_page(page=page)
                    page.add(Container(content=notification.base))

                elif page_id == '/search':
                    print(page_id)
                    if '/search' not in self.page_cache:
                        
                        cached_data = {
                            'query': '',
                            'filters': [],
                            'top_menu_icons': top_menu_icons(
                                        left_icon="icons/arrow-left.svg", 
                                        left_icon_action=lambda e: app_state.go_back(e, page=page ),


                                        search_bar=Container(
                                            padding=padding.only(left=2, right=2),
                                            content= TextField(
                                            label='Search',
                                            text_size=15,
                                            label_style=TextStyle(color='black'),
                                            content_padding=padding.only(left=23, top=20,right=22),
                                            autofocus=True,
                                            color='black',
                                            cursor_color='black',
                                            width=238, border_width=0.6, suffix=Icon(name="close", color=colors.BLACK), 
                                            border_color='black', height=38, border_radius=8.6
                                            ),
                                        ),

                                        search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                                        notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification'))
                                        ),
                            
                        }
                    
                        self.page_cache[page_id] = await create_search_page(cached_data, page)
                    search_page = self.page_cache[page_id]
                    page.add(Container(content=search_page.base))
                
                elif page_id == '/side_menu':
                    self.is_shimmering = True
                    self.page_cache[page_id] = await create_side_menu_page(page=page)
                    side_menu = self.page_cache[page_id]
                    page.add(Container(content=side_menu.base))
                    

                elif page_id == '/track':
                    print('Analytic button clicked')
                    update_icon('track')
                    self.is_shimmering = True
                    # skeleton_page = create_track_skeleton(page)
                    # page.add(skeleton_page)
                    # page.update()

                    # asyncio.create_task(asyncio.to_thread(self.shimmer_animation, skeleton_page))
                    # await asyncio.sleep(0.1)

                    
                    # check to see if the page instance exists in the cache, if not, create an instance.
                    # if '/track' not in self.page_cache:      
                    cached_data = {
                        'top_menu_icons': top_menu_icons(
                                                left_icon="icons/menu-2-line.svg", 
                                                search_bar=Image(src='utils/search.svg', width=38, height=38),
                                                left_icon_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/side_menu')),
                                                search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                                                notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification'))
                                                ),
                        
                    }
                    self.page_cache[page_id] = await create_track_page(cached_data, page)
                    asyncio.create_task(asyncio.to_thread(self.shimmer_animation, self.page_cache[page_id].track_skeleton))

                    
                    
                    track_page = self.page_cache[page_id]
                    # sks = track_page.page_content.controls[2].controls[2].content 
                    

                    
                
                    page.add(Container(content=track_page.base))

                    

                elif page_id =='/airdrop_detail':
                    self.is_shimmering = True
                    airdrop_detail = await create_airdrop_detail_page(page=page)
                    page.add(Container(content=airdrop_detail.base))
                    

                elif page_id == '/all_airdrops':
                    self.is_shimmering = True
                    all_airdrops = await create_all_airdrops_page(page=page)
                    asyncio.create_task(asyncio.to_thread(self.shimmer_animation, all_airdrops.airdrop_list_skeleton))
                    page.add(Container(content=all_airdrops.base))

                elif page_id == '/referrals':
                    update_icon('referrals')
                    self.is_shimmering = True


                    if '/referrals' not in  self.page_cache:
                        cached_data = {
                            'top_menu_icons': top_menu_icons(
                            left_icon="icons/menu-2-line.svg", 
                            search_bar=Image(src='utils/search.svg', width=38, height=38),
                            left_icon_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/side_menu')),
                            search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                            notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification'))
                            )
                        }
                        self.page_cache[page_id] = await create_referral_page(cached_data, page)
                        asyncio.create_task(asyncio.to_thread(self.shimmer_animation, self.page_cache[page_id].referral_skeleton))
                    
                    referral_page = self.page_cache[page_id]
                    
                    page.add(Container(content=referral_page.base))
                    

                elif page_id == '/profile':
                    update_icon('profile')
                    self.is_shimmering = True
                    
                    if '/profile' not in self.page_cache:
                        cached_data = {
                            'top_menu_icons': top_menu_icons(
                            left_icon="icons/menu-2-line.svg", 
                            search_bar=Image(src='utils/search.svg', width=38, height=38),
                            left_icon_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/side_menu')),
                            search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                            notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification'))
                            ),
                            'airdrop_activity_overview': airdrop_activity_overview(page=page, percent=75, total_airdrops=200)
                        }
                    
                        self.page_cache[page_id] = await create_profile_page(cached_data, page)
                        asyncio.create_task(asyncio.to_thread(self.shimmer_animation, self.page_cache[page_id].profile_skeleton))
                    
                    profile_page = self.page_cache[page_id]
                    
                    page.add(Container(content=profile_page.base))
                    
                    
                elif page_id == '/watchlist':
                    self.is_shimmering = True
                    
                    self.page_cache[page_id] = await create_watchlist_page(page=page)
                    asyncio.create_task(asyncio.to_thread(self.shimmer_animation, self.page_cache[page_id].airdrop_list_skeleton))
                    watchlist = self.page_cache[page_id] 
                    page.add(Container(content=watchlist.base))
                
                elif page_id == '/settings':
                    self.page_cache[page_id] = await create_settings_page(page=page)
                    settings = self.page_cache[page_id]
                    page.add(Container(content=settings.base))

                elif page_id == '/account_settings':
                    self.page_cache[page_id] = await create_account_settings_page(page=page)
                    account_settings = self.page_cache[page_id]
                    page.add(Container(content=account_settings.base))

                elif page_id == '/notification_settings':
                    self.page_cache[page_id] = await create_notification_settings_page(page=page)
                    notification_settings = self.page_cache[page_id]
                    page.add(Container(content=notification_settings.base))
                
                elif page_id == '/password_settings':
                    self.page_cache[page_id] = await create_change_password_page(page=page)
                    password_settings = self.page_cache[page_id]
                    page.add(Container(content=password_settings.base))
                
                elif page_id == '/language_settings':
                    self.page_cache[page_id] = await create_language_settings_page(page=page)
                    language_settings = self.page_cache[page_id]
                    page.add(Container(content=language_settings.base))
                
                elif page_id == '/report':
                    self.page_cache[page_id] = await create_report_page(page=page)
                    report = self.page_cache[page_id]
                    page.add(Container(content=report.base))

                elif page_id == '/terms':
                    self.page_cache[page_id] = await create_terms_page(page=page)
                    terms_page = self.page_cache[page_id]
                    page.add(Container(content=terms_page.base))

                elif page_id == '/privacy_policy':
                    self.page_cache[page_id] = await create_privacy_policy_page(page=page)
                    privacy_policy_page = self.page_cache[page_id]
                    page.add(Container(content=privacy_policy_page.base))
                
                elif page_id == '/version_info':
                    self.page_cache[page_id] = await create_version_info_page(page=page)
                    version_info_page = self.page_cache[page_id]
                    page.add(Container(content=version_info_page.base))
                
                elif page_id == '/delete_account':
                    self.page_cache[page_id] = await create_delete_account_page(page=page)
                    delete_account_page = self.page_cache[page_id]
                    page.add(Container(content=delete_account_page.base))
                
                # Airdrop Tracker Sub pages

                elif page_id == '/active_page':
                    self.page_cache[page_id] = await create_active_page(page=page)
                    active_page = self.page_cache[page_id]
                    page.add(Container(content=active_page.base))
                
                elif page_id == '/completed_page':
                    self.page_cache[page_id] = await create_completed_page(page=page)
                    completed_page = self.page_cache[page_id]
                    page.add(Container(content=completed_page.base))

                elif page_id == '/pending_page':
                    self.page_cache[page_id] = await create_pending_page(page=page)
                    pending_page = self.page_cache[page_id]
                    page.add(Container(content=pending_page.base))
                elif page_id == '/pending_page':
                    self.page_cache[page_id] = await create_pending_page(page=page)
                    pending_page = self.page_cache[page_id]
                    page.add(Container(content=pending_page.base))
                elif page_id == '/airdrop_upload' and user_json.get('is_admin'):
                    print(f'{user_json  }')
                    self.page_cache[page_id] = await create_airdrop_upload_page(page=page)
                    airdrop_upload_page = self.page_cache[page_id]
                    page.add(Container(content=airdrop_upload_page.base))
                
                    
                
            
            def go_back(self, e, page):
                if len(self.navigation_stack) > 1:
                    
                    self.navigation_stack.pop()
                    # Get the previous route
                    previous_route = self.navigation_stack[-1]
                    
                    # Clear page and load the previous route
                    page.controls.clear()
                    if previous_route in self.page_cache:
                        print(f'the pageee {previous_route}')
                        page.add(Container(content=self.page_cache[previous_route].base))
                    else:
                        # Fallback: Reload the previous route dynamically
                        print(f"Route {previous_route} not cached. Recreating page...")
                        asyncio.run(self.navigate_to(e, page_id=previous_route))
                        
                        
                else:
                    print("No previous route to navigate back to.")
                    self.navigation_stack = ['/']
                    page.controls.clear()
                    page.add(Container(content=home.base))


                page.update()
            
            async def load_track_data(self, num):
                tracked_airdrops = ListView(
                    expand=True,
                    spacing=10,
                    controls=[
                        airdrop_activity_overview(page=page, percent=75, total_airdrops=200),
                    ]
                )
                page_width = page.width
                print(f'the page width {page_width}')
                # Temporary row to hold two cards at a time
                # row = None

                row = ResponsiveRow(
                    controls=[

                    ]
                )

                for i, name in enumerate(airdrop_list[:num]):
                    card = await user_airdrop_card(
                        page=page,
                        name=i,
                        duration='14:14:03',
                        status='Active',
                        airdrop_detail_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/airdrop_detail')),
                        completion_percent=45,
                    )

                    row.controls.append(
                        Container(
                                width=180,
                                col={'xs': 6,"sm": 4, "md": 4, "lg": 2},
                                content=card
                            )
                    )

                    # tracked_airdrops.controls.append(row)

                    # If it's the first card of the row, create a new Row
                    # if i % 2 == 0:
                    #     row = ResponsiveRow(
                    #         controls=[card])
                    #     tracked_airdrops.controls.append(row)  # Add the row to the column
                    
                    # else:
                    #     row.controls.append(card)  # Add the second card to the row

                # print(f'Tracked Airdrop: {tracked_airdrops.controls}')
                tracked_airdrops.controls.append(Container(content=row, margin=margin.only(bottom=50))) 
                return tracked_airdrops

            async def load_profile_data(self, num):

            

                recent_activity =  Row(scroll='auto', 
                width=page.width * 40,
                controls=[

                ])
                for i, name in enumerate(airdrop_list[:num]):
                    card = await user_airdrop_card(
                        page=page,
                        name=name,
                        duration='14:14:03',
                        status='Active',
                        completion_percent=45,
                        airdrop_detail_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/airdrop_detail')),
                    )
                    recent_activity.controls.append(card)
                    await asyncio.sleep(0.05)
                
                profile_data = Column(
                    [ 
                        Row([Text('My reward', size=22,color='black',font_family=APP_FONT_BOLD)]),
                            Row([Text('340', size=22,color='#004CFF',font_family=APP_FONT_BOLD), 
                                Text('Drop points', color='blue', font_family=APP_FONT)]),

                            Row(
                                alignment='spaceBetween',
                                controls = [
                                    Text('Recent activity', size=15,color='black',font_family=APP_FONT_BOLD),
                                    Text('5 hours ago',weight='bold', size=14, color='black', font_family=APP_FONT),
                                    
                                    
                                ]),
                            Container(content=recent_activity),

                    ]
                )
                
                return profile_data 

           
            async def load_watchlist_data(self, num):
                watchlist = Column(
                    height=700,
                    scroll='auto',
                    controls=[]
                )

                
                for idx, name in enumerate(airdrop_list[:num], start=1):  # Start numbering from 1
                    card = await airdrop_card(
                        image_url='5983122776472535666.jpg', 
                        name=name, 
                        page=page,
                        airdrop_detail_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/airdrop_detail')),
                    )
                    
                    # Add the number externally
                    numbered_card = Row(
                        controls=[
                            Container(
                                content=Text(f"{idx}", size=16, color='black',font_family=APP_FONT,weight="bold"),
                                
                            ),
                            card  # Add the existing card as is
                        ]
                    )
                    watchlist.controls.append(numbered_card)
                
                return watchlist

            async def load_all_airdrops_data(self, num):
                all_airdrops = Column(
                    height=700,
                    scroll='auto',
                    controls=[]
                )

                
                for idx, name in enumerate(airdrop_list[:num], start=1):  # Start numbering from 1
                    card = await airdrop_card(
                        image_url='5983122776472535666.jpg', 
                        name=name, 
                        page=page,
                        airdrop_detail_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/airdrop_detail')),
                    )
                    
                    # Add the number externally
                    numbered_card = Row(
                        controls=[
                            Container(
                                content=Text(f"{idx}", size=16, color='black',font_family=APP_FONT,weight="bold"),
                                
                            ),
                            card  # Add the existing card as is
                        ]
                    )
                    all_airdrops.controls.append(numbered_card)
                
                return all_airdrops


            # Airdrop Tracker sub page data
            async def load_active_airdrops(self):
                pass
            
            async def load_completed_airdrops(self):
                pass

            async def load_pending_airdrops(self):
                pass

        async def create_notification_page(page):
            return NotificationPage(
                page=page,
                go_back=lambda e: app_state.go_back(e, page=page ),
            )

        async def create_side_menu_page(page):
            return SideMenuPage(
                page=page,
                user_json=user_json,
                go_back=lambda e: app_state.go_back(e, page=page ),
                home_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/')),
                notification_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification')),
                referral_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/referrals')),
                watchlist_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/watchlist')),
                settings_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/settings')),
                airdrop_upload_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/airdrop_upload')),
            )
            
        async def create_search_page(data, page):
            return SearchPage(
                search_suggestions=await search_suggestions(
                                                page=page,
                                            name='Hot Protocol',
                                            image='hot.png',
                                            upvotes=133,
                                            downvotes=23,
                                            is_verified=True,
                                            total_users=34),
                # query=data["query"],
                # filters=data["filters"],
            
                top_menu_icons=data["top_menu_icons"],
                page=page,
            )

        async def create_track_page(data, page):
            return AnalyticPage(
                                page=page,   
                                on_skeleton_update=app_state.on_skeleton_update,
                                track_skeleton=create_track_skeleton(page),
                                tracked_airdrops=app_state.load_track_data,
                                top_menu_icons=data['top_menu_icons'],
                                drop_down_menu=drop_down_menu,
                                activity_circle=activity_circle(3), 
                                active_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/active_page')),
                                completed_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/completed_page')),
                                pending_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/pending_page')),
                                )

        async def create_referral_page(data, page):
            return RefferalsPage(
                            page=page,
                            user_json=user_json,
                            top_menu_icons=data['top_menu_icons'],
                            referral_skeleton=create_referral_skeleton(page),
                            # referral_data=app_state.load_referral_data,
                            on_skeleton_update=app_state.on_skeleton_update,
                                        )

        async def create_profile_page(data, page):
            return ProfilePage(
                page=page, 
                user_json=user_json,
                level_bar=level_bar,
                on_skeleton_update=app_state.on_skeleton_update,
                profile_skeleton=create_profile_skeleton(),
                top_menu_icons=data['top_menu_icons'], 
                airdrop_activity_overview=data['airdrop_activity_overview'],
                profile_data=app_state.load_profile_data,
                account_settings_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/account_settings')),

            )

        async def create_airdrop_detail_page(page):
            return AirdropDetailPage(
                page=page,
                task_progress_bar=task_progress_bar,
                go_back=lambda e: app_state.go_back(e, page=page ),
                report_url = lambda e: asyncio.run(app_state.navigate_to(e, page_id='/report')),
            )

        async def create_watchlist_page(page):
            return WatchlistPage(
                page=page,
                on_skeleton_update=app_state.on_skeleton_update,
                watchlist=app_state.load_watchlist_data,
                airdrop_list_skeleton=create_airdrop_list_skeleton(),
                top_menu_icons=top_menu_icons(
                                            left_icon="icons/arrow-left.svg", 
                                            search_bar=Image(src='utils/search.svg', width=38, height=38),
                                            left_icon_action=lambda e: app_state.go_back(e, page=page),
                                            search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                                        notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification')) 
                                        ),
            )

        async def create_all_airdrops_page(page):
            return AllAirdropsPage(
                page=page,
                on_skeleton_update=app_state.on_skeleton_update,
                airdrops=app_state.load_all_airdrops_data,
                airdrop_list_skeleton=create_airdrop_list_skeleton(),
                drop_down_menu=drop_down_menu,
                top_menu_icons=top_menu_icons(
                                            left_icon="icons/arrow-left.svg", 
                                            search_bar=Image(src='utils/search.svg', width=38, height=38),
                                            left_icon_action=lambda e: app_state.go_back(e, page=page),
                                            search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                                        notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification')) 
                                        ),
            )

        async def create_settings_page(page):
            return SettingsPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Settings'),
                
                account_settings_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/account_settings')),
                notification_settings_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification_settings')),
                language_settings_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/language_settings')),
                terms_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/terms')),
                privacy_policy_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/privacy_policy')),
                version_info_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/version_info')),
            )

        async def create_account_settings_page(page):
            return AccountSettingsPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Account Settings'),
                change_password_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/password_settings')),
                delete_account_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/delete_account')),
            )

        async def create_change_password_page(page):
            return ChangePasswordPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Change Password'),
            )

        async def create_notification_settings_page(page):
            return NotificationSettingsPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Notification settings'),
            )

        async def create_language_settings_page(page):
            return LanguagePage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Language Settings'),
            )

        async def create_delete_account_page(page):
            return DeleteAccountPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Delete Account')
            )
        
        async def create_report_page(page):
            return ReportPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Report an issue'),

            )

        async def create_terms_page(page):
            return TermsAndConditionPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Terms & Conditions'),
            )

        async def create_privacy_policy_page(page):
            return PrivacyPolicyPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Privacy Policy'),
            )

        async def create_version_info_page(page):
            return VersionInfoPage(
                page=page,
                top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Version Info'),
            )


        # Airdrop Tracker sub pages

        async def create_active_page(page):
            return ActivePage(
                page=page,
                top_menu_icons=top_menu_icons(
                                            left_icon="icons/arrow-left.svg", 
                                            search_bar=Image(src='utils/search.svg', width=38, height=38),
                                            left_icon_action=lambda e: app_state.go_back(e, page=page),
                                            search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                                        notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification')) 
                                        ),
                
            )

        async def create_completed_page(page):
            return CompletedPage(
                page=page,
                top_menu_icons=top_menu_icons(
                                            left_icon="icons/arrow-left.svg", 
                                            search_bar=Image(src='utils/search.svg', width=38, height=38),
                                            left_icon_action=lambda e: app_state.go_back(e, page=page),
                                            search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                                        notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification')) 
                                        ),
                
            )

        async def create_pending_page(page):
            return PendingPage(
                page=page,
                top_menu_icons=top_menu_icons(
                                            left_icon="icons/arrow-left.svg", 
                                            search_bar=Image(src='utils/search.svg', width=38, height=38),
                                            left_icon_action=lambda e: app_state.go_back(e, page=page),
                                            search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                                        notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification')) 
                                        ),
                
            )
        
        async def create_airdrop_upload_page(page):
            return AirdropUploadPage(
                page=page,
                post_airdrop=post_airdrop,
                # top_icons=top_icons,
                # top_menu_icons=top_menu_icons(
                #                             left_icon="icons/arrow-left.svg", 
                #                             search_bar=Image(src='utils/search.svg', width=38, height=38),
                #                             left_icon_action=lambda e: app_state.go_back(e, page=page),
                #                             search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                #                         notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification')) 
                #                         ),
                
            )

        app_state = AppState(page)
            
            


        bottomapp_icons = {
            "home_idle": "icons/home-idle.svg",
            "home_active": "icons/home-active.svg",
            "track_idle": "icons/track-idle.svg",
            "track_active": "icons/track-active.svg",
            "referrals_idle": "icons/referrals-idle.svg",
            "referrals_active": "icons/referrals-active.svg",
            "profile_idle": "icons/profile-idle.svg",
            "profile_active": "icons/profile-active.svg"
        }

        # Initial icon state
        icon_state = {
            "home": bottomapp_icons["home_active"],
            "track": bottomapp_icons["track_idle"],
            "referrals": bottomapp_icons["referrals_idle"],
            "profile": bottomapp_icons["profile_idle"]
        }

        
        def update_icon(clicked_icon):
            for icon in icon_state:
                if icon == clicked_icon:
                    # Set clicked icon to active
                    # print(f"{icon} icon clicked, setting to active")
                    icon_state[icon] = bottomapp_icons[f"{icon}_active"]
                else:
                    # Set other icons to idle
                    # print(f"{icon} icon not clicked, setting to idle")
                    icon_state[icon] = bottomapp_icons[f"{icon}_idle"]
            
            # Update the UI
            home_img.src = icon_state["home"]
            track_img.src = icon_state["track"]
            referrals_img.src = icon_state["referrals"]
            profile_img.src = icon_state["profile"]
            page.update()


        # Define the bottom app bar icons
        home_img = Image(src=icon_state["home"], height=70)
        track_img = Image(src=icon_state["track"], height=70)
        referrals_img = Image(src=icon_state["referrals"], height=70)
        profile_img = Image(src=icon_state["profile"], height=70)


        # def on_resize(e):
        #     # Update the width and height based on the window size
        #     appbar_parent.width = page.width - 10
        #     appbar_parent.height = page.height * 0.1
        #
        #     appbar_parent.margin = margin.only(top=page.window.height - appbar_parent.height)
        #     page.update()


        page.bottom_appbar = BottomAppBar(
            height=100,
            bgcolor='white',
            content=Row(
                alignment='spaceBetween',
                controls=[
                    Container(
                    
                        content=home_img,
                        on_click=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/')),
                    ),
                    Container(
                        content=track_img,
                        on_click=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/track'))
                    ),
                    Container(
                        content=referrals_img,
                        on_click=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/referrals')),
                    ),
                    Container(
                        content=profile_img,
                        on_click=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/profile')),
                    ),
                ],
        )
        )



        




        async def load_home_page(page, airdrop_list):

            trending_airdrops = Row(
            
            scroll='auto',
            controls=[
                ]
            )
            
            for name in airdrop_list[:5]:
                trending_airdrops.controls.append(
                    await trending_airdop_card(
                        airdrop_detail_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/airdrop_detail')),
                        airdrop_name=name, airdrop_image='5983122776472535666.jpg', 
                        airdrop_category='Other', 
                        airdrop_cost='$10',
                        page=page)

                )
            
            upcoming_airdrops = Row(
                    scroll='auto',
                    controls=[]
                )

            for name in airdrop_list[:5]:
                upcoming_airdrops.controls.append(
                    await upcoming_airdrops_card(
                        name=name,
                        airdrop_detail_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/airdrop_detail')),
                        category=name,
                        cost=4,
                        image_url='5983122776472535666.jpg',
                        page=page
                    )
                )
            


            


            cards = [await airdrop_card(image_url='5983122776472535666.jpg', name=name, airdrop_detail_url=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/airdrop_detail')),page=page) for name in airdrop_list[:4]]

            mining_airdrops = Row(
                scroll='auto',
                alignment=MainAxisAlignment.CENTER,
                controls=[
                    Column(cards[:2]),
                    Column(cards[2:])
                ]
            )

            testnet_airdrops = Row(
                scroll='auto',
                alignment=MainAxisAlignment.CENTER,
                controls=[
                    Column(cards[:2]),
                    Column(cards[2:])
                ]
            )



            home = HomePage(
                page=page,
                # on_skeleton_update=self.on_skeleton_update,
                user_json = await get_user_data(),
                home_skeleton=create_home_skeleton(page),
                upcoming_airdrops=upcoming_airdrops,
                top_menu_icons=top_menu_icons(
                            left_icon="icons/menu-2-line.svg", 
                            search_bar=Image(src='utils/search.svg', width=38, height=38),
                            left_icon_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/side_menu')),
                            search_bar_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/search')),
                            notification_action=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/notification'))
                            ),
                goto_track=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/track')),
                airdrop_activity_overview=airdrop_activity_overview(page=page, percent=75, total_airdrops=70),
                mining_airdrops=mining_airdrops,
                testnet_airdrops=testnet_airdrops,
                goto_all_airdrops=lambda e: asyncio.run(app_state.navigate_to(e, page_id='/all_airdrops')), 
                trending_airdrops=trending_airdrops,
                # logout_user=logout_user,
                goto_airdrop_upload=lambda e: page.go('/upload_airdrop')
                )
            return home
        

        # skeleton_page = create_home_skeleton(page)
        # page.add(skeleton_page)
        # page.update()

        # asyncio.create_task(asyncio.to_thread(app_state.shimmer_animation, skeleton_page))
        home = await load_home_page(page=page, airdrop_list=airdrop_list)

        

        # await asyncio.sleep(1)
        page.controls.clear()
        page.add(home.base)
        page.update()

    def revert_to_login():
        page.controls.clear()
        page.add(login.base)
        page.update()


    def add_login():
        page.remove(sign_up.base)
        page.add(login.base)
        page.update()

    def add_signup():
        page.remove(login.base)
        page.add(sign_up.base)
        page.update()


    def goto_home():
        page.remove(all_airdrops.base)
        page.add(home.base)
        page.update()

    login = LoginPage(page=page, login_user=login_user, on_success_callback=handle_login_success, signup_page_url=lambda e: add_signup())
    
    async def create_login_page(page):
        return LoginPage(page=page, login_user=login_user, on_success_callback=handle_login_success, signup_page_url=lambda e: add_signup())
     #Sign up
    sign_up = SignupPage(page=page, 
                        signup_user=signup_user, on_success_callback=add_login, 
                        login_page_url=lambda e: add_login())

    landing_page =  LandingPage(
        page=page
    )
    async def create_change_password_page(page):
        return ChangePasswordPage(
            page=page,
            top_icons=top_icons(page=page,go_back=lambda e: app_state.go_back(e, page=page), page_name='Change Password'),
        )

    # login = logPage(page=page)

    page.add(sign_up.base)
   
    page.update()





# for uvicorn web app
# app = app(target=main_app, export_asgi_app=True)


if __name__ == '__main__':
    app(target=main)




    