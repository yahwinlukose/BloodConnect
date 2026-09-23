package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

/**
 * Represents the expected JSON response from the Django backend for POST /api/auth/login/.
 * The SimpleJWT TokenObtainPairView returns 'access' and 'refresh' tokens.
 */
public class LoginResponse {
    
    @SerializedName("access")
    private String access;

    @SerializedName("refresh")
    private String refresh;

    public String getAccess() {
        return access;
    }

    public void setAccess(String access) {
        this.access = access;
    }

    public String getRefresh() {
        return refresh;
    }

    public void setRefresh(String refresh) {
        this.refresh = refresh;
    }
}
