"""
Music Therapy Agent - Real-world therapeutic music for mental health and cognitive enhancement
Provides personalized music therapy interventions for various psychological and neurological conditions.
"""

import os
from typing import Dict, Any, List
from orion.agent_core import create_orchestrator
from orion.agent_core.utils import function_to_schema
from orion.graph_core import WorkflowGraph
from orion.tool_registry import tool


from dotenv import load_dotenv

load_dotenv()


# Music Therapy Tools
@tool
def create_anxiety_relief_composition(anxiety_level: str, duration_minutes: int, musical_preferences: List[str]) -> Dict[str, Any]:
    """Create therapeutic music composition specifically designed for anxiety relief."""
    try:
        # Therapeutic music parameters for anxiety
        anxiety_params = {
            "mild": {
                "tempo": (60, 80),  # BPM range
                "key_signature": "C Major",
                "rhythm_pattern": "4/4 simple",
                "instruments": ["piano", "strings", "flute"],
                "dynamics": "soft to moderate",
                "progression_type": "slow_descending"
            },
            "moderate": {
                "tempo": (50, 70),
                "key_signature": "F Major",
                "rhythm_pattern": "3/4 waltz",
                "instruments": ["piano", "cello", "acoustic_guitar"],
                "dynamics": "very soft",
                "progression_type": "repetitive_cycles"
            },
            "severe": {
                "tempo": (40, 60),
                "key_signature": "D Major",
                "rhythm_pattern": "free_time",
                "instruments": ["piano", "strings", "nature_sounds"],
                "dynamics": "pianissimo",
                "progression_type": "drone_based"
            }
        }
        
        params = anxiety_params.get(anxiety_level.lower(), anxiety_params["moderate"])
        
        # Generate therapeutic structure
        composition_structure = {
            "intro": {
                "duration": duration_minutes * 0.15,
                "purpose": "Establish calm environment",
                "techniques": ["soft entry", "breathing tempo", "simple melody"]
            },
            "development": {
                "duration": duration_minutes * 0.60,
                "purpose": "Progressive relaxation",
                "techniques": ["repetitive motifs", "gradual tempo decrease", "harmonic resolution"]
            },
            "resolution": {
                "duration": duration_minutes * 0.25,
                "purpose": "Deep relaxation state",
                "techniques": ["sustained notes", "nature integration", "silence spaces"]
            }
        }
        
        # Therapeutic techniques
        therapy_techniques = [
            "Guided breathing synchronization",
            "Progressive muscle relaxation rhythm",
            "Mindfulness anchoring tones",
            "Cognitive distraction melodies",
            "Grounding bass frequencies"
        ]
        
        # Personalization based on preferences
        preferred_instruments = []
        for pref in musical_preferences:
            if pref.lower() in ["classical", "orchestra"]:
                preferred_instruments.extend(["violin", "cello", "piano"])
            elif pref.lower() in ["ambient", "electronic"]:
                preferred_instruments.extend(["synthesizer", "ambient_pads", "reverb_effects"])
            elif pref.lower() in ["nature", "environmental"]:
                preferred_instruments.extend(["nature_sounds", "rain", "ocean_waves"])
        
        # Final composition specification
        composition = {
            "title": f"Anxiety Relief Composition - {anxiety_level.title()} Level",
            "therapeutic_purpose": "Anxiety reduction and nervous system regulation",
            "target_condition": f"{anxiety_level.title()} anxiety",
            "duration_minutes": duration_minutes,
            "musical_parameters": params,
            "structure": composition_structure,
            "therapeutic_techniques": therapy_techniques,
            "personalization": {
                "preferred_instruments": preferred_instruments,
                "adaptation_notes": "Composition adapted to user's musical preferences"
            },
            "usage_instructions": [
                "Use in quiet, comfortable environment",
                "Focus on breathing with the rhythm",
                "Allow thoughts to flow without judgment",
                "Use headphones for optimal experience"
            ],
            "expected_outcomes": [
                "Reduced heart rate and blood pressure",
                "Decreased cortisol levels",
                "Improved mood and emotional regulation",
                "Enhanced sense of calm and control"
            ]
        }
        
        return composition
        
    except Exception as e:
        return {"error": f"Anxiety relief composition error: {str(e)}"}


