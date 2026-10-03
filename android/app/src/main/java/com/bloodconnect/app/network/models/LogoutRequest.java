package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

/**
 * Request body for POST /api/auth/logout/.
 * Django's LogoutView expects the refresh token to blacklist it server-side.
 * The access token is NOT sent here – only the refresh token is blacklisted.
 */
public class LogoutRequest {

    @SerializedName("refresh")
    private String refresh;

    public LogoutRequest(String refresh) {
        this.refresh = refresh;
    }

    // No getter for refresh intentionally – avoids accidental logging of the token value.
}
