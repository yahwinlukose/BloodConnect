package com.bloodconnect.app.network;

import com.bloodconnect.app.network.models.LoginRequest;
import com.bloodconnect.app.network.models.LoginResponse;
import com.bloodconnect.app.network.models.BloodRequestCreateRequest;
import com.bloodconnect.app.network.models.BloodRequestResponse;
import com.bloodconnect.app.network.models.BloodRequest;
import com.bloodconnect.app.network.models.DonorProfile;
import com.bloodconnect.app.network.models.DonorProfileCreateRequest;
import com.bloodconnect.app.network.models.DonorProfileUpdateRequest;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Headers;
import retrofit2.http.POST;
import retrofit2.http.GET;
import retrofit2.http.PATCH;

/**
 * ApiService defines the HTTP API endpoints used by Retrofit to communicate with the Django backend.
 */
public interface ApiService {

    /**
     * Authenticates a user and retrieves access/refresh JWT tokens.
     * Maps to the Django SimpleJWT TokenObtainPairView at /api/auth/login/.
     *
     * @param request The user credentials (email and password).
     * @return A Retrofit Call containing the LoginResponse (tokens).
     */
    @Headers("No-Authentication: true")
    @POST("auth/login/")
    Call<LoginResponse> login(@Body LoginRequest request);

    /**
     * Creates a new blood request.
     * Maps to the Django BloodRequestViewSet at /api/blood-requests/.
     * Requires an Authorization Bearer token header.
     *
     * @param request The blood request form data.
     * @return A Retrofit Call containing the created BloodRequest response.
     */
    @POST("blood-requests/")
    Call<BloodRequestResponse> createBloodRequest(@Body BloodRequestCreateRequest request);

    @GET("blood-requests/")
    Call<List<BloodRequest>> getMyRequests();

    @GET("donors/profile/")
    Call<DonorProfile> getDonorProfile();

    @POST("donors/profile/")
    Call<DonorProfile> createDonorProfile(@Body DonorProfileCreateRequest request);

    @PATCH("donors/profile/")
    Call<DonorProfile> updateDonorProfile(@Body DonorProfileUpdateRequest request);

}
