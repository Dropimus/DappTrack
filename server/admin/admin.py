@app.get("/users", response_model=UsersListResponse)
@limiter.limit("10/minute")
async def get_all_users(
    request: Request,
    current_user: Annotated[UserScheme, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    stmt = select(User).offset(offset).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    if not users:
        return api_response(False, "No users found", [])
    return api_response(True, "Users fetched", [UserScheme.from_orm(u) for u in users])