package com.bloodconnect.app.network;

import android.content.Context;
import android.content.Intent;

import com.bloodconnect.app.auth.LoginActivity;
import com.bloodconnect.app.auth.TokenManager;
import com.bloodconnect.app.network.models.TokenRefreshRequest;
import com.bloodconnect.app.network.models.TokenRefreshResponse;

import okhttp3.Authenticator;
import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.Route;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * RetrofitClient provides a singleton Retrofit instance configured to communicate with the backend.
 *
 * Token-refresh strategy
 * ─────────────────────
 * When the server responds with HTTP 401 for an authenticated request, the OkHttp Authenticator
 * silently calls POST /api/auth/token/refresh/ using the stored refresh token.
 *
 * • Success → the new access token is saved and the original request is retried with the
 *             fresh token. The user never sees a login screen.
 * • Failure (refresh expired/invalid, or refresh token absent) → local tokens are cleared,
 *   and the app navigates to LoginActivity. This is the only code path that forces logout
 *   without explicit user action.
 *
 * The Retrofit singleton is deliberately reset when the session is invalidated so that a
 * subsequent login gets a clean OkHttpClient with the new token in SharedPreferences.
 *
 * Security notes
 * ──────────────
 * • HttpLoggingInterceptor is set to BASIC — it logs only request lines and response codes,
 *   never request/response bodies, so JWTs and passwords never appear in Logcat.
 * • The auth interceptor reads tokens fresh from SharedPreferences on every request so that
 *   a token saved after a refresh is immediately available to the next call.
 */
public class RetrofitClient {

    // Production API base URL – do NOT change.
    private static final String BASE_URL = "https://bloodconnect-y58i.onrender.com/api/";

    private static Retrofit retrofit = null;
    private static final Object lock = new Object();

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /**
     * Returns the singleton ApiService.
     *
     * @param context Application or Activity context (used to access SharedPreferences and,
     *                on forced logout, to start LoginActivity).
     */
    public static ApiService getApiService(Context context) {
        return getClient(context.getApplicationContext()).create(ApiService.class);
    }

    /**
     * Resets the Retrofit singleton. Must be called after logout so that the next
     * login starts with a clean OkHttpClient that will pick up the new tokens.
     */
    public static void resetClient() {
        synchronized (lock) {
            retrofit = null;
        }
    }

    // -------------------------------------------------------------------------
    // Internal
    // -------------------------------------------------------------------------

    private static Retrofit getClient(Context appContext) {
        synchronized (lock) {
            if (retrofit == null) {
                retrofit = buildRetrofit(appContext);
            }
            return retrofit;
        }
    }

    private static Retrofit buildRetrofit(Context appContext) {
        // Log only request lines and HTTP status – never request/response bodies.
        HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
        loggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BASIC);

        // Reads the current access token from SharedPreferences on every request.
        // This is intentional: after a silent token refresh the new access token must be
        // available immediately for the retried request without rebuilding the client.
        Interceptor authInterceptor = chain -> {
            Request original = chain.request();

            String noAuth = original.header("No-Authentication");

            Request.Builder builder = original.newBuilder();

            if (noAuth == null) {
                TokenManager tokenManager = new TokenManager(appContext);
                String accessToken = tokenManager.getAccessToken();
                if (accessToken != null && !accessToken.isEmpty()) {
                    builder.header("Authorization", "Bearer " + accessToken);
                }
            }

            // Strip the internal No-Authentication marker before sending.
            builder.removeHeader("No-Authentication");

            return chain.proceed(builder.build());
        };

