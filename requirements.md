## System Overview
The system is an AI-powered assistant that enables field mechanics to ask questions about specific products and receive accurate answers based exclusively on provided technical documentation (PDF manuals, service guides, schematics).
The system acts as a “product power user”, reducing the need to manually search through documentation while ensuring correct and safe maintenance actions.

## Stakeholders
#### Field Mechanics 
- Primary users, require fast and accurate answers
#### Maintenance Engineers 
- Provide domain knowledge and documentation
#### Product Management 
- Defines scope and supported products
#### IT / AI Engineers 
- Implement and maintain the system
#### Legal & Compliance 
- Ensure safe and compliant answers
#### Company Management 
- Sponsors the solution

## System Requirements (Functional )
#### REQ-1
The system shall allow users to ask natural-language questions about a specific product.
#### REQ-2
The system shall retrieve answers only from the provided product documentation.
#### REQ-3
The system shall support multiple product manuals simultaneously.
#### REQ-4
The system shall identify the relevant product based on user input or follow-up clarification.
#### REQ-5
The system shall provide concise, step-by-step answers suitable for field usage.
#### REQ-6
The system shall explicitly state when the documentation does not contain the requested information.

## Architecture Requirements
#### REQ-7
The system shall separate:
- document ingestion,
- document retrieval,
- answer generation.
#### REQ-8
The AI model shall not be trained on company data but shall use retrieval-augmented generation(RAG).
#### REQ-9
The system shall allow replacement or upgrade of the AI model without re-ingesting documents.

## Testing Requirements
#### REQ-10
The system shall support black-box testing using predefined question–answer pairs.
#### REQ-11
The system shall log all user questions and generated answers for audit and improvement purposes.
#### REQ-12
The system shall detect and flag low-confidence answers.

## Deployment Requirements
#### REQ-13
The system shall be deployable as a backend service without a graphical user interface.
#### REQ-14
The system shall support command-line interaction for PoC demonstration.
#### REQ-15
The system shall be deployable on a local machine or company server.
## Data & AI Requirements
#### REQ-16
The system shall preprocess documents by splitting them into semantically meaningful chunks.
#### REQ-17
The system shall store document embeddings in a vector database.
#### REQ-18
The system shall reject user questions unrelated to the uploaded documentation.
## Ethical & Legal Requirements
#### REQ-19
If a user requests information related to safety-critical operations, warnings, or danger conditions, the system shall:
- base the answer exclusively on the provided documentation,
- preserve the original warning and danger statements,
- present the information in a precise, unambiguous, and structured form,
- explicitly highlight safety warnings and limitations.
#### REQ-20
The system shall clearly state that it is an assistant and not a replacement for certified technicians.

##Non-Functional Requirements
#### NFR-1 (Accuracy)
The system shall not invent information that is not present in the documentation.
#### NFR-2 (Explainability)
The system shall reference the source section or page when answering a question.
#### NFR-3 (Latency)
The system shall respond within 3 seconds for standard queries.
#### NFR-4 (Reliability)
The system shall return a valid response for at least 99% of user queries.
#### NFR-5 (Safety)
The system shall not provide unsafe maintenance instructions that contradict documentation warnings.
#### NFR-6 (Usability)
Answers shall be understandable by non-AI experts and optimized for mobile or tablet screens.

## Assumptions
#### AS-1: 
All official product documentation is available in digital (PDF) form
#### AS-2: 
Documentation content is technically correct and up to date
#### AS-3: 
Users understand basic technical terminology
#### AS-4: 
Internet connectivity is available during usage