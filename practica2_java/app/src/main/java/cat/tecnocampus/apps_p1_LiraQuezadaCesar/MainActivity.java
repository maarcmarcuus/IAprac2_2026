package cat.tecnocampus.apps_p1_LiraQuezadaCesar;

import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentTransaction;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity implements TripListFragment.OnTripSelectedListener {

    public static final List<Trip> trips = new ArrayList<>();

    private final TripListFragment tripListFragment = new TripListFragment();

    private final ActivityResultLauncher<Intent> createTripLauncher = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            result -> {
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    Intent data = result.getData();
                    String destination = data.getStringExtra("destination");
                    String country = data.getStringExtra("country");
                    int days = data.getIntExtra("days", 0);
                    String email = data.getStringExtra("email");
                    double budget = data.getDoubleExtra("budget", 0.0);
                    boolean favorite = data.getBooleanExtra("favorite", false);

                    if (destination != null && country != null && email != null) {
                        trips.add(new Trip(destination, country, days, email, budget, favorite));
                        showList();
                    }
                }
            }
    );

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle(getString(R.string.title_list));
        }

        getSupportFragmentManager().addOnBackStackChangedListener(() -> {
            if (!isLandscapeLayout() && getSupportFragmentManager().getBackStackEntryCount() == 0) {
                if (getSupportActionBar() != null) {
                    getSupportActionBar().setTitle(getString(R.string.title_list));
                }
                tripListFragment.updateList();
            }
        });

        if (savedInstanceState == null) {
            showList();
        } else if (isLandscapeLayout()) {
            showListInContainer(R.id.listContainer);
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.action_add) {
            createTripLauncher.launch(new Intent(this, CreateTripActivity.class));
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onTripSelected(Trip trip) {
        showDetail(trip);
    }

    public void showList() {
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle(getString(R.string.title_list));
        }

        if (isLandscapeLayout()) {
            showListInContainer(R.id.listContainer);
            return;
        }

        getSupportFragmentManager().popBackStackImmediate(null, FragmentManager.POP_BACK_STACK_INCLUSIVE);
        showListInContainer(R.id.fragmentContainer);
    }

    private void showListInContainer(int containerId) {
        Fragment currentFragment = getSupportFragmentManager().findFragmentById(containerId);
        if (currentFragment == tripListFragment && tripListFragment.isAdded()) {
            tripListFragment.updateList();
        } else {
            getSupportFragmentManager()
                    .beginTransaction()
                    .replace(containerId, tripListFragment)
                    .commit();
        }
    }

    private void showDetail(Trip trip) {
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle(getString(R.string.title_detail));
        }

        int detailContainerId = isLandscapeLayout() ? R.id.detailContainer : R.id.fragmentContainer;

        FragmentTransaction transaction = getSupportFragmentManager()
                .beginTransaction()
                .replace(detailContainerId, TripDetailFragment.newInstance(trip));

        if (!isLandscapeLayout()) {
            transaction.addToBackStack(null);
        }

        transaction.commit();
    }

    private boolean isLandscapeLayout() {
        return findViewById(R.id.detailContainer) != null;
    }
}
