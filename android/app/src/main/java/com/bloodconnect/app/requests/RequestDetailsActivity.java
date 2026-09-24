package com.bloodconnect.app.requests;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.bloodconnect.app.R;
import com.bloodconnect.app.auth.LoginActivity;
import com.bloodconnect.app.auth.TokenManager;
import com.bloodconnect.app.network.RetrofitClient;
import com.bloodconnect.app.network.models.BloodRequest;
import com.bloodconnect.app.network.models.DonorMatch;
import com.google.android.material.progressindicator.CircularProgressIndicator;
import com.google.gson.Gson;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class RequestDetailsActivity extends AppCompatActivity {

    private int requestId;
    private Button btnFindDonors;
    private CircularProgressIndicator progressIndicator;
    private TextView tvErrorState;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_request_details);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Request Details");
        }
        toolbar.setNavigationOnClickListener(v -> onBackPressed());

        TextView tvBloodGroup = findViewById(R.id.tvBloodGroup);
        TextView tvUnits = findViewById(R.id.tvUnits);
        TextView tvHospital = findViewById(R.id.tvHospital);
        TextView tvLocation = findViewById(R.id.tvLocation);
        TextView tvDate = findViewById(R.id.tvDate);
        TextView tvUrgency = findViewById(R.id.tvUrgency);
        TextView tvStatus = findViewById(R.id.tvStatus);
        TextView tvDescription = findViewById(R.id.tvDescription);
        
        btnFindDonors = findViewById(R.id.btnFindDonors);
        progressIndicator = findViewById(R.id.progressIndicator);
        tvErrorState = findViewById(R.id.tvErrorState);

        String requestJson = getIntent().getStringExtra("request_json");
        if (requestJson != null) {
            BloodRequest request = new Gson().fromJson(requestJson, BloodRequest.class);
            requestId = request.getId();
            
            tvBloodGroup.setText(request.getBloodGroup() != null ? request.getBloodGroup() : "Unknown");
            tvUnits.setText(request.getUnitsRequired() + " units");
            tvHospital.setText(request.getHospitalName() != null ? request.getHospitalName() : "N/A");
            tvLocation.setText(request.getLocation() != null ? request.getLocation() : "N/A");
            tvDate.setText("Required Date: " + (request.getRequiredDate() != null ? request.getRequiredDate() : "N/A"));
            tvUrgency.setText("Urgency: " + (request.getUrgency() != null ? request.getUrgency() : "N/A"));
            tvStatus.setText("Status: " + (request.getStatus() != null ? request.getStatus() : "N/A"));
            tvDescription.setText(request.getDescription() != null ? request.getDescription() : "");
        } else {
            requestId = getIntent().getIntExtra("request_id", -1);
            if (requestId == -1) {
                Toast.makeText(this, "Invalid request", Toast.LENGTH_SHORT).show();
                finish();
                return;
            }
        }

        btnFindDonors.setOnClickListener(v -> generateMatches());
    }

    private void generateMatches() {
        btnFindDonors.setEnabled(false);
        progressIndicator.setVisibility(View.VISIBLE);
        tvErrorState.setVisibility(View.GONE);

        RetrofitClient.getApiService(this).generateMatches(requestId).enqueue(new Callback<List<DonorMatch>>() {
            @Override
            public void onResponse(@NonNull Call<List<DonorMatch>> call, @NonNull Response<List<DonorMatch>> response) {
                btnFindDonors.setEnabled(true);
                progressIndicator.setVisibility(View.GONE);

                if (response.isSuccessful()) {
                    openMatchedDonors();
                } else if (response.code() == 401) {
                    handleSessionExpired();
                } else {
                    showError("Failed to generate matches. Please try again.");
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<DonorMatch>> call, @NonNull Throwable t) {
                btnFindDonors.setEnabled(true);
                progressIndicator.setVisibility(View.GONE);
                showError("Network error. Please check your connection.");
            }
        });
    }
    
    private void openMatchedDonors() {
        Intent intent = new Intent(this, MatchedDonorsActivity.class);
        intent.putExtra("request_id", requestId);
        startActivity(intent);
    }

    private void handleSessionExpired() {
        Toast.makeText(this, "Session expired. Please log in again.", Toast.LENGTH_LONG).show();
        TokenManager tokenManager = new TokenManager(this);
        tokenManager.clearTokens();
        Intent intent = new Intent(this, LoginActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
    
    private void showError(String message) {
        tvErrorState.setVisibility(View.VISIBLE);
        tvErrorState.setText(message);
    }
}
