
def calculate_base_honor(verdict: str) -> int:
    """
    Determine the base HONOR for a submission verdict.
    verdict: 'legit', 'scam', or 'false'
    Returns positive for rewards, negative for penalties.
    """
    mapping = {
        'legit': 5,
        'scam': -15,
        'false': -10,  # initial penalty; can escalate elsewhere
    }
    return mapping.get(verdict, 0)


def apply_accuracy_multiplier(honor: int, accuracy_multiplier: float) -> int:
    """
    Apply user-specific accuracy multiplier to the base HONOR.
    """
    adjusted = honor * accuracy_multiplier
    return int(round(adjusted))


def get_streak_multiplier(streak_count: int) -> float:
    """
    Return a multiplier based on current streak:
      - streak >=10: 1.5x
      - streak >=5: 1.2x
      - else: 1.0x
    """
    if streak_count >= 10:
        return 1.5
    if streak_count >= 5:
        return 1.2
    return 1.0


def get_tier_bonus(current_honor: int) -> int:
    """
    Provide a flat bonus based on user's current HONOR tier:
      - 700+: +5
      - 350-699: +4
      - 150-349: +3
      - 50-149: +2
      - 0-49: +1
    """
    if current_honor >= 700:
        return 5
    if current_honor >= 350:
        return 4
    if current_honor >= 150:
        return 3
    if current_honor >= 50:
        return 2
    return 1


def compute_total_honor(
    verdict: str,
    accuracy_multiplier: float,
    streak_count: int,
    current_honor: int
) -> int:
    """
    Full pipeline to calculate HONOR change:
      1. Base honor from verdict
      2. Apply accuracy multiplier
      3. Multiply by streak multiplier
      4. Add tier bonus
    Returns net HONOR change.
    """
    base = calculate_base_honor(verdict)
    adjusted = apply_accuracy_multiplier(base, accuracy_multiplier)
    streak_mult = get_streak_multiplier(streak_count)
    after_streak = int(round(adjusted * streak_mult))
    tier_bonus = get_tier_bonus(current_honor)
    return after_streak + tier_bonus
