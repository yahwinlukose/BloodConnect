package com.bloodconnect.app;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;

import androidx.appcompat.app.AppCompatActivity;

import com.bloodconnect.app.auth.LoginActivity;
import com.bloodconnect.app.auth.TokenManager;
import com.bloodconnect.app.home.HomeActivity;

/**
 * SplashActivity is the app entry point.
 *
 * Session-persistence logic
 * ─────────────────────────
 * After the splash delay the activity checks whether access and refresh tokens are already
 * stored in SharedPreferences (via TokenManager).
 *
 * • Tokens present → navigate directly to HomeActivity. The OkHttp Authenticator in
 *   RetrofitClient will silently refresh the access token if it has expired.
 * • Tokens absent  → navigate to LoginActivity.
 *
 * This means users who have previously logged in and have not explicitly logged out
 * remain authenticated across app restarts and Activity recreation.
 */
public class SplashActivity extends AppCompatActivity {

    private static final long SPLASH_DELAY_MS = 2000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            TokenManager tokenManager = new TokenManager(SplashActivity.this);

            Intent intent;
            if (tokenManager.hasTokens()) {
                // User has a saved session – go straight to the authenticated home screen.
                intent = new Intent(SplashActivity.this, HomeActivity.class);
            } else {
                // No saved session – require the user to log in.
                intent = new Intent(SplashActivity.this, LoginActivity.class);
            }

            startActivity(intent);
            finish(); // Remove SplashActivity from the back stack.
        }, SPLASH_DELAY_MS);
    }
}
