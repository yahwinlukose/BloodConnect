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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_request_blood);

        setupToolbar();
        initializeViews();
        setupDropdowns();
        setupDatePicker();
        setupSubmitButton();
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
                // Mock behavior: after successful validation, show toast and finish
                Toast.makeText(this, "Blood request created successfully", Toast.LENGTH_SHORT).show();
                finish();
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
}
