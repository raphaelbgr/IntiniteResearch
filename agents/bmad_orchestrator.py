"""
BMAD Multi-Agent Orchestrator Architecture Proposal

This module integrates BMAD agents with the Agno framework for collaborative
multi-agent research and problem-solving sessions.

ARCHITECTURE OVERVIEW:
======================

┌─────────────────────────────────────────────────────────────────────────┐
│                        BMAD RESEARCH SESSION                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    ORCHESTRATOR AGENT                              │ │
│  │  - Manages user conversation                                       │ │
│  │  - Proposes options to achieve user objective                      │ │
│  │  - Decides which specialist agents to consult                      │ │
│  │  - Synthesizes agent outputs into conclusions                      │ │
│  │  - Has its own Agno session + tool access                          │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                          │
│              ┌───────────────┼───────────────┐                          │
│              │               │               │                          │
│              ▼               ▼               ▼                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │   BMM AGENTS    │ │   CIS AGENTS    │ │  BMGD AGENTS    │           │
│  ├─────────────────┤ ├─────────────────┤ ├─────────────────┤           │
│  │ 📊 Analyst      │ │ 🧠 Brainstorm   │ │ 🏗️ Game Arch   │           │
│  │ 🏛️ Architect    │ │ 💡 Problem Solv │ │ 🎮 Game Design  │           │
│  │ 💻 Developer    │ │ 🎯 Design Think │ │ 👨‍💻 Game Dev    │           │
│  │ 📋 PM           │ │ 🚀 Innovation   │ │ 📋 Game SM      │           │
│  │ 🏃 Scrum Master │ │ 🎤 Presentation │ │                 │           │
│  │ ✍️ Tech Writer  │ │ 📖 Storyteller  │ │                 │           │
│  │ 🎨 UX Designer  │ │                 │ │                 │           │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘           │
│         │                   │                   │                       │
│         └───────────────────┴───────────────────┘                       │
│                              │                                          │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    SHARED KNOWLEDGE BASE                           │ │
│  │  - Vector Store (RAG)                                              │ │
│  │  - Source KB (URLs/References)                                     │ │
│  │  - Agent Conclusions History                                       │ │
│  │  - User Session Context                                            │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                          │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    OUTPUT: /agent-conclusions                      │ │
│  │  - conclusion-YYYYMMDD-HHMMSS.md                                   │ │
│  │  - Synthesized insights from all agents                            │ │
│  │  - Action items and recommendations                                │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘


KEY COMPONENTS:
===============

1. BMadAgentLoader
   - Loads YAML agent definitions from BMAD-METHOD/src
   - Parses persona, menu, and metadata
   - Creates Agno Agent instances with proper instructions

2. BMadOrchestrator
   - Main coordinator agent with its own Agno session
   - Manages user conversation
   - Decides which agents to involve
   - Routes questions to appropriate specialists
   - Synthesizes multi-agent outputs

3. AgentSession
   - Each BMAD agent gets its own Agno session
   - Maintains conversation history per agent
   - Shares knowledge base access
   - Has tool access (web search, etc.)

4. AgentTeam
   - Registry of all loaded agents
   - Agent selection logic based on expertise
   - Parallel agent consultation support
   - Inter-agent communication

5. BMadResearchSession
   - User-facing session manager
   - Conversation loop with options
   - Progress tracking
   - Conclusion generation


WORKFLOW:
=========

1. User selects "BMAD Research" (Option 1)
2. System loads all BMAD agents from YAML
3. Orchestrator greets user, asks about objective
4. Based on objective:
   a. Proposes relevant agents to involve
   b. Offers options (quick analysis, deep dive, specific expert)
5. Orchestrator consults specialists:
   - "Hey Analyst, what's your take on this market?"
   - "Architect, how would you structure this?"
   - "Brainstorm Coach, help us generate options"
6. Each agent responds with its expertise
7. Orchestrator synthesizes and presents options to user
8. Loop continues until user is satisfied
9. Generate conclusion document to /agent-conclusions


AGENT-TO-AGENT COMMUNICATION:
=============================

Option A: Sequential Consultation
- Orchestrator asks one agent at a time
- Builds context from previous responses
- More controlled, easier to follow

Option B: Party Mode (Group Chat)
- Multiple agents in same context
- Agents can reference each other
- More dynamic, can lead to emergent insights

Option C: Hybrid (Recommended)
- Start with targeted consultations
- Bring multiple agents together for synthesis
- User can request specific agents at any time


TOOLS AVAILABLE TO AGENTS:
==========================

1. parallel_search - Web search with DDG
2. consult_agent - Ask another BMAD agent
3. add_to_kb - Save findings to knowledge base
4. search_kb - Query existing knowledge
5. create_task - Define actionable items
6. generate_document - Create structured output


USER INTERACTION FLOW:
======================

```
======================================================================
  BMAD MULTI-AGENT RESEARCH
======================================================================

🧙 BMad Orchestrator: Hello! I'm your research orchestrator.
   I coordinate a team of expert agents to help you achieve your goals.

   Tell me: What would you like to accomplish today?

You: I want to create a mobile app for tracking fitness goals

🧙 BMad Orchestrator: Great objective! Let me consult the team.

   Based on your goal, I recommend involving:

   [1] 📊 Mary (Analyst) - Market research & requirements
   [2] 🏛️ Alex (Architect) - Technical architecture
   [3] 🎨 Uma (UX Designer) - User experience design
   [4] 🧠 Carson (Brainstorm Coach) - Feature ideation

   Options:
   [A] Quick Analysis - All agents give brief input (5 min)
   [B] Deep Dive - Detailed exploration with each agent
   [C] Select specific agents to consult
   [D] Party Mode - Group discussion with all agents

   Your choice:
```


IMPLEMENTATION PHASES:
======================

Phase 1: Core Infrastructure
- BMadAgentLoader (parse YAML)
- Single agent Agno integration
- Basic orchestrator

Phase 2: Multi-Agent Communication
- Agent registry
- Inter-agent messaging
- Shared context

Phase 3: User Experience
- Interactive menu
- Conversation management
- Progress tracking

Phase 4: Output Generation
- Conclusion compilation
- Action item extraction
- Document formatting
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import yaml
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team  # Agno Teams for multi-agent collaboration
from agno.db.sqlite import SqliteDb

from tools.parallel_ddg import ParallelDuckDuckGoSearch
from utils.logger import get_logger
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

logger = get_logger()
console = Console()


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BMadAgentConfig:
    """Configuration parsed from BMAD agent YAML."""
    id: str
    name: str
    title: str
    icon: str
    module: str
    role: str
    identity: str
    communication_style: str
    principles: str
    menu_items: List[Dict[str, str]] = field(default_factory=list)
    yaml_path: str = ""


@dataclass
class AgentMessage:
    """Message in agent conversation."""
    agent_name: str
    content: str
    timestamp: str = ""


# =============================================================================
# BMAD AGENT LOADER
# =============================================================================

class BMadAgentLoader:
    """Loads and parses BMAD agent definitions from YAML files."""

    def __init__(self, bmad_path: str = "C:/Users/rbgnr/git/BMAD-METHOD/src"):
        """Initialize loader.

        Args:
            bmad_path: Path to BMAD-METHOD/src directory
        """
        self.bmad_path = Path(bmad_path)
        self.agents: Dict[str, BMadAgentConfig] = {}

    def discover_agents(self) -> List[Path]:
        """Find all agent YAML files.

        Returns:
            List of paths to agent YAML files
        """
        agent_files = []

        # Search in modules
        modules_path = self.bmad_path / "modules"
        if modules_path.exists():
            for yaml_file in modules_path.glob("**/agents/*.agent.yaml"):
                # Skip reference/example agents
                if "reference" not in str(yaml_file):
                    agent_files.append(yaml_file)

        # Search in core
        core_path = self.bmad_path / "core" / "agents"
        if core_path.exists():
            for yaml_file in core_path.glob("*.agent.yaml"):
                agent_files.append(yaml_file)

        logger.info(f"Discovered {len(agent_files)} BMAD agent definitions")
        return agent_files

    def load_agent(self, yaml_path: Path) -> Optional[BMadAgentConfig]:
        """Load single agent from YAML.

        Args:
            yaml_path: Path to agent YAML file

        Returns:
            BMadAgentConfig or None if parsing fails
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data or 'agent' not in data:
                return None

            agent_data = data['agent']
            metadata = agent_data.get('metadata', {})
            persona = agent_data.get('persona', {})
            menu = agent_data.get('menu', [])

            config = BMadAgentConfig(
                id=metadata.get('id', ''),
                name=metadata.get('name', 'Unknown'),
                title=metadata.get('title', 'Agent'),
                icon=metadata.get('icon', '🤖'),
                module=metadata.get('module', 'core'),
                role=persona.get('role', ''),
                identity=persona.get('identity', ''),
                communication_style=persona.get('communication_style', ''),
                principles=persona.get('principles', ''),
                menu_items=menu,
                yaml_path=str(yaml_path)
            )

            return config

        except Exception as e:
            logger.warning(f"Failed to load agent from {yaml_path}: {e}")
            return None

    def load_all_agents(self) -> Dict[str, BMadAgentConfig]:
        """Load all discovered agents.

        Returns:
            Dict mapping agent name to config
        """
        agent_files = self.discover_agents()

        for yaml_path in agent_files:
            config = self.load_agent(yaml_path)
            if config:
                # Use lowercase name as key
                key = config.name.lower().replace(" ", "-")
                self.agents[key] = config
                logger.info(f"Loaded agent: {config.icon} {config.name} ({config.title})")

        return self.agents


