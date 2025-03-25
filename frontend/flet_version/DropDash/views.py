from flet import *
import asyncio
from skeleton import (
    create_home_skeleton,
    create_track_skeleton, 
    trending_airdrop_skeleton, 
    create_referral_skeleton, 
    create_profile_skeleton,
    create_airdrop_list_skeleton
)
from build_page import (
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
    top_icons,
    level_bar,
    task_progress_bar
)
from airdrop_module import (
    search_suggestions,
    trending_airdop_card, 
    airdrop_card, 
    upcoming_airdrops_card, user_airdrop_card
)
import asyncio
from airdrop_list import airdrop_list

async def HomeView(page):

    trending_airdrops = Row(
        
        scroll='auto',
        controls=[
            ]
        )
        
    for name in airdrop_list[:5]:
        trending_airdrops.controls.append(
            await trending_airdop_card(
                airdrop_detail_url=lambda e: page.go("/airdrop_detail"), 
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
                airdrop_detail_url=lambda e: page.go("/airdrop_detail"),
                category=name,
                cost=4,
                image_url='5983122776472535666.jpg',
                page=page
            )
        )
    


    


    cards = [await airdrop_card(image_url='5983122776472535666.jpg', name=name, airdrop_detail_url=lambda e: page.go("/airdrop_detail"),page=page) for name in airdrop_list[:4]]

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
        home_skeleton=create_home_skeleton(page),
        upcoming_airdrops=upcoming_airdrops,
        top_menu_icons=top_menu_icons(
                    left_icon="icons/menu-2-line.svg", 
                    search_bar=Image(src='utils/search.svg', width=38, height=38),
                    left_icon_action=lambda e: page.go('/side_menu'),
                    search_bar_action=lambda e: page.go('/search'),
                    notification_action=lambda e: page.go('/notification')
                    ),
        goto_track=lambda e: page.go('/track'),
        airdrop_activity_overview=airdrop_activity_overview(page=page, percent=75, total_airdrops=70),
        mining_airdrops=mining_airdrops,
        testnet_airdrops=testnet_airdrops,
        goto_all_airdrops=lambda e: page.go('/all_airdrops'), 
        trending_airdrops=trending_airdrops,
        # logout_user=logout_user,
        goto_airdrop_upload=lambda e: page.go('/upload_airdrop')
        ).base
    print('called view func')

    return home

async def TrackView():
    pass

## track page sub pages

async def ActiveView():
    pass

async def CompletedView():
    pass

async def PendingView():
    pass

## end

async def ReferralView():
    pass

async def ProfileView():
    pass

async def SideMenuView():
    pass

async def SearchView():
    pass

async def NotificationView():
    pass

async def AirdropDetailPage():
    pass

async def AllAirdropsView():
    pass

async def WaitlistView():
    pass

async def SettingsView():
    pass

## sub settings pages

async def AccountSettingsView():
    pass

## accound settings sub page

async def DeleteAccountView():
    pass

## end

async def NotificationSettingsView():
    pass

async def LanguageSettingsView():
    pass

async def TermsAndConditionView():
    pass

async def PrivacyPolicyView():
    pass

async def VersionInfoView():
    pass

## end

async def ContacUsView():
    pass

    