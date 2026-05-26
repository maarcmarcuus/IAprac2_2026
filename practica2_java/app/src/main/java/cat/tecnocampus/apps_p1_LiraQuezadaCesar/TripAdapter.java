package cat.tecnocampus.apps_p1_LiraQuezadaCesar;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class TripAdapter extends RecyclerView.Adapter<TripAdapter.TripViewHolder> {

    public interface OnItemClickListener {
        void onItemClick(Trip trip);
    }

    private final List<Trip> trips;
    private final OnItemClickListener listener;

    public TripAdapter(List<Trip> trips, OnItemClickListener listener) {
        this.trips = trips;
        this.listener = listener;
    }

    public static class TripViewHolder extends RecyclerView.ViewHolder {
        private final TextView tvItemDestination;
        private final TextView tvItemCountry;
        private final TextView tvItemDays;
        private final TextView tvItemBudget;
        private final TextView tvItemFavorite;

        public TripViewHolder(@NonNull View itemView) {
            super(itemView);
            tvItemDestination = itemView.findViewById(R.id.tvItemDestination);
            tvItemCountry = itemView.findViewById(R.id.tvItemCountry);
            tvItemDays = itemView.findViewById(R.id.tvItemDays);
            tvItemBudget = itemView.findViewById(R.id.tvItemBudget);
            tvItemFavorite = itemView.findViewById(R.id.tvItemFavorite);
        }

        public void bind(Trip trip, OnItemClickListener listener) {
            Context context = itemView.getContext();
            tvItemDestination.setText(trip.getDestination());
            tvItemCountry.setText(trip.getCountry());
            tvItemDays.setText(context.getString(R.string.item_days_format, trip.getDays()));
            tvItemBudget.setText(context.getString(R.string.item_budget_format, trip.getBudget()));
            tvItemFavorite.setText(trip.isFavorite()
                    ? context.getString(R.string.favorite_yes)
                    : context.getString(R.string.favorite_no));
            itemView.setOnClickListener(v -> listener.onItemClick(trip));
        }
    }

    @NonNull
    @Override
    public TripViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_trip, parent, false);
        return new TripViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull TripViewHolder holder, int position) {
        holder.bind(trips.get(position), listener);
    }

    @Override
    public int getItemCount() {
        return trips.size();
    }
}
