"""
Unit Tests for Gate Security Checker
Tests FSM logic, scoring system, and event generation
"""
import pytest
from unittest.mock import MagicMock, patch
import time


@pytest.mark.unit
class TestGateCheckerInitialization:
    """Test gate checker initialization."""
    
    @patch('gate_sop_checker.load_config')
    def test_gate_checker_loads_config(self, mock_load_config, sample_gate_config):
        """Test that gate checker loads configuration."""
        mock_load_config.return_value = sample_gate_config
        from gate_sop_checker import GateChecker
        
        checker = GateChecker(config_path="test_config.json")
        assert checker.config == sample_gate_config
    
    @patch('gate_sop_checker.load_config')
    def test_gate_checker_initialization_defaults(self, mock_load_config, sample_gate_config):
        """Test gate checker initialization with defaults."""
        mock_load_config.return_value = sample_gate_config
        from gate_sop_checker import GateChecker
        
        checker = GateChecker()
        assert checker.config is not None


@pytest.mark.unit
class TestPersonStateMachine:
    """Test person FSM state transitions."""
    
    def test_person_initial_state_is_idle(self):
        """Test person starts in IDLE state."""
        from fsm_decision import PersonState, CheckState
        person = PersonState(track_id=1)
        assert person.current_state == CheckState.IDLE
    
    def test_person_enters_gate_area_transition(self):
        """Test transition from IDLE to PRESENT_IN_GA."""
        from fsm_decision import PersonState, CheckState
        person = PersonState(track_id=1)
        person.transition_to(CheckState.PRESENT_IN_GA)
        assert person.current_state == CheckState.PRESENT_IN_GA
    
    def test_person_completes_check_transition(self):
        """Test transition to CHECK_COMPLETED."""
        from fsm_decision import PersonState, CheckState
        person = PersonState(track_id=1)
        person.transition_to(CheckState.CHECK_COMPLETED)
        assert person.current_state == CheckState.CHECK_COMPLETED


@pytest.mark.unit
class TestGuardQualification:
    """Test guard qualification logic."""
    
    def test_guard_in_anchor_qualifies(self):
        """Test that guard in anchor area qualifies."""
        from gate_sop_checker import qualify_guard
        guard_state = {
            "in_anchor": True,
            "dwell_in_anchor": 3.5,
            "in_gate_area": False
        }
        config = {"timers": {"guard_min_dwell_s": 3.0}}
        is_qualified = qualify_guard(guard_state, config)
        assert is_qualified == True
    
    def test_guard_insufficient_dwell_not_qualified(self):
        """Test that guard with insufficient dwell time doesn't qualify."""
        from gate_sop_checker import qualify_guard
        guard_state = {
            "in_anchor": True,
            "dwell_in_anchor": 1.0,  # Less than minimum
            "in_gate_area": False
        }
        config = {"timers": {"guard_min_dwell_s": 3.0}}
        is_qualified = qualify_guard(guard_state, config)
        assert is_qualified == False


@pytest.mark.unit
class TestScoringSystem:
    """Test gate check scoring system."""
    
    def test_base_score_calculation(self):
        """Test base score calculation."""
        from fsm_decision import calculate_score
        person_state = {
            "dwell_in_ga": 6.0,
            "interaction_time": 1.5,
            "min_center_distance": 0.2,
            "max_iou": 0.1
        }
        config = {"scoring": {"base": 0.6, "contact_bonus": 0.2, "pose_bonus": 0.15}}
        score = calculate_score(person_state, config)
        assert score >= 0.6  # At least base score
        assert score <= 1.0
    
    def test_score_with_contact_bonus(self):
        """Test scoring with contact detection."""
        from fsm_decision import calculate_score
        person_state = {
            "dwell_in_ga": 6.0,
            "interaction_time": 2.0,
            "min_center_distance": 0.1,  # Close proximity
            "max_iou": 0.15,  # High overlap
            "pose_reach_count": 0
        }
        config = {"scoring": {"base": 0.6, "contact_bonus": 0.2, "pose_bonus": 0.15}}
        score = calculate_score(person_state, config)
        assert score > 0.6  # Should have contact bonus
    
    def test_score_threshold_check(self):
        """Test score threshold checking."""
        from fsm_decision import check_score_threshold
        config = {"scoring": {"threshold": 0.9}}
        assert check_score_threshold(0.95, config) == True
        assert check_score_threshold(0.85, config) == False


