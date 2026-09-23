package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

/**
 * Represents the exact POST request body for creating a BloodRequest on the Django backend.
 * Required fields must match the Django BloodRequestSerializer.
 * Latitude and longitude are currently omitted (null) as location selection is not yet implemented.
 */
public class BloodRequestCreateRequest {

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
    private String requiredDate; // Format: YYYY-MM-DD

    @SerializedName("description")
    private String description;

    public BloodRequestCreateRequest(String bloodGroup, int unitsRequired, String hospitalName,
                                     String location, String urgency, String requiredDate,
                                     String description) {
        this.bloodGroup = bloodGroup;
        this.unitsRequired = unitsRequired;
        this.hospitalName = hospitalName;
        this.location = location;
        this.urgency = urgency;
        this.requiredDate = requiredDate;
        this.description = description;
        // explicitly set to null as map selection is not implemented yet
        this.latitude = null;
        this.longitude = null;
    }

    public String getBloodGroup() {
        return bloodGroup;
    }

    public void setBloodGroup(String bloodGroup) {
        this.bloodGroup = bloodGroup;
    }

    public int getUnitsRequired() {
        return unitsRequired;
    }

    public void setUnitsRequired(int unitsRequired) {
        this.unitsRequired = unitsRequired;
    }

    public String getHospitalName() {
        return hospitalName;
    }

    public void setHospitalName(String hospitalName) {
        this.hospitalName = hospitalName;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public Double getLatitude() {
        return latitude;
    }

    public void setLatitude(Double latitude) {
        this.latitude = latitude;
    }

    public Double getLongitude() {
        return longitude;
    }

    public void setLongitude(Double longitude) {
        this.longitude = longitude;
    }

    public String getUrgency() {
        return urgency;
    }

    public void setUrgency(String urgency) {
        this.urgency = urgency;
    }

    public String getRequiredDate() {
        return requiredDate;
    }

    public void setRequiredDate(String requiredDate) {
        this.requiredDate = requiredDate;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
