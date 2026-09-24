package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

public class BloodRequest {
    @SerializedName("id")
    private int id;
    
    @SerializedName("requester")
    private Requester requester;
    
    @SerializedName("blood_group")
    private String bloodGroup;
    
    @SerializedName("units_required")
    private int unitsRequired;
    
    @SerializedName("hospital_name")
    private String hospitalName;
    
    @SerializedName("location")
    private String location;
    
    @SerializedName("latitude")
    private Double latitude;
    
    @SerializedName("longitude")
    private Double longitude;
    
    @SerializedName("urgency")
    private String urgency;
    
    @SerializedName("required_date")
    private String requiredDate;
    
    @SerializedName("description")
    private String description;
    
    @SerializedName("status")
    private String status;
    
    @SerializedName("created_at")
    private String createdAt;
    
    @SerializedName("updated_at")
    private String updatedAt;

    public int getId() { return id; }
    public Requester getRequester() { return requester; }
    public String getBloodGroup() { return bloodGroup; }
    public int getUnitsRequired() { return unitsRequired; }
    public String getHospitalName() { return hospitalName; }
    public String getLocation() { return location; }
    public Double getLatitude() { return latitude; }
    public Double getLongitude() { return longitude; }
    public String getUrgency() { return urgency; }
    public String getRequiredDate() { return requiredDate; }
    public String getDescription() { return description; }
    public String getStatus() { return status; }
    public String getCreatedAt() { return createdAt; }
    public String getUpdatedAt() { return updatedAt; }
}
