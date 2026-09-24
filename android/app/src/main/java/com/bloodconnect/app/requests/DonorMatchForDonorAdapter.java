package com.bloodconnect.app.requests;

import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bloodconnect.app.R;
import com.bloodconnect.app.network.models.BloodRequestForDonor;
import com.bloodconnect.app.network.models.DonorMatchForDonor;
import com.google.gson.Gson;

import java.util.List;

public class DonorMatchForDonorAdapter extends RecyclerView.Adapter<DonorMatchForDonorAdapter.ViewHolder> {

    private final List<DonorMatchForDonor> matches;

    public DonorMatchForDonorAdapter(List<DonorMatchForDonor> matches) {
        this.matches = matches;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_blood_request_for_donor, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        DonorMatchForDonor match = matches.get(position);
        BloodRequestForDonor request = match.getBloodRequest();

        if (request != null) {
            holder.tvBloodGroup.setText(request.getBloodGroup());
            holder.tvUrgency.setText(request.getUrgency());
            holder.tvUnits.setText(request.getUnitsRequired() + " units");
            holder.tvHospital.setText(request.getHospitalName());
            holder.tvLocation.setText(request.getLocation());
            holder.tvDate.setText("Required by " + request.getRequiredDate());
        }

        if (match.getDistanceKm() != null) {
            holder.tvDistance.setText(String.format("%.1f km away", match.getDistanceKm()));
        } else {
            holder.tvDistance.setText("Distance unavailable");
        }

        holder.tvStatus.setText(match.getStatus());

        holder.itemView.setOnClickListener(v -> {
            Intent intent = new Intent(v.getContext(), DonorRequestDetailsActivity.class);
            intent.putExtra("match_json", new Gson().toJson(match));
            v.getContext().startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return matches.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvBloodGroup, tvUrgency, tvUnits, tvHospital, tvLocation, tvDate, tvDistance, tvStatus;

        ViewHolder(View itemView) {
            super(itemView);
            tvBloodGroup = itemView.findViewById(R.id.tvBloodGroup);
            tvUrgency = itemView.findViewById(R.id.tvUrgency);
            tvUnits = itemView.findViewById(R.id.tvUnits);
            tvHospital = itemView.findViewById(R.id.tvHospital);
            tvLocation = itemView.findViewById(R.id.tvLocation);
            tvDate = itemView.findViewById(R.id.tvDate);
            tvDistance = itemView.findViewById(R.id.tvDistance);
            tvStatus = itemView.findViewById(R.id.tvStatus);
        }
    }
}
