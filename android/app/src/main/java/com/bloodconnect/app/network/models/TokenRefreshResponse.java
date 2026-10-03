package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

/**
 * Response body from POST /api/auth/token/refresh/.
 * SimpleJWT returns a new access token (and optionally a rotated refresh token).
 */
public class TokenRefreshResponse {

    @SerializedName("access")
    private String access;

    /** Present only when ROTATE_REFRESH_TOKENS = True in Django settings. May be null. */
    @SerializedName("refresh")
    private String refresh;

    public String getAccess() {
        return access;
    }

    public String getRefresh() {
        return refresh;
    }
}
