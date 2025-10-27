import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { MapPin, Navigation, ZoomIn, ZoomOut, Layers, Satellite, Map } from 'lucide-react'

const GPSMap = ({ 
  center = { lat: -6.2088, lng: 106.8456 }, // Jakarta coordinates
  zoom = 13,
  markers = [],
  heatmapData = [],
  onMarkerClick = () => {},
  onMapClick = () => {},
  height = '400px',
  showControls = true
}) => {
  const [mapType, setMapType] = useState('satellite')
  const [currentZoom, setCurrentZoom] = useState(zoom)
  const [isLoading, setIsLoading] = useState(true)
  const mapRef = useRef(null)
  const [mapInstance, setMapInstance] = useState(null)

  // Initialize map
  useEffect(() => {
    if (typeof window !== 'undefined' && window.google) {
      initializeMap()
    } else {
      // Load Google Maps API
      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization`
      script.async = true
      script.defer = true
      script.onload = () => {
        initializeMap()
      }
      document.head.appendChild(script)
    }
  }, [])

  const initializeMap = () => {
    if (mapRef.current && window.google) {
      const map = new window.google.maps.Map(mapRef.current, {
        center: center,
        zoom: currentZoom,
        mapTypeId: mapType === 'satellite' ? 'satellite' : 'roadmap',
        styles: mapType === 'satellite' ? [] : [
          {
            featureType: 'all',
            elementType: 'geometry',
            stylers: [{ color: '#242f3e' }]
          },
          {
            featureType: 'water',
            elementType: 'geometry',
            stylers: [{ color: '#17263c' }]
          },
          {
            featureType: 'landscape',
            elementType: 'geometry',
            stylers: [{ color: '#2c3e50' }]
          }
        ]
      })

      setMapInstance(map)
      setIsLoading(false)

      // Add markers
      markers.forEach(marker => {
        const mapMarker = new window.google.maps.Marker({
          position: { lat: marker.lat, lng: marker.lng },
          map: map,
          title: marker.title,
          icon: marker.icon || {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="#ef4444"/>
              </svg>
            `),
            scaledSize: new window.google.maps.Size(24, 24),
            anchor: new window.google.maps.Point(12, 24)
          }
        })

        if (marker.onClick) {
          mapMarker.addListener('click', () => marker.onClick(marker))
        }
      })

      // Add heatmap layer if data exists
      if (heatmapData.length > 0) {
        const heatmap = new window.google.maps.visualization.HeatmapLayer({
          data: heatmapData.map(point => ({
            location: new window.google.maps.LatLng(point.lat, point.lng),
            weight: point.weight || 1
          })),
          map: map,
          radius: 50,
          opacity: 0.6
        })
      }

      // Add click listener
      map.addListener('click', (event) => {
        onMapClick({
          lat: event.latLng.lat(),
          lng: event.latLng.lng()
        })
      })
    }
  }

  const handleZoomIn = () => {
    if (mapInstance) {
      const newZoom = Math.min(currentZoom + 1, 20)
      setCurrentZoom(newZoom)
      mapInstance.setZoom(newZoom)
    }
  }

  const handleZoomOut = () => {
    if (mapInstance) {
      const newZoom = Math.max(currentZoom - 1, 1)
      setCurrentZoom(newZoom)
      mapInstance.setZoom(newZoom)
    }
  }

  const toggleMapType = () => {
    const newType = mapType === 'satellite' ? 'roadmap' : 'satellite'
    setMapType(newType)
    if (mapInstance) {
      mapInstance.setMapTypeId(newType === 'satellite' ? 'satellite' : 'roadmap')
    }
  }

  return (
    <div className="relative w-full" style={{ height }}>
      {/* Map Container */}
      <div
        ref={mapRef}
        className="w-full h-full rounded-lg overflow-hidden"
        style={{ minHeight: '300px' }}
      />

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center rounded-lg">
          <div className="flex items-center space-x-2 text-white">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
            <span>Loading Map...</span>
          </div>
        </div>
      )}

      {/* Map Controls */}
      {showControls && (
        <div className="absolute top-4 right-4 flex flex-col space-y-2">
          {/* Zoom Controls */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <button
              onClick={handleZoomIn}
              className="p-2 hover:bg-gray-100 transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <div className="border-t border-gray-200"></div>
            <button
              onClick={handleZoomOut}
              className="p-2 hover:bg-gray-100 transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
          </div>

          {/* Map Type Toggle */}
          <button
            onClick={toggleMapType}
            className="bg-white rounded-lg shadow-lg p-2 hover:bg-gray-100 transition-colors"
            title={`Switch to ${mapType === 'satellite' ? 'Road' : 'Satellite'} view`}
          >
            {mapType === 'satellite' ? <Map className="w-4 h-4" /> : <Satellite className="w-4 h-4" />}
          </button>

          {/* Layers Toggle */}
          <button
            className="bg-white rounded-lg shadow-lg p-2 hover:bg-gray-100 transition-colors"
            title="Toggle Layers"
          >
            <Layers className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Map Info */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-3">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Navigation className="w-4 h-4" />
          <span>Zoom: {currentZoom}</span>
          <span>•</span>
          <span>{mapType === 'satellite' ? 'Satellite' : 'Road'} view</span>
        </div>
      </div>
    </div>
  )
}

export default GPSMap

