package com.bloodconnect.app.auth;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.bloodconnect.app.R;
import com.bloodconnect.app.home.HomeActivity;
import com.bloodconnect.app.network.RetrofitClient;
import com.bloodconnect.app.network.models.LoginRequest;
import com.bloodconnect.app.network.models.LoginResponse;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    private TextInputEditText etEmail;
    private TextInputEditText etPassword;
    private MaterialButton btnLogin;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        etEmail = findViewById(R.id.etEmail);
        etPassword = findViewById(R.id.etPassword);
        btnLogin = findViewById(R.id.btnLogin);
        TextView tvRegister = findViewById(R.id.tvRegister);

        btnLogin.setOnClickListener(v -> performLogin());

        // Navigate to Register Screen
        tvRegister.setOnClickListener(v -> {
            Intent intent = new Intent(LoginActivity.this, RegisterActivity.class);
            startActivity(intent);
        });
    }

    private void performLogin() {
        String email = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString();

        if (TextUtils.isEmpty(email)) {
            etEmail.setError("Email is required");
            return;
        }

        if (TextUtils.isEmpty(password)) {
            etPassword.setError("Password is required");
            return;
        }

        // Disable button to prevent multiple simultaneous requests
        btnLogin.setEnabled(false);
        btnLogin.setText("Logging in...");

        LoginRequest request = new LoginRequest(email, password);

        RetrofitClient.getApiService(LoginActivity.this).login(request).enqueue(new Callback<LoginResponse>() {
            @Override
            public void onResponse(@NonNull Call<LoginResponse> call, @NonNull Response<LoginResponse> response) {
                // Always re-enable the button when request finishes
                btnLogin.setEnabled(true);
                btnLogin.setText(getString(R.string.login));

                if (response.isSuccessful() && response.body() != null) {
                    // HTTP 200 - Login successful
                    LoginResponse loginResponse = response.body();
                    
                    // Save tokens securely
                    TokenManager tokenManager = new TokenManager(LoginActivity.this);
                    tokenManager.saveAccessToken(loginResponse.getAccess());
                    tokenManager.saveRefreshToken(loginResponse.getRefresh());

                    Toast.makeText(LoginActivity.this, "Login successful", Toast.LENGTH_SHORT).show();
                    
                    // Navigate to Home
                    Intent intent = new Intent(LoginActivity.this, HomeActivity.class);
                    startActivity(intent);
                    finish(); // Prevent user from returning to login
                } else if (response.code() == 400 || response.code() == 401) {
                    // HTTP 400/401 - Invalid credentials
                    Toast.makeText(LoginActivity.this, "Invalid email or password", Toast.LENGTH_LONG).show();
                } else {
                    // Other HTTP errors
                    Toast.makeText(LoginActivity.this, "Server error. Please try again later.", Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<LoginResponse> call, @NonNull Throwable t) {
                // Network failure
                btnLogin.setEnabled(true);
                btnLogin.setText(getString(R.string.login));
                Toast.makeText(LoginActivity.this, "Unable to connect to server. Please check your connection.", Toast.LENGTH_LONG).show();
            }
        });
    }
}
