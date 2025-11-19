# 🛡️ VigyanShield — AI-Powered Cyber Alert Triage System

**VigyanShield** is an intelligent, modular cybersecurity triage framework designed for **CERT-In**, defense agencies, and critical infrastructure protection.  
It leverages **Large Language Models (LLMs)**, **Retrieval-Augmented Generation (RAG)**, and the **Model-Context Protocol (MCP)** to automate, explain, and prioritize cyber alerts in real time.

---

## 🚀 Project Overview

- **Objective:** Automate the triage of massive cybersecurity alerts using AI-powered reasoning and context-aware interpretation.  
- **Goal:** Reduce analyst fatigue, speed up incident response, and provide explainable AI insights for national cybersecurity operations.  
- **Core Idea:** Transform raw alerts from multiple sources into structured, interpretable, and actionable threat reports.

---

## 🧠 Key Features

- **Alert Ingestion & Normalization**
  - Handles 10,000+ alerts/hour from SIEMs, NetFlow, DNS monitors, etc.
  - Standardizes alerts into a unified schema for processing.

- ** Metadata Extraction**
  - Removes redundant or low-risk alerts.
  - Extracts critical fields — IPs, ports, timestamps, alert type — in <100ms/alert.

- **Contextual Log Correlation**
  - Fetches matching records from NetFlow, DNS, PCAP, and firewall logs.
  - Builds a time-bounded snapshot around each event for precise analysis.

- **MCP Engine** [ Yet to be implemented ]
  - Converts alerts + logs into structured “cyber case files” (JSON/YAML).
  - Ensures traceable, consistent input for AI reasoning.

- **LLM Agent Orchestrator**
  - Classifies threats (e.g., DDoS, BGP hijack, DNS spoof) with human-like reasoning.
  - Generates natural language explanations for transparency.

- **RAG Retriever**
  - Iteratively validates and enriches the AI’s understanding.

- **Threat Report Generator**
  - Produces human- and machine-readable reports.
  - Includes reasoning, supporting logs, and mitigation steps.

- **Analyst Interaction Layer**
  - Dashboard for reviewing, querying, and refining AI outputs.
  - Keeps a human-in-the-loop for accountability and learning.

---

## 🧩 Tech Stack

- **Core AI:** Langchain
- **Data Pipeline:** Python, FastAPI, Elasticsearch/Splunk, JSON/YAML  
- **Frontend:** streamlit 
- **Integration:** APIs, VectorDB

--- 

## Project Setup

### Navigate to the project structure

Inside the cloned project, you’ll find two key folders:

- backend/
- vigyan-shield/

### Build the backend Docker image
- **docker build -t agent-app ./backend**

### Verify the backend image build
- **docker images**


#### You should now see agent-app listed among your local images.

### Navigate to the Vigyan-Shield IPFIX generator
- **cd vigyan-shield/ipfix-generator**


#### Then build the Docker image:
- **docker build -t ipfix-generator:v2 .**

### Build the IPFIX collector image
- cd ../ipfixcol2
- **docker build -t ipfixcol:v2 .**

### Run Docker Compose
- Go back to the main Vigyan-Shield directory:
- cd ../
- **docker compose up**

### Check active Docker networks
- **docker network list**

##### You should see a network named:
- vigyan-shield_demo
### Connect containers within the same network
To run containers on the same network:
- **docker run --network vigyan-shield_demo agent-app**

##### ✅ Verification

##### Once setup completes:
docker ps