@pytest.mark.unit
class TestEventGeneration:
    """Test event generation and logging."""
    
    def test_person_entered_gate_area_event(self):
        """Test P_ENTERED_GA event generation."""
        from event_system import EventLogger, EventType
        logger = EventLogger()
        logger.log_event(EventType.P_ENTERED_GA, track_id=123)
        events = logger.get_events(track_id=123)
        assert len(events) > 0
        assert events[0]["event_type"] == EventType.P_ENTERED_GA
    
    def test_contact_started_event(self):
        """Test CONTACT_STARTED event generation."""
        from event_system import EventLogger, EventType
        logger = EventLogger()
        logger.log_event(
            EventType.CONTACT_STARTED,
            track_id=123,
            other_track_id=456,
            metadata={"distance": 0.15}
        )
        events = logger.get_events(track_id=123)
        assert len(events) > 0
    
    def test_event_timeline_ordering(self):
        """Test that events are ordered by timestamp."""
        from event_system import EventLogger, EventType
        logger = EventLogger()
        logger.log_event(EventType.P_ENTERED_GA, track_id=123)
        time.sleep(0.01)
        logger.log_event(EventType.CONTACT_STARTED, track_id=123)
        events = logger.get_events(track_id=123)
        assert len(events) == 2
        assert events[0]["timestamp"] < events[1]["timestamp"]


@pytest.mark.unit
class TestSessionManagement:
    """Test session creation and management."""
    
    def test_session_creation(self):
        """Test creating a new session."""
        from event_system import SessionManager
        manager = SessionManager()
        session_id = manager.create_session(visitor_track_id=123, guard_track_id=456)
        assert session_id is not None
        assert "123" in session_id
    
    def test_session_completion(self):
        """Test completing a session."""
        from event_system import SessionManager
        manager = SessionManager()
        session_id = manager.create_session(visitor_track_id=123, guard_track_id=456)
        manager.complete_session(session_id, score=0.95)
        session = manager.get_session(session_id)
        assert session["completed"] == True
        assert session["score"] == 0.95


@pytest.mark.unit
class TestDwellTimeTracking:
    """Test dwell time tracking."""
    
    def test_dwell_time_accumulation(self):
        """Test that dwell time accumulates correctly."""
        from gate_sop_checker import update_dwell_time
        state = {"dwell_in_ga": 0.0}
        dt = 0.033  # 30 FPS
        updated = update_dwell_time(state, dt, in_zone=True)
        assert updated["dwell_in_ga"] > 0.0
    
    def test_dwell_time_not_incremented_outside_zone(self):
        """Test dwell time doesn't increment outside zone."""
        from gate_sop_checker import update_dwell_time
        state = {"dwell_in_ga": 1.0}
        dt = 0.033
        updated = update_dwell_time(state, dt, in_zone=False)
        assert updated["dwell_in_ga"] == 1.0  # Should not change


@pytest.mark.unit
class TestHysteresisLogic:
    """Test hysteresis and debouncing."""
    
    def test_contact_debouncing(self):
        """Test contact detection debouncing."""
        from gate_sop_checker import check_contact_with_hysteresis
        # First contact
        is_contact, counter = check_contact_with_hysteresis(
            distance=0.1,
            threshold=0.3,
            current_counter=0,
            required_frames=3
        )
        assert counter == 1
        assert is_contact == False  # Not enough frames yet
    
    def test_contact_confirmed_after_threshold(self):
        """Test contact confirmed after threshold frames."""
        from gate_sop_checker import check_contact_with_hysteresis
        # Simulate 3 consecutive frames
        counter = 0
        for _ in range(3):
            is_contact, counter = check_contact_with_hysteresis(
                distance=0.1,
                threshold=0.3,
                current_counter=counter,
                required_frames=3
            )
        assert is_contact == True


@pytest.mark.integration
class TestGateCheckerFullPipeline:
    """Test full gate checker pipeline."""
    
    @patch('gate_sop_checker.load_config')
    @patch('gate_sop_checker.GateDatabase')
    def test_process_frame_with_detections(self, mock_db, mock_config, sample_gate_config):
        """Test processing a frame with detections."""
        mock_config.return_value = sample_gate_config
        mock_db.return_value = MagicMock()
        
        from gate_sop_checker import GateChecker
        checker = GateChecker()
        
        frame = MagicMock()
        detections = [
            {"track_id": 1, "bbox": [0.4, 0.4, 0.6, 0.6], "confidence": 0.85}
        ]
        
        result = checker.process_frame(frame, detections)
        assert "decisions" in result
        assert "stats" in result




















