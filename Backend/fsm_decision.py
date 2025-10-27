#!/usr/bin/env python3
"""
FSM Decision Layer for Gate Security
Implements state machine with hysteresis, grace periods, and multi-signal confirmation
"""

import time
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


class CheckState(Enum):
    """States for gate check FSM"""
    IDLE = "idle"
    PRESENT_IN_GA = "present_in_gate_area"
    GUARD_PRESENT = "guard_present"
    INTERACTION_WINDOW = "interaction_window"
    CHECK_COMPLETED = "check_completed"
    CHECK_FAILED = "check_failed"


@dataclass
class PersonState:
    """FSM state for a single person"""
    track_id: int
    current_state: CheckState = CheckState.IDLE
    
    # Timers (accumulated time)
    dwell_in_ga: float = 0.0  # Time spent in gate area
    guard_overlap_time: float = 0.0  # Time guard was present
    interaction_time: float = 0.0  # Time in contact/interaction
    
    # Timestamps
    state_entered_at: float = field(default_factory=time.time)
    session_started_at: Optional[float] = None
    last_update_at: float = field(default_factory=time.time)
    
    # Flags
    in_gate_area: bool = False
    guard_assigned: Optional[int] = None  # Guard track ID
    in_occlusion: bool = False
    occlusion_started_at: Optional[float] = None
    
    # Interaction metrics
    contact_count: int = 0
    pose_reach_count: int = 0
    min_center_distance: float = float('inf')
    max_iou: float = 0.0
    
    # Hysteresis
    consecutive_in_ga: int = 0
    consecutive_out_ga: int = 0
    consecutive_contact: int = 0
    consecutive_no_contact: int = 0
    
    # Completion tracking
    completion_score: float = 0.0
    cooldown_until: Optional[float] = None
    
    def transition_to(self, new_state: CheckState):
        """Transition to new state"""
        if new_state != self.current_state:
            self.current_state = new_state
            self.state_entered_at = time.time()
    
    @property
    def time_in_current_state(self) -> float:
        """Time spent in current state"""
        return time.time() - self.state_entered_at
    
    @property
    def session_duration(self) -> float:
        """Total session duration"""
        if self.session_started_at is None:
            return 0.0
        return time.time() - self.session_started_at
    
    def reset(self):
        """Reset state to IDLE"""
        self.current_state = CheckState.IDLE
        self.dwell_in_ga = 0.0
        self.guard_overlap_time = 0.0
        self.interaction_time = 0.0
        self.session_started_at = None
        self.in_gate_area = False
        self.guard_assigned = None
        self.in_occlusion = False
        self.occlusion_started_at = None
        self.contact_count = 0
        self.pose_reach_count = 0
        self.min_center_distance = float('inf')
        self.max_iou = 0.0
        self.consecutive_in_ga = 0
        self.consecutive_out_ga = 0
        self.consecutive_contact = 0
        self.consecutive_no_contact = 0
        self.completion_score = 0.0
    
    def is_in_cooldown(self) -> bool:
        """Check if in cooldown period"""
        if self.cooldown_until is None:
            return False
        return time.time() < self.cooldown_until
    
    def set_cooldown(self, duration: float = 10.0):
        """Set cooldown period"""
        self.cooldown_until = time.time() + duration


@dataclass
class GuardState:
    """State for guard tracks"""
    track_id: int
    
    # Timers
    dwell_in_anchor: float = 0.0
    dwell_in_ga: float = 0.0
    
    # Flags
    in_anchor: bool = False
    in_gate_area: bool = False
    is_qualified: bool = False  # Meets anchor requirements
    
    # Timestamps
    anchor_entered_at: Optional[float] = None
    last_update_at: float = field(default_factory=time.time)
    
    def update_presence(self, in_anchor: bool, in_ga: bool, dt: float):
        """Update guard presence"""
        # Update anchor dwell
        if in_anchor:
            self.dwell_in_anchor += dt
            if self.anchor_entered_at is None:
                self.anchor_entered_at = time.time()
        else:
            self.anchor_entered_at = None
        
        # Update GA dwell
        if in_ga:
            self.dwell_in_ga += dt
        
        self.in_anchor = in_anchor
        self.in_gate_area = in_ga
        self.last_update_at = time.time()


