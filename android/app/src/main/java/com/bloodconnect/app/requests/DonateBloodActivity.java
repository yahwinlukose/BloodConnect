package com.bloodconnect.app.requests;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.bloodconnect.app.R;
import com.bloodconnect.app.auth.LoginActivity;
import com.bloodconnect.app.auth.TokenManager;
import com.bloodconnect.app.profile.DonorProfileActivity;
import com.bloodconnect.app.network.RetrofitClient;
import com.bloodconnect.app.network.models.DonorMatchForDonor;
import com.google.android.material.progressindicator.CircularProgressIndicator;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class DonateBloodActivity extends AppCompatActivity {

    private RecyclerView recyclerView;
    private SwipeRefreshLayout swipeRefresh;
    private TextView tvEmptyState;
    private CircularProgressIndicator progressIndicator;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_donate_blood);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Donate Blood");
        }
        toolbar.setNavigationOnClickListener(v -> onBackPressed());

        recyclerView = findViewById(R.id.recyclerView);
        swipeRefresh = findViewById(R.id.swipeRefresh);
        tvEmptyState = findViewById(R.id.tvEmptyState);
        progressIndicator = findViewById(R.id.progressIndicator);

        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        swipeRefresh.setOnRefreshListener(this::fetchMatches);

        fetchMatches();
    }

    @Override
    protected void onResume() {
        super.onResume();
        fetchMatches();
    }

    private void fetchMatches() {
        if (!swipeRefresh.isRefreshing()) {
            progressIndicator.setVisibility(View.VISIBLE);
        }
        tvEmptyState.setVisibility(View.GONE);
        recyclerView.setVisibility(View.GONE);

        RetrofitClient.getApiService(this).getDonorMatches().enqueue(new Callback<List<DonorMatchForDonor>>() {
            @Override
            public void onResponse(@NonNull Call<List<DonorMatchForDonor>> call, @NonNull Response<List<DonorMatchForDonor>> response) {
                swipeRefresh.setRefreshing(false);
                progressIndicator.setVisibility(View.GONE);

                if (response.isSuccessful() && response.body() != null) {
                    List<DonorMatchForDonor> matches = response.body();
                    if (matches.isEmpty()) {
                        tvEmptyState.setText("No blood requests are currently available for you.");
                        tvEmptyState.setVisibility(View.VISIBLE);
                    } else {
                        DonorMatchForDonorAdapter adapter = new DonorMatchForDonorAdapter(matches);
                        recyclerView.setAdapter(adapter);
                        recyclerView.setVisibility(View.VISIBLE);
                    }
                } else if (response.code() == 403) {
                    tvEmptyState.setText("You must create a Donor Profile to donate blood.");
                    tvEmptyState.setVisibility(View.VISIBLE);
                    Toast.makeText(DonateBloodActivity.this, "Please create a Donor Profile", Toast.LENGTH_LONG).show();
                    startActivity(new Intent(DonateBloodActivity.this, DonorProfileActivity.class));
                } else if (response.code() == 401) {
                    handleSessionExpired();
                } else {
                    tvEmptyState.setText("Failed to load requests. Please try again.");
                    tvEmptyState.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<DonorMatchForDonor>> call, @NonNull Throwable t) {
                swipeRefresh.setRefreshing(false);
                progressIndicator.setVisibility(View.GONE);
                tvEmptyState.setText("Network error. Please check your connection.");
                tvEmptyState.setVisibility(View.VISIBLE);
            }
        });
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