# =============================================================================
# AGNO AGENT FACTORY
# =============================================================================

class AgnoAgentFactory:
    """Creates Agno agents from BMAD configurations."""

    def __init__(
        self,
        lmstudio_config: Dict[str, Any],
        session_dir: Path
    ):
        """Initialize factory.

        Args:
            lmstudio_config: LMStudio connection config
            session_dir: Directory for agent sessions
        """
        self.lmstudio_config = lmstudio_config
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def create_agent(
        self,
        config: BMadAgentConfig,
        tools: Optional[List] = None
    ) -> Agent:
        """Create Agno agent from BMAD config.

        Args:
            config: BMAD agent configuration
            tools: Optional list of tools for the agent

        Returns:
            Configured Agno Agent
        """
        # Create model
        model = OpenAIChat(
            id=self.lmstudio_config.get('model', 'local-model'),
            api_key=self.lmstudio_config.get('api_key', 'lm-studio'),
            base_url=self.lmstudio_config.get('base_url', 'http://localhost:1234/v1'),
            temperature=self.lmstudio_config.get('temperature', 0.7),
            max_tokens=self.lmstudio_config.get('max_tokens', 4096)
        )

        # Create session storage
        db_path = self.session_dir / f"{config.name.lower()}_session.db"
        storage = SqliteDb(
            db_url=f"sqlite:///{db_path}",
            session_table=f"{config.name.lower()}_sessions"
        )

        # Build instructions from BMAD persona
        instructions = self._build_instructions(config)

        # Default tools if not provided
        if tools is None:
            tools = [
                ParallelDuckDuckGoSearch(
                    enable_search=True,
                    enable_news=True,
                    fixed_max_results=5,
                    timeout=10
                )
            ]

        # Create agent
        agent = Agent(
            name=config.name,
            model=model,
            db=storage,
            tools=tools,
            description=f"{config.icon} {config.title}: {config.identity[:100]}...",
            instructions=instructions,
            markdown=True,
            debug_mode=False
        )

        logger.info(f"Created Agno agent: {config.icon} {config.name}")
        return agent

    def _build_instructions(self, config: BMadAgentConfig) -> str:
        """Build agent instructions from BMAD config.

        Args:
            config: BMAD agent configuration

        Returns:
            Formatted instructions string
        """
        return dedent(f"""\
            You are {config.name}, {config.title}.

            **Your Role:** {config.role}

            **Your Identity:** {config.identity}

            **Communication Style:** {config.communication_style}

            **Core Principles:** {config.principles}

            **Important Guidelines:**
            - Stay in character as {config.name}
            - Provide expert insights from your specialized perspective
            - Be collaborative when working with other agents
            - Focus on actionable, practical advice
            - Use your icon {config.icon} when introducing yourself

            **Available Tools:**
            - Web search for research and fact-finding
            - You can ask to consult other expert agents if needed

            Remember: You are part of a collaborative team working to help the user
            achieve their objectives. Contribute your unique expertise while being
            open to insights from other specialists.
        """)


