package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

/**
 * Request body for POST /api/auth/token/refresh/.
 * SimpleJWT expects the stored refresh token to issue a new access token.
 */
public class TokenRefreshRequest {

    @SerializedName("refresh")
    private String refresh;

    public TokenRefreshRequest(String refresh) {
        this.refresh = refresh;
    }

    // No getter for refresh intentionally – avoids accidental logging of the token value.
}
