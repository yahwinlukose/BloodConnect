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
import com.bloodconnect.app.network.RetrofitClient;
import com.bloodconnect.app.network.models.DonorMatch;
import com.google.android.material.progressindicator.CircularProgressIndicator;

import java.util.ArrayList;
import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MatchedDonorsActivity extends AppCompatActivity {

    private int requestId;
    private RecyclerView recyclerView;
    private DonorMatchAdapter adapter;
    private SwipeRefreshLayout swipeRefreshLayout;
    private CircularProgressIndicator progressIndicator;
    private TextView tvEmptyState;
    private TextView tvErrorState;
    private List<DonorMatch> donorMatches = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_matched_donors);

        requestId = getIntent().getIntExtra("request_id", -1);
        if (requestId == -1) {
            Toast.makeText(this, "Invalid request ID", Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Matched Donors");
        }
        toolbar.setNavigationOnClickListener(v -> onBackPressed());

        recyclerView = findViewById(R.id.recyclerView);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);
        progressIndicator = findViewById(R.id.progressIndicator);
        tvEmptyState = findViewById(R.id.tvEmptyState);
        tvErrorState = findViewById(R.id.tvErrorState);

        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new DonorMatchAdapter(donorMatches);
        recyclerView.setAdapter(adapter);

        swipeRefreshLayout.setOnRefreshListener(this::fetchMatches);

        fetchMatches();
    }

    private void fetchMatches() {
        if (!swipeRefreshLayout.isRefreshing()) {
            progressIndicator.setVisibility(View.VISIBLE);
        }
        tvEmptyState.setVisibility(View.GONE);
        tvErrorState.setVisibility(View.GONE);

        RetrofitClient.getApiService(this).getMatches(requestId).enqueue(new Callback<List<DonorMatch>>() {
            @Override
            public void onResponse(@NonNull Call<List<DonorMatch>> call, @NonNull Response<List<DonorMatch>> response) {
                progressIndicator.setVisibility(View.GONE);
                swipeRefreshLayout.setRefreshing(false);

                if (response.isSuccessful() && response.body() != null) {
                    donorMatches.clear();
                    donorMatches.addAll(response.body());
                    adapter.notifyDataSetChanged();

                    if (donorMatches.isEmpty()) {
                        tvEmptyState.setVisibility(View.VISIBLE);
                        recyclerView.setVisibility(View.GONE);
                    } else {
                        tvEmptyState.setVisibility(View.GONE);
                        recyclerView.setVisibility(View.VISIBLE);
                    }
                } else if (response.code() == 401) {
                    handleSessionExpired();
                } else if (response.code() == 204) {
                    donorMatches.clear();
                    adapter.notifyDataSetChanged();
                    tvEmptyState.setVisibility(View.VISIBLE);
                    recyclerView.setVisibility(View.GONE);
                } else {
                    showError("Failed to fetch matches. Please try again.");
                }
            }

            @Override
            public void onFailure(@NonNull Call<List<DonorMatch>> call, @NonNull Throwable t) {
                progressIndicator.setVisibility(View.GONE);
                swipeRefreshLayout.setRefreshing(false);
                showError("Network error. Please check your connection.");
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

    private void showError(String message) {
        recyclerView.setVisibility(View.GONE);
        tvErrorState.setVisibility(View.VISIBLE);
        tvErrorState.setText(message);
    }
}
