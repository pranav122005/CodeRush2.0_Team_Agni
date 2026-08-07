# NEXUS Project Context

## Project

-   Project: NEXUS - Enterprise x402 Payment Verification & Settlement
    Mesh.
-   Netflix is only the demo Resource Server.
-   The actual product is the NEXUS Mesh.

## Current Flow

1.  User clicks Play.
2.  Frontend calls GET /api/v1/content/{movie_id}.
3.  Backend responds with HTTP 402 Payment Required and x402 payment
    requirements.
4.  Frontend opens Payment Modal.
5.  User pays.
6.  Frontend calls the Mesh.
7.  Mesh verifies and settles payment.
8.  Receipt generated.
9.  Movie unlocked.

## Current Progress

Completed: - Netflix frontend - Movie selection - Feature panel -
Payment modal - FastAPI backend - HTTP 402 challenge

Pending: - Compatibility Layer - Facilitator Registry - Verification
Service - Settlement Service - Receipt Service - Observability - Plugin
System

## Architecture

Netflix Frontend → Netflix Backend (Resource Server) → NEXUS Mesh →
Official Algorand Facilitator → Algorand TestNet

## Mesh Folder Structure

app/ - api - compatibility - registry - verification - settlement -
receipt - observability - plugins - services - schemas - models -
database - config - utils

## Planned APIs

-   POST /api/v1/verify
-   POST /api/v1/settle
-   GET /api/v1/receipt/{receipt_id}
-   GET /api/v1/trace/{trace_id}
-   GET /api/v1/health
-   GET /api/v1/facilitators

## Algorand Repository

Reuse: - x402 protocol - HTTP 402 flow - Wallet integration -
Facilitator client - Middleware

Build: - Compatibility Layer - Facilitator Registry - Routing Engine -
Verification - Settlement - Receipt - Dashboard - Plugins

## Networks

-   Algorand (Official)
-   Ethereum (Simulator)
-   Solana (Simulator)

## Receipt

-   Receipt ID
-   Payment ID
-   Transaction ID
-   Verification Status
-   Settlement Status
-   Network
-   Timestamp
-   Trace ID
-   Receipt Signature

## Important Decisions

-   Netflix is only a demo.
-   Mesh is a separate project.
-   Remove Groq from verification.
-   Use deterministic replay protection.
