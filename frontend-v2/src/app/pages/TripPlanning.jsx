import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import riderService from '../../services/rider.service';
import './TripPlanning.css';

// Fix Leaflet default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Reverse geocoding using Nominatim (OpenStreetMap)
const reverseGeocode = async (lat, lng) => {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
      {
        headers: {
          'Accept-Language': 'en',
        }
      }
    );
    const data = await response.json();
    
    if (data && data.address) {
      // Build a concise display name
      const parts = [];
      const addr = data.address;
      
      // Priority order for display
      if (addr.road) parts.push(addr.road);
      if (addr.neighbourhood) parts.push(addr.neighbourhood);
      else if (addr.suburb) parts.push(addr.suburb);
      if (addr.city || addr.town || addr.village) {
        parts.push(addr.city || addr.town || addr.village);
      }
      
      return parts.length > 0 ? parts.slice(0, 2).join(', ') : data.display_name?.split(',').slice(0, 2).join(',');
    }
    return null;
  } catch (error) {
    console.error('Reverse geocoding failed:', error);
    return null;
  }
};

// Map component with DRAGGABLE PIN for selected location type
const MapComponent = ({ 
  mapCenter, 
  selectingType,
  currentLocation,
  onLocationChange,
  onMapReady,
  otherLocation
}) => {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const activeMarkerRef = useRef(null);
  const otherMarkerRef = useRef(null);

  // Custom icons
  const pickupIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  const dropIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  // Initialize map
  useEffect(() => {
    const timer = setTimeout(() => {
      if (mapContainerRef.current && !mapInstanceRef.current) {
        try {
          // Center on current location if available, otherwise map center
          const center = currentLocation 
            ? [currentLocation.lat, currentLocation.lng] 
            : mapCenter;
          
          const map = L.map(mapContainerRef.current, {
            center: center,
            zoom: 15,
            zoomControl: true
          });
          
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
          }).addTo(map);

          mapInstanceRef.current = map;
          onMapReady(true);
          
          setTimeout(() => {
            map.invalidateSize();
          }, 100);
        } catch (error) {
          console.error('Failed to initialize map:', error);
        }
      }
    }, 100);

    return () => {
      clearTimeout(timer);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
        onMapReady(false);
      }
    };
  }, []);

  // Add/update the active draggable marker
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    // Remove existing active marker
    if (activeMarkerRef.current) {
      activeMarkerRef.current.remove();
      activeMarkerRef.current = null;
    }

    const icon = selectingType === 'pickup' ? pickupIcon : dropIcon;
    const location = currentLocation || { lat: mapCenter[0], lng: mapCenter[1] };
    
    const marker = L.marker([location.lat, location.lng], { 
      icon: icon,
      draggable: true 
    }).addTo(mapInstanceRef.current);
    
    marker.bindPopup(
      selectingType === 'pickup' 
        ? '<b>📍 Pickup Location</b><br/>Drag to adjust' 
        : '<b>🎯 Drop-off Location</b><br/>Drag to adjust'
    ).openPopup();
    
    marker.on('dragend', (e) => {
      const pos = e.target.getLatLng();
      onLocationChange(pos.lat, pos.lng);
    });
    
    activeMarkerRef.current = marker;
    
    // Pan map to marker
    mapInstanceRef.current.panTo([location.lat, location.lng]);
    
  }, [selectingType, currentLocation?.lat, currentLocation?.lng]);

  // Show other location as static marker (if exists)
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    // Remove existing other marker
    if (otherMarkerRef.current) {
      otherMarkerRef.current.remove();
      otherMarkerRef.current = null;
    }

    if (otherLocation) {
      const icon = selectingType === 'pickup' ? dropIcon : pickupIcon;
      
      const marker = L.marker([otherLocation.lat, otherLocation.lng], { 
        icon: icon,
        opacity: 0.6
      }).addTo(mapInstanceRef.current);
      
      otherMarkerRef.current = marker;
    }
  }, [otherLocation?.lat, otherLocation?.lng, selectingType]);

  return (
    <div 
      ref={mapContainerRef} 
      style={{ height: '100%', width: '100%' }}
    />
  );
};

