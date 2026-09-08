# API Summary

Base prefix: /api

## Auth
- POST /auth/register
- POST /auth/login
- GET /auth/me

## Cases and Investigations
- GET /cases
- GET /cases/{case_id}
- POST /investigations
- GET /investigations
- GET /investigations/{investigation_id}
- POST /investigations/{investigation_id}/restart

## Locations
- GET /investigations/{investigation_id}/locations
- GET /investigations/{investigation_id}/locations/{location_id}
- POST /investigations/{investigation_id}/locations/{location_id}/search

## Suspects and Chat
- GET /investigations/{investigation_id}/suspects
- GET /investigations/{investigation_id}/suspects/{suspect_id}
- GET /investigations/{investigation_id}/suspects/{suspect_id}/messages
- POST /investigations/{investigation_id}/suspects/{suspect_id}/messages
- POST /investigations/{investigation_id}/suspects/{suspect_id}/confront

## Evidence and Notes
- GET /investigations/{investigation_id}/clues
- GET /investigations/{investigation_id}/contradictions
- GET /investigations/{investigation_id}/notes
- POST /investigations/{investigation_id}/notes
- PATCH /investigations/{investigation_id}/notes/{note_id}
- DELETE /investigations/{investigation_id}/notes/{note_id}

## Evidence Board
- GET /investigations/{investigation_id}/board
- PUT /investigations/{investigation_id}/board

## Accusation
- POST /investigations/{investigation_id}/accusations
- GET /investigations/{investigation_id}/result

## System
- GET /health
- GET /ai/status

OpenAPI docs are exposed by FastAPI at /docs and /openapi.json.
