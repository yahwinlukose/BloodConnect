package com.bloodconnect.app.requests;

import android.app.DatePickerDialog;
import android.os.Bundle;
import android.text.TextUtils;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.bloodconnect.app.R;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import com.google.android.material.textfield.TextInputLayout;

import android.widget.Button;
import android.Manifest;
import android.content.pm.PackageManager;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import org.maplibre.android.MapLibre;
import org.maplibre.android.maps.MapView;
import org.maplibre.android.maps.MapLibreMap;
import org.maplibre.android.maps.Style;
import org.maplibre.android.style.sources.RasterSource;
import org.maplibre.android.style.sources.TileSet;
import org.maplibre.android.style.layers.RasterLayer;
import org.maplibre.android.location.LocationComponent;
import org.maplibre.android.location.LocationComponentActivationOptions;
import org.maplibre.android.location.modes.CameraMode;
import org.maplibre.android.location.modes.RenderMode;

import java.util.Calendar;
import java.util.Locale;

public class RequestBloodActivity extends AppCompatActivity {

    private AutoCompleteTextView inputBloodGroup;
    private TextInputLayout layoutBloodGroup;

    private TextInputEditText inputUnits;
    private TextInputLayout layoutUnits;

    private TextInputEditText inputHospital;
    private TextInputLayout layoutHospital;

    private TextInputEditText inputLocation;
    private TextInputLayout layoutLocation;

    private TextInputEditText inputDate;
    private TextInputLayout layoutDate;

    private AutoCompleteTextView inputUrgency;
    private TextInputLayout layoutUrgency;

    private TextInputEditText inputDescription;
    private TextInputLayout layoutDescription;

    private MaterialButton btnSubmitRequest;
    private Button btnUseMyLocation;
    private MapView mapView;
    private MapLibreMap mapLibreMap;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        MapLibre.getInstance(this);
        setContentView(R.layout.activity_request_blood);