class DecisionEngine:
    """FSM-based decision engine with scoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Extract config values
        self.timers = config.get('timers', {})
        self.proximity = config.get('proximity', {})
        self.pose = config.get('pose', {})
        self.guard_logic = config.get('guard_anchor_logic', {})
        self.scoring = config.get('scoring', {})
        self.noise_filter = config.get('noise_filtering', {})
        
        # State storage
        self.person_states: Dict[int, PersonState] = {}
        self.guard_states: Dict[int, GuardState] = {}
    
    def get_person_state(self, track_id: int) -> PersonState:
        """Get or create person state"""
        if track_id not in self.person_states:
            self.person_states[track_id] = PersonState(track_id=track_id)
        return self.person_states[track_id]
    
    def get_guard_state(self, track_id: int) -> GuardState:
        """Get or create guard state"""
        if track_id not in self.guard_states:
            self.guard_states[track_id] = GuardState(track_id=track_id)
        return self.guard_states[track_id]
    
    def update_person(self, track_id: int, 
                     in_gate_area: bool,
                     guard_track_id: Optional[int],
                     is_in_contact: bool,
                     contact_metrics: Dict[str, float],
                     pose_detected: bool,
                     dt: float) -> Dict[str, Any]:
        """
        Update person FSM and return decision
        
        Args:
            track_id: Person track ID
            in_gate_area: Whether person is in gate area
            guard_track_id: Assigned guard track ID (or None)
            is_in_contact: Whether in contact with guard
            contact_metrics: {'center_distance', 'iou'}
            pose_detected: Whether pose interaction detected
            dt: Time delta
        
        Returns:
            Decision dict with state, transitions, and completion status
        """
        state = self.get_person_state(track_id)
        
        # Update last update time
        state.last_update_at = time.time()
        
        # Start session if entering GA
        if in_gate_area and state.session_started_at is None:
            state.session_started_at = time.time()
        
        # Update timers
        self._update_timers(state, in_gate_area, guard_track_id, 
                           is_in_contact, dt)
        
        # Update metrics
        self._update_metrics(state, contact_metrics, pose_detected)
        
        # Hysteresis for presence
        if in_gate_area:
            state.consecutive_in_ga += 1
            state.consecutive_out_ga = 0
        else:
            state.consecutive_out_ga += 1
            state.consecutive_in_ga = 0
        
        # Hysteresis for contact
        if is_in_contact:
            state.consecutive_contact += 1
            state.consecutive_no_contact = 0
        else:
            state.consecutive_no_contact += 1
            state.consecutive_contact = 0
        
        # Update state flags
        state.in_gate_area = in_gate_area
        state.guard_assigned = guard_track_id
        
        # FSM transitions
        prev_state = state.current_state
        self._process_fsm_transitions(state, guard_track_id, is_in_contact, pose_detected)
        
        # Check for completion
        completion_result = self._check_completion_criteria(state)
        
        return {
            'track_id': track_id,
            'state': state.current_state.value,
            'prev_state': prev_state.value,
            'state_changed': prev_state != state.current_state,
            'dwell_in_ga': state.dwell_in_ga,
            'guard_overlap_time': state.guard_overlap_time,
            'interaction_time': state.interaction_time,
            'session_duration': state.session_duration,
            'completion': completion_result,
            'score': state.completion_score
        }
    
    def _update_timers(self, state: PersonState, in_gate_area: bool,
                      guard_track_id: Optional[int], is_in_contact: bool, dt: float):
        """Update state timers"""
        # Dwell in GA (pause during brief occlusion)
        if in_gate_area:
            state.dwell_in_ga += dt
        elif state.in_occlusion:
            # Don't decrement during occlusion
            pass
        
        # Guard overlap
        if guard_track_id is not None:
            guard_state = self.guard_states.get(guard_track_id)
            if guard_state and guard_state.is_qualified:
                state.guard_overlap_time += dt
        
        # Interaction time
        if is_in_contact:
            state.interaction_time += dt
    
    def _update_metrics(self, state: PersonState, contact_metrics: Dict[str, float],
                       pose_detected: bool):
        """Update interaction metrics"""
        if 'center_distance' in contact_metrics:
            state.min_center_distance = min(state.min_center_distance,
                                           contact_metrics['center_distance'])
        
        if 'iou' in contact_metrics:
            state.max_iou = max(state.max_iou, contact_metrics['iou'])
        
        if pose_detected:
            state.pose_reach_count += 1
    
    def _process_fsm_transitions(self, state: PersonState, 
                                 guard_track_id: Optional[int],
                                 is_in_contact: bool, 
                                 pose_detected: bool):
        """Process FSM state transitions"""
        min_consensus = self.noise_filter.get('multi_frame_consensus', 3)
        
        current = state.current_state
        
        if current == CheckState.IDLE:
            # IDLE → PRESENT_IN_GA
            if state.consecutive_in_ga >= min_consensus:
                state.transition_to(CheckState.PRESENT_IN_GA)
        
        elif current == CheckState.PRESENT_IN_GA:
            # Exit to IDLE if left GA
            if state.consecutive_out_ga >= min_consensus:
                state.transition_to(CheckState.IDLE)
            
            # → GUARD_PRESENT if guard qualified
            elif guard_track_id is not None:
                guard_state = self.guard_states.get(guard_track_id)
                if guard_state and guard_state.is_qualified:
                    state.transition_to(CheckState.GUARD_PRESENT)
        
        elif current == CheckState.GUARD_PRESENT:
            # Exit to PRESENT_IN_GA if guard left
            if guard_track_id is None:
                state.transition_to(CheckState.PRESENT_IN_GA)
            
            # Exit to IDLE if person left GA
            elif state.consecutive_out_ga >= min_consensus:
                state.transition_to(CheckState.IDLE)
            
            # → INTERACTION_WINDOW if contact/pose detected
            elif state.consecutive_contact >= min_consensus or pose_detected:
                state.transition_to(CheckState.INTERACTION_WINDOW)
        
        elif current == CheckState.INTERACTION_WINDOW:
            # Can transition back to GUARD_PRESENT if interaction ended
            if state.consecutive_no_contact >= min_consensus * 2:
                state.transition_to(CheckState.GUARD_PRESENT)
            
            # Exit to IDLE if person left GA
            elif state.consecutive_out_ga >= min_consensus:
                state.transition_to(CheckState.IDLE)
    
    def _check_completion_criteria(self, state: PersonState) -> Dict[str, Any]:
        """Check if all criteria for check completion are met"""
        result = {
            'completed': False,
            'criteria_met': {},
            'score': 0.0,
            'threshold': self.scoring.get('threshold', 0.9)
        }
        
        # Don't check if in cooldown
        if state.is_in_cooldown():
            return result
        
        # Must be in appropriate state
        if state.current_state not in [CheckState.GUARD_PRESENT, 
                                       CheckState.INTERACTION_WINDOW]:
            return result
        
        # Check criteria
        criteria = {}
        
        # 1. Person dwell time
        min_person_dwell = self.timers.get('person_min_dwell_s', 6.0)
        criteria['person_dwell'] = state.dwell_in_ga >= min_person_dwell
        
        # 2. Guard dwell time
        min_guard_dwell = self.timers.get('guard_min_dwell_s', 3.0)
        criteria['guard_dwell'] = state.guard_overlap_time >= min_guard_dwell
        
        # 3. Interaction time
        min_interaction = self.timers.get('interaction_min_overlap_s', 1.2)
        criteria['interaction'] = state.interaction_time >= min_interaction
        
        # 4. Calculate score
        score = self._calculate_score(state)
        criteria['score'] = score >= result['threshold']
        
        result['criteria_met'] = criteria
        result['score'] = score
        state.completion_score = score
        
        # All criteria must be met
        if all(criteria.values()):
            result['completed'] = True
            state.transition_to(CheckState.CHECK_COMPLETED)
            state.set_cooldown(10.0)  # 10 second cooldown
        
        return result
    
    def _calculate_score(self, state: PersonState) -> float:
        """Calculate explainable completion score"""
        base = self.scoring.get('base', 0.6)
        contact_bonus = self.scoring.get('contact_bonus', 0.2)
        pose_bonus = self.scoring.get('pose_bonus', 0.15)
        persistence_bonus = self.scoring.get('reid_persistence_bonus', 0.05)
        
        score = base
        
        # Contact confidence
        if state.interaction_time > 0:
            # Higher score for closer proximity
            center_dist_scale = self.proximity.get('center_dist_scale', 0.35)
            if state.min_center_distance < float('inf'):
                contact_conf = max(0.0, 1.0 - (state.min_center_distance / center_dist_scale))
            else:
                contact_conf = 0.0
            
            # Also consider IoU
            iou_min = self.proximity.get('iou_min', 0.03)
            iou_conf = min(1.0, state.max_iou / (iou_min * 3))
            
            contact_conf = max(contact_conf, iou_conf)
            score += contact_bonus * contact_conf
        
        # Pose confidence
        if state.pose_reach_count > 0:
            pose_conf = min(1.0, state.pose_reach_count / 10.0)
            score += pose_bonus * pose_conf
        
        # Persistence bonus
        session_len = state.session_duration
        persistence_conf = min(1.0, session_len / 10.0)
        score += persistence_bonus * persistence_conf
        
        return min(1.0, score)
    
    def update_guard(self, track_id: int, in_anchor: bool, in_gate_area: bool, dt: float):
        """Update guard state"""
        guard_state = self.get_guard_state(track_id)
        guard_state.update_presence(in_anchor, in_gate_area, dt)
        
        # Check if guard is qualified
        min_guard_dwell = self.timers.get('guard_min_dwell_s', 3.0)
        mode = self.guard_logic.get('mode', 'either')
        
        if mode == 'strict_anchor':
            # Must be in anchor
            guard_state.is_qualified = guard_state.dwell_in_anchor >= min_guard_dwell
        
        elif mode == 'either':
            # Can be in anchor OR in gate area
            guard_state.is_qualified = (
                guard_state.dwell_in_anchor >= min_guard_dwell or
                (guard_state.in_gate_area and guard_state.dwell_in_ga >= min_guard_dwell)
            )
        
        elif mode == 'no_anchor':
            # Just needs to exist (for ID-based guard detection)
            guard_state.is_qualified = True
        
        return guard_state.is_qualified
    
    def check_session_timeout(self, track_id: int) -> bool:
        """Check if session has timed out"""
        if track_id not in self.person_states:
            return False
        
        state = self.person_states[track_id]
        timeout = self.timers.get('session_timeout_s', 8.0)
        
        time_since_update = time.time() - state.last_update_at
        
        if time_since_update >= timeout:
            # Reset to IDLE
            state.reset()
            return True
        
        return False
    
    def cleanup_old_states(self, active_track_ids: List[int]):
        """Remove states for inactive tracks"""
        # Person states
        to_remove = []
        for track_id in self.person_states:
            if track_id not in active_track_ids:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.person_states[track_id]
        
        # Guard states
        to_remove = []
        for track_id in self.guard_states:
            if track_id not in active_track_ids:
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del self.guard_states[track_id]
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of all states"""
        return {
            'total_persons': len(self.person_states),
            'total_guards': len(self.guard_states),
            'persons_by_state': self._count_by_state(),
            'qualified_guards': sum(1 for g in self.guard_states.values() if g.is_qualified)
        }
    
    def _count_by_state(self) -> Dict[str, int]:
        """Count persons by state"""
        counts = {}
        for state_enum in CheckState:
            counts[state_enum.value] = 0
        
        for person_state in self.person_states.values():
            counts[person_state.current_state.value] += 1
        
        return counts

