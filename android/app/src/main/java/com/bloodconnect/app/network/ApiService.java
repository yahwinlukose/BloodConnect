package com.bloodconnect.app.network;

import com.bloodconnect.app.network.models.LoginRequest;
import com.bloodconnect.app.network.models.LoginResponse;
import com.bloodconnect.app.network.models.BloodRequestCreateRequest;
import com.bloodconnect.app.network.models.BloodRequestResponse;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Headers;
import retrofit2.http.POST;

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

}
