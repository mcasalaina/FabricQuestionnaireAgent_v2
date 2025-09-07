# Fabric Questionnaire Agent Application

A windowed application that uses Azure AI Foundry agents to answer questions from a structured dataset represented by a Microsoft Fabric Data Agent. Features both individual question processing and Excel import/export functionality, with a command-line interface also available.

## Overview

This tool implements a dual-agent system that:

1. **Question Answerer**: Uses Microsoft Fabric Data Agent to search structured datasets and generate answers
2. **Answer Checker**: Validates that responses actually address the questions asked

If the Answer Checker rejects a response, the Question Answerer reformulates and the cycle repeats up to 10 attempts. If no data is found in the Fabric dataset for a question, the system returns a blank response as expected behavior.

## Features

- **Windowed GUI**: User-friendly interface built with Python tkinter
- **Excel Integration**: Import questions from Excel files and export results
- **Real-time Progress**: Live reasoning display showing agent workflow
- **Character Limit Control**: Configurable answer length with automatic retries
- **Fabric Data Grounding**: All answers sourced from structured datasets via Fabric Data Agent
- **Dual-agent Validation**: Two-stage validation ensures answer quality and relevance
- **Blank Response Handling**: Returns empty responses when no data is available (not an error)
- **Command-line Interface**: CLI available for automation and scripting

## Installation

### Prerequisites

- Python 3.8 or higher
- Azure subscription with AI Foundry project
- Microsoft Fabric Data Agent published and configured
- Azure CLI installed and authenticated (`az login`)
- Fabric Data Agent connection configured in your AI Foundry project

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Primary GUI Application

Run the main windowed application:

```bash
python question_answerer.py
```

**Single Question Mode:**
1. Enter your context (default: "Microsoft Azure AI")
2. Set character limit (default: 2000)
3. Type your question and click "Ask!"
4. Monitor progress in the Reasoning tab
5. View results in Answer tab (no Documentation tab in Fabric mode)

**Excel Import Mode:**
1. Click "Import From Excel" button
2. Select Excel file with questions
3. System auto-detects question columns
4. Monitor real-time processing progress
5. Choose save location when complete

### CLI Interface

For automation and scripting:

```bash
python question_answerer.py --question "What are the sales figures for Q1?"
```

With verbose logging:
```bash
python question_answerer.py --question "What products were sold in January?" --verbose
```

## Example Output

```
================================================================================
FINAL ANSWER:
================================================================================
Based on the structured dataset, here's what I found:

The Q1 sales data shows total revenue of $2.4M across all product categories. 
The Software division led with $1.2M (50%), followed by Hardware at $800K (33%), 
and Services at $400K (17%). This represents a 15% increase compared to Q4 of 
the previous year.

================================================================================
```

## Architecture

### Components

| Component | Responsibility | Data Source |
|-----------|---------------|-------------|
| **Question Answerer** | Searches structured datasets via Fabric Data Agent and generates answers | Microsoft Fabric Data Agent |
| **Answer Checker** | Validates that responses actually address the questions asked | No external data source |

### Workflow

1. **Read Input**: Accept a question from the GUI or command line
2. **Answer Generation**: Question Answerer queries Fabric Data Agent for relevant information
3. **Blank Response Check**: If no data found, return blank response (expected behavior)
4. **Validation**: Answer Checker reviews the response for relevance to the original question
5. **Decision**:
   - If Answer Checker approves: Output the final answer and terminate successfully
   - If Answer Checker rejects: Log rejection reasons, increment attempt counter, and retry (up to 10 attempts)

## Configuration

### Environment Setup

#### Step 1: Create Environment File

Copy the template file and configure your values:

```bash
cp .env.template .env
```

Then edit `.env` with your actual Azure AI Foundry and Fabric configuration values.

### Required Environment Variables

The application requires the following environment variables to be set in your `.env` file:

| Variable | Description | Where to Find |
|----------|-------------|---------------|
| `AZURE_OPENAI_ENDPOINT` | Azure AI Foundry project endpoint | Azure AI Foundry Portal > Project Overview > Project Details |
| `AZURE_OPENAI_MODEL_DEPLOYMENT` | Your deployed model name | Azure AI Foundry Portal > Models + Endpoints |
| `FABRIC_CONNECTION_ID` | Fabric Data Agent connection ID | Azure AI Foundry Portal > Management Center > Connected Resources |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights connection string (optional) | Azure Portal > Application Insights > Overview |
| `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED` | Enable AI content tracing (optional) | Set to `true` or `false` |