// Vehicle category icons
const vehicleIcons = {
  BIKE: '🏍️',
  AUTO: '🛺',
  SEDAN: '🚗'
};

function TripPlanning() {
  const navigate = useNavigate();
  const token = localStorage.getItem('jwt_token');
  
  // Booking flow state
  const [step, setStep] = useState('SELECT_LOCATIONS'); // SELECT_LOCATIONS, SELECT_VEHICLE, CONFIRM
  const [showMap, setShowMap] = useState(false); // Map hidden by default
  const [selectingType, setSelectingType] = useState(null); // 'pickup' or 'drop'
  
  // Map state
  const [mapReady, setMapReady] = useState(false);
  
  // Location state - null by default
  const [pickupLocation, setPickupLocation] = useState(null);
  const [dropLocation, setDropLocation] = useState(null);
  const [pickupAddress, setPickupAddress] = useState('');
  const [dropAddress, setDropAddress] = useState('');
  const [geocoding, setGeocoding] = useState(false);
  
  // Fare estimation state
  const [fareEstimates, setFareEstimates] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [estimatingFares, setEstimatingFares] = useState(false);
  
  // Booking state
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState(null);
  
  // Map center (default to Hyderabad)
  const [mapCenter] = useState([17.3850, 78.4867]);

  useEffect(() => {
    if (!token) {
      navigate('/login');
    }
  }, [token, navigate]);

  // Open map for selecting a location
  const openMapForSelection = async (type) => {
    setSelectingType(type);
    setShowMap(true);
    setMapReady(false);
    
    // If no location is set yet, set to map center and get address
    const currentLoc = type === 'pickup' ? pickupLocation : dropLocation;
    if (!currentLoc) {
      // Set initial location to map center
      const lat = mapCenter[0];
      const lng = mapCenter[1];
      setGeocoding(true);
      const address = await reverseGeocode(lat, lng);
      
      if (type === 'pickup') {
        setPickupLocation({ lat, lng });
        setPickupAddress(address || `${lat.toFixed(4)}, ${lng.toFixed(4)}`);
      } else {
        setDropLocation({ lat, lng });
        setDropAddress(address || `${lat.toFixed(4)}, ${lng.toFixed(4)}`);
      }
      setGeocoding(false);
    }
  };

  // Close map
  const closeMap = () => {
    setShowMap(false);
    setSelectingType(null);
  };

  // Confirm location from map
  const handleConfirmLocation = () => {
    setShowMap(false);
    setSelectingType(null);
  };

  // Callback for map ready
  const handleMapReady = useCallback((ready) => {
    setMapReady(ready);
  }, []);

  // Handle location change from dragging pin
  const handleLocationChange = useCallback(async (lat, lng) => {
    setGeocoding(true);
    const address = await reverseGeocode(lat, lng);
    
    if (selectingType === 'pickup') {
      setPickupLocation({ lat, lng });
      setPickupAddress(address || `${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    } else if (selectingType === 'drop') {
      setDropLocation({ lat, lng });
      setDropAddress(address || `${lat.toFixed(4)}, ${lng.toFixed(4)}`);
    }
    
    setGeocoding(false);
    // Clear estimates when locations change
    setFareEstimates([]);
    setSelectedVehicle(null);
    setStep('SELECT_LOCATIONS');
  }, [selectingType]);

  const handleFetchFares = async () => {
    if (!pickupLocation || !dropLocation) {
      setError('Please select both pickup and drop locations');
      return;
    }

    try {
      setEstimatingFares(true);
      setError(null);
      
      const estimates = await riderService.getAllFareEstimates(
        pickupLocation.lat,
        pickupLocation.lng,
        dropLocation.lat,
        dropLocation.lng
      );
      
      if (estimates.length === 0) {
        setError('No fare estimates available for this route. Location may not be supported.');
        return;
      }
      
      setFareEstimates(estimates);
      setStep('SELECT_VEHICLE');
    } catch (err) {
      setError(err.message || 'Failed to fetch fare estimates');
    } finally {
      setEstimatingFares(false);
    }
  };

  const handleSelectVehicle = (category) => {
    setSelectedVehicle(category);
    setStep('CONFIRM');
  };

  const handleBookRide = async () => {
    if (!selectedVehicle || !pickupLocation || !dropLocation) {
      setError('Please complete all booking steps');
      return;
    }

    try {
      setBooking(true);
      setError(null);
      
      const trip = await riderService.createTrip(
        pickupLocation.lat,
        pickupLocation.lng,
        dropLocation.lat,
        dropLocation.lng,
        selectedVehicle
      );
      
      navigate(`/app/rider/trip/${trip.trip_id}`);
    } catch (err) {
      setError(err.message || 'Failed to book ride');
      setBooking(false);
    }
  };

  const resetLocations = () => {
    setPickupLocation(null);
    setDropLocation(null);
    setPickupAddress('');
    setDropAddress('');
    setFareEstimates([]);
    setSelectedVehicle(null);
    setStep('SELECT_LOCATIONS');
    setShowMap(false);
    setSelectingType(null);
    setError(null);
  };

  const getSelectedFare = () => {
    return fareEstimates.find(e => e.category === selectedVehicle);
  };

  return (
    <div className="trip-planning" style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <button 
          onClick={() => navigate('/app/rider-dashboard')}
          style={{
            background: 'rgba(255,255,255,0.2)',
            border: 'none',
            borderRadius: '8px',
            padding: '8px 14px',
            color: 'white',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          ← Back
        </button>
        <h1 style={{ margin: 0, fontSize: '18px', fontWeight: '600' }}>Book a Ride</h1>
        <div style={{ width: '60px' }}></div>
      </header>

      {/* Main Content - Only shown when map is hidden */}
      {!showMap && (
        <div style={{ padding: '20px' }}>
          {/* Location Selection Card */}
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '20px',
            marginBottom: '16px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
          }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#374151' }}>📍 Trip Details</h3>
            
            {/* Pickup Location */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              padding: '14px',
              background: pickupLocation ? '#f0fdf4' : '#f9fafb',
              borderRadius: '12px',
              marginBottom: '12px',
              border: pickupLocation ? '2px solid #22c55e' : '2px solid #e5e7eb'
            }}>
              <span style={{ fontSize: '28px', marginRight: '14px' }}>📍</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '12px', color: '#16a34a', fontWeight: '700', marginBottom: '4px' }}>PICKUP</div>
                <div style={{ 
                  fontSize: '14px', 
                  color: pickupAddress ? '#374151' : '#9ca3af',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {pickupAddress || 'Tap to select location'}
                </div>
              </div>
              <button
                onClick={() => openMapForSelection('pickup')}
                style={{
                  background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '12px 18px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  boxShadow: '0 2px 8px rgba(34, 197, 94, 0.3)',
                  whiteSpace: 'nowrap'
                }}
              >
                {pickupLocation ? '✏️ Change' : '🗺️ Select'}
              </button>
            </div>
            
            {/* Divider */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              padding: '0 14px',
              marginBottom: '12px'
            }}>
              <div style={{ 
                width: '2px', 
                height: '20px', 
                background: '#d1d5db',
                marginLeft: '11px'
              }}></div>
            </div>
            
            {/* Drop Location */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              padding: '14px',
              background: dropLocation ? '#fef2f2' : '#f9fafb',
              borderRadius: '12px',
              border: dropLocation ? '2px solid #ef4444' : '2px solid #e5e7eb'
            }}>
              <span style={{ fontSize: '28px', marginRight: '14px' }}>🎯</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '12px', color: '#dc2626', fontWeight: '700', marginBottom: '4px' }}>DROP-OFF</div>
                <div style={{ 
                  fontSize: '14px', 
                  color: dropAddress ? '#374151' : '#9ca3af',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {dropAddress || 'Tap to select location'}
                </div>
              </div>
              <button
                onClick={() => openMapForSelection('drop')}
                style={{
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '12px 18px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  boxShadow: '0 2px 8px rgba(239, 68, 68, 0.3)',
                  whiteSpace: 'nowrap'
                }}
              >
                {dropLocation ? '✏️ Change' : '🗺️ Select'}
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              background: '#fef2f2',
              color: '#dc2626',
              padding: '14px 16px',
              borderRadius: '12px',
              marginBottom: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>⚠️ {error}</span>
              <button 
                onClick={() => setError(null)}
                style={{ background: 'none', border: 'none', color: '#dc2626', cursor: 'pointer', fontSize: '20px' }}
              >×</button>
            </div>
          )}

          {/* Get Fare Button - Step 1 */}
          {step === 'SELECT_LOCATIONS' && pickupLocation && dropLocation && (
            <button 
              onClick={handleFetchFares}
              disabled={estimatingFares}
              style={{
                width: '100%',
                padding: '16px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: estimatingFares ? 'default' : 'pointer',
                opacity: estimatingFares ? 0.7 : 1,
                marginBottom: '16px'
              }}
            >
              {estimatingFares ? '⏳ Getting Fare Estimates...' : '💰 Get Fare Estimates'}
            </button>
          )}

          {/* Vehicle Selection - Step 2 */}
          {step === 'SELECT_VEHICLE' && fareEstimates.length > 0 && (
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
            }}>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#374151' }}>🚗 Choose Your Ride</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {fareEstimates.map((estimate) => (
                  <div 
                    key={estimate.category}
                    onClick={() => handleSelectVehicle(estimate.category)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '14px',
                      background: selectedVehicle === estimate.category ? '#eef2ff' : '#f9fafb',
                      border: selectedVehicle === estimate.category ? '2px solid #667eea' : '2px solid transparent',
                      borderRadius: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <span style={{ fontSize: '32px', marginRight: '14px' }}>{vehicleIcons[estimate.category] || '🚗'}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: '600', color: '#374151', fontSize: '15px' }}>{estimate.category}</div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        {estimate.distance_km?.toFixed(1)} km • {estimate.eta_minutes || '~10'} min
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: '700', fontSize: '18px', color: '#374151' }}>
                        ₹{estimate.final_fare?.toFixed(0)}
                      </div>
                      {estimate.surge_multiplier > 1 && (
                        <div style={{ fontSize: '11px', color: '#f59e0b', fontWeight: '600' }}>
                          ⚡ {estimate.surge_multiplier}x
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <button 
                onClick={resetLocations}
                style={{
                  width: '100%',
                  marginTop: '16px',
                  padding: '12px',
                  background: 'none',
                  border: '1px solid #e5e7eb',
                  borderRadius: '10px',
                  color: '#6b7280',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                ← Change locations
              </button>
            </div>
          )}

          {/* Confirmation - Step 3 */}
          {step === 'CONFIRM' && selectedVehicle && (
            <div style={{
              background: 'white',
              borderRadius: '16px',
              padding: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
            }}>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#374151' }}>✅ Confirm Booking</h3>
              
              <div style={{
                background: '#f9fafb',
                borderRadius: '12px',
                padding: '16px',
                marginBottom: '16px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <span style={{ color: '#6b7280' }}>Vehicle</span>
                  <span style={{ fontWeight: '600' }}>{vehicleIcons[selectedVehicle]} {selectedVehicle}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <span style={{ color: '#6b7280' }}>Distance</span>
                  <span>{getSelectedFare()?.distance_km?.toFixed(1)} km</span>
                </div>
                <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '10px', marginTop: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: '600', fontSize: '16px' }}>Total Fare</span>
                    <span style={{ fontWeight: '700', fontSize: '22px', color: '#16a34a' }}>
                      ₹{getSelectedFare()?.final_fare?.toFixed(0)}
                    </span>
                  </div>
                </div>
              </div>

              <button 
                onClick={handleBookRide}
                disabled={booking}
                style={{
                  width: '100%',
                  padding: '16px',
                  background: booking ? '#9ca3af' : 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: booking ? 'default' : 'pointer'
                }}
              >
                {booking ? '⏳ Booking Your Ride...' : '🚀 Confirm & Book'}
              </button>
              
              <button 
                onClick={() => setStep('SELECT_VEHICLE')}
                disabled={booking}
                style={{
                  width: '100%',
                  marginTop: '12px',
                  padding: '12px',
                  background: 'none',
                  border: '1px solid #e5e7eb',
                  borderRadius: '10px',
                  color: '#6b7280',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                ← Choose different vehicle
              </button>
            </div>
          )}
        </div>
      )}

      {/* Map Overlay - Full screen when selecting */}
      {showMap && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* Map Header */}
          <div style={{
            background: selectingType === 'pickup' ? '#22c55e' : '#ef4444',
            color: 'white',
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            gap: '14px'
          }}>
            <button 
              onClick={closeMap}
              style={{
                background: 'rgba(255,255,255,0.2)',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 14px',
                color: 'white',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              ← Back
            </button>
            <span style={{ fontSize: '24px' }}>{selectingType === 'pickup' ? '📍' : '🎯'}</span>
            <span style={{ fontWeight: '600', fontSize: '16px' }}>
              {selectingType === 'pickup' ? 'Select Pickup Location' : 'Select Drop-off Location'}
            </span>
          </div>
          
          {/* Map Container */}
          <div style={{ flex: 1, position: 'relative' }}>
            <MapComponent 
              mapCenter={mapCenter}
              selectingType={selectingType}
              currentLocation={selectingType === 'pickup' ? pickupLocation : dropLocation}
              onLocationChange={handleLocationChange}
              onMapReady={handleMapReady}
              otherLocation={selectingType === 'pickup' ? dropLocation : pickupLocation}
            />
            
            {/* Instruction Banner */}
            {mapReady && !geocoding && (
              <div style={{
                position: 'absolute',
                top: '16px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'white',
                padding: '10px 20px',
                borderRadius: '25px',
                boxShadow: '0 2px 12px rgba(0,0,0,0.2)',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                zIndex: 500,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span>👆</span> Drag the pin to adjust location
              </div>
            )}
            
            {/* Loading */}
            {!mapReady && (
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                background: 'white',
                padding: '20px 30px',
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
              }}>
                Loading map...
              </div>
            )}
            
            {/* Geocoding indicator */}
            {geocoding && (
              <div style={{
                position: 'absolute',
                top: '20px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'white',
                padding: '10px 20px',
                borderRadius: '20px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                fontSize: '14px',
                zIndex: 500
              }}>
                ⏳ Getting address...
              </div>
            )}
          </div>
          
          {/* Bottom Panel with address and confirm button */}
          <div style={{
            background: 'white',
            padding: '20px',
            borderTop: '1px solid #e5e7eb'
          }}>
            <div style={{
              background: selectingType === 'pickup' ? '#f0fdf4' : '#fef2f2',
              padding: '14px',
              borderRadius: '12px',
              marginBottom: '16px'
            }}>
              <div style={{ 
                fontSize: '12px', 
                color: selectingType === 'pickup' ? '#16a34a' : '#dc2626', 
                fontWeight: '600',
                marginBottom: '4px'
              }}>
                {selectingType === 'pickup' ? 'PICKUP LOCATION' : 'DROP-OFF LOCATION'}
              </div>
              <div style={{ fontSize: '15px', color: '#374151' }}>
                {selectingType === 'pickup' 
                  ? (pickupAddress || 'Drag the pin to select location')
                  : (dropAddress || 'Drag the pin to select location')
                }
              </div>
            </div>
            
            <button
              onClick={handleConfirmLocation}
              disabled={geocoding || (selectingType === 'pickup' ? !pickupLocation : !dropLocation)}
              style={{
                width: '100%',
                padding: '16px',
                background: selectingType === 'pickup' ? '#22c55e' : '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                opacity: geocoding ? 0.7 : 1
              }}
            >
              {geocoding ? 'Getting address...' : `Confirm ${selectingType === 'pickup' ? 'Pickup' : 'Drop-off'}`}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default TripPlanning;