@tool
def design_cognitive_enhancement_music(cognitive_goal: str, session_length: int, difficulty_level: str) -> Dict[str, Any]:
    """Design music therapy interventions for cognitive enhancement and brain training."""
    try:
        # Cognitive enhancement parameters
        cognitive_protocols = {
            "memory_enhancement": {
                "frequency_focus": "40Hz binaural beats",
                "rhythm_pattern": "Consistent 4/4 with memory cues",
                "instruments": ["piano", "bells", "soft_percussion"],
                "techniques": ["melodic repetition", "pattern recognition", "auditory mnemonics"]
            },
            "attention_training": {
                "frequency_focus": "Beta waves (15-30Hz)",
                "rhythm_pattern": "Variable tempo with attention anchors",
                "instruments": ["strings", "woodwinds", "focused_tones"],
                "techniques": ["selective attention cues", "distraction filtering", "sustained focus"]
            },
            "creativity_boost": {
                "frequency_focus": "Alpha waves (8-13Hz)",
                "rhythm_pattern": "Free-flowing with creative spaces",
                "instruments": ["jazz_ensemble", "improvisational", "harmonic_variations"],
                "techniques": ["divergent thinking prompts", "creative pauses", "harmonic exploration"]
            }
        }
        
        protocol = cognitive_protocols.get(cognitive_goal.lower(), cognitive_protocols["attention_training"])
        
        # Session structure for cognitive training
        session_phases = {
            "preparation": {
                "duration": session_length * 0.10,
                "purpose": "Mental preparation and focus",
                "music_type": "Simple, grounding tones"
            },
            "activation": {
                "duration": session_length * 0.20,
                "purpose": "Brain activation and engagement",
                "music_type": "Increasing complexity and tempo"
            },
            "training": {
                "duration": session_length * 0.50,
                "purpose": "Active cognitive training",
                "music_type": "Protocol-specific intervention music"
            },
            "integration": {
                "duration": session_length * 0.20,
                "purpose": "Skill consolidation and rest",
                "music_type": "Gentle, integrative harmonies"
            }
        }
        
        # Difficulty adjustments
        difficulty_settings = {
            "beginner": {
                "complexity": "Low",
                "distractions": "Minimal",
                "tempo_changes": "Gradual",
                "cognitive_load": "Light"
            },
            "intermediate": {
                "complexity": "Moderate",
                "distractions": "Controlled",
                "tempo_changes": "Moderate",
                "cognitive_load": "Moderate"
            },
            "advanced": {
                "complexity": "High",
                "distractions": "Multiple",
                "tempo_changes": "Rapid",
                "cognitive_load": "High"
            }
        }
        
        enhancement_protocol = {
            "protocol_name": f"Cognitive Enhancement - {cognitive_goal.title()}",
            "target_cognitive_domain": cognitive_goal,
            "session_duration": session_length,
            "difficulty_level": difficulty_level,
            "musical_protocol": protocol,
            "session_structure": session_phases,
            "difficulty_parameters": difficulty_settings.get(difficulty_level.lower(), difficulty_settings["beginner"]),
            "expected_benefits": [
                f"Improved {cognitive_goal} performance",
                "Enhanced neural connectivity",
                "Better cognitive flexibility",
                "Increased mental stamina"
            ],
            "tracking_metrics": [
                "Session completion rate",
                "Subjective difficulty rating",
                "Performance improvement markers",
                "Engagement level assessment"
            ]
        }
        
        return enhancement_protocol
        
    except Exception as e:
        return {"error": f"Cognitive enhancement protocol error: {str(e)}"}


