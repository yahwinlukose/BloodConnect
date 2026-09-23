package com.bloodconnect.app.auth;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * TokenManager is responsible for securely storing and retrieving JWT authentication tokens.
 * It uses Android SharedPreferences with a private file dedicated to BloodConnect.
 * Note: It handles the access and refresh tokens but DOES NOT store the user's password.
 */
public class TokenManager {

    private static final String PREF_NAME = "bloodconnect_auth_prefs";
    private static final String KEY_ACCESS_TOKEN = "access_token";
    private static final String KEY_REFRESH_TOKEN = "refresh_token";

    private final SharedPreferences prefs;

    public TokenManager(Context context) {
        prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
    }

    /**
     * Saves the JWT access token.
     */
    public void saveAccessToken(String token) {
        prefs.edit().putString(KEY_ACCESS_TOKEN, token).apply();
    }

    /**
     * Saves the JWT refresh token.
     */
    public void saveRefreshToken(String token) {
        prefs.edit().putString(KEY_REFRESH_TOKEN, token).apply();
    }

    /**
     * Retrieves the stored JWT access token, or null if not present.
     */
    public String getAccessToken() {
        return prefs.getString(KEY_ACCESS_TOKEN, null);
    }

    /**
     * Retrieves the stored JWT refresh token, or null if not present.
     */
    public String getRefreshToken() {
        return prefs.getString(KEY_REFRESH_TOKEN, null);
    }

    /**
     * Checks whether authentication tokens currently exist.
     */
    public boolean hasTokens() {
        return getAccessToken() != null && getRefreshToken() != null;
    }

    /**
     * Clears all stored tokens during logout.
     */
    public void clearTokens() {
        prefs.edit().clear().apply();
    }
}
