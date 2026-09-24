package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

public class DonorProfile {
    @SerializedName("id")
    private int id;
    
    @SerializedName("user")
    private Requester user;
    
    @SerializedName("blood_group")
    private String bloodGroup;
    
    @SerializedName("date_of_birth")
    private String dateOfBirth;
    
    @SerializedName("gender")
    private String gender;
    
    @SerializedName("location")
    private String location;
    
    @SerializedName("latitude")
    private Double latitude;
    
    @SerializedName("longitude")
    private Double longitude;
    
    @SerializedName("is_available")
    private Boolean isAvailable;
    
    @SerializedName("last_donation_date")
    private String lastDonationDate;
    
    @SerializedName("created_at")
    private String createdAt;
    
    @SerializedName("updated_at")
    private String updatedAt;

    public int getId() { return id; }
    public Requester getUser() { return user; }
    public String getBloodGroup() { return bloodGroup; }
    public String getDateOfBirth() { return dateOfBirth; }
    public String getGender() { return gender; }
    public String getLocation() { return location; }
    public Double getLatitude() { return latitude; }
    public Double getLongitude() { return longitude; }
    public Boolean getIsAvailable() { return isAvailable; }
    public String getLastDonationDate() { return lastDonationDate; }
    public String getCreatedAt() { return createdAt; }
    public String getUpdatedAt() { return updatedAt; }
}
