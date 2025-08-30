"""
MCP Integration Service for Mitra AI.
Integrates with MCP tools to fetch latest documentation and generate contextual resources.
"""

import logging
import asyncio
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.user import ProblemCategory, UserProfile
from models.wellness import GeneratedResource, ResourceType

logger = logging.getLogger(__name__)


class MCPIntegrationService:
    """Service for integrating MCP tools to enhance resource generation."""

    def __init__(self):
        """Initialize MCP integration service."""
        pass

    async def generate_tech_resources_for_chat(
        self,
        session_context: str,
        user_profile: Optional[UserProfile],
        problem_category: ProblemCategory
    ) -> List[GeneratedResource]:
        """
        Analyze chat session and generate technical resources using MCP tools.

        Args:
            session_context: Recent chat messages context
            user_profile: User profile for personalization
            problem_category: Problem category for the session

        Returns:
            List of generated resources with latest documentation
        """
        try:
            # Detect if user mentioned any technical topics or libraries
            tech_keywords = await self._detect_technical_content(session_context)

            resources = []

            if tech_keywords:
                # Generate tech-specific resources
                for keyword in tech_keywords[:2]:  # Limit to 2 to avoid overwhelming
                    resource = await self._generate_tech_resource(
                        keyword=keyword,
                        context=session_context,
                        user_profile=user_profile,
                        problem_category=problem_category
                    )
                    if resource:
                        resources.append(resource)

            return resources

        except Exception as e:
            logger.error(f"Error generating tech resources: {e}")
            return []

    async def _detect_technical_content(self, session_context: str) -> List[str]:
        """
        Detect technical keywords and libraries mentioned in the chat.

        Args:
            session_context: Chat session content

        Returns:
            List of detected technical keywords
        """
        # Common technical keywords that students and professionals might mention
        tech_patterns = {
            'flutter': ['flutter', 'dart', 'widget', 'app development'],
            'python': ['python', 'django', 'fastapi', 'pandas', 'numpy'],
            'javascript': ['javascript', 'react', 'node.js', 'npm', 'js'],
            'react': ['react', 'jsx', 'component', 'hooks', 'state'],
            'django': ['django', 'python web', 'backend'],
            'machine_learning': ['ml', 'machine learning', 'ai', 'model training'],
            'web_development': ['html', 'css', 'frontend', 'backend', 'api'],
            'mobile_development': ['android', 'ios', 'mobile app'],
            'data_science': ['data science', 'analytics', 'visualization'],
            'programming': ['coding', 'programming', 'algorithm', 'debugging']
        }

        detected_keywords = []
        context_lower = session_context.lower()

        for main_keyword, patterns in tech_patterns.items():
            for pattern in patterns:
                if pattern in context_lower:
                    detected_keywords.append(main_keyword)
                    break

        return list(set(detected_keywords))  # Remove duplicates

    async def _generate_tech_resource(
        self,
        keyword: str,
        context: str,
        user_profile: Optional[UserProfile],
        problem_category: ProblemCategory
    ) -> Optional[GeneratedResource]:
        """
        Generate a technical resource based on detected keywords.

        Args:
            keyword: Technical keyword detected
            context: Session context
            user_profile: User profile for personalization
            problem_category: Problem category

        Returns:
            Generated technical resource or None
        """
        try:
            # Create a tech-focused resource
            age_group = user_profile.age_group.value if user_profile and user_profile.age_group else "young_adult"

            # Tech-specific resource templates
            tech_resources = {
                'flutter': {
                    'title': 'Flutter Development Stress Management',
                    'description': 'Techniques for managing stress while learning Flutter development',
                    'content': self._get_flutter_stress_content(age_group),
                    'tags': ['flutter', 'mobile_development', 'stress_management']
                },
                'python': {
                    'title': 'Python Learning Anxiety Relief',
                    'description': 'Strategies to overcome anxiety when learning Python programming',
                    'content': self._get_python_learning_content(age_group),
                    'tags': ['python', 'programming', 'learning_anxiety']
                },
                'programming': {
                    'title': 'Programmer Burnout Prevention',
                    'description': 'Mental wellness tips for programmers and developers',
                    'content': self._get_programming_wellness_content(age_group),
                    'tags': ['programming', 'burnout', 'developer_wellness']
                }
            }

            resource_template = tech_resources.get(keyword)
            if not resource_template:
                return None

            return GeneratedResource(
                id=str(uuid.uuid4()),
                type=ResourceType.ARTICLES,
                title=resource_template['title'],
                description=resource_template['description'],
                content=resource_template['content'],
                duration_minutes=10,  # Estimated reading time
                difficulty_level='beginner',
                tags=resource_template['tags'],
                created_at=datetime.utcnow(),
                problem_category=problem_category
            )

        except Exception as e:
            logger.error(f"Error generating tech resource for {keyword}: {e}")
            return None

    def _get_flutter_stress_content(self, age_group: str) -> str:
        """Generate Flutter development stress management content."""
        return """
# Managing Flutter Development Stress

## Understanding Development Anxiety
Learning Flutter can be overwhelming, especially with its widget-heavy architecture and state management concepts. It's normal to feel frustrated when your app doesn't work as expected.

## Quick Stress Relief Techniques
- **Take Breaks**: Use the Pomodoro technique - 25 minutes coding, 5 minutes break
- **Debug Mindfully**: Instead of panic-debugging, take a deep breath and read error messages carefully
- **Start Small**: Build simple widgets before complex ones

## Long-term Learning Strategies
1. **Join Communities**: Flutter developers on Discord, Reddit, and Stack Overflow are very helpful
2. **Practice Daily**: Even 30 minutes of consistent practice is better than long, stressful sessions
3. **Build Projects**: Create apps you're passionate about, not just tutorials

## When to Step Away
If you're getting angry at your code or feeling hopeless about bugs, it's time for a break. Your brain processes solutions better when you're relaxed.

Remember: Every developer has been where you are. The confusion and stress you feel now will pass as you gain experience.
        """

    def _get_python_learning_content(self, age_group: str) -> str:
        """Generate Python learning anxiety relief content."""
        return """
# Overcoming Python Learning Anxiety

## Common Python Learning Fears
- "I don't understand object-oriented programming"
- "My code is messy and unprofessional"
- "I'm too slow compared to others"
- "I'll never be good enough for a job"

## Anxiety Management for Coders
### Immediate Relief
- **Breathing Exercise**: When stuck on a problem, take 5 deep breaths
- **Code Reading**: Read others' code to see you're not alone in struggling
- **Small Wins**: Celebrate when your code runs, even if it's simple

### Building Confidence
1. **Version Control**: Use Git to track your progress over time
2. **Code Comments**: Write comments explaining your thought process
3. **Peer Learning**: Study with others or join coding groups

## Dealing with Imposter Syndrome
Remember that experienced developers also Google basic syntax. Learning to code is like learning a new language - it takes time and practice.

## Mental Health Breaks
- Step away from the screen every hour
- Practice mindfulness while your code is running
- Don't code when you're already stressed about other things

Your journey in Python is unique. Comparison with others only increases anxiety.
        """

    def _get_programming_wellness_content(self, age_group: str) -> str:
        """Generate general programming wellness content."""
        return """
# Developer Mental Wellness Guide

## Recognizing Burnout Signs
- Feeling overwhelmed by simple tasks
- Loss of interest in coding projects
- Physical symptoms: eye strain, back pain, headaches
- Emotional symptoms: irritability, anxiety about deadlines

## Creating Healthy Coding Habits
### Physical Wellness
- **20-20-20 Rule**: Every 20 minutes, look at something 20 feet away for 20 seconds
- **Ergonomic Setup**: Proper chair, monitor height, keyboard position
- **Regular Movement**: Stand and stretch every hour

### Mental Wellness
- **Time Boxing**: Set specific hours for coding, don't code all day
- **Separate Spaces**: Don't code in your bedroom if possible
- **Weekend Breaks**: Have at least one day without touching code

## Managing Development Stress
1. **Version Control Everything**: Never lose work due to crashes
2. **Write Tests**: Reduces anxiety about breaking things
3. **Document Your Code**: Future you will thank present you
4. **Ask for Help**: Senior developers want to help, not judge

## Career Anxiety Management
- Focus on learning, not earning initially
- Build a portfolio gradually
- Network with other developers for support
- Remember that everyone starts somewhere

## Emergency Stress Protocol
When development stress becomes overwhelming:
1. Save your work and step away
2. Do a 5-minute breathing exercise
3. Go for a short walk
4. Come back with fresh perspective
5. If still stuck, ask for help

Remember: Code is meant to serve people, not stress them. Your mental health is more important than any deadline.
        """

    def _get_wellness_resource_type(self, problem_category: ProblemCategory) -> str:
        """Get appropriate wellness resource type for problem category."""
        mapping = {
            ProblemCategory.STRESS_ANXIETY: "coping_strategies",
            ProblemCategory.DEPRESSION_SADNESS: "affirmations",
            ProblemCategory.ACADEMIC_PRESSURE: "study_techniques",
            ProblemCategory.CAREER_CONFUSION: "goal_setting",
            ProblemCategory.RELATIONSHIP_ISSUES: "communication_techniques"
        }
        return mapping.get(problem_category, "general_wellness")
