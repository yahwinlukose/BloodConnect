package com.bloodconnect.app.home;

import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.bloodconnect.app.R;
import com.bloodconnect.app.requests.RequestBloodActivity;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.google.android.material.card.MaterialCardView;

public class HomeActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        
        // Mock unified user actions
        MaterialCardView cardDonate = findViewById(R.id.cardDonateBlood);
        MaterialCardView cardRequest = findViewById(R.id.cardRequestBlood);
        
        cardDonate.setOnClickListener(v -> {
            Toast.makeText(this, "Navigating to Donate flow...", Toast.LENGTH_SHORT).show();
        });
        
        cardRequest.setOnClickListener(v -> {
            startActivity(new Intent(this, RequestBloodActivity.class));
        });

        // Setup bottom navigation
        BottomNavigationView bottomNav = findViewById(R.id.bottomNavigation);
        bottomNav.setOnItemSelectedListener(item -> {
            int itemId = item.getItemId();
            if (itemId == R.id.nav_home) {
                return true;
            } else if (itemId == R.id.nav_requests) {
                Toast.makeText(this, "Requests selected", Toast.LENGTH_SHORT).show();
                return true;
            } else if (itemId == R.id.nav_profile) {
                Toast.makeText(this, "Profile selected", Toast.LENGTH_SHORT).show();
                return true;
            }
            return false;
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.home_toolbar_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.btnNotifications) {
            Toast.makeText(this, "Notifications coming soon", Toast.LENGTH_SHORT).show();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}
