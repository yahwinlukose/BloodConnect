package com.bloodconnect.app.auth;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.bloodconnect.app.R;
import com.bloodconnect.app.home.HomeActivity;
import com.google.android.material.button.MaterialButton;

public class RegisterActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        MaterialButton btnRegister = findViewById(R.id.btnRegister);
        TextView tvLogin = findViewById(R.id.tvLogin);

        // Mock register - bypasses actual auth for now
        btnRegister.setOnClickListener(v -> {
            Toast.makeText(this, "Registering...", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent(RegisterActivity.this, HomeActivity.class);
            startActivity(intent);
            finishAffinity(); // Clear stack
        });

        // Navigate back to Login Screen
        tvLogin.setOnClickListener(v -> {
            finish();
        });
    }
}
