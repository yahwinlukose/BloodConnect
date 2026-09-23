package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

/**
 * Represents the JSON request body expected by the Django backend for POST /api/auth/login/.
 * The Django backend expects standard credentials: 'email' and 'password'.
 */
public class LoginRequest {

    @SerializedName("email")
    private String email;

    @SerializedName("password")
    private String password;

    public LoginRequest(String email, String password) {
        this.email = email;
        this.password = password;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
