package com.bloodconnect.app.auth;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.bloodconnect.app.R;
import com.bloodconnect.app.network.RetrofitClient;
import com.bloodconnect.app.network.models.RegisterRequest;
import com.bloodconnect.app.network.models.RegisterResponse;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import com.google.android.material.textfield.TextInputLayout;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Handles new user registration.
 *
 * Flow:
 *  1. Validate all fields locally (required checks + password strength).
 *  2. POST to /api/auth/register/ via Retrofit.
 *  3. On HTTP 201 → show success Toast, navigate to LoginActivity with email pre-filled.
 *  4. On HTTP 400 → parse Django field-level errors and surface them inline.
 *  5. On network failure → show a generic connectivity message.
 *
 * Passwords are never stored, logged, or sent anywhere except the registration endpoint.
 */
public class RegisterActivity extends AppCompatActivity {

    /** Common/weak passwords explicitly rejected on the client side before hitting the network. */
    private static final Set<String> COMMON_PASSWORDS = new HashSet<>(Arrays.asList(
            "password", "password1", "12345678", "123456789", "1234567890",
            "qwerty123", "qwerty1", "qwertyui", "test1234", "test123",
            "abc12345", "iloveyou", "welcome1", "letmein1", "monkey123",
            "dragon12", "master12", "sunshine", "shadow12", "superman"
    ));

    private TextInputLayout tilFirstName;
    private TextInputLayout tilLastName;
    private TextInputLayout tilRegEmail;
    private TextInputLayout tilRegPhone;
    private TextInputLayout tilRegPassword;

    private TextInputEditText etRegFirstName;
    private TextInputEditText etRegLastName;
    private TextInputEditText etRegEmail;
    private TextInputEditText etRegPhone;
    private TextInputEditText etRegPassword;

    private MaterialButton btnRegister;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        // Bind layouts (for inline error display)
        tilFirstName    = findViewById(R.id.tilFirstName);
        tilLastName     = findViewById(R.id.tilLastName);
        tilRegEmail     = findViewById(R.id.tilRegEmail);
        tilRegPhone     = findViewById(R.id.tilRegPhone);
        tilRegPassword  = findViewById(R.id.tilRegPassword);

        // Bind edit texts
        etRegFirstName  = findViewById(R.id.etRegFirstName);
        etRegLastName   = findViewById(R.id.etRegLastName);
        etRegEmail      = findViewById(R.id.etRegEmail);
        etRegPhone      = findViewById(R.id.etRegPhone);
        etRegPassword   = findViewById(R.id.etRegPassword);

        btnRegister = findViewById(R.id.btnRegister);
        TextView tvLogin = findViewById(R.id.tvLogin);

        btnRegister.setOnClickListener(v -> attemptRegister());

