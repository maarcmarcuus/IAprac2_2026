package cat.tecnocampus.apps_p1_LiraQuezadaCesar;

import android.content.Context;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

public class TripListFragment extends Fragment {

    public interface OnTripSelectedListener {
        void onTripSelected(Trip trip);
    }

    private OnTripSelectedListener listener;
    private RecyclerView recyclerView;
    private TextView tvEmptyList;
    private TripAdapter adapter;

    @Override
    public void onAttach(@NonNull Context context) {
        super.onAttach(context);
        if (context instanceof OnTripSelectedListener) {
            listener = (OnTripSelectedListener) context;
        } else {
            throw new RuntimeException(context + " must implement OnTripSelectedListener");
        }
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_trip_list, container, false);

        recyclerView = view.findViewById(R.id.rvTrips);
        tvEmptyList = view.findViewById(R.id.tvEmptyList);

        adapter = new TripAdapter(MainActivity.trips, trip -> {
            if (listener != null) {
                listener.onTripSelected(trip);
            }
        });

        recyclerView.setLayoutManager(new GridLayoutManager(requireContext(), 2));
        recyclerView.setAdapter(adapter);

        updateList();

        return view;
    }

    public void updateList() {
        if (adapter == null) return;
        adapter.notifyDataSetChanged();
        if (MainActivity.trips.isEmpty()) {
            tvEmptyList.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
        } else {
            tvEmptyList.setVisibility(View.GONE);
            recyclerView.setVisibility(View.VISIBLE);
        }
    }

    @Override
    public void onDetach() {
        super.onDetach();
        listener = null;
    }
}
