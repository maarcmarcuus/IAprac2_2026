package cat.tecnocampus.apps_p1_LiraQuezadaCesar;

import android.content.res.Configuration;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

public class TripDetailFragment extends Fragment {

    private static final String ARG_DESTINATION = "destination";
    private static final String ARG_COUNTRY = "country";
    private static final String ARG_DAYS = "days";
    private static final String ARG_EMAIL = "email";
    private static final String ARG_BUDGET = "budget";
    private static final String ARG_FAVORITE = "favorite";

    public static TripDetailFragment newInstance(Trip trip) {
        TripDetailFragment fragment = new TripDetailFragment();
        Bundle args = new Bundle();
        args.putString(ARG_DESTINATION, trip.getDestination());
        args.putString(ARG_COUNTRY, trip.getCountry());
        args.putInt(ARG_DAYS, trip.getDays());
        args.putString(ARG_EMAIL, trip.getEmail());
        args.putDouble(ARG_BUDGET, trip.getBudget());
        args.putBoolean(ARG_FAVORITE, trip.isFavorite());
        fragment.setArguments(args);
        return fragment;
    }

    private String destination = "";
    private String country = "";
    private int days = 0;
    private String email = "";
    private double budget = 0.0;
    private boolean favorite = false;

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Bundle args = getArguments();
        if (args != null) {
            destination = args.getString(ARG_DESTINATION, "");
            country = args.getString(ARG_COUNTRY, "");
            days = args.getInt(ARG_DAYS, 0);
            email = args.getString(ARG_EMAIL, "");
            budget = args.getDouble(ARG_BUDGET, 0.0);
            favorite = args.getBoolean(ARG_FAVORITE, false);
        }
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_trip_detail, container, false);

        TextView tvDestination = view.findViewById(R.id.tvDestination);
        TextView tvCountry = view.findViewById(R.id.tvCountry);
        TextView tvDays = view.findViewById(R.id.tvDays);
        TextView tvEmail = view.findViewById(R.id.tvEmail);
        TextView tvBudget = view.findViewById(R.id.tvBudget);
        TextView tvFavorite = view.findViewById(R.id.tvFavorite);
        Button btnBack = view.findViewById(R.id.btnBack);

        tvDestination.setText(getString(R.string.detail_destination_format, destination));
        tvCountry.setText(getString(R.string.detail_country_format, country));
        tvDays.setText(getString(R.string.detail_days_format, days));
        tvEmail.setText(getString(R.string.detail_email_format, email));
        tvBudget.setText(getString(R.string.detail_budget_format, budget));
        tvFavorite.setText(getString(R.string.detail_favorite_format,
                favorite ? getString(R.string.yes) : getString(R.string.no)));

        btnBack.setVisibility(
                getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE
                        ? View.GONE
                        : View.VISIBLE);

        btnBack.setOnClickListener(v -> ((MainActivity) requireActivity()).showList());

        return view;
    }
}
