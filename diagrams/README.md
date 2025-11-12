# Strix Sequence Diagrams

This directory contains PlantUML sequence diagrams documenting the key flows and interactions in the Strix codebase.

## Diagrams

### 1. CLI Startup and Agent Initialization (`01_cli_startup_sequence.puml`)
Shows the complete flow from CLI command execution through agent initialization and sandbox creation.

**Key flows:**
- Environment validation
- Docker image pulling
- CLI app initialization
- Agent creation
- Sandbox setup

### 2. Agent Execution Loop (`02_agent_execution_loop.puml`)
Documents the main agent execution loop, including:
- Message checking
- LLM generation
- Tool execution
- State management
- Error handling

### 3. Sandbox Creation and Tool Execution (`03_sandbox_tool_execution.puml`)
Details how sandboxes are created and how tools are executed within them:
- Docker container creation
- Tool server initialization
- Tool execution routing (sandbox vs local)
- Result handling

### 4. Multi-Agent Creation and Delegation (`04_multi_agent_delegation.puml`)
Shows how agents create sub-agents and delegate tasks:
- Agent creation request
- State inheritance
- Thread-based execution
- Completion reporting

### 5. Inter-Agent Communication (`05_inter_agent_communication.puml`)
Documents the message passing system between agents:
- Message sending
- Message queue management
- Message receiving and processing
- User message handling

### 6. LLM Request Flow (`06_llm_request_flow.puml`)
Details the LLM request lifecycle:
- Request preparation
- Memory compression
- Cache preparation
- API request/response
- Error handling

### 7. CLI UI Updates (`07_cli_ui_updates.puml`)
Shows how the CLI UI stays synchronized with agent execution:
- UI update loop
- Agent tree updates
- Chat view updates
- User interactions

## Viewing the Diagrams

### Pre-generated Images

All diagrams have been pre-generated and are available in both PNG and SVG formats:
- **PNG files** - Good for quick viewing and embedding
- **SVG files** - Vector format, perfect for zooming and high-quality viewing

Simply open any `.png` or `.svg` file in Cursor or any image viewer to view the diagrams.

### Regenerating Diagrams

If you modify the `.puml` files, you can regenerate the images:

1. **Install PlantUML** (if not already installed):
   ```bash
   # Using Homebrew (macOS)
   brew install plantuml
   
   # Using npm
   npm install -g node-plantuml
   
   # Or download from http://plantuml.com/download
   ```

2. **Generate images:**
   ```bash
   cd diagrams
   
   # Generate PNG
   plantuml -tpng *.puml
   
   # Generate SVG
   plantuml -tsvg *.puml
   
   # Generate both
   plantuml -tpng -tsvg *.puml
   ```

### Using Online Tools

1. **PlantUML Online Server:**
   - Copy the contents of any `.puml` file
   - Paste into http://www.plantuml.com/plantuml/uml/
   - View the rendered diagram

2. **VS Code Extension:**
   - Install "PlantUML" extension
   - Open any `.puml` file
   - Use "PlantUML: Preview Current Diagram" command

### Using Mermaid (Alternative)

If you prefer Mermaid format, you can convert these diagrams. The codebase already generates Mermaid diagrams for agent graphs (see `AGENT_GRAPH.md`).

## Diagram Conventions

- **Activation boxes** show when components are active
- **Alt blocks** show conditional flows
- **Loop blocks** show iterative processes
- **Notes** provide additional context
- **Participant colors** are used to distinguish component types

## Related Documentation

- [AGENT_GRAPH.md](../AGENT_GRAPH.md) - Agent graph persistence and visualization
- [README.md](../README.md) - Project overview
- [strix_in_depth_details.md](../strix_in_depth_details.md) - Detailed architecture documentation

## Contributing

When adding new features or modifying existing flows:

1. Update the relevant sequence diagram(s)
2. Add new diagrams for new major flows
3. Keep diagrams focused on a single flow or interaction
4. Use consistent naming conventions
5. Include error handling paths where relevant

