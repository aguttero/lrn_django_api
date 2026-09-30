I put the serializer, the two views and the URL routes in the file above. Your logout view already worked. I only changed its schema decorator.

**Logged-in user revokes their own token.** `request.auth` is the `Token` object that authenticated the request, so `request.auth.delete()` is enough.

**Admin revokes another user by email.** `AdminRevokeUserTokenView` is a POST endpoint that takes `{"email": "..."}` in the body.
- `IsAdminUser` requires `is_staff=True`. If you want only superusers to do this, write a small permission class that checks `is_superuser`.
- I look the user up with `email__iexact`, because `normalize_email` only lowercases the domain part of an address, so case can differ.
- DRF's `Token` has a one-to-one link to the user, so `Token.objects.filter(user=user).delete()` removes at most one row.

**Fixes to your schema decorator.** `responses={200: dict(detail=...)}` isn't a valid drf-spectacular response definition, so I replaced it with `OpenApiResponse`. Your admin email input also gets its own serializer, so Swagger documents the body.

**Things to be aware of:**
- Revoking a token isn't a ban. Your `CreateTokenView` (`ObtainAuthToken`) does `get_or_create`, so the user can log in again and get a fresh token. To lock someone out, also set `user.is_active = False`. `TokenAuthentication` rejects inactive users.
- Because `ObtainAuthToken` reuses the same token, the token never expires on its own. Logout and admin revoke are the only ways it goes away.
- There's a leftover `print(user)` between `# ZAG` and `# EZAG` in `UserSerializer.update`. You probably want to remove it, because it would print user details to your server logs.