        // Navigate back to Login
        tvLogin.setOnClickListener(v -> finish());
    }

    // -------------------------------------------------------------------------
    // Registration logic
    // -------------------------------------------------------------------------

    private void attemptRegister() {
        // Clear any previous inline errors
        clearErrors();

        String firstName = etRegFirstName.getText().toString().trim();
        String lastName  = etRegLastName.getText().toString().trim();
        String email     = etRegEmail.getText().toString().trim();
        String phone     = etRegPhone.getText().toString().trim();
        // Retrieve password from the view but do NOT store it in a field variable beyond this scope
        String password  = etRegPassword.getText().toString();

        boolean valid = true;

        if (TextUtils.isEmpty(firstName)) {
            tilFirstName.setError(getString(R.string.err_field_required));
            valid = false;
        }

        if (TextUtils.isEmpty(lastName)) {
            tilLastName.setError(getString(R.string.err_field_required));
            valid = false;
        }

        if (TextUtils.isEmpty(email)) {
            tilRegEmail.setError(getString(R.string.err_field_required));
            valid = false;
        }

        if (TextUtils.isEmpty(phone)) {
            tilRegPhone.setError(getString(R.string.err_field_required));
            valid = false;
        }

        // Client-side password validation (Django is the authoritative validator)
        String passwordError = validatePasswordLocally(password);
        if (passwordError != null) {
            tilRegPassword.setError(passwordError);
            valid = false;
        }

        if (!valid) {
            return; // Do NOT send the request when local validation fails
        }

        // Disable button to prevent duplicate submissions
        btnRegister.setEnabled(false);
        btnRegister.setText(getString(R.string.registering));

        RegisterRequest request = new RegisterRequest(email, password, firstName, lastName, phone);

        RetrofitClient.getApiService(RegisterActivity.this)
                .register(request)
                .enqueue(new Callback<RegisterResponse>() {

                    @Override
                    public void onResponse(@NonNull Call<RegisterResponse> call,
                                           @NonNull Response<RegisterResponse> response) {
                        btnRegister.setEnabled(true);
                        btnRegister.setText(getString(R.string.register));

                        if (response.code() == 201 && response.body() != null) {
                            // HTTP 201 Created – registration successful
                            handleRegistrationSuccess(response.body().getEmail());
                        } else if (response.code() == 400) {
                            // HTTP 400 – field-level validation errors from Django
                            handleBackendValidationErrors(response);
                        } else {
                            Toast.makeText(RegisterActivity.this,
                                    "Server error. Please try again later.",
                                    Toast.LENGTH_LONG).show();
                        }
                    }

                    @Override
                    public void onFailure(@NonNull Call<RegisterResponse> call, @NonNull Throwable t) {
                        btnRegister.setEnabled(true);
                        btnRegister.setText(getString(R.string.register));
                        Toast.makeText(RegisterActivity.this,
                                "Unable to connect to server. Please check your connection.",
                                Toast.LENGTH_LONG).show();
                    }
                });
    }

    // -------------------------------------------------------------------------
    // Success handler
    // -------------------------------------------------------------------------

    /**
     * Called on HTTP 201. Shows a success Toast and navigates to LoginActivity,
     * pre-filling the email field so the user can log in immediately.
     * Does NOT auto-authenticate the user.
     */
    private void handleRegistrationSuccess(String registeredEmail) {
        Toast.makeText(this, getString(R.string.registration_success), Toast.LENGTH_LONG).show();

        Intent intent = new Intent(RegisterActivity.this, LoginActivity.class);
        // Pass the email so LoginActivity can pre-fill it
        intent.putExtra(LoginActivity.EXTRA_EMAIL, registeredEmail);
        // Clear the back-stack so the user cannot press Back to return to the registration form
        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        startActivity(intent);
        finish();
    }

    // -------------------------------------------------------------------------
    // Backend error parsing
    // -------------------------------------------------------------------------

    /**
     * Parses Django DRF 400 validation errors and surfaces them as inline field errors.
     *
     * Django returns errors in the form:
     *   { "password": ["This password is too short.", "…"], "email": ["…"], … }
     *
     * Each value is a JSON array of error strings. This method maps each field to its
     * corresponding TextInputLayout and shows the first error message.
     * Any unrecognised field errors are collected and shown in a Toast.
     */
    private void handleBackendValidationErrors(@NonNull Response<RegisterResponse> response) {
        if (response.errorBody() == null) {
            Toast.makeText(this, "Registration failed. Please check your details.", Toast.LENGTH_LONG).show();
            return;
        }

        try {
            String rawError = response.errorBody().string();
            JSONObject errorJson = new JSONObject(rawError);

            StringBuilder genericErrors = new StringBuilder();

            java.util.Iterator<String> keys = errorJson.keys();
            while (keys.hasNext()) {
                String field = keys.next();
                // Each field value may be a JSONArray of strings or a plain string
                String firstMessage = extractFirstMessage(errorJson, field);
                if (firstMessage == null) continue;

                switch (field) {
                    case "email":
                        tilRegEmail.setError(firstMessage);
                        break;
                    case "password":
                        tilRegPassword.setError(firstMessage);
                        break;
                    case "first_name":
                        tilFirstName.setError(firstMessage);
                        break;
                    case "last_name":
                        tilLastName.setError(firstMessage);
                        break;
                    case "phone":
                        tilRegPhone.setError(firstMessage);
                        break;
                    default:
                        // "non_field_errors", "detail", or any other top-level key
                        if (genericErrors.length() > 0) genericErrors.append("\n");
                        genericErrors.append(firstMessage);
                        break;
                }
            }

            if (genericErrors.length() > 0) {
                Toast.makeText(this, genericErrors.toString(), Toast.LENGTH_LONG).show();
            }

        } catch (IOException | org.json.JSONException e) {
            Toast.makeText(this, "Registration failed. Please check your details.", Toast.LENGTH_LONG).show();
        }
    }

    /** Extracts the first error message string from a JSONObject field (array or string). */
    private String extractFirstMessage(JSONObject errorJson, String field) {
        try {
            Object value = errorJson.get(field);
            if (value instanceof JSONArray) {
                JSONArray arr = (JSONArray) value;
                if (arr.length() > 0) return arr.getString(0);
            } else if (value instanceof String) {
                return (String) value;
            }
        } catch (org.json.JSONException ignored) {
            // Fall through
        }
        return null;
    }

    // -------------------------------------------------------------------------
    // Local password validation (client-side pre-check only)
    // Django's validate_password() remains the authoritative final check.
    // -------------------------------------------------------------------------

    /**
     * Returns a human-readable error string if the password fails client-side checks,
     * or null if it passes all checks.
     *
     * Checks performed (in order):
     *  1. Not empty / required
     *  2. Minimum 8 characters
     *  3. Not entirely numeric
     *  4. Not in the common-passwords denylist
     */
    private String validatePasswordLocally(String password) {
        if (TextUtils.isEmpty(password)) {
            return getString(R.string.err_field_required);
        }
        if (password.length() < 8) {
            return getString(R.string.err_password_too_short);
        }
        if (password.matches("\\d+")) {
            return getString(R.string.err_password_all_digits);
        }
        if (COMMON_PASSWORDS.contains(password.toLowerCase(java.util.Locale.ROOT))) {
            return getString(R.string.err_password_too_common);
        }
        return null; // Passes all local checks
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    /** Clears all inline field errors before a new validation pass. */
    private void clearErrors() {
        tilFirstName.setError(null);
        tilLastName.setError(null);
        tilRegEmail.setError(null);
        tilRegPhone.setError(null);
        tilRegPassword.setError(null);
    }
}
