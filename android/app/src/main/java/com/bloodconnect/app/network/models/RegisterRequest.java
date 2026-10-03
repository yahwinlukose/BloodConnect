package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

/**
 * Represents the JSON request body expected by the Django backend for POST /api/auth/register/.
 * Fields match the UserRegistrationSerializer: email, password, first_name, last_name, phone.
 */
public class RegisterRequest {

    @SerializedName("email")
    private String email;

    @SerializedName("password")
    private String password;

    @SerializedName("first_name")
    private String firstName;

    @SerializedName("last_name")
    private String lastName;

    @SerializedName("phone")
    private String phone;

    public RegisterRequest(String email, String password, String firstName, String lastName, String phone) {
        this.email = email;
        this.password = password;
        this.firstName = firstName;
        this.lastName = lastName;
        this.phone = phone;
    }

    public String getEmail() { return email; }
    public String getFirstName() { return firstName; }
    public String getLastName() { return lastName; }
    public String getPhone() { return phone; }
    // NOTE: password getter intentionally omitted to avoid accidental logging
}