**Example `.env` file:**

```bash
AZURE_OPENAI_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4o-mini
FABRIC_CONNECTION_ID=/subscriptions/your-sub/resourceGroups/your-rg/providers/Microsoft.MachineLearningServices/workspaces/your-project/connections/your-fabric-connection
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true
```

**Important Security Notes:**

- Never commit your `.env` file to version control (it's already in `.gitignore`)
- The `.env.template` file shows the required structure without sensitive values
- Application Insights connection string enables Azure AI Foundry tracing for monitoring and debugging

### Microsoft Fabric Data Agent Setup

Before using this application, you must:

1. **Create and Publish a Fabric Data Agent** in Microsoft Fabric with your structured datasets
2. **Configure Connection in Azure AI Foundry**: Add the Fabric Data Agent as a knowledge source
3. **Set Up Authentication**: Ensure proper permissions for data access via Identity Passthrough

The Fabric connection ID should be in the format:
```
/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<project-name>/connections/<connection-name>
```

### Azure AI Foundry Tracing

The application includes built-in Azure AI Foundry tracing integration that provides:

- **Distributed Tracing**: Full visibility into dual-agent workflows
- **Performance Monitoring**: Track execution times and bottlenecks  
- **Gen AI Content Capture**: Record prompts and responses (when enabled)
- **Error Tracking**: Detailed error context and stack traces
- **Resource Usage**: Monitor token consumption and API calls

Traces appear in:

- **Azure AI Foundry Portal** → Tracing tab
- **Azure Portal** → Application Insights → Transaction search

Set `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=false` in production if you want to exclude AI content from traces for privacy reasons.

### FoundryAgentSession Helper

The `FoundryAgentSession` class in `utils/resource_manager.py` provides a context manager for safely managing Azure AI Foundry agent and thread resources. This helper is **required** because:

1. **Resource Cleanup**: Azure AI Foundry agents and threads are persistent resources that must be explicitly deleted to avoid resource leaks
2. **Exception Safety**: Ensures cleanup occurs even if exceptions are raised during agent operations
3. **Cost Management**: Prevents accumulation of unused resources that could incur costs

Usage example:

```python
with FoundryAgentSession(client, model="gpt-4o-mini", 
                        name="my-agent", 
                        instructions="You are a helpful assistant") as (agent, thread):
    # Use agent and thread for operations
    # Resources are automatically cleaned up when exiting the context
```

The context manager handles:

- Creating agent and thread resources on entry
- Automatic cleanup on exit (even if exceptions occur)
- Robust error handling during cleanup to prevent masking original exceptions

### API Configuration

The tool uses Azure AI Foundry with integrated Bing search grounding. For alternative search APIs, consider:

- Google Custom Search API
- Bing Search API  
- SerpAPI

## Limitations

- **Demo Implementation**: Uses basic web search and text processing
- **Rate Limiting**: May encounter rate limits with free APIs
- **Language Support**: Optimized for English questions
- **Fact Checking**: Uses heuristic-based validation rather than advanced fact-checking

## Development

### Project Structure

```text
QuestionnaireAgent_v2/
├── question_answerer.py         # Main GUI application
├── main.py                      # Legacy CLI entry point
├── agents/                      # Agent implementations
│   ├── __init__.py
│   ├── question_answerer.py
│   ├── answer_checker.py
│   └── link_checker.py
├── utils/                       # Shared utilities
│   ├── __init__.py
│   ├── logger.py
│   ├── resource_manager.py      # Azure AI Foundry resource management
│   └── web_search.py
├── tests/                       # Test suite
├── requirements.txt             # Python dependencies
├── setup.py                     # Installation script
├── README.md                    # This documentation
└── README_Questionnaire_UI.md   # Detailed UI documentation
```

### Adding New Features

To extend the system:

1. **New Validation**: Add checks to `AnswerChecker`
2. **Better Search**: Upgrade `WebSearcher` with more sophisticated APIs
3. **Advanced NLP**: Integrate language models for better synthesis and validation
4. **Caching**: Add response caching to reduce API calls

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please read the contributing guidelines and submit pull requests for any improvements.
