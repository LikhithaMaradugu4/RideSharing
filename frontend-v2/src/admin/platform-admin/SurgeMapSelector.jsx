import { useState, useEffect, useRef, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet-draw';

/**
 * Normalize a boundary value into a valid GeoJSON object that L.geoJSON() can parse.
 * Handles: raw coordinate arrays, Polygon geometry, or Feature/FeatureCollection.
 */
function normalizeGeoJson(raw) {
  const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;

  // Empty or null-ish values
  if (!parsed || (typeof parsed === 'object' && !Array.isArray(parsed) && Object.keys(parsed).length === 0)) {
    return null;
  }

  // Already a Feature or FeatureCollection
  if (parsed.type === 'Feature' || parsed.type === 'FeatureCollection') return parsed;

  // A Geometry object (Polygon, MultiPolygon, etc.)
  if (parsed.type && parsed.coordinates) return { type: 'Feature', geometry: parsed, properties: {} };

  // Raw coordinates array — assume Polygon
  if (Array.isArray(parsed) && parsed.length > 0) {
    let coords = parsed;
    // [[lng,lat], ...] → wrap in outer ring
    if (typeof coords[0][0] === 'number') {
      coords = [coords];
    }
    return { type: 'Feature', geometry: { type: 'Polygon', coordinates: coords }, properties: {} };
  }

  return null; // Unrecognized — treat as empty rather than crash
}

/**
 * SurgeMapSelector — Leaflet-based polygon drawing component.
 *
 * Props:
 *   initialGeoJson  – pre-existing boundary GeoJSON string (for edit mode)
 *   onPolygonChange  – callback(geoJsonString | null)
 *   cityBoundary     – optional city boundary GeoJSON string to show on map
 *   height           – map container height (default 400)
 */
const SurgeMapSelector = ({ initialGeoJson = null, onPolygonChange, cityBoundary = null, height = 400 }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const drawnItemsRef = useRef(null);
  const drawControlRef = useRef(null);
  const cityLayerRef = useRef(null);

  // Initialize map once
  useEffect(() => {
    if (mapInstanceRef.current) return;

    const map = L.map(mapRef.current, {
      center: [20.5937, 78.9629],  // default: India center
      zoom: 5,
      scrollWheelZoom: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);

    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    drawnItemsRef.current = drawnItems;

    const drawControl = new L.Control.Draw({
      position: 'topright',
      draw: {
        polygon: {
          allowIntersection: false,
          showArea: false,
          shapeOptions: { color: '#e74c3c', weight: 2, fillOpacity: 0.15 },
        },
        polyline: false,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false,
      },
      edit: {
        featureGroup: drawnItems,
        remove: true,
      },
    });
    map.addControl(drawControl);
    drawControlRef.current = drawControl;

    // On polygon created
    map.on(L.Draw.Event.CREATED, (e) => {
      drawnItems.clearLayers();
      drawnItems.addLayer(e.layer);
      emitGeoJson(drawnItems);
    });

    // On polygon edited
    map.on(L.Draw.Event.EDITED, () => {
      emitGeoJson(drawnItems);
    });

    // On polygon deleted
    map.on(L.Draw.Event.DELETED, () => {
      emitGeoJson(drawnItems);
    });

    mapInstanceRef.current = map;

    // Cleanup
    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  const emitGeoJson = useCallback((drawnItems) => {
    if (!onPolygonChange) return;
    const layers = [];
    drawnItems.eachLayer((layer) => layers.push(layer));
    if (layers.length === 0) {
      onPolygonChange(null);
      return;
    }
    const geoJson = layers[0].toGeoJSON();
    onPolygonChange(JSON.stringify(geoJson.geometry));
  }, [onPolygonChange]);

  // Load initial GeoJSON (edit mode)
  useEffect(() => {
    if (!mapInstanceRef.current || !drawnItemsRef.current) return;
    const drawnItems = drawnItemsRef.current;
    drawnItems.clearLayers();

    if (initialGeoJson) {
      try {
        const normalized = normalizeGeoJson(initialGeoJson);
        if (normalized) {
          const geoJsonLayer = L.geoJSON(normalized, {
            style: { color: '#e74c3c', weight: 2, fillOpacity: 0.15 },
          });
          geoJsonLayer.eachLayer((layer) => drawnItems.addLayer(layer));
          mapInstanceRef.current.fitBounds(drawnItems.getBounds(), { padding: [40, 40] });
        }
      } catch (err) {
        console.warn('Failed to parse initial GeoJSON:', err);
      }
    }
  }, [initialGeoJson]);

  // Show city boundary if provided
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    // Remove old city layer
    if (cityLayerRef.current) {
      mapInstanceRef.current.removeLayer(cityLayerRef.current);
      cityLayerRef.current = null;
    }

    if (cityBoundary) {
      try {
        const normalized = normalizeGeoJson(cityBoundary);
        if (normalized) {
          const cityLayer = L.geoJSON(normalized, {
            style: { color: '#3498db', weight: 2, fillOpacity: 0.05, dashArray: '6 4' },
          });
          cityLayer.addTo(mapInstanceRef.current);
          cityLayerRef.current = cityLayer;
          mapInstanceRef.current.fitBounds(cityLayer.getBounds(), { padding: [40, 40] });
        }
      } catch (err) {
        console.warn('Failed to parse city boundary:', err);
      }
    }
  }, [cityBoundary]);

  // Force map resize when container is shown
  useEffect(() => {
    const timer = setTimeout(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    }, 200);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div style={{ position: 'relative' }}>
      <div ref={mapRef} style={{ height, width: '100%', borderRadius: 8, border: '1px solid #ddd' }} />
      <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
        Use the draw tool (top-right) to draw a polygon. Click vertices to complete.
      </div>
    </div>
  );
};

export default SurgeMapSelector;
