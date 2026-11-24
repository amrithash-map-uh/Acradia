# SAHAAY --- AI-Powered Government Scheme Assistant

> Helping people discover government welfare schemes, understand their
> benefits, and connect with organizations that can assist them.

SAHAAY is a citizen-focused platform designed to make government welfare
schemes easier to discover and access. It combines personalized scheme
matching, AI-assisted explanations, voice-friendly guidance, and a
connection to nearby NGOs.

Government schemes are often spread across multiple portals and
documents. Even when someone is eligible, finding the right scheme and
understanding how to apply can be difficult. SAHAAY aims to reduce that
gap through one guided experience.

------------------------------------------------------------------------

## Table of Contents

-   [The Problem](#the-problem)
-   [Our Approach](#our-approach)
-   [MVP Scope](#mvp-scope)
-   [How It Works](#how-it-works)
-   [System Architecture](#system-architecture)
-   [Technology Stack](#technology-stack)
-   [Core Modules](#core-modules)
-   [Getting Started](#getting-started)
-   [Project Structure](#project-structure)
-   [Data and Trust](#data-and-trust)
-   [Roadmap](#roadmap)
-   [Contributing](#contributing)

------------------------------------------------------------------------

## The Problem

A large number of central and state welfare schemes exist, but
information about them is distributed across different websites and
sources. This creates several barriers:

-   **Fragmented information:** Citizens may need to visit multiple
    portals to find relevant schemes.
-   **Complex eligibility rules:** It can be difficult to understand
    whether a scheme applies to a person's circumstances.
-   **Language and accessibility barriers:** Information presented
    mainly as text can be hard to use for people who prefer local
    languages or spoken guidance.
-   **Limited assistance:** People who need help with applications may
    not know which local organization to approach.
-   **Lack of follow-up:** It can be difficult to know what happened
    after asking an organization for help.

The result is that people who could benefit from welfare programs may
never discover or apply for them.

## Our Approach

SAHAAY brings scheme discovery and assistance into a single workflow.

1.  A user provides basic details such as age, income, location, and
    occupation.
2.  The platform compares the profile with scheme eligibility criteria.
3.  Relevant schemes are presented with clear explanations and source
    information.
4.  An AI assistant helps answer follow-up questions using the scheme
    knowledge base.
5.  Users who need additional support can submit a help request to an
    available NGO.

The platform is designed to make information easier to understand---not
to replace official government decisions or application portals.

## MVP Scope

The first version focuses on demonstrating the complete citizen journey
with a small, curated dataset. It should be possible to test the main
workflow without building every long-term feature.

### Included in the MVP

  -----------------------------------------------------------------------
  Module                              MVP behaviour
  ----------------------------------- -----------------------------------
  User profile                        Collect age, income, location,
                                      occupation, and preferred language

  Scheme catalogue                    Store a curated set of schemes with
                                      descriptions and eligibility
                                      criteria

  Eligibility matching                Apply rule-based filters to find
                                      potentially relevant schemes

  Scheme results                      Show matched schemes and explain
                                      the relevant eligibility conditions

  AI assistance                       Answer questions using retrieved
                                      information from the available
                                      scheme dataset

  Voice output                        Read scheme explanations aloud
                                      where text-to-speech is configured

  NGO help request                    Let a user submit a request for
                                      assistance

  Basic NGO routing                   Associate a request with an
                                      available, registered NGO using
                                      location information where
                                      supported
  -----------------------------------------------------------------------

### Not required for the first MVP

These are longer-term goals, not assumptions about what the initial
prototype already supports:

-   Coverage of 700+ schemes across India
-   Support for 1,100+ languages
-   Production-grade GPS-based NGO discovery
-   Full NGO case-management dashboards and automated progress tracking
-   Public ratings and reviews at scale
-   Direct integration with government application systems
-   Production deployment across multiple states

------------------------------------------------------------------------

## How It Works

### 1. Citizen journey

``` mermaid
flowchart TD
    A([Open SAHAAY]) --> B[Enter basic profile]
    B --> C[Submit profile]
    C --> D[Check scheme eligibility]
    D --> E[Display matching schemes]
    E --> F[Open a scheme]
    F --> G[Read clear explanation]
    G --> H{Need more help?}
    H -- No --> I([End])
    H -- Yes --> J[Ask AI assistant]
    J --> K{Need human assistance?}
    K -- No --> I
    K -- Yes --> L[Submit NGO help request]
    L --> M[Route request to an available NGO]
    M --> N([Await assistance])
```

### 2. Scheme matching and AI assistance

Eligibility filtering and AI explanations serve different purposes. The
matching step uses explicit rules; the AI assistant retrieves relevant
scheme information to explain it in natural language.

``` mermaid
flowchart TD
    A[User profile] --> B[Backend API]
    B --> C[Eligibility rules]
    D[Scheme catalogue] --> C
    C --> E[Eligible scheme shortlist]
    E --> F[Scheme details]
    F --> G[Knowledge base retrieval]
    H[User question] --> I[AI assistant]
    G --> I
    I --> J[Context-based answer]
    E --> K[Results shown in web app]
    J --> K
```

### 3. NGO assistance workflow

``` mermaid
flowchart TD
    A[User requests assistance] --> B[Create help request]
    B --> C[Capture location and request details]
    C --> D[Find a suitable registered NGO]
    D --> E{NGO available?}
    E -- Yes --> F[Assign or forward request]
    E -- No --> G[Keep request pending or show alternatives]
    F --> H[NGO reviews request]
    H --> I[Provide assistance]
    I --> J[Update request status]
    J --> K[User can view progress]
```

The exact assignment and status-update process will depend on the NGO
features implemented in the MVP.

## System Architecture

SAHAAY uses a web frontend connected to a Python API. The API handles
profile data, eligibility checks, scheme retrieval, and help requests.
The AI layer uses retrieved scheme information to ground its responses.

``` mermaid
flowchart TB
    U[Citizen / User] --> FE[Web frontend<br/>HTML, CSS, JavaScript]
    FE <--> API[FastAPI backend]

    API --> PROFILE[Profile handling]
    API --> MATCH[Eligibility matching engine]
    API --> SCHEMES[(MySQL database<br/>Scheme and user records)]
    MATCH --> SCHEMES

    API --> RAG[RAG assistant]
    RAG --> KB[(Scheme knowledge base)]
    RAG --> LLM[Language model]
    LLM --> RAG

    API --> VOICE[Text-to-speech layer]
    API --> NGO[NGO assistance module]
    NGO --> DB[(NGO and request records)]

    VOICE --> FE
    RAG --> API
    NGO --> API
    API --> FE
```

### Request lifecycle

1.  The frontend sends a profile or question to the backend.
2.  FastAPI validates the request and invokes the relevant service.
3.  The eligibility module checks the profile against scheme criteria.
4.  For AI questions, the retrieval layer searches the scheme knowledge
    base and supplies relevant context to the assistant.
5.  The backend returns results to the frontend.
6.  If the user asks for human assistance, the NGO module records and
    routes the request.

------------------------------------------------------------------------

## Technology Stack

  -----------------------------------------------------------------------
  Layer                   Technology              Responsibility
  ----------------------- ----------------------- -----------------------
  Frontend                HTML, CSS, JavaScript   User interface and
                                                  interactions

  Backend                 Python, FastAPI         API endpoints and
                                                  application logic

  Database                MySQL                   User, scheme, NGO, and
                                                  request records

  Cloud database hosting  AWS RDS                 Managed MySQL hosting
                                                  when deployed

  AI                      Retrieval-Augmented     Answers grounded in
                          Generation (RAG)        scheme information

  Voice output            Coqui TTS               Convert text
                                                  explanations into
                                                  speech

  Voice messaging         Google API              Voice-message delivery
                                                  where configured
  -----------------------------------------------------------------------

The MVP can use a smaller local dataset and local development setup
before cloud deployment or broader integrations are introduced.

## Core Modules

### User profile

Collects only the details needed for scheme discovery, such as age,
income, location, occupation, and language preference.

### Scheme catalogue

Stores scheme names, descriptions, eligibility requirements, benefits,
application guidance, and source references. The quality of this data
directly affects matching and AI answers.

### Eligibility engine

Applies explicit eligibility conditions to the user's profile. It
narrows the catalogue before the user explores scheme details.

> A match indicates that a scheme may be relevant based on the available
> criteria. It is not an official confirmation of eligibility or benefit
> approval.

### AI assistant

Uses retrieval-augmented generation (RAG): it retrieves relevant
passages from the scheme knowledge base and uses that context to answer
user questions. Answers should identify their supporting scheme
information and avoid presenting unsupported claims as facts.

### Voice assistance

Provides spoken versions of explanations to make information easier to
access. Language coverage depends on the configured speech and language
services.

### NGO assistance

Allows users to request help from an organization. The longer-term
direction includes verified NGO profiles, location-aware routing, and
request progress updates.

------------------------------------------------------------------------

## Getting Started

**Requirements:** Python 3.10+

``` bash
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser (API docs: **http://127.0.0.1:8000/docs**).

*Works out of the box with local SQLite—no database setup or API key required.*

------------------------------------------------------------------------

## Project Structure

A suggested structure for the MVP:

``` text
sahaay/
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── routes/
│       │   ├── profiles.py
│       │   ├── schemes.py
│       │   ├── assistant.py
│       │   └── ngo.py
│       ├── services/
│       │   ├── eligibility.py
│       │   ├── retrieval.py
│       │   └── voice.py
│       ├── models/
│       └── database/
│
├── data/
│   └── schemes/
│
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

This is a proposed organization, not a claim that every file or module
already exists.

------------------------------------------------------------------------

## Data and Trust

SAHAAY is intended to make public welfare information easier to
understand. That makes accuracy and transparency essential.

-   Prefer official government portals and datasets when collecting
    scheme information.
-   Keep the source URL and last-reviewed date for each scheme.
-   Clearly show eligibility conditions and distinguish confirmed data
    from generated explanations.
-   Do not treat an AI-generated response as an official government
    decision.
-   Collect only the personal information needed for the requested
    service.
-   Obtain user consent before sharing a help request or personal
    details with an NGO.
-   Verify NGO identities and provide a way to report outdated or
    incorrect information.

Potential information sources include
[MyScheme](https://www.myscheme.gov.in/) and
[data.gov.in](https://www.data.gov.in/), along with other reviewed
public sources.

------------------------------------------------------------------------

## Roadmap

-   [ ] Build the initial web interface and profile form
-   [ ] Add a curated scheme dataset
-   [ ] Implement rule-based eligibility matching
-   [ ] Display matched schemes and eligibility explanations
-   [ ] Add RAG-based question answering over scheme information
-   [ ] Add text-to-speech for scheme explanations
-   [ ] Implement NGO registration and help-request submission
-   [ ] Add location-aware NGO discovery
-   [ ] Add request status updates and user feedback
-   [ ] Expand verified scheme and language coverage

------------------------------------------------------------------------

## Contributing

Contributions, suggestions, and issue reports are welcome.

1.  Fork the repository.
2.  Create a feature branch: `git checkout -b feature/your-feature`
3.  Commit your changes: `git commit -m "Add your feature"`
4.  Push the branch: `git push origin feature/your-feature`
5.  Open a pull request describing the change.

For major changes, open an issue first so the proposed approach can be
discussed.

------------------------------------------------------------------------

## Project Status

SAHAAY is being developed as an MVP. The initial goal is to validate the
core workflow---profile intake, scheme matching, understandable scheme
information, AI assistance, and an NGO help request---before expanding
data coverage and integrations.

## License

Choose and add a license before publishing the repository for public
reuse. If you intend to make the project open source, a license such as
MIT may be suitable; confirm that it matches your team's requirements.