# =============================================================================
# BMAD TEAM FACTORY (Agno Teams Integration)
# =============================================================================

class BMadTeamFactory:
    """Creates Agno Team from BMAD agent configurations.

    Key Design for single provider (LMStudio):
    - Single model set on Team - all member agents inherit it
    - Team coordinates sequential API calls (1 at a time)
    - Perfect for LMStudio with 1 API call at a time
    """

    def __init__(self, lmstudio_config: Dict[str, Any], session_dir: Path):
        self.lmstudio_config = lmstudio_config
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _create_model(self) -> OpenAIChat:
        """Create the shared LMStudio model for the Team."""
        return OpenAIChat(
            id=self.lmstudio_config.get("model", "local-model"),
            api_key=self.lmstudio_config.get("api_key", "lm-studio"),
            base_url=self.lmstudio_config.get("base_url", "http://localhost:1234/v1"),
            temperature=self.lmstudio_config.get("temperature", 0.7),
            max_tokens=self.lmstudio_config.get("max_tokens", 4096)
        )

    def create_agent_for_team(self, config: BMadAgentConfig) -> Agent:
        """Create agent WITHOUT model - it inherits from Team!"""
        instructions = f"You are {config.name}, {config.title}. Role: {config.role}"
        return Agent(
            name=config.name,
            role=f"{config.icon} {config.title}: {config.role[:100]}",
            instructions=instructions,
            tools=[ParallelDuckDuckGoSearch(enable_search=True, enable_news=True, fixed_max_results=5, timeout=10)],
            markdown=True,
            add_name_to_context=True,
        )

    def create_team(self, agent_configs: Dict[str, BMadAgentConfig], team_name: str = "BMAD Expert Team") -> Team:
        """Create Agno Team with all BMAD agents sharing single model."""
        members = [self.create_agent_for_team(c) for c in agent_configs.values()]
        roster_lines = [f"- {c.icon} {c.name} ({c.title}): {c.role[:80]}" for c in agent_configs.values()]
        roster = chr(10).join(roster_lines)

        team_instructions = f"""You are the BMAD Expert Team Orchestrator.

Your Team of Experts:
{roster}

Your Responsibilities:
1. Understand the user objective clearly
2. Decide which experts to consult based on the question
3. Ask focused questions to each expert
4. Synthesize insights from multiple experts into coherent advice
5. Help the user reach actionable conclusions
"""

        db_path = self.session_dir / "bmad_team_session.db"
        storage = SqliteDb(db_url=f"sqlite:///{db_path}", session_table="bmad_team_sessions")

        team = Team(
            name=team_name,
            model=self._create_model(),
            members=members,
            instructions=team_instructions,
            db=storage,
            markdown=True,
            show_members_responses=True,
            add_datetime_to_context=True,
        )
        return team


