package com.bloodconnect.app.requests;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.bloodconnect.app.R;
import com.bloodconnect.app.network.models.BloodRequest;

import java.util.List;

public class BloodRequestAdapter extends RecyclerView.Adapter<BloodRequestAdapter.ViewHolder> {

    private final List<BloodRequest> bloodRequests;

    public BloodRequestAdapter(List<BloodRequest> bloodRequests) {
        this.bloodRequests = bloodRequests;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_blood_request, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        BloodRequest request = bloodRequests.get(position);
        holder.tvBloodGroup.setText(request.getBloodGroup() != null ? request.getBloodGroup() : "Unknown");
        holder.tvUnits.setText(request.getUnitsRequired() + " units");
        holder.tvHospital.setText(request.getHospitalName() != null ? request.getHospitalName() : "N/A");
        holder.tvLocation.setText(request.getLocation() != null ? request.getLocation() : "N/A");
        holder.tvDate.setText(request.getRequiredDate() != null ? request.getRequiredDate() : "N/A");
        holder.tvUrgency.setText("Urgency: " + (request.getUrgency() != null ? request.getUrgency() : "N/A"));
        holder.tvStatus.setText("Status: " + (request.getStatus() != null ? request.getStatus() : "N/A"));

        holder.itemView.setOnClickListener(v -> {
            android.content.Intent intent = new android.content.Intent(v.getContext(), RequestDetailsActivity.class);
            intent.putExtra("request_json", new com.google.gson.Gson().toJson(request));
            v.getContext().startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return bloodRequests.size();
    }

    static class ViewHolder extends RecyclerView.ViewHolder {
        TextView tvBloodGroup, tvUnits, tvHospital, tvLocation, tvDate, tvUrgency, tvStatus;

        public ViewHolder(@NonNull View itemView) {
            super(itemView);
            tvBloodGroup = itemView.findViewById(R.id.tvBloodGroup);
            tvUnits = itemView.findViewById(R.id.tvUnits);
            tvHospital = itemView.findViewById(R.id.tvHospital);
            tvLocation = itemView.findViewById(R.id.tvLocation);
            tvDate = itemView.findViewById(R.id.tvDate);
            tvUrgency = itemView.findViewById(R.id.tvUrgency);
            tvStatus = itemView.findViewById(R.id.tvStatus);
        }
    }
}
