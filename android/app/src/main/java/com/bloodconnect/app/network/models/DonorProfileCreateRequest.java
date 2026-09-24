package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

public class DonorProfileCreateRequest {
    @SerializedName("blood_group") private String bloodGroup;
    @SerializedName("date_of_birth") private String dateOfBirth;
    @SerializedName("gender") private String gender;
    @SerializedName("location") private String location;
    @SerializedName("latitude") private Double latitude;
    @SerializedName("longitude") private Double longitude;
    @SerializedName("is_available") private Boolean isAvailable;
    @SerializedName("last_donation_date") private String lastDonationDate;

    public DonorProfileCreateRequest(String bloodGroup, String gender, String dateOfBirth, String location, Double latitude, Double longitude, Boolean isAvailable, String lastDonationDate) {
        this.bloodGroup = bloodGroup;
        this.gender = gender;
        this.dateOfBirth = dateOfBirth;
        this.location = location;
        this.latitude = latitude;
        this.longitude = longitude;
        this.isAvailable = isAvailable;
        this.lastDonationDate = lastDonationDate;
    }
}
