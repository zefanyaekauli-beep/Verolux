import React from 'react'
import VideoFeed from '../components/VideoFeed'

export default function VideoWall(){
  return (
    <div className="min-h-screen verolux-pattern p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 verolux-card">
          <h1 className="verolux-heading-3">Video Wall</h1>
          <p className="verolux-body-secondary">Live multi-camera monitoring</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <VideoFeed title="Loading Dock" source="file:videoplayback.mp4" />
          <VideoFeed title="Warehouse A" source="webcam:0" />
          <VideoFeed title="Office Entrance" source="webcam:1" />
          <VideoFeed title="Parking Lot" source="webcam:2" />
          <VideoFeed title="Perimeter East" source="webcam:3" />
          <VideoFeed title="Server Room" source="webcam:4" />
        </div>
      </div>
    </div>
  )
}



