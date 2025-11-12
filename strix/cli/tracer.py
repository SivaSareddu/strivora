import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4


logger = logging.getLogger(__name__)

_global_tracer: Optional["Tracer"] = None


def get_global_tracer() -> Optional["Tracer"]:
    return _global_tracer


def set_global_tracer(tracer: "Tracer") -> None:
    global _global_tracer  # noqa: PLW0603
    _global_tracer = tracer


class Tracer:
    def __init__(self, run_name: str | None = None):
        self.run_name = run_name
        self.run_id = run_name or f"run-{uuid4().hex[:8]}"
        self.start_time = datetime.now(UTC).isoformat()
        self.end_time: str | None = None

        self.agents: dict[str, dict[str, Any]] = {}
        self.tool_executions: dict[int, dict[str, Any]] = {}
        self.chat_messages: list[dict[str, Any]] = []

        self.vulnerability_reports: list[dict[str, Any]] = []
        self.final_scan_result: str | None = None

        self.scan_results: dict[str, Any] | None = None
        self.scan_config: dict[str, Any] | None = None
        self.run_metadata: dict[str, Any] = {
            "run_id": self.run_id,
            "run_name": self.run_name,
            "start_time": self.start_time,
            "end_time": None,
            "target": None,
            "scan_type": None,
            "status": "running",
        }
        self._run_dir: Path | None = None
        self._next_execution_id = 1
        self._next_message_id = 1

    def set_run_name(self, run_name: str) -> None:
        self.run_name = run_name
        self.run_id = run_name

    def get_run_dir(self) -> Path:
        if self._run_dir is None:
            runs_dir = Path.cwd() / "agent_runs"
            runs_dir.mkdir(exist_ok=True)

            run_dir_name = self.run_name if self.run_name else self.run_id
            self._run_dir = runs_dir / run_dir_name
            self._run_dir.mkdir(exist_ok=True)

        return self._run_dir

    def add_vulnerability_report(
        self,
        title: str,
        content: str,
        severity: str,
    ) -> str:
        report_id = f"vuln-{len(self.vulnerability_reports) + 1:04d}"

        report = {
            "id": report_id,
            "title": title.strip(),
            "content": content.strip(),
            "severity": severity.lower().strip(),
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

        self.vulnerability_reports.append(report)
        logger.info(f"Added vulnerability report: {report_id} - {title}")
        return report_id

    def set_final_scan_result(
        self,
        content: str,
        success: bool = True,
    ) -> None:
        self.final_scan_result = content.strip()

        self.scan_results = {
            "scan_completed": True,
            "content": content,
            "success": success,
        }

        logger.info(f"Set final scan result: success={success}")

    def log_agent_creation(
        self, agent_id: str, name: str, task: str, parent_id: str | None = None
    ) -> None:
        agent_data: dict[str, Any] = {
            "id": agent_id,
            "name": name,
            "task": task,
            "status": "running",
            "parent_id": parent_id,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "tool_executions": [],
        }

        self.agents[agent_id] = agent_data

    def log_chat_message(
        self,
        content: str,
        role: str,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        message_id = self._next_message_id
        self._next_message_id += 1

        message_data = {
            "message_id": message_id,
            "content": content,
            "role": role,
            "agent_id": agent_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
        }

        self.chat_messages.append(message_data)
        return message_id

    def log_tool_execution_start(self, agent_id: str, tool_name: str, args: dict[str, Any]) -> int:
        execution_id = self._next_execution_id
        self._next_execution_id += 1

        now = datetime.now(UTC).isoformat()
        execution_data = {
            "execution_id": execution_id,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "args": args,
            "status": "running",
            "result": None,
            "timestamp": now,
            "started_at": now,
            "completed_at": None,
        }

        self.tool_executions[execution_id] = execution_data

        if agent_id in self.agents:
            self.agents[agent_id]["tool_executions"].append(execution_id)

        return execution_id

    def update_tool_execution(
        self, execution_id: int, status: str, result: Any | None = None
    ) -> None:
        if execution_id in self.tool_executions:
            self.tool_executions[execution_id]["status"] = status
            self.tool_executions[execution_id]["result"] = result
            self.tool_executions[execution_id]["completed_at"] = datetime.now(UTC).isoformat()

    def update_agent_status(
        self, agent_id: str, status: str, error_message: str | None = None
    ) -> None:
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = status
            self.agents[agent_id]["updated_at"] = datetime.now(UTC).isoformat()
            if error_message:
                self.agents[agent_id]["error_message"] = error_message

    def set_scan_config(self, config: dict[str, Any]) -> None:
        self.scan_config = config
        self.run_metadata.update(
            {
                "target": config.get("target", {}),
                "scan_type": config.get("scan_type", "general"),
                "user_instructions": config.get("user_instructions", ""),
                "max_iterations": config.get("max_iterations", 200),
            }
        )

    def save_run_data(self) -> None:
        try:
            run_dir = self.get_run_dir()
            self.end_time = datetime.now(UTC).isoformat()

            if self.final_scan_result:
                scan_report_file = run_dir / "scan_report.md"
                with scan_report_file.open("w", encoding="utf-8") as f:
                    f.write("# Security Scan Report\n\n")
                    f.write(
                        f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                    )
                    f.write(f"{self.final_scan_result}\n")
                logger.info(f"Saved final scan report to: {scan_report_file}")

            if self.vulnerability_reports:
                vuln_dir = run_dir / "vulnerabilities"
                vuln_dir.mkdir(exist_ok=True)

                severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
                sorted_reports = sorted(
                    self.vulnerability_reports,
                    key=lambda x: (severity_order.get(x["severity"], 5), x["timestamp"]),
                )

                for report in sorted_reports:
                    vuln_file = vuln_dir / f"{report['id']}.md"
                    with vuln_file.open("w", encoding="utf-8") as f:
                        f.write(f"# {report['title']}\n\n")
                        f.write(f"**ID:** {report['id']}\n")
                        f.write(f"**Severity:** {report['severity'].upper()}\n")
                        f.write(f"**Found:** {report['timestamp']}\n\n")
                        f.write("## Description\n\n")
                        f.write(f"{report['content']}\n")

                vuln_csv_file = run_dir / "vulnerabilities.csv"
                with vuln_csv_file.open("w", encoding="utf-8", newline="") as f:
                    import csv

                    fieldnames = ["id", "title", "severity", "timestamp", "file"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for report in sorted_reports:
                        writer.writerow(
                            {
                                "id": report["id"],
                                "title": report["title"],
                                "severity": report["severity"].upper(),
                                "timestamp": report["timestamp"],
                                "file": f"vulnerabilities/{report['id']}.md",
                            }
                        )

                logger.info(
                    f"Saved {len(self.vulnerability_reports)} vulnerability reports to: {vuln_dir}"
                )
                logger.info(f"Saved vulnerability index to: {vuln_csv_file}")

            # Save agent graph in multiple formats
            self._save_agent_graph(run_dir)

            logger.info(f"📊 Essential scan data saved to: {run_dir}")

        except (OSError, RuntimeError):
            logger.exception("Failed to save scan data")

    def _calculate_duration(self) -> float:
        try:
            start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
            if self.end_time:
                end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
                return (end - start).total_seconds()
        except (ValueError, TypeError):
            pass
        return 0.0

    def get_agent_tools(self, agent_id: str) -> list[dict[str, Any]]:
        return [
            exec_data
            for exec_data in self.tool_executions.values()
            if exec_data.get("agent_id") == agent_id
        ]

    def get_real_tool_count(self) -> int:
        return sum(
            1
            for exec_data in self.tool_executions.values()
            if exec_data.get("tool_name") not in ["scan_start_info", "subagent_start_info"]
        )

    def get_total_llm_stats(self) -> dict[str, Any]:
        from strix.tools.agents_graph.agents_graph_actions import _agent_instances

        total_stats = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cached_tokens": 0,
            "cache_creation_tokens": 0,
            "cost": 0.0,
            "requests": 0,
            "failed_requests": 0,
        }

        for agent_instance in _agent_instances.values():
            if hasattr(agent_instance, "llm") and hasattr(agent_instance.llm, "_total_stats"):
                agent_stats = agent_instance.llm._total_stats
                total_stats["input_tokens"] += agent_stats.input_tokens
                total_stats["output_tokens"] += agent_stats.output_tokens
                total_stats["cached_tokens"] += agent_stats.cached_tokens
                total_stats["cache_creation_tokens"] += agent_stats.cache_creation_tokens
                total_stats["cost"] += agent_stats.cost
                total_stats["requests"] += agent_stats.requests
                total_stats["failed_requests"] += agent_stats.failed_requests

        total_stats["cost"] = round(total_stats["cost"], 4)

        return {
            "total": total_stats,
            "total_tokens": total_stats["input_tokens"] + total_stats["output_tokens"],
        }

    def _generate_mermaid_graph(self, agent_graph: dict[str, Any]) -> str:
        """Generate a Mermaid diagram representation of the agent graph."""
        lines = ["graph TD"]
        
        # Status styling
        lines.append("    classDef running fill:#22c55e,stroke:#16a34a,color:#000")
        lines.append("    classDef waiting fill:#fbbf24,stroke:#f59e0b,color:#000")
        lines.append("    classDef completed fill:#10b981,stroke:#059669,color:#000")
        lines.append("    classDef failed fill:#ef4444,stroke:#dc2626,color:#fff")
        lines.append("    classDef stopped fill:#6b7280,stroke:#4b5563,color:#fff")
        lines.append("")
        
        # Create nodes
        nodes = agent_graph.get("nodes", {})
        edges = agent_graph.get("edges", [])
        
        if not nodes:
            lines.append("    NoAgents[No agents in graph]")
            return "\n".join(lines)
        
        # Add all nodes with labels
        for agent_id, node in nodes.items():
            name = node.get("name", "Unknown")
            status = node.get("status", "unknown")
            # Sanitize node name for Mermaid
            safe_id = agent_id.replace("-", "_")
            label = f"{name}\\n{status}"
            lines.append(f'    {safe_id}["{label}"]')
            
            # Apply styling based on status
            if status == "running":
                lines.append(f"    class {safe_id} running")
            elif status == "waiting":
                lines.append(f"    class {safe_id} waiting")
            elif status == "completed":
                lines.append(f"    class {safe_id} completed")
            elif status in ["failed", "error"]:
                lines.append(f"    class {safe_id} failed")
            elif status == "stopped":
                lines.append(f"    class {safe_id} stopped")
        
        lines.append("")
        
        # Add delegation edges
        delegation_edges = [e for e in edges if e.get("type") == "delegation"]
        for edge in delegation_edges:
            from_id = edge.get("from", "").replace("-", "_")
            to_id = edge.get("to", "").replace("-", "_")
            if from_id and to_id:
                lines.append(f"    {from_id} --> {to_id}")
        
        # Add message edges (with different style)
        message_edges = [e for e in edges if e.get("type") == "message"]
        if message_edges:
            lines.append("")
            lines.append("    %% Inter-agent messages")
            for edge in message_edges:
                from_id = edge.get("from", "").replace("-", "_")
                to_id = edge.get("to", "").replace("-", "_")
                if from_id and to_id and from_id != "user":
                    msg_type = edge.get("message_type", "msg")
                    lines.append(f"    {from_id} -.{msg_type}.-> {to_id}")
        
        return "\n".join(lines)

    def _generate_text_graph(self, agent_graph: dict[str, Any]) -> str:
        """Generate a human-readable text representation of the agent graph."""
        lines = ["# Agent Graph Structure", ""]
        
        nodes = agent_graph.get("nodes", {})
        edges = agent_graph.get("edges", [])
        
        if not nodes:
            lines.append("No agents in the graph.")
            return "\n".join(lines)
        
        # Find root agent(s)
        root_agents = [
            agent_id for agent_id, node in nodes.items()
            if node.get("parent_id") is None
        ]
        
        if not root_agents and nodes:
            root_agents = [next(iter(nodes.keys()))]
        
        def build_tree(agent_id: str, depth: int = 0) -> None:
            if agent_id not in nodes:
                return
                
            node = nodes[agent_id]
            indent = "  " * depth
            prefix = "└─ " if depth > 0 else ""
            
            name = node.get("name", "Unknown")
            status = node.get("status", "unknown")
            task = node.get("task", "No task")
            
            # Status emoji
            status_emoji = {
                "running": "🟢",
                "waiting": "🟡",
                "completed": "✅",
                "failed": "❌",
                "stopped": "⏹️",
                "error": "🔴",
            }.get(status, "⚪")
            
            lines.append(f"{indent}{prefix}{status_emoji} **{name}** ({agent_id})")
            lines.append(f"{indent}   Status: {status}")
            lines.append(f"{indent}   Task: {task[:100]}{'...' if len(task) > 100 else ''}")
            
            if node.get("finished_at"):
                lines.append(f"{indent}   Completed: {node['finished_at']}")
            
            lines.append("")
            
            # Find children
            children = [
                edge["to"] for edge in edges
                if edge.get("from") == agent_id and edge.get("type") == "delegation"
            ]
            
            for child_id in children:
                build_tree(child_id, depth + 1)
        
        # Build tree for each root
        for root_id in root_agents:
            build_tree(root_id)
        
        # Add summary statistics
        lines.append("---")
        lines.append("")
        lines.append("## Summary Statistics")
        lines.append("")
        lines.append(f"- **Total Agents**: {len(nodes)}")
        
        status_counts = {}
        for node in nodes.values():
            status = node.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            lines.append(f"- **{status.capitalize()}**: {count}")
        
        lines.append(f"- **Total Edges**: {len(edges)}")
        delegation_count = sum(1 for e in edges if e.get("type") == "delegation")
        message_count = sum(1 for e in edges if e.get("type") == "message")
        lines.append(f"  - Delegation: {delegation_count}")
        lines.append(f"  - Messages: {message_count}")
        
        return "\n".join(lines)

    def _save_agent_graph(self, run_dir: Path) -> None:
        """Save the agent graph in multiple formats."""
        try:
            from strix.tools.agents_graph.agents_graph_actions import _agent_graph
            
            if not _agent_graph.get("nodes"):
                logger.info("No agent graph data to save (no agents were created)")
                return
            
            # 1. Save raw JSON
            graph_json_file = run_dir / "agent_graph.json"
            with graph_json_file.open("w", encoding="utf-8") as f:
                json.dump(_agent_graph, f, indent=2, default=str)
            logger.info(f"Saved agent graph JSON to: {graph_json_file}")
            
            # 2. Save Mermaid diagram
            mermaid_content = self._generate_mermaid_graph(_agent_graph)
            mermaid_file = run_dir / "agent_graph.mmd"
            with mermaid_file.open("w", encoding="utf-8") as f:
                f.write(mermaid_content)
            logger.info(f"Saved agent graph Mermaid diagram to: {mermaid_file}")
            
            # 3. Save Markdown with embedded Mermaid
            markdown_file = run_dir / "agent_graph.md"
            with markdown_file.open("w", encoding="utf-8") as f:
                f.write("# Agent Execution Graph\n\n")
                f.write(f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
                f.write("## Visual Diagram\n\n")
                f.write("```mermaid\n")
                f.write(mermaid_content)
                f.write("\n```\n\n")
                f.write(self._generate_text_graph(_agent_graph))
            logger.info(f"Saved agent graph markdown to: {markdown_file}")
            
            # 4. Save detailed node information
            nodes_file = run_dir / "agent_nodes.json"
            nodes_data = {
                "generated_at": datetime.now(UTC).isoformat(),
                "total_agents": len(_agent_graph.get("nodes", {})),
                "agents": _agent_graph.get("nodes", {}),
            }
            with nodes_file.open("w", encoding="utf-8") as f:
                json.dump(nodes_data, f, indent=2, default=str)
            logger.info(f"Saved detailed agent nodes to: {nodes_file}")
            
        except ImportError:
            logger.warning("Could not import agent graph (agents_graph module not available)")
        except (OSError, RuntimeError):
            logger.exception("Failed to save agent graph")

    def cleanup(self) -> None:
        self.save_run_data()
