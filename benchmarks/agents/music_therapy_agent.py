"""
Music Therapy Agent - Real-world therapeutic music for mental health and cognitive enhancement
Provides personalized music therapy interventions for various psychological and neurological conditions.
"""

import os
import asyncio
import json
import random
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from orion.agent_core import create_orchestrator, build_async_agent
from orion.agent_core.utils import function_to_schema
from orion.graph_core import WorkflowGraph
from orion.tool_registry import tool


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
            "executive_function": {
                "frequency_focus": "Theta waves (4-8Hz)",
                "rhythm_pattern": "Complex polyrhythms",
                "instruments": ["multiple_layers", "orchestral", "structured_complexity"],
                "techniques": ["task switching cues", "working memory challenges", "inhibitory control"]
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
        
        # Neuroplasticity-based recommendations
        neuroplasticity_factors = [
            "Consistent practice schedule (daily 20-30 minutes)",
            "Progressive difficulty increase",
            "Multi-sensory engagement",
            "Attention to emotional response",
            "Rest periods for consolidation"
        ]
        
        enhancement_protocol = {
            "protocol_name": f"Cognitive Enhancement - {cognitive_goal.title()}",
            "target_cognitive_domain": cognitive_goal,
            "session_duration": session_length,
            "difficulty_level": difficulty_level,
            "musical_protocol": protocol,
            "session_structure": session_phases,
            "difficulty_parameters": difficulty_settings.get(difficulty_level.lower(), difficulty_settings["beginner"]),
            "neuroplasticity_principles": neuroplasticity_factors,
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
            "stressed": {
                "tempo": (45, 65),
                "key": "pentatonic",
                "instruments": ["meditation_bells", "ambient_pads", "breathing_sounds"],
                "dynamics": "very_soft",
                "emotional_tone": "grounding_centering"
            },
            "energetic": {
                "tempo": (70, 90),
                "key": "major",
                "instruments": ["upbeat_acoustic", "light_percussion", "positive_vocals"],
                "dynamics": "moderate",
                "emotional_tone": "uplifting_motivating"
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
            progress = i / (num_phases - 1)
            
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
        
        # Therapeutic interventions
        intervention_techniques = {
            "current_mood_validation": f"Acknowledge and validate {current_mood} feelings",
            "gradual_shift": "Slowly guide emotional state toward target",
            "positive_anchoring": "Establish positive emotional associations",
            "consolidation": "Reinforce new emotional state"
        }
        
        # Personalized recommendations
        usage_recommendations = [
            "Listen in a comfortable, private space",
            "Use during natural transition periods",
            "Practice deep breathing during listening",
            "Journal about emotional changes if helpful",
            "Repeat daily for best results"
        ]
        
        mood_regulation_plan = {
            "therapy_plan": f"Mood Regulation: {current_mood.title()} → {target_mood.title()}",
            "current_mood_profile": current_params,
            "target_mood_profile": target_params,
            "transition_duration": transition_time,
            "transition_phases": transition_phases,
            "intervention_techniques": intervention_techniques,
            "usage_recommendations": usage_recommendations,
            "success_indicators": [
                "Gradual mood improvement",
                "Reduced emotional intensity",
                "Increased emotional awareness",
                "Better mood regulation skills"
            ],
            "clinical_notes": "Monitor for any adverse emotional reactions and adjust accordingly"
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
            "sleep_maintenance": {
                "wave_pattern": "Theta waves (4-8Hz)",
                "tempo": (30, 45),
                "instruments": ["continuous_tones", "nature_sounds", "minimal_percussion"],
                "techniques": ["sustained_sleep", "dream_enhancement", "night_terror_prevention"]
            },
            "early_waking": {
                "wave_pattern": "Alpha waves (8-13Hz) transitioning to Delta",
                "tempo": (45, 60),
                "instruments": ["gradual_fade", "morning_prevention", "extended_sleep_cues"],
                "techniques": ["sleep_extension", "circadian_regulation", "morning_anxiety_reduction"]
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
            elif factor.lower() == "temperature":
                environmental_adaptations["temperature_comfort"] = {
                    "technique": "Cooling soundscape",
                    "frequency_range": "Mid-range frequencies",
                    "volume": "Gentle"
                }
        
        # Sleep cycle optimization
        sleep_phases = {
            "preparation": {
                "duration": sleep_duration * 0.15,
                "purpose": "Sleep onset preparation",
                "music_type": "Calming, anxiety-reducing tones"
            },
            "sleep_induction": {
                "duration": sleep_duration * 0.25,
                "purpose": "Transition to sleep",
                "music_type": "Progressive relaxation soundscape"
            },
            "deep_sleep": {
                "duration": sleep_duration * 0.50,
                "purpose": "Maintain deep sleep",
                "music_type": "Minimal, consistent background"
            },
            "sleep_maintenance": {
                "duration": sleep_duration * 0.10,
                "purpose": "Prevent early waking",
                "music_type": "Gentle, reassuring tones"
            }
        }
        
        # Clinical recommendations
        clinical_recommendations = [
            "Use consistently for 2-3 weeks for optimal results",
            "Combine with sleep hygiene practices",
            "Monitor sleep quality improvements",
            "Adjust volume to barely audible level",
            "Consider sleep study if issues persist"
        ]
        
        sleep_therapy_plan = {
            "therapy_protocol": f"Sleep Therapy for {sleep_issue.title()}",
            "target_condition": sleep_issue,
            "total_duration": sleep_duration,
            "therapeutic_protocol": protocol,
            "environmental_adaptations": environmental_adaptations,
            "sleep_phase_structure": sleep_phases,
            "clinical_recommendations": clinical_recommendations,
            "expected_outcomes": [
                "Improved sleep onset time",
                "Enhanced sleep quality",
                "Reduced nighttime awakenings",
                "Better morning alertness"
            ],
            "monitoring_metrics": [
                "Time to fall asleep",
                "Number of awakenings",
                "Sleep quality rating",
                "Morning mood assessment"
            ]
        }
        
        return sleep_therapy_plan
        
    except Exception as e:
        return {"error": f"Sleep therapy soundscape error: {str(e)}"}


@tool
def create_pain_management_audio(pain_type: str, pain_level: int, session_duration: int) -> Dict[str, Any]:
    """Create therapeutic audio for pain management and chronic pain relief."""
    try:
        # Pain management protocols
        pain_protocols = {
            "chronic_pain": {
                "frequency_focus": "Low frequency vibrations (40-100Hz)",
                "rhythm_pattern": "Slow, steady, predictable",
                "instruments": ["low_strings", "singing_bowls", "gentle_percussion"],
                "techniques": ["distraction", "endorphin_release", "nervous_system_calming"]
            },
            "acute_pain": {
                "frequency_focus": "Mid-range frequencies (200-800Hz)",
                "rhythm_pattern": "Breathing-synchronized",
                "instruments": ["flute", "soft_piano", "nature_sounds"],
                "techniques": ["immediate_relief", "stress_reduction", "focus_redirection"]
            },
            "headache": {
                "frequency_focus": "Gentle mid-range (300-600Hz)",
                "rhythm_pattern": "Slow, flowing",
                "instruments": ["ambient_pads", "soft_rain", "distant_chimes"],
                "techniques": ["tension_release", "circulation_improvement", "relaxation_response"]
            },
            "muscle_tension": {
                "frequency_focus": "Rhythmic pulses (60-80Hz)",
                "rhythm_pattern": "Massage-like rhythm",
                "instruments": ["rhythmic_drones", "pulsing_tones", "wave_sounds"],
                "techniques": ["muscle_relaxation", "tension_release", "circulation_enhancement"]
            }
        }
        
        protocol = pain_protocols.get(pain_type.lower(), pain_protocols["chronic_pain"])
        
        # Pain level adjustments
        pain_level_adjustments = {
            "low": (1, 3),
            "moderate": (4, 6),
            "high": (7, 10)
        }
        
        if pain_level <= 3:
            intensity_level = "low"
        elif pain_level <= 6:
            intensity_level = "moderate"
        else:
            intensity_level = "high"
        
        # Session structure for pain relief
        session_structure = {
            "preparation": {
                "duration": session_duration * 0.10,
                "purpose": "Pain acknowledgment and preparation",
                "techniques": ["breathing_preparation", "mindfulness_grounding"]
            },
            "acute_intervention": {
                "duration": session_duration * 0.30,
                "purpose": "Immediate pain relief",
                "techniques": ["distraction", "endorphin_stimulation", "nervous_system_regulation"]
            },
            "sustained_relief": {
                "duration": session_duration * 0.50,
                "purpose": "Ongoing pain management",
                "techniques": ["deep_relaxation", "pain_signal_interruption", "healing_visualization"]
            },
            "integration": {
                "duration": session_duration * 0.10,
                "purpose": "Relief consolidation",
                "techniques": ["positive_anchoring", "self_efficacy_building"]
            }
        }
        
        # Evidence-based techniques
        evidence_based_techniques = [
            "Gate control theory application",
            "Endogenous opioid system activation",
            "Neuroplasticity-based pain reduction",
            "Autonomic nervous system regulation",
            "Mindfulness-based pain management"
        ]
        
        # Clinical integration
        clinical_integration = {
            "use_with_medication": "Can complement but not replace prescribed medications",
            "frequency_of_use": "2-3 times daily or as needed",
            "contraindications": "None known for audio therapy",
            "monitoring_required": "Track pain levels and functional improvement"
        }
        
        pain_management_protocol = {
            "protocol_name": f"Pain Management Audio - {pain_type.title()}",
            "target_condition": pain_type,
            "pain_level": pain_level,
            "intensity_category": intensity_level,
            "session_duration": session_duration,
            "therapeutic_protocol": protocol,
            "session_structure": session_structure,
            "evidence_based_techniques": evidence_based_techniques,
            "clinical_integration": clinical_integration,
            "expected_outcomes": [
                "Reduced pain intensity",
                "Improved pain coping",
                "Better quality of life",
                "Reduced medication dependence"
            ],
            "success_metrics": [
                "Pain scale rating improvement",
                "Functional activity increase",
                "Sleep quality improvement",
                "Mood enhancement"
            ]
        }
        
        return pain_management_protocol
        
    except Exception as e:
        return {"error": f"Pain management audio error: {str(e)}"}


async def music_therapy_agent(therapy_query: str) -> str:
    """Music therapy agent that provides personalized therapeutic music interventions."""
    try:
        # This would integrate with the orchestrator to analyze the query and route to appropriate tools
        return f"Processing music therapy intervention for: {therapy_query}"
    except Exception as e:
        return f"Error in music therapy analysis: {str(e)}"


class MusicTherapyAgent:
    """Real-world music therapy agent for mental health and cognitive enhancement."""
    
    def __init__(self):
        self.name = "MusicTherapyAgent"
        self.complexity_level = 8
        self.description = "Real-world music therapy agent for anxiety relief, cognitive enhancement, mood regulation, and pain management"
    
    async def create_workflow(self) -> WorkflowGraph:
        """Create the music therapy workflow."""
        try:
            api_key = os.environ.get("API_KEY", "")
            base_url = os.environ.get("BASE_URL", "https://api.openai.com/v1")
            
            if not api_key:
                raise ValueError("API_KEY environment variable is required")
            
            # Create tools for different therapy domains
            anxiety_tools = [
                await function_to_schema(create_anxiety_relief_composition, func_name="create_anxiety_relief_composition", enhance_description=True),
                await function_to_schema(create_mood_regulation_playlist, func_name="create_mood_regulation_playlist", enhance_description=True),
            ]
            
            cognitive_tools = [
                await function_to_schema(design_cognitive_enhancement_music, func_name="design_cognitive_enhancement_music", enhance_description=True),
            ]
            
            wellness_tools = [
                await function_to_schema(develop_sleep_therapy_soundscape, func_name="develop_sleep_therapy_soundscape", enhance_description=True),
                await function_to_schema(create_pain_management_audio, func_name="create_pain_management_audio", enhance_description=True),
            ]
            
            # Create response agent
            response_agent = await function_to_schema(music_therapy_agent, func_name="music_therapy_agent", enhance_description=True)
            
            # Create main orchestrator with routing capability
            all_tools = anxiety_tools + cognitive_tools + wellness_tools + [response_agent]
            main_orchestrator = create_orchestrator(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=all_tools
            )
            
            # Create specialized LLM execution nodes
            anxiety_therapist = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=anxiety_tools
            )
            
            cognitive_specialist = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=cognitive_tools
            )
            
            wellness_therapist = build_async_agent(
                api_key=api_key,
                base_url=base_url,
                llm_model="gpt-4",
                tools=wellness_tools
            )
            
            # Create workflow graph
            execution_graph = WorkflowGraph()
            
            # Add main orchestrator
            execution_graph.add_orchestrator_node("main_orchestrator", main_orchestrator)
            
            # Add LLM execution nodes
            execution_graph.add_node("anxiety_therapist", anxiety_therapist)
            execution_graph.add_node("cognitive_specialist", cognitive_specialist)
            execution_graph.add_node("wellness_therapist", wellness_therapist)
            
            # Add tool nodes
            execution_graph.add_node("anxiety_composer", create_anxiety_relief_composition)
            execution_graph.add_node("mood_regulator", create_mood_regulation_playlist)
            execution_graph.add_node("cognitive_enhancer", design_cognitive_enhancement_music)
            execution_graph.add_node("sleep_therapist", develop_sleep_therapy_soundscape)
            execution_graph.add_node("pain_manager", create_pain_management_audio)
            
            # Connect orchestrator to specialized agents
            execution_graph.add_edge("__start__", "main_orchestrator")
            execution_graph.add_edge("main_orchestrator", "anxiety_therapist")
            execution_graph.add_edge("main_orchestrator", "cognitive_specialist")
            execution_graph.add_edge("main_orchestrator", "wellness_therapist")
            
            # Connect specialized agents to their tools
            execution_graph.add_edge("anxiety_therapist", "anxiety_composer")
            execution_graph.add_edge("anxiety_therapist", "mood_regulator")
            execution_graph.add_edge("cognitive_specialist", "cognitive_enhancer")
            execution_graph.add_edge("wellness_therapist", "sleep_therapist")
            execution_graph.add_edge("wellness_therapist", "pain_manager")
            
            # Add human interaction
            execution_graph.add_human_in_the_loop("main_orchestrator")
            
            return execution_graph
            
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
            },
            {
                "scenario": "Pain management for chronic pain",
                "prompt": "Create a 25-minute pain management audio session for someone with chronic back pain at level 7/10. They need help managing daily pain flares.",
                "category": "pain_management"
            }
        ]
    
    async def provide_music_therapy(self, scenario: str) -> Dict[str, Any]:
        """Provide personalized music therapy intervention."""
        try:
            workflow = await self.create_workflow()
            compiled_graph = workflow.compile()
            
            result = await compiled_graph.execute(initial_input=scenario)
            
            return {
                "agent": self.name,
                "scenario": scenario,
                "therapy_plan": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "agent": self.name,
                "scenario": scenario,
                "error": str(e),
                "status": "error"
            }


# Export the agent
__all__ = ["MusicTherapyAgent", "music_therapy_agent"] 