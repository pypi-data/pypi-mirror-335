# bedrock-tracing

`bedrock_tracing` is a Python library that provides OpenTelemetry tracing capabilities for AWS Bedrock Agent interactions. It enables automatic tracing of API calls, helping users capture and analyze distributed traces for debugging and observability.


## Installation

`pip install bedrock_tracing`

## Features

- OpenTelemetry tracing for AWS Bedrock Agent interactions
- Integration with environment variables for credentials and configuration

## @trace_decorator - Tracing Bedrock Agent Responses
The `@trace_decorator` simplifies tracing for Bedrock agent interactions using OpenTelemetry. It automatically captures relevant trace data, including:

- Session details: session.id, agent.id, and agent.alias_id
- Agent responses: Captures and logs agent-generated text
- Trace events: Processes structured trace data from Bedrock responses

When applied to a function that streams Bedrock agent responses, the decorator ensures each invocation is traced, enriching observability for debugging and performance analysis.

## Usage

```python
import os
import uuid
import boto3
from dotenv import load_dotenv
from bedrock_tracing import trace_decorator
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider

# Load environment variables
load_dotenv()

def generate_session_id():
    return str(uuid.uuid4())

@trace_decorator
def invoke_bedrock_agent(brt, question, session_id):
    """Invokes the Bedrock agent and processes trace data using the decorator."""
    response = brt.invoke_agent(
        agentId=os.getenv("BEDROCK_AGENT_ID"),
        agentAliasId=os.getenv("BEDROCK_AGENT_ALIAS_ID"),
        inputText=question,
        enableTrace=True,
        sessionId=session_id,
        endSession=False,
    )
    return response.get("completion", [])

# Setup OpenTelemetry tracing
resource = Resource(attributes={
    SERVICE_NAME: "bedrock-agent-trace-testing-application"
})
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# AWS Bedrock Agent client setup
bs = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION")
)
brt = bs.client("bedrock-agent-runtime")

# Execute agent interaction
session_id = generate_session_id()
question = "Tell me about Oracle integration not exceeding 100 words."
agent_response = invoke_bedrock_agent(brt, question, session_id)
```

## License

`bedrock_tracing` is licensed under the MIT License.
