package com.bloodconnect.app.requests;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bloodconnect.app.R;
import com.bloodconnect.app.network.models.DonorMatch;

import java.util.List;

public class DonorMatchAdapter extends RecyclerView.Adapter<DonorMatchAdapter.ViewHolder> {

    private final List<DonorMatch> donorMatches;

    public DonorMatchAdapter(List<DonorMatch> donorMatches) {
        this.donorMatches = donorMatches;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_donor_match, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        DonorMatch match = donorMatches.get(position);
        
        if (match.getDonor() != null && match.getDonor().getUser() != null) {
            String firstName = match.getDonor().getUser().getFirstName();
            String lastName = match.getDonor().getUser().getLastName();
            String name = (firstName != null ? firstName : "") + " " + (lastName != null ? lastName : "");
            holder.tvDonorName.setText(name.trim().isEmpty() ? "Unknown Donor" : name.trim());
        } else {
            holder.tvDonorName.setText("Unknown Donor");
        }

        if (match.getDonor() != null) {
            holder.tvBloodGroup.setText(match.getDonor().getBloodGroup() != null ? match.getDonor().getBloodGroup() : "N/A");
            holder.tvAvailability.setText(match.getDonor().isAvailable() ? "Available" : "Unavailable");
            holder.tvAvailability.setTextColor(match.getDonor().isAvailable() ? 0xFF388E3C : 0xFFD32F2F); // Green vs Red
            holder.tvLocation.setText(match.getDonor().getLocation() != null ? match.getDonor().getLocation() : "Location unknown");
        } else {
            holder.tvBloodGroup.setText("N/A");
            holder.tvAvailability.setText("Unknown");
            holder.tvLocation.setText("Location unknown");
        }

        if (match.getDistanceKm() != null) {
            holder.tvDistance.setText(String.format("%.2f km away", match.getDistanceKm()));
        } else {
            holder.tvDistance.setText("Distance unavailable");
        }

        holder.tvMatchScore.setText("Match Score: " + match.getMatchScore());
        holder.tvMatchStatus.setText(match.getStatus() != null ? match.getStatus() : "UNKNOWN");
    }

    @Override
    public int getItemCount() {
        return donorMatches.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvDonorName, tvBloodGroup, tvAvailability, tvLocation, tvDistance, tvMatchScore, tvMatchStatus;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            tvDonorName = itemView.findViewById(R.id.tvDonorName);
            tvBloodGroup = itemView.findViewById(R.id.tvBloodGroup);
            tvAvailability = itemView.findViewById(R.id.tvAvailability);
            tvLocation = itemView.findViewById(R.id.tvLocation);
            tvDistance = itemView.findViewById(R.id.tvDistance);
            tvMatchScore = itemView.findViewById(R.id.tvMatchScore);
            tvMatchStatus = itemView.findViewById(R.id.tvMatchStatus);
        }
    }
}
