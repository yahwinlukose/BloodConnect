package com.bloodconnect.app.profile;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.bloodconnect.app.R;
import com.bloodconnect.app.auth.LoginActivity;
import com.bloodconnect.app.auth.TokenManager;
import com.bloodconnect.app.network.RetrofitClient;
import com.bloodconnect.app.network.models.DonorProfile;
import com.bloodconnect.app.network.models.DonorProfileCreateRequest;
import com.bloodconnect.app.network.models.DonorProfileUpdateRequest;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.datepicker.CalendarConstraints;
import com.google.android.material.datepicker.DateValidatorPointBackward;
import com.google.android.material.datepicker.MaterialDatePicker;
import com.google.android.material.switchmaterial.SwitchMaterial;
import com.google.android.material.textfield.TextInputEditText;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class DonorProfileActivity extends AppCompatActivity {

    private AutoCompleteTextView inputBloodGroup;
    private AutoCompleteTextView inputGender;
    private TextInputEditText inputDob;
    private TextInputEditText inputLocation;
    private TextInputEditText inputLatitude;
    private TextInputEditText inputLongitude;
    private TextInputEditText inputLastDonation;
    private SwitchMaterial switchAvailable;
    private MaterialButton btnSubmit;
    private View progressOverlay;

    private boolean isEditMode = false;
    private SimpleDateFormat apiDateFormat = new SimpleDateFormat("yyyy-MM-dd", Locale.US);

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_donor_profile);

        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle("Donor Profile");
        }
        
        androidx.appcompat.widget.Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }
        toolbar.setNavigationOnClickListener(v -> onBackPressed());

        inputBloodGroup = findViewById(R.id.inputBloodGroup);
        inputGender = findViewById(R.id.inputGender);
        inputDob = findViewById(R.id.inputDob);
        inputLocation = findViewById(R.id.inputLocation);
        inputLatitude = findViewById(R.id.inputLatitude);
        inputLongitude = findViewById(R.id.inputLongitude);
        inputLastDonation = findViewById(R.id.inputLastDonation);
        switchAvailable = findViewById(R.id.switchAvailable);
        btnSubmit = findViewById(R.id.btnSubmitProfile);
        progressOverlay = findViewById(R.id.progressOverlay);

        setupDropdowns();
        setupDatePickers();

        btnSubmit.setOnClickListener(v -> submitProfile());

        fetchProfile();
    }

    private void setupDropdowns() {
        String[] bloodGroups = new String[]{"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"};
        ArrayAdapter<String> bgAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, bloodGroups);
        inputBloodGroup.setAdapter(bgAdapter);

        String[] genders = new String[]{"MALE", "FEMALE", "OTHER", "PREFER_NOT_TO_SAY"};
        ArrayAdapter<String> genderAdapter = new ArrayAdapter<>(this, android.R.layout.simple_dropdown_item_1line, genders);
        inputGender.setAdapter(genderAdapter);
    }

    private void setupDatePickers() {
        inputDob.setOnClickListener(v -> showDatePicker(inputDob));
        inputLastDonation.setOnClickListener(v -> showDatePicker(inputLastDonation));
    }

    private void showDatePicker(TextInputEditText field) {
        CalendarConstraints constraints = new CalendarConstraints.Builder()
                .setValidator(DateValidatorPointBackward.now())
                .build();

        MaterialDatePicker<Long> picker = MaterialDatePicker.Builder.datePicker()
                .setCalendarConstraints(constraints)
                .setTitleText("Select Date")
                .build();

        picker.addOnPositiveButtonClickListener(selection -> {
            field.setText(apiDateFormat.format(new Date(selection)));
        });

        picker.show(getSupportFragmentManager(), "DATE_PICKER");
    }

    private void fetchProfile() {
        setLoading(true);
        RetrofitClient.getApiService(this).getDonorProfile().enqueue(new Callback<DonorProfile>() {
            @Override
            public void onResponse(@NonNull Call<DonorProfile> call, @NonNull Response<DonorProfile> response) {
                setLoading(false);
                if (response.isSuccessful() && response.body() != null) {
                    isEditMode = true;
                    btnSubmit.setText("Update Profile");
                    populateForm(response.body());
                } else if (response.code() == 404) {
                    isEditMode = false;
                    btnSubmit.setText("Create Donor Profile");
                } else if (response.code() == 401) {
                    handleSessionExpired();
                } else {
                    Toast.makeText(DonorProfileActivity.this, "Failed to load profile.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(@NonNull Call<DonorProfile> call, @NonNull Throwable t) {
                setLoading(false);
                Toast.makeText(DonorProfileActivity.this, "Network error fetching profile.", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void populateForm(DonorProfile profile) {
        inputBloodGroup.setText(profile.getBloodGroup(), false);
        inputGender.setText(profile.getGender(), false);
        inputDob.setText(profile.getDateOfBirth());
        inputLocation.setText(profile.getLocation() != null ? profile.getLocation() : "");
        inputLatitude.setText(profile.getLatitude() != null ? String.valueOf(profile.getLatitude()) : "");
        inputLongitude.setText(profile.getLongitude() != null ? String.valueOf(profile.getLongitude()) : "");
        inputLastDonation.setText(profile.getLastDonationDate() != null ? profile.getLastDonationDate() : "");
        switchAvailable.setChecked(profile.getIsAvailable() != null ? profile.getIsAvailable() : true);
    }

    private void submitProfile() {
        String bloodGroup = inputBloodGroup.getText().toString();
        String gender = inputGender.getText().toString();
        String dob = inputDob.getText().toString();
        String location = inputLocation.getText().toString().trim();
        String latStr = inputLatitude.getText().toString().trim();
        String lngStr = inputLongitude.getText().toString().trim();
        String lastDonation = inputLastDonation.getText().toString();
        boolean isAvailable = switchAvailable.isChecked();

        // Validation
        if (TextUtils.isEmpty(bloodGroup)) {
            Toast.makeText(this, "Blood Group is required", Toast.LENGTH_SHORT).show();
            return;
        }
        if (TextUtils.isEmpty(gender)) {
            Toast.makeText(this, "Gender is required", Toast.LENGTH_SHORT).show();
            return;
        }
        if (TextUtils.isEmpty(dob)) {
            Toast.makeText(this, "Date of Birth is required", Toast.LENGTH_SHORT).show();
            return;
        }

        Double latitude = null;
        if (!TextUtils.isEmpty(latStr)) {
            try {
                latitude = Double.parseDouble(latStr);
                if (latitude < -90 || latitude > 90) {
                    inputLatitude.setError("Latitude must be between -90 and 90");
                    return;
                }
            } catch (NumberFormatException e) {
                inputLatitude.setError("Invalid latitude");
                return;
            }
        }

        Double longitude = null;
        if (!TextUtils.isEmpty(lngStr)) {
            try {
                longitude = Double.parseDouble(lngStr);
                if (longitude < -180 || longitude > 180) {
                    inputLongitude.setError("Longitude must be between -180 and 180");
                    return;
                }
            } catch (NumberFormatException e) {
                inputLongitude.setError("Invalid longitude");
                return;
            }
        }

        if (TextUtils.isEmpty(lastDonation)) {
            lastDonation = null;
        }

        setLoading(true);

        if (isEditMode) {
            DonorProfileUpdateRequest request = new DonorProfileUpdateRequest(bloodGroup, gender, dob, location, latitude, longitude, isAvailable, lastDonation);
            RetrofitClient.getApiService(this).updateDonorProfile(request).enqueue(new Callback<DonorProfile>() {
                @Override
                public void onResponse(@NonNull Call<DonorProfile> call, @NonNull Response<DonorProfile> response) {
                    setLoading(false);
                    if (response.isSuccessful()) {
                        Toast.makeText(DonorProfileActivity.this, "Profile updated successfully", Toast.LENGTH_SHORT).show();
                    } else if (response.code() == 401) {
                        handleSessionExpired();
                    } else {
                        Toast.makeText(DonorProfileActivity.this, "Update failed. Check your inputs.", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(@NonNull Call<DonorProfile> call, @NonNull Throwable t) {
                    setLoading(false);
                    Toast.makeText(DonorProfileActivity.this, "Network error.", Toast.LENGTH_SHORT).show();
                }
            });
        } else {
            DonorProfileCreateRequest request = new DonorProfileCreateRequest(bloodGroup, gender, dob, location, latitude, longitude, isAvailable, lastDonation);
            RetrofitClient.getApiService(this).createDonorProfile(request).enqueue(new Callback<DonorProfile>() {
                @Override
                public void onResponse(@NonNull Call<DonorProfile> call, @NonNull Response<DonorProfile> response) {
                    setLoading(false);
                    if (response.isSuccessful()) {
                        Toast.makeText(DonorProfileActivity.this, "Profile created successfully", Toast.LENGTH_SHORT).show();
                        isEditMode = true;
                        btnSubmit.setText("Update Profile");
                    } else if (response.code() == 401) {
                        handleSessionExpired();
                    } else {
                        Toast.makeText(DonorProfileActivity.this, "Creation failed. Check your inputs.", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(@NonNull Call<DonorProfile> call, @NonNull Throwable t) {
                    setLoading(false);
                    Toast.makeText(DonorProfileActivity.this, "Network error.", Toast.LENGTH_SHORT).show();
                }
            });
        }
    }

    private void setLoading(boolean loading) {
        progressOverlay.setVisibility(loading ? View.VISIBLE : View.GONE);
        btnSubmit.setEnabled(!loading);
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
