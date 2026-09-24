package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

public class DonorMatchForDonor {
    @SerializedName("id")
    private int id;

    @SerializedName("blood_request")
    private BloodRequestForDonor bloodRequest;

    @SerializedName("distance_km")
    private Double distanceKm;

    @SerializedName("match_score")
    private String matchScore;

    @SerializedName("status")
    private String status;

    @SerializedName("created_at")
    private String createdAt;

    @SerializedName("responded_at")
    private String respondedAt;

    public int getId() { return id; }
    public BloodRequestForDonor getBloodRequest() { return bloodRequest; }
    public Double getDistanceKm() { return distanceKm; }
    public String getMatchScore() { return matchScore; }
    public String getStatus() { return status; }
    public String getCreatedAt() { return createdAt; }
    public String getRespondedAt() { return respondedAt; }
}