        setupToolbar();
        initializeViews();
        setupDropdowns();
        setupDatePicker();
        setupSubmitButton();
        setupMap(savedInstanceState);
    }

    private void setupToolbar() {
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setDisplayShowHomeEnabled(true);
        }
        toolbar.setNavigationOnClickListener(v -> onBackPressed());
    }

    private void initializeViews() {
        inputBloodGroup = findViewById(R.id.inputBloodGroup);
        layoutBloodGroup = findViewById(R.id.layoutBloodGroup);

        inputUnits = findViewById(R.id.inputUnits);
        layoutUnits = findViewById(R.id.layoutUnits);

        inputHospital = findViewById(R.id.inputHospital);
        layoutHospital = findViewById(R.id.layoutHospital);

        inputLocation = findViewById(R.id.inputLocation);
        layoutLocation = findViewById(R.id.layoutLocation);

        inputDate = findViewById(R.id.inputDate);
        layoutDate = findViewById(R.id.layoutDate);

        inputUrgency = findViewById(R.id.inputUrgency);
        layoutUrgency = findViewById(R.id.layoutUrgency);

        inputDescription = findViewById(R.id.inputDescription);
        layoutDescription = findViewById(R.id.layoutDescription);

        btnSubmitRequest = findViewById(R.id.btnSubmitRequest);
        btnUseMyLocation = findViewById(R.id.btnUseMyLocation);
        mapView = findViewById(R.id.mapView);
    }

    private void setupMap(Bundle savedInstanceState) {
        mapView.onCreate(savedInstanceState);
        mapView.getMapAsync(map -> {
            mapLibreMap = map;

            TileSet tileSet = new TileSet("2.1.0", "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png");
            RasterSource rasterSource = new RasterSource("osm-source", tileSet, 256);
            RasterLayer rasterLayer = new RasterLayer("osm-layer", "osm-source");

            Style.Builder styleBuilder = new Style.Builder()
                    .withSource(rasterSource)
                    .withLayer(rasterLayer);

            map.setStyle(styleBuilder, style -> {
                // Style loaded
            });
        });

        btnUseMyLocation.setOnClickListener(v -> {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                enableLocationComponent();
            } else {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, 100);
            }
        });
    }

    private void setupDropdowns() {
        // Blood Group Dropdown
        String[] bloodGroups = new String[]{"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"};
        ArrayAdapter<String> bloodGroupAdapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_dropdown_item_1line,
                bloodGroups
        );
        inputBloodGroup.setAdapter(bloodGroupAdapter);

        // Urgency Dropdown
        String[] urgencies = new String[]{"NORMAL", "URGENT", "CRITICAL"};
        ArrayAdapter<String> urgencyAdapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_dropdown_item_1line,
                urgencies
        );
        inputUrgency.setAdapter(urgencyAdapter);
        inputUrgency.setText("NORMAL", false);
    }

    private void setupDatePicker() {
        inputDate.setOnClickListener(v -> {
            Calendar calendar = Calendar.getInstance();
            int year = calendar.get(Calendar.YEAR);
            int month = calendar.get(Calendar.MONTH);
            int day = calendar.get(Calendar.DAY_OF_MONTH);

            DatePickerDialog datePickerDialog = new DatePickerDialog(
                    this,
                    (view, selectedYear, selectedMonth, selectedDay) -> {
                        String dateString = String.format(Locale.getDefault(), "%04d-%02d-%02d", selectedYear, selectedMonth + 1, selectedDay);
                        inputDate.setText(dateString);
                        layoutDate.setError(null);
                    },
                    year, month, day
            );

            // Do not allow selecting a past date
            datePickerDialog.getDatePicker().setMinDate(System.currentTimeMillis() - 1000);
            datePickerDialog.show();
        });
    }

    private void setupSubmitButton() {
        btnSubmitRequest.setOnClickListener(v -> {
            if (validateInput()) {
                submitRequestToApi();
            }
        });
    }

    /**
     * Submits the validated blood request to the Django backend via Retrofit.
     * Latitude and longitude are deliberately omitted (sent as null in the model)
     * because location/map selection has not been implemented yet in the UI.
     */
    private void submitRequestToApi() {
        // Disable button to prevent duplicate submissions
        btnSubmitRequest.setEnabled(false);
        btnSubmitRequest.setText("Submitting...");

        String bloodGroup = inputBloodGroup.getText().toString().trim();
        int units = Integer.parseInt(inputUnits.getText().toString().trim());
        String hospital = inputHospital.getText().toString().trim();
        String location = inputLocation.getText().toString().trim();
        String date = inputDate.getText().toString().trim();
        String urgency = inputUrgency.getText().toString().trim();
        String description = inputDescription.getText().toString().trim();

        com.bloodconnect.app.network.models.BloodRequestCreateRequest request =
            new com.bloodconnect.app.network.models.BloodRequestCreateRequest(
                bloodGroup, units, hospital, location, urgency, date, description
        );

        if (mapLibreMap != null) {
            org.maplibre.android.geometry.LatLng target = mapLibreMap.getCameraPosition().target;
            double lat = Math.round(target.getLatitude() * 1000000.0) / 1000000.0;
            double lng = Math.round(target.getLongitude() * 1000000.0) / 1000000.0;
            request.setLatitude(lat);
            request.setLongitude(lng);
        }

        com.bloodconnect.app.network.RetrofitClient.getApiService(this)
            .createBloodRequest(request)
            .enqueue(new retrofit2.Callback<com.bloodconnect.app.network.models.BloodRequestResponse>() {
                @Override
                public void onResponse(
                        @androidx.annotation.NonNull retrofit2.Call<com.bloodconnect.app.network.models.BloodRequestResponse> call,
                        @androidx.annotation.NonNull retrofit2.Response<com.bloodconnect.app.network.models.BloodRequestResponse> response) {

                    btnSubmitRequest.setEnabled(true);
                    btnSubmitRequest.setText("Submit Blood Request");

                    if (response.isSuccessful() && response.body() != null) {
                        // HTTP 201 Created
                        Toast.makeText(RequestBloodActivity.this, "Blood request created successfully", Toast.LENGTH_SHORT).show();
                        finish(); // Returns to HomeActivity
                    } else if (response.code() == 400) {
                        // HTTP 400 Bad Request / Validation Error
                        String errorBody = "";
                        try {
                            if (response.errorBody() != null) {
                                errorBody = response.errorBody().string();
                                android.util.Log.e("API_ERROR", errorBody);
                            }
                        } catch (Exception e) {}
                        Toast.makeText(RequestBloodActivity.this, "Invalid request. Please check your input.\n" + errorBody, Toast.LENGTH_LONG).show();
                    } else if (response.code() == 401 || response.code() == 403) {
                        // HTTP 401 Unauthorized
                        Toast.makeText(RequestBloodActivity.this, "Session expired. Please log in again.", Toast.LENGTH_LONG).show();
                    } else {
                        // Other HTTP errors
                        Toast.makeText(RequestBloodActivity.this, "Server error. Please try again later.", Toast.LENGTH_LONG).show();
                    }
                }

                @Override
                public void onFailure(
                        @androidx.annotation.NonNull retrofit2.Call<com.bloodconnect.app.network.models.BloodRequestResponse> call,
                        @androidx.annotation.NonNull Throwable t) {

                    btnSubmitRequest.setEnabled(true);
                    btnSubmitRequest.setText("Submit Blood Request");
                    Toast.makeText(RequestBloodActivity.this, "Unable to connect to server. Please check your connection.", Toast.LENGTH_LONG).show();
                }
            });
    }

    private boolean validateInput() {
        boolean isValid = true;

        String bloodGroup = inputBloodGroup.getText().toString().trim();
        String unitsStr = inputUnits.getText().toString().trim();
        String hospital = inputHospital.getText().toString().trim();
        String location = inputLocation.getText().toString().trim();
        String date = inputDate.getText().toString().trim();
        String urgency = inputUrgency.getText().toString().trim();

        // Validate Blood Group
        if (TextUtils.isEmpty(bloodGroup)) {
            layoutBloodGroup.setError("Please select a blood group");
            isValid = false;
        } else {
            layoutBloodGroup.setError(null);
        }

        // Validate Units
        if (TextUtils.isEmpty(unitsStr)) {
            layoutUnits.setError("Please enter units required");
            isValid = false;
        } else {
            try {
                int units = Integer.parseInt(unitsStr);
                if (units < 1) {
                    layoutUnits.setError("Minimum 1 unit required");
                    isValid = false;
                } else {
                    layoutUnits.setError(null);
                }
            } catch (NumberFormatException e) {
                layoutUnits.setError("Invalid number");
                isValid = false;
            }
        }

        // Validate Hospital
        if (TextUtils.isEmpty(hospital)) {
            layoutHospital.setError("Hospital name is required");
            isValid = false;
        } else {
            layoutHospital.setError(null);
        }

        // Validate Location
        if (TextUtils.isEmpty(location)) {
            layoutLocation.setError("Location is required");
            isValid = false;
        } else {
            layoutLocation.setError(null);
        }

        // Validate Date
        if (TextUtils.isEmpty(date)) {
            layoutDate.setError("Required date is required");
            isValid = false;
        } else {
            layoutDate.setError(null);
        }

        // Validate Urgency
        if (TextUtils.isEmpty(urgency)) {
            layoutUrgency.setError("Urgency is required");
            isValid = false;
        } else {
            layoutUrgency.setError(null);
        }

        return isValid;
    }

    @SuppressWarnings({"MissingPermission"})
    private void enableLocationComponent() {
        if (mapLibreMap != null && mapLibreMap.getStyle() != null) {
            LocationComponent locationComponent = mapLibreMap.getLocationComponent();
            locationComponent.activateLocationComponent(
                    LocationComponentActivationOptions.builder(this, mapLibreMap.getStyle()).build());
            locationComponent.setLocationComponentEnabled(true);
            locationComponent.setCameraMode(CameraMode.TRACKING);
            locationComponent.setRenderMode(RenderMode.COMPASS);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @androidx.annotation.NonNull String[] permissions, @androidx.annotation.NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 100 && grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            enableLocationComponent();
        } else {
            Toast.makeText(this, "Location permission denied", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onStart() {
        super.onStart();
        mapView.onStart();
    }

    @Override
    protected void onResume() {
        super.onResume();
        mapView.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
        mapView.onPause();
    }

    @Override
    protected void onStop() {
        super.onStop();
        mapView.onStop();
    }

    @Override
    protected void onSaveInstanceState(@androidx.annotation.NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        mapView.onSaveInstanceState(outState);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        mapView.onDestroy();
    }

    @Override
    public void onLowMemory() {
        super.onLowMemory();
        mapView.onLowMemory();
    }
}
