package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

public class DonorMatch {
    @SerializedName("id")
    private int id;

    @SerializedName("donor")
    private MatchedDonor donor;

    @SerializedName("distance_km")
    private Double distanceKm;

    @SerializedName("match_score")
    private int matchScore;

    @SerializedName("status")
    private String status;

    public int getId() {
        return id;
    }

    public MatchedDonor getDonor() {
        return donor;
    }

    public Double getDistanceKm() {
        return distanceKm;
    }

    public int getMatchScore() {
        return matchScore;
    }

    public String getStatus() {
        return status;
    }
}