# =============================================================================
# BMAD ORCHESTRATOR (Main Coordinator)
# =============================================================================

class BMadOrchestrator:
    """Main orchestrator that coordinates BMAD agents for user objectives.

    All storage is scoped to the research_id for proper isolation.
    """

    def __init__(
        self,
        research_id: str,
        lmstudio_config: Dict[str, Any],
        session_dir: Path,
        source_kb=None,
        vector_store=None,
        bmad_path: str = "C:/Users/rbgnr/git/BMAD-METHOD/src"
    ):
        """Initialize orchestrator.

        Args:
            research_id: Unique research session ID (scopes all storage)
            lmstudio_config: LMStudio connection config
            session_dir: Directory for agent sessions (research-scoped)
            source_kb: Optional shared SourceKnowledgeBase
            vector_store: Optional shared VectorStore
            bmad_path: Path to BMAD-METHOD/src
        """
        self.research_id = research_id
        self.lmstudio_config = lmstudio_config
        self.session_dir = session_dir
        self.bmad_path = bmad_path

        # Shared storage (can be used by all agents)
        self.source_kb = source_kb
        self.vector_store = vector_store

        # Load BMAD agent configs
        self.loader = BMadAgentLoader(bmad_path)
        self.agent_configs = self.loader.load_all_agents()

        # Create agent factory with research-scoped storage
        self.factory = AgnoAgentFactory(lmstudio_config, session_dir)

        # Agent instances (created on demand, stored with research_id scope)
        self.agents: Dict[str, Agent] = {}

        # Conversation history (persisted per research)
        self.conversation_history: List[AgentMessage] = []

        # Create orchestrator agent
        self.orchestrator = self._create_orchestrator()

    def _create_orchestrator(self) -> Agent:
        """Create the main orchestrator agent."""
        model = OpenAIChat(
            id=self.lmstudio_config.get('model', 'local-model'),
            api_key=self.lmstudio_config.get('api_key', 'lm-studio'),
            base_url=self.lmstudio_config.get('base_url', 'http://localhost:1234/v1'),
            temperature=0.7,
            max_tokens=4096
        )

        db_path = self.session_dir / "orchestrator_session.db"
        storage = SqliteDb(
            db_url=f"sqlite:///{db_path}",
            session_table="orchestrator_sessions"
        )

        # Build agent roster for instructions
        agent_roster = self._build_agent_roster()

        instructions = dedent(f"""\
            You are the BMad Orchestrator 🧙, a master facilitator coordinating a team
            of expert agents to help users achieve their objectives.

            **Your Team of Experts:**
            {agent_roster}

            **Your Responsibilities:**
            1. Understand the user's objective clearly
            2. Propose which experts would be most helpful
            3. Offer options for how to proceed (quick analysis, deep dive, etc.)
            4. Coordinate consultations with specialist agents
            5. Synthesize insights from multiple experts
            6. Help the user reach actionable conclusions

            **Communication Style:**
            - Friendly and professional
            - Present clear options with numbers
            - Summarize expert inputs concisely
            - Guide the user through the process

            **When consulting experts:**
            - Frame questions that play to each expert's strengths
            - Provide context from previous discussions
            - Look for complementary perspectives

            **Output Format:**
            - Use clear headers and bullet points
            - Present options as numbered lists
            - Highlight key insights with emphasis

            Remember: Your goal is to orchestrate a productive multi-expert session
            that delivers real value to the user.
        """)

        return Agent(
            name="BMad Orchestrator",
            model=model,
            db=storage,
            tools=[
                ParallelDuckDuckGoSearch(
                    enable_search=True,
                    enable_news=True,
                    fixed_max_results=5,
                    timeout=10
                )
            ],
            description="🧙 Master Orchestrator coordinating expert agents",
            instructions=instructions,
            markdown=True
        )

    def _build_agent_roster(self) -> str:
        """Build formatted list of available agents."""
        lines = []
        for key, config in self.agent_configs.items():
            lines.append(f"- {config.icon} **{config.name}** ({config.title}): {config.role}")
        return "\n".join(lines)

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get or create agent by name.

        Args:
            name: Agent name (case-insensitive)

        Returns:
            Agno Agent instance or None
        """
        key = name.lower().replace(" ", "-")

        # Return cached if exists
        if key in self.agents:
            return self.agents[key]

        # Create if config exists
        if key in self.agent_configs:
            config = self.agent_configs[key]
            agent = self.factory.create_agent(config)
            self.agents[key] = agent
            return agent

        return None

    def list_agents(self) -> List[Tuple[str, str, str]]:
        """List available agents.

        Returns:
            List of (icon, name, title) tuples
        """
        return [
            (config.icon, config.name, config.title)
            for config in self.agent_configs.values()
        ]

    async def consult_agent(
        self,
        agent_name: str,
        question: str,
        context: str = ""
    ) -> str:
        """Consult a specific agent.

        Args:
            agent_name: Name of agent to consult
            question: Question to ask
            context: Optional context from previous discussions

        Returns:
            Agent's response
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return f"Agent '{agent_name}' not found."

        # Build prompt with context
        prompt = question
        if context:
            prompt = f"**Context from previous discussion:**\n{context}\n\n**Question:**\n{question}"

        # Run agent
        response = agent.run(prompt)

        # Extract content
        if hasattr(response, 'content'):
            content = response.content
        elif isinstance(response, dict):
            content = response.get('content', str(response))
        else:
            content = str(response)

        # Record in history
        config = self.agent_configs.get(agent_name.lower().replace(" ", "-"))
        icon = config.icon if config else "🤖"
        self.conversation_history.append(AgentMessage(
            agent_name=f"{icon} {agent_name}",
            content=content
        ))

        return content

    async def orchestrate(self, user_message: str) -> str:
        """Main orchestration - process user message.

        Args:
            user_message: User's input

        Returns:
            Orchestrator's response
        """
        # Build context from history
        context = ""
        if self.conversation_history:
            context = "\n\n".join([
                f"**{msg.agent_name}:** {msg.content[:500]}..."
                for msg in self.conversation_history[-5:]  # Last 5 messages
            ])

        # Build prompt
        prompt = f"{user_message}"
        if context:
            prompt = f"**Recent Discussion:**\n{context}\n\n**User says:**\n{user_message}"

        # Run orchestrator
        response = self.orchestrator.run(prompt)

        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, dict):
            return response.get('content', str(response))
        return str(response)


