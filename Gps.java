// GPSListener for python for android api

import android.location.LocationManager;
import android.location.LocationListener;
import android.location.Location;
import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.location.Geocoder;
import android.location.Address;
import java.util.Locale;
import java.lang.StringBuffer;
import java.util.List;
import java.io.IOException;
import android.util.Log;

public class Gps{
	
	public static double dblLatitude;
	public static double dblLongitude;
	private LocationManager locManager;
	private LocationListener locListener;
	private static final String TAG = "python";
	
	private Geocoder gc;
	
	public Gps(Context pyContext){
		String x = "";
		Gps.dblLatitude = 0.0;
		Gps.dblLongitude = 0.0;
		locManager = (LocationManager)pyContext.getSystemService(Context.LOCATION_SERVICE);
		locListener = new GPSListener();
		locManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5000, 10, locListener);
		
		if(Geocoder.isPresent()){
			gc = new Geocoder(pyContext, Locale.getDefault());
		}
	}
	
	public String getGeoLocation(double lat, double lng){
		String s = "";
		if(isGeocoderPresent()){
			try{
				StringBuffer sb = new StringBuffer();
			// RETRIEVE GEOLOCATION ADDRESS
				List<Address>list = this.gc.getFromLocation(lat, lng, 1);
			// GET THE FIRST INDEX WE ONLY NEED THE FIRST ONE AS SPECIFIED
				Address addr = list.get(0);
			// CITY
				sb.append(addr.getLocality() + "\n");
			// COUNTY
				sb.append(addr.getSubAdminArea() + "\n");
			// COUNTRY
				sb.append(addr.getAdminArea() + "\n");
			// POSTCODE
				sb.append(addr.getPostalCode() + "\n");
			// SECOND ADDRESS
				sb.append(addr.getThoroughfare() + "\n");
			// USUALLY HOUSE NUMBER
				sb.append(addr.getSubThoroughfare());
				s = sb.toString();
			}
			catch(IOException err){
				s = "Error";
			}
		}
		return s;
	}
	
	private void print(String  string){
		Log.i(Gps.TAG, string);
	}
	
	public boolean isGeocoderPresent(){
		return Geocoder.isPresent();
	}
	
	public boolean isLocationEnabled(){
		return locManager.isProviderEnabled(LocationManager.GPS_PROVIDER);
	}
	
	public double getLatitude(){
		return Gps.dblLatitude;
	}
	
	public double getLongitude(){
		return Gps.dblLongitude;
	}
	
	public void stopListening(){
		// Closes the listener thread
		this.locManager.removeUpdates(this.locListener);
	}
	
	private class GPSListener implements LocationListener{
		// GPS Listener background running thread which updates on GPS coordinates
		@Override
		public void onLocationChanged(Location location){
			Gps.dblLatitude = location.getLatitude();
			Gps.dblLongitude = location.getLongitude();
		}
		
		@Override
		public void onProviderDisabled(String provider){
			
		}
		@Override
		public void onProviderEnabled(String provider){
			
		}
		
		@Override
		public void onStatusChanged(String provider, int status, Bundle extras){
			
		}
		
	}
	
}
