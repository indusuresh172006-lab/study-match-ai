"""
StudyMatch AI - Intelligent Study Group Formation & Peer-Teaching Recommender
Implements an optimization-based complementary matching algorithm to partition
students into balanced study groups of 3 to 5 members where weak topics are covered
by strong members.
"""
from typing import List, Dict, Any, Tuple, Set, Optional
import math


def calculate_complementarity(student_a: Dict[str, Any], student_b: Dict[str, Any]) -> int:
    """
    Calculate the mutual pedagogical synergy between two students:
    - Number of A's weak topics covered by B's strong topics
    - PLUS Number of B's weak topics covered by A's strong topics
    """
    a_weak = set(student_a.get("weak_topics", []))
    a_strong = set(student_a.get("strong_topics", []))
    b_weak = set(student_b.get("weak_topics", []))
    b_strong = set(student_b.get("strong_topics", []))

    covered_a_by_b = len(a_weak.intersection(b_strong))
    covered_b_by_a = len(b_weak.intersection(a_strong))

    return covered_a_by_b + covered_b_by_a


def calculate_group_coverage(group_members: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate the topic coverage metrics for a study group:
    - All weak topics needing help
    - All covered weak topics (at least one peer is strong in it)
    - Uncovered topics
    - Coverage rate percentage
    """
    all_weak: Set[str] = set()
    all_strong: Set[str] = set()

    for s in group_members:
        all_weak.update(s.get("weak_topics", []))
        all_strong.update(s.get("strong_topics", []))

    covered_topics = all_weak.intersection(all_strong)
    uncovered_topics = all_weak - covered_topics

    coverage_rate = (len(covered_topics) / max(len(all_weak), 1)) * 100.0 if all_weak else 100.0

    return {
        "total_weak_topics": len(all_weak),
        "covered_topics": sorted(list(covered_topics)),
        "uncovered_topics": sorted(list(uncovered_topics)),
        "coverage_rate": round(coverage_rate, 2),
    }


def form_balanced_study_groups(
    students: List[Dict[str, Any]],
    min_size: int = 3,
    max_size: int = 5,
) -> List[Dict[str, Any]]:
    """
    Partitions a class of students into balanced study groups of 3 to 5 students
    using a Maximum-Complementarity Greedy Optimization strategy.

    Guarantees:
    - Each group contains between min_size (3) and max_size (5) students.
    - Weak topics are paired with strong students wherever possible.
    - Deterministic and non-random results.
    """
    n_students = len(students)
    if n_students == 0:
        return []

    if n_students < min_size:
        return []

    # Determine optimal number of groups so that every group has size in [min_size, max_size]
    # For instance: 6 -> two groups of 3; 7 -> 4 + 3; 8 -> 4 + 4; 9 -> 5 + 4; 10 -> 5 + 5 or 3+3+4.
    num_groups = max(1, round(n_students / 4.0))
    # Ensure num_groups can satisfy min_size:
    while num_groups * max_size < n_students:
        num_groups += 1
    while num_groups * min_size > n_students and num_groups > 1:
        num_groups -= 1

    # Initialize empty groups
    groups: List[List[Dict[str, Any]]] = [[] for _ in range(num_groups)]
    unassigned = list(students)

    # Sort students by number of weak topics descending (help most at-risk students first)
    unassigned.sort(key=lambda s: len(s.get("weak_topics", [])), reverse=True)

    # Step 1: Seed each group with a student who has weak topics to provide anchor points
    for g_idx in range(num_groups):
        if unassigned:
            groups[g_idx].append(unassigned.pop(0))

    # Step 2: Iteratively assign remaining students to the group that maximizes complementarity
    while unassigned:
        candidate = unassigned.pop(0)

        best_group_idx = -1
        best_synergy_score = -1.0

        for g_idx, group in enumerate(groups):
            # Check size constraint
            if len(group) >= max_size:
                continue

            # Calculate total complementarity with current group members
            synergy = sum(calculate_complementarity(candidate, member) for member in group)
            # Bonus for covering an existing uncovered weak topic in the group
            current_cov = calculate_group_coverage(group)
            new_cov = calculate_group_coverage(group + [candidate])
            newly_covered = len(new_cov["covered_topics"]) - len(current_cov["covered_topics"])
            total_score = synergy + (newly_covered * 5.0)

            # Prioritize groups that haven't reached min_size yet
            if len(group) < min_size:
                total_score += 10.0

            if total_score > best_synergy_score:
                best_synergy_score = total_score
                best_group_idx = g_idx

        # If all valid groups were full, place in smallest available group
        if best_group_idx == -1:
            best_group_idx = min(range(num_groups), key=lambda i: len(groups[i]))

        groups[best_group_idx].append(candidate)

    # Format result with group metadata
    formatted_groups = []
    for idx, group in enumerate(groups):
        metrics = calculate_group_coverage(group)
        formatted_groups.append({
            "group_name": f"Study Group {chr(65 + idx)}", # Group A, Group B, Group C...
            "member_count": len(group),
            "members": group,
            "coverage_metrics": metrics,
        })

    return formatted_groups


def generate_peer_teaching_recommendations(
    group_members: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generates specific peer-teaching pairings within a study group:
    - Who should teach whom
    - Which topic should be taught
    - Pedagogical reason for selection
    - Weak topic to be improved
    """
    recommendations = []

    # Map of topic -> list of strong students
    topic_tutors: Dict[str, List[Dict[str, Any]]] = {}
    for member in group_members:
        for t in member.get("strong_topics", []):
            if t not in topic_tutors:
                topic_tutors[t] = []
            topic_tutors[t].append(member)

    # For every member with a weak topic, match with best available tutor in the group
    for learner in group_members:
        for weak_t in learner.get("weak_topics", []):
            tutors = topic_tutors.get(weak_t, [])
            # Filter out self
            tutors = [t for t in tutors if t.get("id") != learner.get("id")]

            if tutors:
                # Pick tutor with highest mastery score in that topic
                best_tutor = max(
                    tutors,
                    key=lambda t: t.get("mastery_scores", {}).get(weak_t, 85.0)
                )
                tutor_score = best_tutor.get("mastery_scores", {}).get(weak_t, 85.0)
                learner_score = learner.get("mastery_scores", {}).get(weak_t, 35.0)

                reason = (
                    f"{best_tutor.get('name', 'Tutor')} demonstrated strong mastery in {weak_t} "
                    f"({tutor_score:.0f}%) and can effectively mentor {learner.get('name', 'Learner')} "
                    f"({learner_score:.0f}%) through core concepts and problem-solving steps."
                )

                recommendations.append({
                    "tutor_id": best_tutor.get("id"),
                    "tutor_name": best_tutor.get("name"),
                    "learner_id": learner.get("id"),
                    "learner_name": learner.get("name"),
                    "topic_name": weak_t,
                    "reason": reason,
                    "weak_topic_improved": weak_t,
                    "tutor_score": tutor_score,
                    "learner_score": learner_score,
                })

    return recommendations


def match_study_schedules(
    members_schedules: Dict[int, List[Dict[str, Any]]],
    member_names: Dict[int, str],
) -> List[Dict[str, Any]]:
    """
    Computes overlapping available study times for a study group:
    Input:
        members_schedules: { student_id: [{"day_of_week": "Monday", "start_time": "17:00", "end_time": "19:00"}, ...] }
        member_names: { student_id: "Name" }
    Returns:
        List of recommended common sessions sorted by attendance match.
    """
    if not members_schedules:
        return []

    total_members = len(members_schedules)
    results = []

    def to_minutes(value: str) -> int:
        hour_text, minute_text = value.split(":", 1)
        hour, minute = int(hour_text), int(minute_text)
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Invalid study time: {value}")
        return hour * 60 + minute

    def format_time(value: int) -> str:
        return f"{value // 60:02d}:{value % 60:02d}"

    days = sorted({
        slot["day_of_week"]
        for slots in members_schedules.values()
        for slot in slots
    })
    for day in days:
        for mode in ("online", "offline"):
            available_by_student = {}
            boundaries = set()
            for student_id, slots in members_schedules.items():
                matching_slots = []
                for slot in slots:
                    slot_mode = slot.get("study_mode", "online").lower()
                    if slot["day_of_week"] != day or slot_mode not in (mode, "either"):
                        continue
                    start = to_minutes(slot["start_time"])
                    end = to_minutes(slot["end_time"])
                    if end <= start:
                        continue
                    matching_slots.append((start, end))
                    boundaries.update((start, end))
                available_by_student[student_id] = matching_slots

            ordered_boundaries = sorted(boundaries)
            for start, end in zip(ordered_boundaries, ordered_boundaries[1:]):
                if end <= start:
                    continue
                attendees = {
                    student_id
                    for student_id, slots in available_by_student.items()
                    if any(slot_start <= start and slot_end >= end for slot_start, slot_end in slots)
                }
                if not attendees:
                    continue

                count = len(attendees)
                names = sorted(
                    member_names.get(student_id, f"Student {student_id}")
                    for student_id in attendees
                )
                match_rate = round((count / max(total_members, 1)) * 100.0, 1)
                if (
                    results
                    and results[-1]["day_of_week"] == day
                    and results[-1]["study_mode"] == mode
                    and results[-1]["end_time"] == format_time(start)
                    and results[-1]["available_students"] == names
                ):
                    results[-1]["end_time"] = format_time(end)
                    continue
                results.append({
                    "day_of_week": day,
                    "start_time": format_time(start),
                    "end_time": format_time(end),
                    "study_mode": mode,
                    "available_count": count,
                    "total_members": total_members,
                    "match_percentage": match_rate,
                    "available_students": names,
                    "is_unanimous": (count == total_members),
                })

    # Sort primarily by attendance count descending
    results.sort(
        key=lambda r: (
            r["available_count"],
            r["match_percentage"],
            to_minutes(r["end_time"]) - to_minutes(r["start_time"]),
        ),
        reverse=True,
    )
    return results
