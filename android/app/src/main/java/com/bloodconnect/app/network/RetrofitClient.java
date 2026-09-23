package com.bloodconnect.app.network;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * RetrofitClient provides a singleton instance of Retrofit configured to communicate with the backend API.
 */
public class RetrofitClient {

    // Base URL points to the local development server.
    // 10.0.2.2 is used instead of 127.0.1.1 or localhost because the Android emulator 
    // runs in a virtual machine and maps 10.0.2.2 to the host machine's loopback interface.
    private static final String BASE_URL = "http://10.0.2.2:8001/api/";
    private static Retrofit retrofit = null;

    /**
     * Gets the singleton instance of Retrofit.
     * Configures the OkHttpClient with an interceptor to log HTTP requests and responses for debugging.
     *
     * @param context Application or Activity context to initialize TokenManager
     * @return Retrofit instance
     */
    public static Retrofit getClient(android.content.Context context) {
        if (retrofit == null) {
            
            // Set up interceptor for network debugging
            // IMPORTANT: Level.BASIC logs request lines and response status without exposing bodies.
            // This prevents sensitive information (like JWT tokens and passwords) from appearing in Logcat.
            HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
            loggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BASIC);

            // Auth interceptor to inject Bearer token
            okhttp3.Interceptor authInterceptor = chain -> {
                okhttp3.Request original = chain.request();
                okhttp3.Request.Builder builder = original.newBuilder();

                com.bloodconnect.app.auth.TokenManager tokenManager = new com.bloodconnect.app.auth.TokenManager(context);
                String token = tokenManager.getAccessToken();

                if (token != null && !token.isEmpty()) {
                    builder.header("Authorization", "Bearer " + token);
                }

                return chain.proceed(builder.build());
            };

            OkHttpClient client = new OkHttpClient.Builder()
                    .addInterceptor(authInterceptor)
                    .addInterceptor(loggingInterceptor)
                    .build();

            // Build Retrofit instance with Gson converter
            retrofit = new Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .client(client)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit;
    }

    /**
     * Helper method to directly get the ApiService instance.
     *
     * @param context Application or Activity context
     * @return ApiService
     */
    public static ApiService getApiService(android.content.Context context) {
        return getClient(context).create(ApiService.class);
    }
}
