package com.bloodconnect.app.network;

import com.bloodconnect.app.network.models.LoginRequest;
import com.bloodconnect.app.network.models.LoginResponse;
import com.bloodconnect.app.network.models.RegisterRequest;
import com.bloodconnect.app.network.models.RegisterResponse;
import com.bloodconnect.app.network.models.LogoutRequest;
import com.bloodconnect.app.network.models.TokenRefreshRequest;
import com.bloodconnect.app.network.models.TokenRefreshResponse;
import com.bloodconnect.app.network.models.BloodRequestCreateRequest;
import com.bloodconnect.app.network.models.BloodRequestResponse;
import com.bloodconnect.app.network.models.BloodRequest;
import com.bloodconnect.app.network.models.DonorProfile;
import com.bloodconnect.app.network.models.DonorProfileCreateRequest;
import com.bloodconnect.app.network.models.DonorProfileUpdateRequest;
import com.bloodconnect.app.network.models.DonorMatch;
import com.bloodconnect.app.network.models.DonorMatchForDonor;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Headers;
import retrofit2.http.POST;
import retrofit2.http.GET;
import retrofit2.http.PATCH;
import retrofit2.http.Path;

/**
 * ApiService defines the HTTP API endpoints used by Retrofit to communicate with the Django backend.
 */
public interface ApiService {

    /**
     * Registers a new user account.
     * Maps to the Django RegisterView (UserRegistrationSerializer) at /api/auth/register/.
     * Returns HTTP 201 on success with the new user's public fields.
     * Returns HTTP 400 with field-level validation errors on failure.
     *
     * @param request The registration form data (email, password, first_name, last_name, phone).
     * @return A Retrofit Call containing the RegisterResponse on success.
     */
    @Headers("No-Authentication: true")
    @POST("auth/register/")
    Call<RegisterResponse> register(@Body RegisterRequest request);

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
     * Logs out the user by blacklisting the refresh token server-side.
     * Maps to the Django LogoutView at /api/auth/logout/.
     * Requires an Authorization Bearer token (the current access token).
     * Best-effort: the client MUST clear local tokens regardless of the HTTP outcome.
     *
     * @param request The refresh token to blacklist.
     * @return A Retrofit Call with a Void response body (HTTP 200 on success).
     */
    @POST("auth/logout/")
    Call<Void> logout(@Body LogoutRequest request);

    /**
     * Issues a new access token using the stored refresh token.
     * Maps to SimpleJWT TokenRefreshView at /api/auth/token/refresh/.
     * Tagged No-Authentication so the auth interceptor does not attempt to inject the
     * (already-expired) access token into this request.
     *
     * @param request The refresh token.
     * @return A Retrofit Call containing the new access token (and optionally a rotated refresh token).
     */
    @Headers("No-Authentication: true")
    @POST("auth/token/refresh/")
    Call<TokenRefreshResponse> refreshToken(@Body TokenRefreshRequest request);

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

    @POST("blood-requests/{requestId}/matches/generate/")
    Call<List<DonorMatch>> generateMatches(@Path("requestId") int requestId);

    @GET("blood-requests/{requestId}/matches/")
    Call<List<DonorMatch>> getMatches(@Path("requestId") int requestId);

    @GET("donors/matches/")
    Call<List<DonorMatchForDonor>> getDonorMatches();

    @POST("donors/matches/{matchId}/accept/")
    Call<DonorMatchForDonor> acceptDonorMatch(@Path("matchId") int matchId);

    @POST("donors/matches/{matchId}/reject/")
    Call<DonorMatchForDonor> rejectDonorMatch(@Path("matchId") int matchId);

}
