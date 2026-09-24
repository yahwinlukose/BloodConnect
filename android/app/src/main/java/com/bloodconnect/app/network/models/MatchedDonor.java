package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

public class MatchedDonor {
    @SerializedName("id")
    private int id;

    @SerializedName("user")
    private MatchUser user;

    @SerializedName("blood_group")
    private String bloodGroup;

    @SerializedName("gender")
    private String gender;

    @SerializedName("location")
    private String location;

    @SerializedName("is_available")
    private boolean isAvailable;

    public int getId() {
        return id;
    }

    public MatchUser getUser() {
        return user;
    }

    public String getBloodGroup() {
        return bloodGroup;
    }

    public String getGender() {
        return gender;
    }

    public String getLocation() {
        return location;
    }

    public boolean isAvailable() {
        return isAvailable;
    }
}
