package com.bloodconnect.app.requests;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.bloodconnect.app.R;
import com.bloodconnect.app.auth.LoginActivity;
import com.bloodconnect.app.auth.TokenManager;
import com.bloodconnect.app.network.RetrofitClient;
import com.bloodconnect.app.network.models.BloodRequestForDonor;
import com.bloodconnect.app.network.models.DonorMatchForDonor;
import com.google.gson.Gson;

import java.io.IOException;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class DonorRequestDetailsActivity extends AppCompatActivity {

    private static final String TAG = "DonorRequestDetails";

    private DonorMatchForDonor match;
    private TextView tvStatus, tvErrorState;
    private LinearLayout llActions;
    private Button btnAccept, btnReject;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_donor_request_details);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Request Details");
        }
        toolbar.setNavigationOnClickListener(v -> onBackPressed());

        TextView tvBloodGroup = findViewById(R.id.tvBloodGroup);
        TextView tvUrgency = findViewById(R.id.tvUrgency);
        TextView tvUnits = findViewById(R.id.tvUnits);
        TextView tvHospital = findViewById(R.id.tvHospital);
        TextView tvLocation = findViewById(R.id.tvLocation);
        TextView tvDate = findViewById(R.id.tvDate);
        TextView tvDistance = findViewById(R.id.tvDistance);
        TextView tvDescription = findViewById(R.id.tvDescription);
        TextView tvDescriptionLabel = findViewById(R.id.tvDescriptionLabel);

        tvStatus = findViewById(R.id.tvStatus);
        tvErrorState = findViewById(R.id.tvErrorState);
        llActions = findViewById(R.id.llActions);
        btnAccept = findViewById(R.id.btnAccept);
        btnReject = findViewById(R.id.btnReject);

        String matchJson = getIntent().getStringExtra("match_json");
        if (matchJson != null) {
            match = new Gson().fromJson(matchJson, DonorMatchForDonor.class);
            BloodRequestForDonor request = match.getBloodRequest();

            if (request != null) {
                tvBloodGroup.setText(request.getBloodGroup());
                tvUrgency.setText(request.getUrgency());
                tvUnits.setText(request.getUnitsRequired() + " units");
                tvHospital.setText(request.getHospitalName());
                tvLocation.setText(request.getLocation());
                tvDate.setText(request.getRequiredDate());

                if (request.getDescription() != null && !request.getDescription().isEmpty()) {
                    tvDescription.setText(request.getDescription());
                } else {
                    tvDescription.setVisibility(View.GONE);
                    tvDescriptionLabel.setVisibility(View.GONE);
                }
            }

            if (match.getDistanceKm() != null) {
                tvDistance.setText(String.format("%.1f km away", match.getDistanceKm()));
            } else {
                tvDistance.setText("Distance unavailable");
            }

            updateStatusUI(match.getStatus());

        } else {
            Toast.makeText(this, "Error loading details", Toast.LENGTH_SHORT).show();
            finish();
        }

        btnAccept.setOnClickListener(v -> handleAction("ACCEPT"));
        btnReject.setOnClickListener(v -> handleAction("REJECT"));
    }

    private void updateStatusUI(String status) {
        tvStatus.setText(status);
        if ("PENDING".equals(status) || "NOTIFIED".equals(status)) {
            llActions.setVisibility(View.VISIBLE);
        } else {
            llActions.setVisibility(View.GONE);
        }
    }

    private void handleAction(String action) {
        setButtonsEnabled(false);
        tvErrorState.setVisibility(View.GONE);

        Call<DonorMatchForDonor> call;
        if ("ACCEPT".equals(action)) {
            call = RetrofitClient.getApiService(this).acceptDonorMatch(match.getId());
        } else {
            call = RetrofitClient.getApiService(this).rejectDonorMatch(match.getId());
        }

        call.enqueue(new Callback<DonorMatchForDonor>() {
            @Override
            public void onResponse(@NonNull Call<DonorMatchForDonor> call, @NonNull Response<DonorMatchForDonor> response) {
                if (response.isSuccessful() && response.body() != null) {
                    DonorMatchForDonor updatedMatch = response.body();
                    updateStatusUI(updatedMatch.getStatus());

                    String message = "ACCEPT".equals(action) ?
                            "You have successfully accepted the request!" :
                            "You have declined this request.";
                    Toast.makeText(DonorRequestDetailsActivity.this, message, Toast.LENGTH_LONG).show();
                } else if (response.code() == 401) {
                    handleSessionExpired();
                } else if (response.code() == 400) {
                    try {
                        String errorBody = response.errorBody() != null ? response.errorBody().string() : "Validation error";
                        Log.e(TAG, "Backend validation error: " + errorBody);
                        showError("Failed to update status. Please refresh and try again.");
                    } catch (IOException e) {
                        showError("Invalid request.");
                    }
                } else {
                    showError("An unexpected error occurred.");
                }
            }

            @Override
            public void onFailure(@NonNull Call<DonorMatchForDonor> call, @NonNull Throwable t) {
                showError("Network error. Please check your connection.");
            }
        });
    }

    private void setButtonsEnabled(boolean enabled) {
        btnAccept.setEnabled(enabled);
        btnReject.setEnabled(enabled);
    }

    private void showError(String message) {
        setButtonsEnabled(true);
        tvErrorState.setText(message);
        tvErrorState.setVisibility(View.VISIBLE);
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
}
