# AI-Powered Construction Plan Analysis & Quote Generation System

This repository contains the implementation of an AI-driven platform for automated analysis of construction plans and instant generation of accurate cost estimations.

## Project Overview

The solution empowers construction companies by significantly reducing manual quoting efforts, ensuring precision, and streamlining decision-making processes.

### Key Features

- **Document Handling**: Support for PDF, CAD, BIM files with automated plan classification
- **Element Recognition**: AI-powered detection of structural components, openings, MEP systems, and annotations
- **Dimension Extraction**: Automatic scale detection and precise measurements (±2% accuracy)
- **Quantity Takeoff**: Automated calculation for materials, labor, and equipment needs
- **Cost Estimation**: Real-time cost estimation with market data integration
- **Plugin Architecture**: Modular, extensible system supporting trade-specific plugins

## Repository Structure

- `/backend`: FastAPI-based RESTful API and AI services
- `/frontend`: React.js web interface with Tailwind CSS and ShadCN components
- `/plugins`: Core and additional trade-specific plugins
- `/docs`: Documentation for users, developers, and API

## Technology Stack

- **Backend**: Python with FastAPI, TensorFlow/PyTorch for AI models
- **Frontend**: React.js with Tailwind CSS and ShadCN components
- **Database**: MySQL
- **Deployment**: HostGator shared hosting via cPanel with Git integration

## Getting Started

Detailed setup and development instructions are available in the respective directories:

- [Backend Setup](/backend/README.md)
- [Frontend Setup](/frontend/README.md)
- [Plugin Development](/plugins/README.md)