@tool
def create_mood_regulation_playlist(current_mood: str, target_mood: str, transition_time: int) -> Dict[str, Any]:
    """Create therapeutic music playlist for mood regulation and emotional balance."""
    try:
        # Mood-based musical characteristics
        mood_characteristics = {
            "depressed": {
                "tempo": (40, 60),
                "key": "minor",
                "instruments": ["piano", "strings", "soft_vocals"],
                "dynamics": "soft",
                "emotional_tone": "melancholic_but_hopeful"
            },
            "anxious": {
                "tempo": (50, 70),
                "key": "major",
                "instruments": ["acoustic_guitar", "flute", "nature_sounds"],
                "dynamics": "gentle",
                "emotional_tone": "calming_reassuring"
            },
            "angry": {
                "tempo": (60, 80),
                "key": "minor_to_major",
                "instruments": ["orchestral", "controlled_percussion", "strings"],
                "dynamics": "moderate_to_soft",
                "emotional_tone": "validating_to_peaceful"
            },
            "calm": {
                "tempo": (60, 80),
                "key": "major",
                "instruments": ["balanced_ensemble", "harmonious_blend"],
                "dynamics": "comfortable",
                "emotional_tone": "stable_content"
            }
        }
        
        current_params = mood_characteristics.get(current_mood.lower(), mood_characteristics["anxious"])
        target_params = mood_characteristics.get(target_mood.lower(), mood_characteristics["calm"])
        
        # Create transition plan
        transition_phases = []
        num_phases = min(max(transition_time // 10, 3), 6)  # 3-6 phases
        phase_duration = transition_time / num_phases
        
        for i in range(num_phases):
            progress = i / (num_phases - 1) if num_phases > 1 else 1
            
            # Interpolate between current and target
            phase_tempo = (
                current_params["tempo"][0] + progress * (target_params["tempo"][0] - current_params["tempo"][0]),
                current_params["tempo"][1] + progress * (target_params["tempo"][1] - current_params["tempo"][1])
            )
            
            phase = {
                "phase_number": i + 1,
                "duration": phase_duration,
                "tempo_range": phase_tempo,
                "emotional_focus": f"Transition {int(progress * 100)}% from {current_mood} to {target_mood}",
                "therapeutic_techniques": [
                    "Gradual tempo adjustment",
                    "Harmonic progression",
                    "Emotional validation"
                ]
            }
            transition_phases.append(phase)
        
        mood_regulation_plan = {
            "therapy_plan": f"Mood Regulation: {current_mood.title()} → {target_mood.title()}",
            "current_mood_profile": current_params,
            "target_mood_profile": target_params,
            "transition_duration": transition_time,
            "transition_phases": transition_phases,
            "usage_recommendations": [
                "Listen in a comfortable, private space",
                "Use during natural transition periods",
                "Practice deep breathing during listening"
            ],
            "success_indicators": [
                "Gradual mood improvement",
                "Reduced emotional intensity",
                "Increased emotional awareness"
            ]
        }
        
        return mood_regulation_plan
        
    except Exception as e:
        return {"error": f"Mood regulation playlist error: {str(e)}"}


@tool
def develop_sleep_therapy_soundscape(sleep_issue: str, sleep_duration: int, environmental_factors: List[str]) -> Dict[str, Any]:
    """Develop therapeutic soundscape for sleep disorders and sleep quality improvement."""
    try:
        # Sleep therapy protocols
        sleep_protocols = {
            "insomnia": {
                "wave_pattern": "Delta waves (0.5-4Hz)",
                "tempo": (40, 50),
                "instruments": ["ambient_drones", "soft_strings", "whispered_vocals"],
                "techniques": ["progressive_relaxation", "sleep_induction", "anxiety_reduction"]
            },
            "restless_sleep": {
                "wave_pattern": "Consistent Delta waves",
                "tempo": (35, 50),
                "instruments": ["stable_harmonies", "grounding_bass", "consistent_rhythm"],
                "techniques": ["deep_sleep_promotion", "movement_reduction", "sleep_consolidation"]
            }
        }
        
        protocol = sleep_protocols.get(sleep_issue.lower(), sleep_protocols["insomnia"])
        
        # Environmental adaptations
        environmental_adaptations = {}
        for factor in environmental_factors:
            if factor.lower() == "noise":
                environmental_adaptations["noise_masking"] = {
                    "technique": "White/pink noise integration",
                    "frequency_range": "20Hz-20kHz",
                    "volume": "Consistent low level"
                }
            elif factor.lower() == "light":
                environmental_adaptations["light_sensitivity"] = {
                    "technique": "Darkness-promoting frequencies",
                    "frequency_range": "Very low frequencies",
                    "volume": "Minimal"
                }
        
        sleep_therapy_plan = {
            "therapy_protocol": f"Sleep Therapy for {sleep_issue.title()}",
            "target_condition": sleep_issue,
            "total_duration": sleep_duration,
            "therapeutic_protocol": protocol,
            "environmental_adaptations": environmental_adaptations,
            "expected_outcomes": [
                "Improved sleep onset time",
                "Enhanced sleep quality",
                "Reduced nighttime awakenings",
                "Better morning alertness"
            ]
        }
        
        return sleep_therapy_plan
        
    except Exception as e:
        return {"error": f"Sleep therapy soundscape error: {str(e)}"}


class MusicTherapyAgent:
    """Real-world music therapy agent for mental health and cognitive enhancement."""
    
    def __init__(self):
        self.name = "MusicTherapyAgent"
        self.complexity_level = 8
        self.description = "Real-world music therapy agent for anxiety relief, cognitive enhancement, mood regulation, and sleep therapy"
    
    async def create_workflow(self) -> WorkflowGraph:
        """Create the music therapy workflow."""
        try:
            api_key = os.environ.get("API_KEY", "")
            base_url = os.environ.get("BASE_URL", "https://api.openai.com/v1")
            
            if not api_key:
                raise ValueError("API_KEY environment variable is required")
            
            # Create workflow graph
            workflow = WorkflowGraph()
            
            # Create tool schemas for orchestrator
            tools = [
                await function_to_schema(create_anxiety_relief_composition, func_name="create_anxiety_relief_composition", enhance_description=True),
                await function_to_schema(design_cognitive_enhancement_music, func_name="design_cognitive_enhancement_music", enhance_description=True),
                await function_to_schema(create_mood_regulation_playlist, func_name="create_mood_regulation_playlist", enhance_description=True),
                await function_to_schema(develop_sleep_therapy_soundscape, func_name="develop_sleep_therapy_soundscape", enhance_description=True),
            ]
            
            # Create orchestrator agent
            orchestrator_agent = create_orchestrator(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=tools
            )
            
            # Add orchestrator node
            workflow.add_orchestrator_node("music_therapy_orchestrator", orchestrator_agent)
            
            # Add tool nodes
            workflow.add_node("create_anxiety_relief_composition", create_anxiety_relief_composition)
            workflow.add_node("design_cognitive_enhancement_music", design_cognitive_enhancement_music)
            workflow.add_node("create_mood_regulation_playlist", create_mood_regulation_playlist)
            workflow.add_node("develop_sleep_therapy_soundscape", develop_sleep_therapy_soundscape)
            
            # Connect workflow
            workflow.add_edge("__start__", "music_therapy_orchestrator")
            workflow.add_edge("music_therapy_orchestrator", "create_anxiety_relief_composition")
            workflow.add_edge("music_therapy_orchestrator", "design_cognitive_enhancement_music")
            workflow.add_edge("music_therapy_orchestrator", "create_mood_regulation_playlist")
            workflow.add_edge("music_therapy_orchestrator", "develop_sleep_therapy_soundscape")
            
            # All tools lead to end
            workflow.add_edge("create_anxiety_relief_composition", "__end__")
            workflow.add_edge("design_cognitive_enhancement_music", "__end__")
            workflow.add_edge("create_mood_regulation_playlist", "__end__")
            workflow.add_edge("develop_sleep_therapy_soundscape", "__end__")
            
            return workflow
            
        except Exception as e:
            print(f"Error creating workflow: {e}")
            raise
    
    def get_real_world_scenarios(self) -> List[Dict[str, Any]]:
        """Get real-world music therapy scenarios for therapeutic application."""
        return [
            {
                "scenario": "Anxiety relief for college student",
                "prompt": "Create a 20-minute anxiety relief composition for a college student with moderate anxiety who prefers classical music. They have an important exam tomorrow.",
                "category": "anxiety_management"
            },
            {
                "scenario": "Cognitive enhancement for elderly",
                "prompt": "Design a 30-minute cognitive enhancement music session for memory improvement in a 70-year-old with mild cognitive decline. Beginner difficulty level.",
                "category": "cognitive_therapy"
            },
            {
                "scenario": "Mood regulation for depression",
                "prompt": "Create a mood regulation playlist to help someone transition from depressed to calm mood over 45 minutes. They're currently feeling very low.",
                "category": "mood_therapy"
            },
            {
                "scenario": "Sleep therapy for insomnia",
                "prompt": "Develop a sleep therapy soundscape for someone with chronic insomnia. They need 8 hours of sleep support and have issues with noise and light sensitivity.",
                "category": "sleep_therapy"
            }
        ]


# Export the agent
__all__ = ["MusicTherapyAgent"]