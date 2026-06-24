# STORIES.md

## Epic: Core Targeting Functionality

### Story 1: As a drone operator, I want to draw a target on the map using a mouse or touch input, so that I can specify a location without needing GPS coordinates.
*Acceptance Criteria:*
- The application displays a base map (OpenStreetMap) with zoom and pan controls.
- Clicking or tapping on the map places a circular marker at the exact position.
- The marker is labeled with a unique alphanumeric ID (e.g., "Target-001") and displays the latitude/longitude coordinates in a panel.
- The marker is visually distinct (e.g., red circle with a crosshair) and can be selected.

### Story 2: As a user, I want to adjust the target position by dragging the marker, so that I can fine-tune the location.
*Acceptance Criteria:*
- Dragging the marker on desktop or mobile devices updates its position in real-time.
- Visual feedback (e.g
