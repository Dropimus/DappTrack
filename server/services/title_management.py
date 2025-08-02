
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User

"""
Update user titles based on honor_points thresholds.
Titles & HONOR Thresholds:
- Chosen Seeker: 0 to 49
- Legionnaire: 50 to 149
- Centurion: 150 to 349
- Imperator: 350 to 699
- Dominus of Dropimus: 700+
"""

def determine_title(honor_points: int) -> str:
    if honor_points >= 700:
        return "Dominus of Dropimus"
    if honor_points >= 350:
        return "Imperator"
    if honor_points >= 150:
        return "Centurion"
    if honor_points >= 50:
        return "Legionnaire"
    return "Chosen Seeker"

async def update_user_title(db: AsyncSession, user: User) -> None:
    """
    Update the user's title based on their current honor_points.
    """
    new_title = determine_title(user.honor_points)
    if user.title != new_title:
        user.title = new_title
        await db.commit()
        await db.refresh(user)