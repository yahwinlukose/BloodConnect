package com.bloodconnect.app.network.models;

import com.google.gson.annotations.SerializedName;

/**
 * Represents the response from the Django backend upon successfully creating a blood request.
 */
public class BloodRequestResponse {

    @SerializedName("id")
    private int id;

    @SerializedName("status")
    private String status;

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