# =============================================================================
# BMAD OPERATOR (Auto-User)
# =============================================================================

class BMadOperator:
    """Automated operator that simulates user interaction."""

    def __init__(self, lmstudio_config: Dict[str, Any], goal: str):
        self.goal = goal
        self.model = OpenAIChat(
            id=lmstudio_config.get('model', 'local-model'),
            api_key=lmstudio_config.get('api_key', 'lm-studio'),
            base_url=lmstudio_config.get('base_url', 'http://localhost:1234/v1'),
            temperature=0.7,
        )
        self.agent = Agent(
            name="Operator",
            model=self.model,
            instructions=dedent(f"""\
                You are the User/Operator in this AUTOMATED research session.
                Your goal is: {goal}

                **Your Responsibilities:**
                1. Read the messages from the BMAD Team.
                2. Make decisions on how to proceed to achieve your goal.
                3. Provide clear guidance, feedback, or follow-up questions.
                4. If the team asks for a decision (e.g., choose an option), choose the best one for your goal.
                5. When you are satisfied with the results, respond with 'conclude' to generate the final report.
                6. Keep your responses concise and direct.
                7. NEVER ask the user for input - this is fully automated.
                8. Always provide a complete response, never leave it open-ended.
            """),
            markdown=True
        )
        self.turn_count = 0
        self.max_turns = 20  # Safety limit

    def decide(self, context: str) -> str:
        """Decide on the next response based on context."""
        self.turn_count += 1
        
        # Safety check - auto-conclude after max turns
        if self.turn_count >= self.max_turns:
            console.print(f"[bold yellow]Max turns ({self.max_turns}) reached. Auto-concluding...[/bold yellow]")
            return "conclude"
        
        # Prepare prompt for operator
        prompt = dedent(f"""\
            **Conversation Context:**
            {context[-2000:]}  

            **Turn {self.turn_count}/{self.max_turns}**
            
            Based on the conversation above, what is your next response?
            Remember: You must respond completely and autonomously. Do not ask me (the real user) anything.
            If you have achieved the goal or gotten sufficient information, respond with 'conclude'.
            
            **Your Response:**
        """)
        
        try:
            response = self.agent.run(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Ensure we got a valid response
            if not content or content.strip() == "":
                console.print("[bold red]Operator returned empty response. Auto-concluding...[/bold red]")
                return "conclude"
            
            return content
        except Exception as e:
            console.print(f"[bold red]Error in operator decision: {e}[/bold red]")
            logger.error(f"Operator error: {e}")
            return "conclude"


# =============================================================================
# BMAD RESEARCH SESSION (User-facing)
# =============================================================================

class BMadResearchSession:
    """Interactive BMAD research session with user.

    All storage is scoped to the research_id:
    - generation/{research_id}/bmad-sessions/  - Agent session DBs
    - generation/{research_id}/agent-conclusions/  - Final conclusions
    - generation/{research_id}/kb/  - Shared knowledge base
    - generation/{research_id}/rag/  - Vector store
    """

    def __init__(
        self,
        research_id: str,
        research_dir: Path,
        lmstudio_config: Dict[str, Any],
        source_kb=None,
        vector_store=None
    ):
        """Initialize session.

        Args:
            research_id: Unique session ID (scopes all storage)
            research_dir: Research directory (generation/{research_id}/)
            lmstudio_config: LMStudio config
            source_kb: Optional existing SourceKnowledgeBase
            vector_store: Optional existing VectorStore
        """
        self.research_id = research_id
        self.research_dir = research_dir
        self.lmstudio_config = lmstudio_config

        # Shared storage (reuse from main research if provided)
        self.source_kb = source_kb
        self.vector_store = vector_store

        # Create research-scoped directories
        self.session_dir = research_dir / "bmad-sessions"
        self.conclusions_dir = research_dir / "agent-conclusions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.conclusions_dir.mkdir(parents=True, exist_ok=True)

        # Initialize orchestrator with research-scoped storage
        self.orchestrator = BMadOrchestrator(
            research_id=research_id,
            lmstudio_config=lmstudio_config,
            session_dir=self.session_dir,
            source_kb=source_kb,
            vector_store=vector_store
        )

        # Session state
        self.user_objective: str = ""
        self.conclusions: List[str] = []
        self.agents_consulted: List[str] = []

    def display_welcome(self):
        """Display welcome message and available agents."""
        print("\n" + "=" * 70)
        print("  🧙 BMAD MULTI-AGENT RESEARCH SESSION")
        print("=" * 70)
        print("\nAvailable Expert Agents:\n")

        for icon, name, title in self.orchestrator.list_agents():
            print(f"  {icon} {name} - {title}")

        print("\n" + "-" * 70)
        print("The orchestrator will coordinate these experts to help you.")
        print("Type 'quit' to exit, 'agents' to list agents, 'conclude' to generate conclusion.")
        print("-" * 70)

    async def run_interactive(self):
        """Run interactive session loop."""
        self.display_welcome()

        # Initial greeting from orchestrator
        greeting = await self.orchestrator.orchestrate(
            "Introduce yourself briefly and ask the user about their objective."
        )
        print(f"\n🧙 Orchestrator: {greeting}")

        # Main loop
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'quit':
                    print("\nEnding session...")
                    break

                if user_input.lower() == 'agents':
                    self.display_welcome()
                    continue

                if user_input.lower() == 'conclude':
                    await self.generate_conclusion()
                    continue

                if user_input.lower().startswith('ask '):
                    # Direct agent consultation: "ask Mary about market size"
                    parts = user_input[4:].split(' about ', 1)
                    if len(parts) == 2:
                        agent_name, question = parts
                        response = await self.orchestrator.consult_agent(
                            agent_name.strip(),
                            question.strip()
                        )
                        config = self.orchestrator.agent_configs.get(
                            agent_name.strip().lower().replace(" ", "-")
                        )
                        icon = config.icon if config else "🤖"
                        print(f"\n{icon} {agent_name}: {response}")
                        continue

                # Regular orchestration
                response = await self.orchestrator.orchestrate(user_input)
                print(f"\n🧙 Orchestrator: {response}")

            except KeyboardInterrupt:
                print("\n\nSession interrupted.")
                break

    async def generate_conclusion(self) -> Optional[Path]:
        """Generate conclusion document from session."""
        print("\n" + "=" * 50)
        print("GENERATING CONCLUSION")
        print("=" * 50)

        # Ask orchestrator to synthesize
        synthesis_prompt = dedent("""\
            Based on our entire discussion, please generate a comprehensive conclusion that:

            1. Summarizes the user's objective
            2. Lists key insights from each expert consulted
            3. Provides actionable recommendations
            4. Identifies next steps
            5. Notes any areas needing further exploration

            Format as a well-structured document with clear sections.
        """)

        conclusion = await self.orchestrator.orchestrate(synthesis_prompt)

        # Save to file
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"conclusion-{timestamp}.md"
        filepath = self.conclusions_dir / filename

        # Add header
        header = f"""# BMAD Multi-Agent Research Conclusion

**Session ID:** {self.research_id}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Experts Consulted:** {len(self.orchestrator.agents)}

---

"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + conclusion)

        print(f"\nConclusion saved to: {filepath}")
        return filepath

    async def run_auto_mode(self, goal: str):
        """Run fully automated session with Operator."""
        operator = BMadOperator(self.lmstudio_config, goal)

        console.print(Panel(f"[bold green]Starting Auto Mode[/bold green]\nGoal: {goal}", title="BMAD Auto Mode"))

        # Initial greeting
        greeting = await self.orchestrator.orchestrate(
            "Introduce yourself briefly and ask the user about their objective."
        )
        console.print(Panel(Markdown(greeting), title="Orchestrator", border_style="blue"))

        # Operator's first move
        conversation_log = f"Orchestrator: {greeting}"
        user_input = operator.decide(conversation_log)
        console.print(Panel(Markdown(user_input), title="Operator (Auto-User)", border_style="green"))

        while True:
            try:
                # Check for exit commands
                if user_input.lower() == 'quit':
                    console.print("[bold red]Operator requested to quit.[/bold red]")
                    break

                if user_input.lower() == 'conclude':
                    await self.generate_conclusion()
                    break

                if user_input.lower().startswith('ask '):
                    # Direct agent consultation
                    parts = user_input[4:].split(' about ', 1)
                    if len(parts) == 2:
                        agent_name, question = parts
                        response = await self.orchestrator.consult_agent(
                            agent_name.strip(),
                            question.strip()
                        )
                        console.print(Panel(Markdown(f"{response}"), title=f"{agent_name}", border_style="magenta"))

                        conversation_log += f"\nUser: {user_input}\n{agent_name}: {response}"
                        user_input = operator.decide(conversation_log)
                        console.print(Panel(Markdown(user_input), title="Operator (Auto-User)", border_style="green"))
                        continue

                # Regular orchestration
                response = await self.orchestrator.orchestrate(user_input)
                console.print(Panel(Markdown(response), title="Orchestrator", border_style="blue"))

                conversation_log += f"\nUser: {user_input}\nOrchestrator: {response}"
                user_input = operator.decide(conversation_log)
                console.print(Panel(Markdown(user_input), title="Operator (Auto-User)", border_style="green"))

            except KeyboardInterrupt:
                console.print("[bold red]Session interrupted.[/bold red]")
                break




# =============================================================================
# BMAD TEAMS SESSION (Agno Teams - Recommended)
# =============================================================================

class BMadTeamsSession:
    """Interactive BMAD research session using Agno Teams.

    This is the recommended approach - uses Agno Teams for true multi-agent
    collaboration with a single shared model (LMStudio).

    All storage is scoped to the research_id:
    - generation/{research_id}/bmad-sessions/  - Team session DB
    - generation/{research_id}/agent-conclusions/  - Final conclusions
    """

    def __init__(
        self,
        research_id: str,
        research_dir: Path,
        lmstudio_config: Dict[str, Any],
        source_kb=None,
        vector_store=None,
        bmad_path: str = "C:/Users/rbgnr/git/BMAD-METHOD/src"
    ):
        self.research_id = research_id
        self.research_dir = research_dir
        self.lmstudio_config = lmstudio_config
        self.bmad_path = bmad_path
        self.source_kb = source_kb
        self.vector_store = vector_store

        # Create research-scoped directories
        self.session_dir = research_dir / "bmad-sessions"
        self.conclusions_dir = research_dir / "agent-conclusions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.conclusions_dir.mkdir(parents=True, exist_ok=True)

        # Load BMAD agents
        self.loader = BMadAgentLoader(bmad_path)
        self.agent_configs = self.loader.load_all_agents()

        # Create Team factory and Team
        self.factory = BMadTeamFactory(lmstudio_config, self.session_dir)
        self.team = self.factory.create_team(self.agent_configs)

        self.conversation_history: List[str] = []

    def list_agents(self) -> List[Tuple[str, str, str]]:
        return [(c.icon, c.name, c.title) for c in self.agent_configs.values()]

    def display_welcome(self):
        print(chr(10) + "=" * 70)
        print("  BMAD MULTI-AGENT TEAM SESSION")
        print("  Powered by Agno Teams (sequential API calls)")
        print("=" * 70)
        print(chr(10) + "Available Expert Agents:" + chr(10))
        for icon, name, title in self.list_agents():
            print(f"  {icon} {name} - {title}")
        print(chr(10) + "-" * 70)
        print("Commands: quit to exit, conclude to generate conclusion")
        print("-" * 70)

    def chat_sync(self, user_message: str) -> str:
        """Send message to team and get response (sync)."""
        response = self.team.run(user_message)
        content = response.content if hasattr(response, "content") else str(response)
        self.conversation_history.append(f"User: {user_message}")
        self.conversation_history.append(f"Team: {content[:500]}...")
        return content

    async def chat(self, user_message: str) -> str:
        """Send message to team and get response (async)."""
        response = await self.team.arun(user_message)
        content = response.content if hasattr(response, "content") else str(response)
        self.conversation_history.append(f"User: {user_message}")
        self.conversation_history.append(f"Team: {content[:500]}...")
        return content

    def run_interactive_sync(self):
        """Run interactive session loop (synchronous)."""
        self.display_welcome()
        print(chr(10) + "Team Leader: Hello! I am coordinating expert agents to help you.")
        print("   What would you like to accomplish today?" + chr(10))
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    print(chr(10) + "Ending session...")
                    break
                if user_input.lower() == "agents":
                    self.display_welcome()
                    continue
                if user_input.lower() == "conclude":
                    self.generate_conclusion_sync()
                    continue
                print(chr(10) + "Consulting the team..." + chr(10))
                response = self.chat_sync(user_input)
                print(chr(10) + "Team Response:" + chr(10) + response + chr(10))
            except KeyboardInterrupt:
                print(chr(10) + chr(10) + "Session interrupted.")
                break

    async def run_interactive(self):
        """Run interactive session loop (async)."""
        self.display_welcome()
        print(chr(10) + "Team Leader: Hello! I am coordinating expert agents to help you.")
        print("   What would you like to accomplish today?" + chr(10))
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    print(chr(10) + "Ending session...")
                    break
                if user_input.lower() == "agents":
                    self.display_welcome()
                    continue
                if user_input.lower() == "conclude":
                    await self.generate_conclusion()
                    continue
                print(chr(10) + "Consulting the team..." + chr(10))
                response = await self.chat(user_input)
                print(chr(10) + "Team Response:" + chr(10) + response + chr(10))
            except KeyboardInterrupt:
                print(chr(10) + chr(10) + "Session interrupted.")
                break

    def generate_conclusion_sync(self) -> Optional[Path]:
        return self._save_conclusion(self.chat_sync("Synthesize our discussion into a conclusion with: 1) Summary, 2) Key insights, 3) Recommendations, 4) Next steps."))

    async def generate_conclusion(self) -> Optional[Path]:
        return self._save_conclusion(await self.chat("Synthesize our discussion into a conclusion with: 1) Summary, 2) Key insights, 3) Recommendations, 4) Next steps."))

    def _save_conclusion(self, conclusion: str) -> Optional[Path]:
        from datetime import datetime
        print(chr(10) + "=" * 50)
        print("GENERATING CONCLUSION")
        print("=" * 50)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filepath = self.conclusions_dir / f"conclusion-{timestamp}.md"
        header = f"""# BMAD Multi-Agent Team Conclusion

**Session ID:** {self.research_id}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + conclusion)
        print(chr(10) + f"Conclusion saved to: {filepath}")
        print(chr(10) + f"Conclusion saved to: {filepath}")
        return filepath

    def run_auto_mode(self, goal: str):
        """Run fully automated session with Operator.
        
        This mode runs completely autonomously - NO user input required.
        The BMadOperator (AI agent) makes all decisions automatically.
        """
        console.print("\n")
        console.print(Panel(
            f"[bold green]Starting FULLY AUTOMATED Mode[/bold green]\n"
            f"Goal: {goal}\n\n"
            f"[yellow]The Operator (AI) will make all decisions automatically.\n"
            f"This is 100% autonomous - NO user input needed.[/yellow]",
            title="🤖 BMAD Auto Mode",
            border_style="green"
        ))
        
        operator = BMadOperator(self.lmstudio_config, goal)

        # Initial greeting
        greeting = "Team Leader: Hello! I am coordinating expert agents to help you.\n   What would you like to accomplish today?"
        console.print(Panel(Markdown(greeting), title="💬 System", border_style="blue"))

        # Operator's first move
        conversation_log = f"{greeting}"
        console.print("[bold cyan]🤖 Operator is thinking...[/bold cyan]")
        user_input = operator.decide(conversation_log)
        console.print(Panel(Markdown(user_input), title="🤖 Operator (Auto-User)", border_style="green"))

        iteration = 0
        max_iterations = 30  # Global safety limit
        
        while iteration < max_iterations:
            iteration += 1
            console.print(f"\n[dim]--- Iteration {iteration}/{max_iterations} ---[/dim]\n")
            
            try:
                # Check for exit commands from Operator
                if "quit" in user_input.lower():
                    console.print("[bold red]✓ Operator requested to quit.[/bold red]")
                    break
                
                if "conclude" in user_input.lower():
                    console.print("[bold green]✓ Operator requested conclusion. Generating...[/bold green]")
                    self.generate_conclusion_sync()
                    break

                # Send to team
                console.print("[bold yellow]📡 Consulting the team...[/bold yellow]")
                response = self.chat_sync(user_input)

                console.print(Panel(Markdown(response), title="👥 Team Response", border_style="blue"))

                # Operator decides next move
                conversation_log += f"\nUser: {user_input}\nTeam: {response}"
                
                # Truncate context if too long (keep last 3000 chars)
                if len(conversation_log) > 3000:
                    conversation_log = "...[earlier conversation truncated]...\n" + conversation_log[-3000:]
                
                console.print("[bold cyan]🤖 Operator is thinking...[/bold cyan]")
                user_input = operator.decide(conversation_log)
                console.print(Panel(Markdown(user_input), title="🤖 Operator (Auto-User)", border_style="green"))

            except KeyboardInterrupt:
                console.print("\n[bold red]⚠ Session interrupted by user (Ctrl+C).[/bold red]")
                break
            except Exception as e:
                console.print(f"\n[bold red]❌ Error in auto mode: {e}[/bold red]")
                logger.error(f"Auto mode error: {e}", exc_info=True)
                break
        
        if iteration >= max_iterations:
            console.print(f"\n[bold yellow]⚠ Max iterations ({max_iterations}) reached. Auto-concluding...[/bold yellow]")
            self.generate_conclusion_sync()
        
        console.print("\n[bold green]✓ Auto mode session complete![/bold green]\n")


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    """Example usage - Uses Agno Teams for true multi-agent collaboration."""

    import asyncio

    # LMStudio config (single provider)
    lmstudio_config = {
        'model': 'local-model',
        'base_url': 'http://localhost:1234/v1',
        'api_key': 'lm-studio',
        'temperature': 0.7,
        'max_tokens': 4096
    }

    # Create Teams-based session (recommended)
    session = BMadTeamsSession(
        research_id="bmad-test-001",
        research_dir=Path("./generation/bmad-test"),
        lmstudio_config=lmstudio_config
    )

    # Run interactive (sync version for simplicity)
    # session.run_interactive_sync()
    
    # Example Auto Mode
    session.run_auto_mode(goal="Create a comprehensive marketing strategy for a new AI coffee machine.")
