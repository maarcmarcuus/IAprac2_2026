package cat.tecnocampus.apps_p1_LiraQuezadaCesar;

import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.util.Patterns;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import androidx.appcompat.app.AppCompatActivity;

public class CreateTripActivity extends AppCompatActivity {

    private EditText etDestination;
    private EditText etCountry;
    private EditText etDays;
    private EditText etEmail;
    private EditText etBudget;
    private CheckBox cbFavorite;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_create_trip);

        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle(getString(R.string.title_create));
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        etDestination = findViewById(R.id.etDestination);
        etCountry = findViewById(R.id.etCountry);
        etDays = findViewById(R.id.etDays);
        etEmail = findViewById(R.id.etEmail);
        etBudget = findViewById(R.id.etBudget);
        cbFavorite = findViewById(R.id.cbFavorite);
        Button btnSave = findViewById(R.id.btnSave);
        Button btnClear = findViewById(R.id.btnClear);

        btnSave.setOnClickListener(v -> {
            if (validateForm()) {
                showConfirmationDialog();
            }
        });

        btnClear.setOnClickListener(v -> clearForm());
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
    }

    private boolean validateForm() {
        boolean valid = true;

        String destination = etDestination.getText().toString().trim();
        String country = etCountry.getText().toString().trim();
        String days = etDays.getText().toString().trim();
        String email = etEmail.getText().toString().trim();
        String budget = etBudget.getText().toString().trim();

        if (destination.isEmpty()) {
            etDestination.setError(getString(R.string.error_required));
            valid = false;
        }

        if (country.isEmpty()) {
            etCountry.setError(getString(R.string.error_required));
            valid = false;
        }

        if (days.isEmpty()) {
            etDays.setError(getString(R.string.error_required));
            valid = false;
        } else {
            try {
                if (Integer.parseInt(days) <= 0) {
                    etDays.setError(getString(R.string.error_number));
                    valid = false;
                }
            } catch (NumberFormatException e) {
                etDays.setError(getString(R.string.error_number));
                valid = false;
            }
        }

        if (email.isEmpty()) {
            etEmail.setError(getString(R.string.error_required));
            valid = false;
        } else if (!Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            etEmail.setError(getString(R.string.error_email));
            valid = false;
        }

        if (budget.isEmpty()) {
            etBudget.setError(getString(R.string.error_required));
            valid = false;
        } else {
            try {
                if (Double.parseDouble(budget) <= 0) {
                    etBudget.setError(getString(R.string.error_number));
                    valid = false;
                }
            } catch (NumberFormatException e) {
                etBudget.setError(getString(R.string.error_number));
                valid = false;
            }
        }

        return valid;
    }

    private void showConfirmationDialog() {
        new AlertDialog.Builder(this)
                .setTitle(getString(R.string.confirm_title))
                .setMessage(getString(R.string.confirm_message))
                .setPositiveButton(getString(R.string.yes), (dialog, which) -> returnTripToList())
                .setNegativeButton(getString(R.string.no), null)
                .show();
    }

    private void returnTripToList() {
        Intent resultIntent = new Intent();
        resultIntent.putExtra("destination", etDestination.getText().toString().trim());
        resultIntent.putExtra("country", etCountry.getText().toString().trim());
        resultIntent.putExtra("days", Integer.parseInt(etDays.getText().toString().trim()));
        resultIntent.putExtra("email", etEmail.getText().toString().trim());
        resultIntent.putExtra("budget", Double.parseDouble(etBudget.getText().toString().trim()));
        resultIntent.putExtra("favorite", cbFavorite.isChecked());
        setResult(RESULT_OK, resultIntent);
        finish();
    }

    private void clearForm() {
        etDestination.getText().clear();
        etCountry.getText().clear();
        etDays.getText().clear();
        etEmail.getText().clear();
        etBudget.getText().clear();
        cbFavorite.setChecked(false);
        etDestination.setError(null);
        etCountry.setError(null);
        etDays.setError(null);
        etEmail.setError(null);
        etBudget.setError(null);
    }
}