        // When the server returns HTTP 401 on an authenticated request, attempt a silent
        // token refresh before giving up and forcing the user to log in again.
        Authenticator tokenRefreshAuthenticator = new Authenticator() {
            @Override
            public Request authenticate(Route route, Response response) {
                // Guard: if this is already a refresh/login/logout request, do not retry.
                String requestUrl = response.request().url().toString();
                if (requestUrl.contains("auth/token/refresh/")
                        || requestUrl.contains("auth/login/")
                        || requestUrl.contains("auth/logout/")) {
                    return null; // Give up, do not retry.
                }

                // Guard: stop after one refresh attempt to prevent infinite loops.
                if (responseCount(response) >= 2) {
                    forceLogout(appContext);
                    return null;
                }

                TokenManager tokenManager = new TokenManager(appContext);
                String refreshToken = tokenManager.getRefreshToken();
                if (refreshToken == null || refreshToken.isEmpty()) {
                    // No refresh token stored – force logout immediately.
                    forceLogout(appContext);
                    return null;
                }

                // Perform a synchronous token refresh (called on a background OkHttp thread).
                synchronized (RetrofitClient.class) {
                    // Check if another thread already refreshed the token
                    TokenManager tm = new TokenManager(appContext);
                    String currentAccessToken = tm.getAccessToken();
                    String originalToken = response.request().header("Authorization");
                    if (originalToken != null && currentAccessToken != null && !originalToken.contains(currentAccessToken)) {
                        return response.request().newBuilder()
                                .header("Authorization", "Bearer " + currentAccessToken)
                                .build();
                    }

                    try {
                        // Build a minimal Retrofit instance without the authenticator to avoid
                        // recursive calls during the refresh itself.
                        Retrofit refreshRetrofit = new Retrofit.Builder()
                                .baseUrl(BASE_URL)
                                .client(new OkHttpClient.Builder()
                                        .addInterceptor(loggingInterceptor)
                                        .build())
                                .addConverterFactory(GsonConverterFactory.create())
                                .build();

                        ApiService refreshService = refreshRetrofit.create(ApiService.class);
                        retrofit2.Response<TokenRefreshResponse> refreshResponse =
                                refreshService.refreshToken(new TokenRefreshRequest(refreshToken))
                                              .execute();

                        if (refreshResponse.isSuccessful() && refreshResponse.body() != null) {
                            TokenRefreshResponse body = refreshResponse.body();
                            String newAccessToken = body.getAccess();

                            if (newAccessToken == null || newAccessToken.isEmpty()) {
                                forceLogout(appContext);
                                return null;
                            }

                            // Persist the new tokens.
                            tm.saveAccessToken(newAccessToken);
                            // Save rotated refresh token only if the server returned one.
                            if (body.getRefresh() != null && !body.getRefresh().isEmpty()) {
                                tm.saveRefreshToken(body.getRefresh());
                            }

                            // Retry the original request with the new access token.
                            return response.request().newBuilder()
                                    .header("Authorization", "Bearer " + newAccessToken)
                                    .build();

                        } else {
                            // Refresh token is invalid or expired – force logout.
                            forceLogout(appContext);
                            return null;
                        }

                    } catch (Exception e) {
                        // Network failure during refresh – do not force logout; the user may just
                        // be offline. Return null to propagate the 401 to the caller.
                        return null;
                    }
                }
            }
        };

        OkHttpClient client = new OkHttpClient.Builder()
                .addInterceptor(authInterceptor)
                .authenticator(tokenRefreshAuthenticator)
                .addInterceptor(loggingInterceptor)
                .build();

        return new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build();
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /** Counts how many 401 responses have been received for the same request chain. */
    private static int responseCount(Response response) {
        int result = 1;
        while ((response = response.priorResponse()) != null) {
            result++;
        }
        return result;
    }

    /**
     * Clears local tokens, resets the Retrofit singleton, and navigates to LoginActivity.
     * Called only when the refresh token is confirmed invalid/expired.
     * Uses FLAG_ACTIVITY_NEW_TASK because this is triggered from an OkHttp background thread.
     */
    private static void forceLogout(Context appContext) {
        TokenManager tokenManager = new TokenManager(appContext);
        tokenManager.clearTokens();

        // Reset the singleton so the next login gets a clean client.
        synchronized (lock) {
            retrofit = null;
        }

        Intent intent = new Intent(appContext, LoginActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        appContext.startActivity(intent);
    }
}
